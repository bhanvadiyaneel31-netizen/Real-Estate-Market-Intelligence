"""
Unit and integration tests for the background Scheduler and ML training loop resiliency.
"""

import pytest
from unittest import mock
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd

from app.db.models import Base, FeaturedListing
from app.core.scheduler import get_next_feature_version, run_periodic_rescrape_and_retrain
from app.ml.trainer import ModelTrainer
from app.ml.models.classification import LogisticRegressionModel
from app.ml.registry import ModelRegistry


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
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_get_next_feature_version_empty(db_session: Session) -> None:
    """
    Verify get_next_feature_version defaults to '1.0.1' when database table is empty.
    """
    next_ver = get_next_feature_version(db_session)
    assert next_ver == "1.0.1"


def test_get_next_feature_version_increment(db_session: Session) -> None:
    """
    Verify get_next_feature_version correctly increments patch level for semantic versions.
    """
    # Insert mock featured listings for versions '1.0.0' and '1.0.5'
    l1 = FeaturedListing(
        external_id="1001",
        feature_set_version="1.0.0",
        price=150000.0,
        bedrooms=3,
        area=1200.0,
        neighborhood="Somerset",
        price_per_sqft=125.0,
        is_below_market_value=1,
    )
    l2 = FeaturedListing(
        external_id="1002",
        feature_set_version="1.0.5",
        price=200000.0,
        bedrooms=4,
        area=1600.0,
        neighborhood="Somerset",
        price_per_sqft=125.0,
        is_below_market_value=0,
    )
    db_session.add_all([l1, l2])
    db_session.commit()

    next_ver = get_next_feature_version(db_session)
    assert next_ver == "1.0.6"


def test_trainer_resiliency_single_model_failure(db_session: Session) -> None:
    """
    Verify train_all continues fitting other models if a single model throws an exception.
    """
    # Create mock database training listings
    listings = []
    for i in range(10):
        listings.append(
            FeaturedListing(
                external_id=f"100{i}",
                feature_set_version="1.0.0",
                price=150000.0 + i * 10000,
                bedrooms=3,
                area=1200.0 + i * 50,
                neighborhood="Somerset",
                price_per_sqft=125.0,
                is_below_market_value=1 if i < 5 else 0,
            )
        )
    db_session.add_all(listings)
    db_session.commit()

    # Create model trainer
    # Mock registry so we don't write files to the actual saved_models directory during tests
    with mock.patch("app.ml.trainer.ModelRegistry") as mock_reg_cls:
        mock_registry = mock_reg_cls.return_value
        trainer = ModelTrainer(db_session, registry=mock_registry)
        
        # Force LogisticRegressionModel.fit to raise a training exception
        with mock.patch.object(LogisticRegressionModel, "fit", side_effect=ValueError("Training mock error")):
            elapsed, metrics = trainer.train_all(feature_set_version="1.0.0")

            assert elapsed > 0.0
            # Logistic regression metric should be missing (or not updated) due to failure
            assert "logistic_classification" not in metrics
            # But other models (e.g. xgboost_regression, ridge_regression) should be fitted and returned successfully
            assert "xgboost_regression" in metrics
            assert "ridge_regression" in metrics


@mock.patch("app.core.scheduler.AmesSandboxScraper")
@mock.patch("app.core.scheduler.ETLPipeline")
@mock.patch("app.core.scheduler.ModelTrainer")
def test_rescrape_and_retrain_scraper_failure_fallback(
    mock_trainer_cls: mock.MagicMock,
    mock_pipeline_cls: mock.MagicMock,
    mock_scraper_cls: mock.MagicMock,
    db_session: Session,
) -> None:
    """
    Verify periodic job continues and completes model retraining even if scraper encounters network failure.
    """
    # Force scraper.scrape_listings to throw connection exception
    mock_scraper = mock_scraper_cls.return_value
    mock_scraper.scrape_listings.side_effect = ConnectionError("Mock Connection Error")

    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run.return_value = 5  # Returns 5 cleaned featured listings

    mock_trainer = mock_trainer_cls.return_value
    mock_trainer.train_all.return_value = (1.5, {"xgboost_regression": {"r2": 0.85}})

    # Patch SessionLocal to return our in-memory SQLite session
    with mock.patch("app.core.scheduler.SessionLocal", return_value=db_session):
        # Trigger scheduled job
        run_periodic_rescrape_and_retrain()

        # Assert Pipeline.run was called with the next version '1.0.1'
        mock_pipeline_cls.assert_called_once_with(db_session, feature_set_version="1.0.1")
        mock_pipeline.run.assert_called_once()
        
        # Assert Trainer.train_all was triggered
        mock_trainer.train_all.assert_called_once_with(feature_set_version="1.0.1")
