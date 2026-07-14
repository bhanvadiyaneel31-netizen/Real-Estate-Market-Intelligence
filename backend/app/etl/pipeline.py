"""
ETL Pipeline module for coordinating cleaning, feature engineering, and database upserts.
"""

import logging
from sqlalchemy.orm import Session
from app.db.models import RawListing, FeaturedListing
from app.etl.cleaner import PropertyCleaner
from app.etl.feature_engineer import PropertyFeatureEngineer

logger = logging.getLogger("app.etl.pipeline")


class ETLPipeline:
    """
    ETLPipeline orchestrates the loading, cleaning, feature engineering,
    and storage of real estate listings.
    """

    def __init__(self, db: Session, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize ETLPipeline with db session and version.
        """
        self.db = db
        self.feature_set_version = feature_set_version
        self.cleaner = PropertyCleaner()
        self.feature_engineer = PropertyFeatureEngineer()

    def run(self) -> int:
        """
        Executes the ETL pipeline:
        1. Loads raw listings from raw_listings table.
        2. Deduplicates raw listings (keeps the latest by scraped_at).
        3. Cleans listings.
        4. Engineers features.
        5. Writes/upserts records into featured_listings table.

        Returns:
            int: Number of featured listings saved.
        """
        logger.info(f"Starting ETL Pipeline for version: {self.feature_set_version}")

        # 1. Load raw listings (order by scraped_at desc so latest is seen first)
        raw_query = self.db.query(RawListing).order_by(RawListing.scraped_at.desc()).all()
        if not raw_query:
            logger.warning("No raw listings found in the database. Cannot run ETL.")
            return 0

        # 2. Deduplicate raw listings by external_id (keeping the latest based on order_by desc)
        seen_ids = set()
        deduplicated_raw = []
        for rl in raw_query:
            if rl.external_id not in seen_ids:
                seen_ids.add(rl.external_id)
                deduplicated_raw.append(rl)

        logger.info(
            f"Loaded {len(raw_query)} raw listings. Deduplicated to {len(deduplicated_raw)} unique listings."
        )

        # 3. Clean listings
        df_cleaned = self.cleaner.clean_listings(deduplicated_raw)
        if df_cleaned.empty:
            logger.warning("No listings left after cleaning.")
            return 0

        # 4. Feature engineering
        df_featured = self.feature_engineer.engineer_features(df_cleaned)
        if df_featured.empty:
            logger.warning("No listings left after feature engineering.")
            return 0

        # 5. Write to DB
        try:
            # Delete existing features for this version to overwrite/refresh cleanly
            deleted_count = (
                self.db.query(FeaturedListing)
                .filter(FeaturedListing.feature_set_version == self.feature_set_version)
                .delete()
            )
            if deleted_count > 0:
                logger.info(
                    f"Cleared {deleted_count} existing featured listings for version {self.feature_set_version}."
                )

            saved_count = 0
            for _, row in df_featured.iterrows():
                featured_listing = FeaturedListing(
                    external_id=row["external_id"],
                    feature_set_version=self.feature_set_version,
                    price=row["price"],
                    bedrooms=row["bedrooms"],
                    area=row["area"],
                    neighborhood=row["neighborhood"],
                    has_central_air=row["has_central_air"],
                    has_garage=row["has_garage"],
                    has_pool=row["has_pool"],
                    fireplace_count=row["fireplace_count"],
                    price_per_sqft=row["price_per_sqft"],
                    description_length=row["description_length"],
                    has_luxury_keywords=row["has_luxury_keywords"],
                    is_below_market_value=row["is_below_market_value"],
                )
                self.db.add(featured_listing)
                saved_count += 1

            self.db.commit()
            logger.info(f"Successfully saved {saved_count} featured listings to the database.")
            return saved_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during database transaction in ETL pipeline: {e}", exc_info=True)
            raise e
