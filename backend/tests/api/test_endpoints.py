"""
Integration and unit tests for the FastAPI endpoint routers.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_endpoint_success() -> None:
    """
    Test that POST /api/predict/ returns 200 with prediction payload on valid input.
    """
    payload = {
        "bedrooms": 3,
        "area": 1800.0,
        "neighborhood": "Somerset",
        "has_central_air": 1,
        "has_garage": 1,
        "has_pool": 0,
        "fireplace_count": 1,
        "description_text": "Beautiful house with spacious rooms and luxury details.",
    }
    response = client.post("/api/predict/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "estimated_price" in data
    assert "confidence" in data
    assert "proxy_explainability_factors" in data
    assert "is_below_market_value" in data
    assert "price_tier" in data
    assert "models_used" in data

    assert isinstance(data["estimated_price"], float)
    assert 0.50 <= data["confidence"] <= 0.98
    assert isinstance(data["proxy_explainability_factors"], list)
    assert isinstance(data["is_below_market_value"], bool)
    assert data["price_tier"] in ("Low", "Medium", "High")
    assert data["models_used"]["price_estimator"] == "xgboost_regression"
    assert data["models_used"]["factor_explainer"] == "decision_tree_regression"

    # Regression test: Ensure no single feature attribution dominates unreasonably (max 50% of estimated price)
    estimated_price = data["estimated_price"]
    limit = 0.50 * estimated_price
    for factor in data["proxy_explainability_factors"]:
        assert abs(factor["impact"]) <= limit, (
            f"Spurious attribution: feature '{factor['feature']}' has impact "
            f"${factor['impact']:.2f} which exceeds 50% of estimated price (${estimated_price:.2f})"
        )



def test_predict_endpoint_validation_error() -> None:
    """
    Test that POST /api/predict/ returns 422 when invalid types/ranges are submitted.
    """
    # area <= 0 and has_pool > 1 are invalid
    payload = {
        "bedrooms": 3,
        "area": -50.0,
        "neighborhood": "Somerset",
        "has_central_air": 1,
        "has_garage": 1,
        "has_pool": 2,
        "fireplace_count": 1,
    }
    response = client.post("/api/predict/", json=payload)
    assert response.status_code == 422


def test_similar_properties_endpoint_success() -> None:
    """
    Test that POST /api/similar-properties/ returns 200 with similar listings list.
    """
    payload = {
        "bedrooms": 3,
        "area": 1500.0,
        "neighborhood": "NAmes",
        "has_central_air": 1,
        "has_garage": 1,
        "has_pool": 0,
        "fireplace_count": 0,
        "k": 3,
    }
    response = client.post("/api/similar-properties/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "similar_properties" in data
    assert "model_used" in data
    assert isinstance(data["similar_properties"], list)
    assert data["model_used"] == "knn_retrieval"

    if len(data["similar_properties"]) > 0:
        prop = data["similar_properties"][0]
        assert "external_id" in prop
        assert "title" in prop
        assert "distance" in prop


def test_market_trends_endpoint_success() -> None:
    """
    Test that GET /api/market-trend/ returns 200 with aggregated neighborhood stats.
    """
    response = client.get("/api/market-trend/?version=1.0.0")
    assert response.status_code == 200

    data = response.json()
    assert "feature_set_version" in data
    assert "neighborhood_trends" in data
    assert isinstance(data["neighborhood_trends"], list)

    if len(data["neighborhood_trends"]) > 0:
        trend = data["neighborhood_trends"][0]
        assert "neighborhood" in trend
        assert "median_price" in trend
        assert "median_price_per_sqft" in trend
        assert "total_listings" in trend


def test_model_metrics_endpoint_success() -> None:
    """
    Test that GET /api/model-metrics/ returns 200 with metrics registry log.
    """
    response = client.get("/api/model-metrics/")
    assert response.status_code == 200

    data = response.json()
    assert "xgboost_regression" in data
    assert "metrics" in data["xgboost_regression"]
    assert "rmse" in data["xgboost_regression"]["metrics"]


def test_similar_properties_endpoint_validation_error() -> None:
    """
    Test that POST /api/similar-properties/ returns 422 when invalid parameters (e.g. k <= 0) are provided.
    """
    payload = {
        "bedrooms": 3,
        "area": 1500.0,
        "neighborhood": "NAmes",
        "has_central_air": 1,
        "has_garage": 1,
        "has_pool": 0,
        "fireplace_count": 0,
        "k": -1,  # k must be >= 1
    }
    response = client.post("/api/similar-properties/", json=payload)
    assert response.status_code == 422


def test_predict_endpoint_missing_model_error() -> None:
    """
    Test that POST /api/predict/ handles model file missing errors cleanly without stack trace leakage.
    """
    payload = {
        "bedrooms": 3,
        "area": 1800.0,
        "neighborhood": "Somerset",
        "has_central_air": 1,
        "has_garage": 1,
        "has_pool": 0,
        "fireplace_count": 1,
    }
    from unittest import mock
    with mock.patch("app.ml.predictor.Predictor.run_all_predictions", side_effect=FileNotFoundError("Mock model missing")):
        response = client.post("/api/predict/", json=payload)
        assert response.status_code in (404, 503)
        data = response.json()
        assert "detail" in data
        assert "traceback" not in response.text


def test_listings_endpoint_success() -> None:
    """
    Verify GET /api/listings/ returns a structured payload with listings list and pagination.
    """
    response = client.get("/api/listings/?limit=10&page=1")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "listings" in data
    assert "page" in data
    assert "limit" in data
    assert isinstance(data["listings"], list)


def test_listings_endpoint_error_handling() -> None:
    """
    Verify GET /api/listings/ returns 500 error on database exceptions and hides tracebacks.
    """
    from unittest import mock
    with mock.patch("sqlalchemy.orm.Query.count", side_effect=Exception("Database crash mock")):
        response = client.get("/api/listings/")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "traceback" not in response.text


