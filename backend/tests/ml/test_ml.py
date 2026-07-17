"""
Unit tests for all machine learning models, predictor, and model registry.
"""

import os
import shutil
import tempfile
from typing import Generator
import numpy as np
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import Base, RawListing, FeaturedListing
from app.ml.models import (
    DecisionTreeRegressionModel,
    KNNRetrievalModel,
    LassoRegressionModel,
    LinearRegressionModel,
    LogisticRegressionModel,
    NaiveBayesTextModel,
    RandomForestRegressionModel,
    RidgeRegressionModel,
    SVMPriceTierModel,
    XGBoostRegressionModel,
)
from app.ml.predictor import Predictor
from app.ml.registry import ModelRegistry


@pytest.fixture
def registry_dir() -> Generator[str, None, None]:
    """
    Provides a temporary directory for ModelRegistry.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


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


@pytest.fixture
def dummy_train_data() -> pd.DataFrame:
    """
    Generate mock training data representing featured listings.
    """
    np.random.seed(42)
    n_samples = 30
    return pd.DataFrame(
        {
            "external_id": [str(1000 + i) for i in range(n_samples)],
            "price": np.random.uniform(50000.0, 500000.0, n_samples),
            "bedrooms": np.random.randint(1, 6, n_samples),
            "area": np.random.uniform(500.0, 3000.0, n_samples),
            "neighborhood": np.random.choice(["Somerset", "CollegeCreek", "NAmes"], n_samples),
            "has_central_air": np.random.randint(0, 2, n_samples),
            "has_garage": np.random.randint(0, 2, n_samples),
            "has_pool": np.random.randint(0, 2, n_samples),
            "fireplace_count": np.random.randint(0, 3, n_samples),
            "price_per_sqft": np.random.uniform(50.0, 250.0, n_samples),
            "description_length": np.random.randint(20, 200, n_samples),
            "has_luxury_keywords": np.random.randint(0, 2, n_samples),
            "is_below_market_value": np.random.randint(0, 2, n_samples),
            "description_text": [
                f"House {i} is in Somerset and is very beautiful" for i in range(n_samples)
            ],
        }
    )


def test_regression_models(dummy_train_data: pd.DataFrame) -> None:
    """
    Verify all regression models fit, predict, and evaluate successfully.
    """
    regression_models = [
        LinearRegressionModel(),
        RidgeRegressionModel(),
        LassoRegressionModel(),
        RandomForestRegressionModel(),
        XGBoostRegressionModel(),
        DecisionTreeRegressionModel(),
    ]

    for model in regression_models:
        model.fit(dummy_train_data)
        preds = model.predict(dummy_train_data)
        assert len(preds) == len(dummy_train_data)
        assert isinstance(preds, np.ndarray)

        metrics = model.evaluate(dummy_train_data)
        assert "rmse" in metrics
        assert "r2" in metrics
        assert isinstance(metrics["rmse"], float)
        assert isinstance(metrics["r2"], float)


def test_classification_models(dummy_train_data: pd.DataFrame) -> None:
    """
    Verify all classification models fit, predict, and evaluate successfully.
    """
    classification_models = [
        LogisticRegressionModel(),
        SVMPriceTierModel(),
        NaiveBayesTextModel(),
    ]

    for model in classification_models:
        model.fit(dummy_train_data)
        preds = model.predict(dummy_train_data)
        assert len(preds) == len(dummy_train_data)

        metrics = model.evaluate(dummy_train_data)
        assert "accuracy" in metrics
        assert isinstance(metrics["accuracy"], float)


def test_knn_retrieval_model(dummy_train_data: pd.DataFrame) -> None:
    """
    Verify KNN retrieval model correctly fits and queries neighbors.
    """
    model = KNNRetrievalModel()
    model.fit(dummy_train_data)

    # Test predict dummy implementation
    preds = model.predict(dummy_train_data.head(5))
    assert len(preds) == 5

    # Test neighbor queries
    neighbor_ids, distances = model.query_neighbors(dummy_train_data.head(3), k=5)
    assert len(neighbor_ids) == 3
    assert len(neighbor_ids[0]) == 5
    assert isinstance(distances, np.ndarray)
    assert distances.shape == (3, 5)

    # Check metrics
    metrics = model.evaluate(dummy_train_data)
    assert "mean_neighbor_distance" in metrics


def test_model_registry_flow(
    dummy_train_data: pd.DataFrame, registry_dir: str
) -> None:
    """
    Verify registry properly dumps and reloads model instances.
    """
    registry = ModelRegistry(base_dir=registry_dir)
    model = XGBoostRegressionModel()
    model.fit(dummy_train_data)

    metrics = {"rmse": 12000.0, "r2": 0.85}
    registry.save_model("xgb_test", model, metrics)

    # Reload from registry
    loaded_model = registry.load_model("xgb_test")
    assert isinstance(loaded_model, XGBoostRegressionModel)
    assert loaded_model.feature_set_version == "1.0.0"

    # Make predictions with loaded model
    preds = loaded_model.predict(dummy_train_data)
    assert len(preds) == len(dummy_train_data)

    # Verify metrics list is written
    all_metrics = registry.get_latest_metrics()
    assert "xgb_test" in all_metrics
    assert all_metrics["xgb_test"]["metrics"]["r2"] == 0.85



def test_predictor_queries(
    dummy_train_data: pd.DataFrame, registry_dir: str, db_session: Session
) -> None:
    """
    Verify predictor loads models from registry and successfully makes predictions.
    """
    # 1. Fit and save models to mock registry directory
    registry = ModelRegistry(base_dir=registry_dir)

    xgb = XGBoostRegressionModel()
    xgb.fit(dummy_train_data)
    registry.save_model("xgboost_regression", xgb, {"rmse": 10.0})

    log_reg = LogisticRegressionModel()
    log_reg.fit(dummy_train_data)
    registry.save_model("logistic_classification", log_reg, {"accuracy": 0.9})

    svm = SVMPriceTierModel()
    svm.fit(dummy_train_data)
    registry.save_model("svm_classification", svm, {"accuracy": 0.8})

    knn = KNNRetrievalModel()
    knn.fit(dummy_train_data)
    registry.save_model("knn_retrieval", knn, {"dist": 0.1})

    # Add mock raw listing records to db_session to mock comparables fetching
    for _, row in dummy_train_data.iterrows():
        rl = RawListing(
            source="ames_sandbox",
            external_id=row["external_id"],
            url=f"http://sandbox/{row['external_id']}",
            title=f"Title {row['external_id']}",
            price=f"${int(row['price']):,}",
            location=f"{row['neighborhood']}, Ames, IA",
            bedrooms=f"{int(row['bedrooms'])} BR",
            area=f"{int(row['area'])} sqft",
        )
        db_session.add(rl)
    db_session.commit()

    # 2. Instantiate Predictor and query endpoints
    predictor = Predictor(registry=registry)
    query_features = {
        "bedrooms": 3,
        "area": 1500.0,
        "neighborhood": "Somerset",
        "has_central_air": 1,
        "has_garage": 1,
        "has_pool": 0,
        "fireplace_count": 1,
        "description_length": 100,
        "has_luxury_keywords": 1,
    }

    # Price estimation
    price_pred = predictor.predict_price(query_features)
    assert isinstance(price_pred, float)

    # Below market value flag
    below_mv = predictor.predict_is_below_market_value(query_features)
    assert below_mv in (0, 1)

    # Price tier
    tier = predictor.predict_price_tier(query_features)
    assert tier in ("Low", "Medium", "High")

    # Comparables retrieval
    comparables = predictor.get_similar_properties(db_session, query_features, k=3)
    assert len(comparables) == 3
    assert "price" in comparables[0]
    assert "distance" in comparables[0]
