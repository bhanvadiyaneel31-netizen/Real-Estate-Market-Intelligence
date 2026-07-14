"""
Unit tests for PropertyCleaner, PropertyFeatureEngineer, and ETLPipeline.
"""

from datetime import datetime, timedelta
from typing import Generator
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import Base, RawListing, FeaturedListing
from app.etl.cleaner import PropertyCleaner
from app.etl.feature_engineer import PropertyFeatureEngineer
from app.etl.pipeline import ETLPipeline


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Fixture providing an in-memory SQLite database session.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    try:
        yield session
    finally:
        session.close()


def test_property_cleaner_happy_path() -> None:
    """
    Test that cleaner correctly parses numbers, location, and drops missing values.
    """
    cleaner = PropertyCleaner()
    raw_data = [
        {
            "external_id": "1",
            "title": "Property 1",
            "price": "$150,000",
            "location": "CollegeCreek, Ames, IA",
            "bedrooms": "3 BR",
            "area": "1,200 sqft",
            "amenities": "Central Air, Garage",
            "description_text": "Beautiful house",
        },
        {
            "external_id": "2",
            "title": "Property 2",
            "price": "200000.0",
            "location": "Somerset, Ames, IA",
            "bedrooms": 4,
            "area": 1500,
            "amenities": "None",
            "description_text": "Nice home",
        },
    ]

    df = cleaner.clean_listings(raw_data)
    assert len(df) == 2
    assert df.loc[0, "price"] == 150000.0
    assert df.loc[0, "area"] == 1200.0
    assert df.loc[0, "bedrooms"] == 3
    assert df.loc[0, "neighborhood"] == "CollegeCreek"

    assert df.loc[1, "price"] == 200000.0
    assert df.loc[1, "area"] == 1500.0
    assert df.loc[1, "bedrooms"] == 4
    assert df.loc[1, "neighborhood"] == "Somerset"


def test_property_cleaner_missing_and_outliers() -> None:
    """
    Test that cleaner drops missing fields and filters outliers.
    """
    cleaner = PropertyCleaner(
        price_min=50000.0, price_max=500000.0, area_min=500.0, area_max=4000.0
    )

    raw_data = [
        # Valid listing
        {
            "external_id": "1",
            "price": "$150,000",
            "location": "Somerset, Ames, IA",
            "bedrooms": "3 BR",
            "area": "1200 sqft",
        },
        # Missing price -> dropped
        {
            "external_id": "2",
            "price": None,
            "location": "Somerset, Ames, IA",
            "bedrooms": "3 BR",
            "area": "1200 sqft",
        },
        # Missing location -> dropped
        {
            "external_id": "3",
            "price": "$150,000",
            "location": None,
            "bedrooms": "3 BR",
            "area": "1200 sqft",
        },
        # Price too high outlier -> dropped
        {
            "external_id": "4",
            "price": "$800,000",
            "location": "Somerset, Ames, IA",
            "bedrooms": "3 BR",
            "area": "1200 sqft",
        },
        # Area too small outlier -> dropped
        {
            "external_id": "5",
            "price": "$150,000",
            "location": "Somerset, Ames, IA",
            "bedrooms": "3 BR",
            "area": "200 sqft",
        },
        # Bedrooms too large outlier -> dropped
        {
            "external_id": "6",
            "price": "$150,000",
            "location": "Somerset, Ames, IA",
            "bedrooms": "12 BR",
            "area": "1200 sqft",
        },
    ]

    df = cleaner.clean_listings(raw_data)
    assert len(df) == 1
    assert df.iloc[0]["external_id"] == "1"


def test_property_feature_engineer_metrics() -> None:
    """
    Test extraction of price_per_sqft, amenities flags, and text features.
    """
    fe = PropertyFeatureEngineer()

    # Raw cleaned dataframe input
    df_cleaned = pd.DataFrame(
        [
            {
                "external_id": "1",
                "price": 100000.0,
                "area": 1000.0,
                "bedrooms": 2,
                "neighborhood": "Somerset",
                "amenities": "Central Air, Garage (Attchd), 2 Fireplace(s)",
                "description_text": "A beautiful and luxurious home in Somerset.",
            },
            {
                "external_id": "2",
                "price": 200000.0,
                "area": 2000.0,
                "bedrooms": 4,
                "neighborhood": "Somerset",
                "amenities": "Pool, Fireplace",
                "description_text": "Plain house with no keywords.",
            },
            {
                "external_id": "3",
                "price": 300000.0,
                "area": 1500.0,
                "bedrooms": 3,
                "neighborhood": "Somerset",
                "amenities": "None",
                "description_text": None,
            },
        ]
    )

    df_featured = fe.engineer_features(df_cleaned)

    assert len(df_featured) == 3

    # Check price_per_sqft
    assert df_featured.loc[0, "price_per_sqft"] == 100.0
    assert df_featured.loc[1, "price_per_sqft"] == 100.0
    assert df_featured.loc[2, "price_per_sqft"] == 200.0

    # Check amenities flags
    assert df_featured.loc[0, "has_central_air"] == 1
    assert df_featured.loc[0, "has_garage"] == 1
    assert df_featured.loc[0, "has_pool"] == 0
    assert df_featured.loc[0, "fireplace_count"] == 2

    assert df_featured.loc[1, "has_central_air"] == 0
    assert df_featured.loc[1, "has_garage"] == 0
    assert df_featured.loc[1, "has_pool"] == 1
    assert df_featured.loc[1, "fireplace_count"] == 1

    assert df_featured.loc[2, "has_central_air"] == 0
    assert df_featured.loc[2, "fireplace_count"] == 0

    # Check description text features
    assert df_featured.loc[0, "description_length"] == 43
    assert df_featured.loc[0, "has_luxury_keywords"] == 1  # "luxury" / "beautiful"

    assert df_featured.loc[1, "description_length"] == 29
    assert df_featured.loc[1, "has_luxury_keywords"] == 0

    assert df_featured.loc[2, "description_length"] == 0
    assert df_featured.loc[2, "has_luxury_keywords"] == 0


def test_property_feature_engineer_is_below_market_value() -> None:
    """
    Test target variable (is_below_market_value) relative to neighborhood medians,
    verifying fallback to city-wide median for neighborhoods with < 5 listings.
    """
    fe = PropertyFeatureEngineer()

    # Somerset count = 5 (>= 5, uses Somerset median = 200k)
    # CollegeCreek count = 2 (< 5, falls back to city-wide median = 180k)
    # Sorted overall: 100k, 120k, 150k, 180k, 200k, 250k, 300k -> city median = 180k
    df_cleaned = pd.DataFrame(
        [
            {"price": 100000.0, "area": 1000.0, "neighborhood": "Somerset", "amenities": "", "description_text": ""},
            {"price": 150000.0, "area": 1000.0, "neighborhood": "Somerset", "amenities": "", "description_text": ""},
            {"price": 200000.0, "area": 1000.0, "neighborhood": "Somerset", "amenities": "", "description_text": ""},
            {"price": 250000.0, "area": 1000.0, "neighborhood": "Somerset", "amenities": "", "description_text": ""},
            {"price": 300000.0, "area": 1000.0, "neighborhood": "Somerset", "amenities": "", "description_text": ""},
            {"price": 120000.0, "area": 1000.0, "neighborhood": "CollegeCreek", "amenities": "", "description_text": ""},
            {"price": 180000.0, "area": 1000.0, "neighborhood": "CollegeCreek", "amenities": "", "description_text": ""},
        ]
    )

    df_featured = fe.engineer_features(df_cleaned)

    # Somerset listings (target_median = Somerset median = 200k)
    # 100k < 200k -> 1
    # 150k < 200k -> 1
    # 200k < 200k -> 0
    # 250k < 200k -> 0
    # 300k < 200k -> 0
    assert df_featured.iloc[0]["is_below_market_value"] == 1
    assert df_featured.iloc[1]["is_below_market_value"] == 1
    assert df_featured.iloc[2]["is_below_market_value"] == 0
    assert df_featured.iloc[3]["is_below_market_value"] == 0
    assert df_featured.iloc[4]["is_below_market_value"] == 0

    # CollegeCreek listings (target_median = city median = 180k)
    # 120k < 180k -> 1
    # 180k < 180k -> 0
    assert df_featured.iloc[5]["is_below_market_value"] == 1
    assert df_featured.iloc[6]["is_below_market_value"] == 0



def test_etl_pipeline_integration(db_session: Session) -> None:
    """
    Test end-to-end ETLPipeline execution, including deduplication and database persistence.
    """
    # 1. Insert raw listings (one duplicate to test deduplication)
    now = datetime.utcnow()
    raw_1_old = RawListing(
        source="ames_sandbox",
        external_id="1001",
        url="http://sandbox/1001",
        title="House 1",
        price="$150,000",
        location="Somerset, Ames, IA",
        bedrooms="3 BR",
        area="1200 sqft",
        amenities="Central Air",
        description_text="Spacious property",
        scraped_at=now - timedelta(hours=2),
    )
    raw_1_new = RawListing(
        source="ames_sandbox",
        external_id="1001",
        url="http://sandbox/1001",
        title="House 1 updated price",
        price="$140,000",  # Updated price
        location="Somerset, Ames, IA",
        bedrooms="3 BR",
        area="1200 sqft",
        amenities="Central Air, Garage",
        description_text="Spacious property",
        scraped_at=now,
    )
    raw_2 = RawListing(
        source="ames_sandbox",
        external_id="1002",
        url="http://sandbox/1002",
        title="House 2",
        price="$250,000",
        location="Somerset, Ames, IA",
        bedrooms="4 BR",
        area="2000 sqft",
        amenities="Pool",
        description_text="Beautiful estate",
        scraped_at=now,
    )

    db_session.add_all([raw_1_old, raw_1_new, raw_2])
    db_session.commit()

    # 2. Run ETL pipeline
    pipeline = ETLPipeline(db_session, feature_set_version="1.0.0")
    saved_count = pipeline.run()

    # We have 2 unique listings (1001 and 1002). Both should be saved.
    assert saved_count == 2

    # Query featured_listings
    featured = db_session.query(FeaturedListing).all()
    assert len(featured) == 2

    # Verify latest raw listing was cleaned & featured (140,000 instead of 150,000)
    feat_1001 = db_session.query(FeaturedListing).filter_by(external_id="1001").first()
    assert feat_1001 is not None
    assert feat_1001.price == 140000.0
    assert feat_1001.has_garage == 1
    assert feat_1001.feature_set_version == "1.0.0"

    feat_1002 = db_session.query(FeaturedListing).filter_by(external_id="1002").first()
    assert feat_1002 is not None
    assert feat_1002.price == 250000.0
    assert feat_1002.has_pool == 1

    # Verify target variable: is_below_market_value
    # Prices: 1001 is 140k, 1002 is 250k.
    # Neighborhood median (Somerset) = (140k + 250k)/2 = 195k.
    # 1001 price (140k) < 195k -> 1
    # 1002 price (250k) >= 195k -> 0
    assert feat_1001.is_below_market_value == 1
    assert feat_1002.is_below_market_value == 0

    # 3. Test overwrite functionality
    # Run pipeline again with same version, should not create duplicates
    saved_count_again = pipeline.run()
    assert saved_count_again == 2
    assert db_session.query(FeaturedListing).count() == 2
