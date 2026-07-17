"""
Unified predictor interface for making price predictions and retrieving comparables.
"""

import logging
from typing import Any, Dict, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import RawListing
from app.ml.registry import ModelRegistry

logger = logging.getLogger("app.ml.predictor")


class Predictor:
    """
    Unified predictor interface used by the FastAPI backend to make predictions
    and retrieve comparable properties using trained models.
    """

    def __init__(self, registry: ModelRegistry = None) -> None:
        """
        Initialize the Predictor with a ModelRegistry.
        """
        self.registry = registry if registry is not None else ModelRegistry()
        self.luxury_keywords = {
            "luxury",
            "beautiful",
            "desirable",
            "spacious",
            "modern",
            "premium",
            "renovated",
            "gorgeous",
            "stunning",
        }

    def _dict_to_df(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Converts a dictionary of features into a single-row pandas DataFrame.
        """
        return pd.DataFrame([features])

    def _enrich_features(self, raw_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically engineer features from raw input parameters to match the schema expected by the models.
        """
        desc_text = raw_features.get("description_text") or ""

        # Construct enriched feature payload
        enriched = {
            "bedrooms": int(raw_features["bedrooms"]),
            "area": float(raw_features["area"]),
            "neighborhood": str(raw_features["neighborhood"]),
            "has_central_air": int(raw_features["has_central_air"]),
            "has_garage": int(raw_features["has_garage"]),
            "has_pool": int(raw_features["has_pool"]),
            "fireplace_count": int(raw_features["fireplace_count"]),
            "description_text": desc_text,
        }
        return enriched


    def get_confidence_score(self, estimated_price: float) -> float:
        """
        Calculate prediction confidence dynamically using XGBoost's test RMSE.
        Logs a warning if the metrics file is missing or has no RMSE key, falling back to baseline.
        """
        default_rmse = 32652.47
        rmse = default_rmse

        try:
            all_metrics = self.registry.get_all_metrics()
            xgb_entry = all_metrics.get("xgboost_regression", {})
            metrics = xgb_entry.get("metrics", {})
            val = metrics.get("rmse")

            if val is not None:
                rmse = float(val)
            else:
                logger.warning(
                    "Model registry is missing the 'rmse' key for 'xgboost_regression'. "
                    f"Using default fallback RMSE (${default_rmse:,.2f})."
                )
        except Exception as e:
            logger.warning(
                f"Failed to load metrics from model registry: {e}. "
                f"Using default fallback RMSE (${default_rmse:,.2f})."
            )

        # Confidence heuristic: 1.0 - (1.2 * RMSE / Price)
        val_conf = 1.0 - (1.2 * rmse) / (estimated_price + 1e-5)
        return float(max(0.5, min(0.98, val_conf)))

    def run_all_predictions(self, raw_features: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Run price prediction, binary classification, price-tier, and proxy explainability factors.

        Returns:
            Tuple[Dict[str, Any], Dict[str, str]]: Prediction payload dictionary and models used dictionary.
        """
        enriched = self._enrich_features(raw_features)
        df = self._dict_to_df(enriched)

        # 1. Price Estimation (XGBoost)
        xgb_model = self.registry.load_model("xgboost_regression")
        pred_price = float(xgb_model.predict(df)[0])

        # 2. Confidence Score (Dynamic RMSE)
        confidence = self.get_confidence_score(pred_price)

        # 3. Proxy Explainability Factors (Decision Tree interpreter)
        proxy_factors = []
        try:
            dt_model = self.registry.load_model("decision_tree_regression")
            # Decision Tree explain_prediction is defined on DecisionTreeRegressionModel wrapper
            if hasattr(dt_model, "explain_prediction"):
                proxy_factors = dt_model.explain_prediction(df)
        except Exception as e:
            logger.error(f"Failed to generate proxy factors from Decision Tree model: {e}")

        # 4. Below Market Value Class (Logistic Regression)
        log_model = self.registry.load_model("logistic_classification")
        is_below = bool(log_model.predict(df)[0] == 1)

        # 5. Price Tier Class (SVM)
        svm_model = self.registry.load_model("svm_classification")
        price_tier = str(svm_model.predict(df)[0])

        payload = {
            "estimated_price": pred_price,
            "confidence": confidence,
            "proxy_explainability_factors": proxy_factors,
            "is_below_market_value": is_below,
            "price_tier": price_tier,
        }

        models_used = {
            "price_estimator": "xgboost_regression",
            "factor_explainer": "decision_tree_regression",
            "below_market_classifier": "logistic_classification",
            "price_tier_classifier": "svm_classification",
        }

        return payload, models_used

    def predict_price(self, raw_features: Dict[str, Any]) -> float:
        """
        Helper method to predict property price.
        """
        enriched = self._enrich_features(raw_features)
        df = self._dict_to_df(enriched)
        model = self.registry.load_model("xgboost_regression")
        return float(model.predict(df)[0])

    def predict_is_below_market_value(self, raw_features: Dict[str, Any]) -> int:
        """
        Helper method to predict below market value target.
        """
        enriched = self._enrich_features(raw_features)
        df = self._dict_to_df(enriched)
        model = self.registry.load_model("logistic_classification")
        return int(model.predict(df)[0])

    def predict_price_tier(self, raw_features: Dict[str, Any]) -> str:
        """
        Helper method to predict price tier.
        """
        enriched = self._enrich_features(raw_features)
        df = self._dict_to_df(enriched)
        model = self.registry.load_model("svm_classification")
        return str(model.predict(df)[0])

    def get_similar_properties(
        self, db: Session, raw_features: Dict[str, Any], k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve K similar properties using the KNN model, fetching raw listing details from the DB.
        """
        # KNN features are subset: bedrooms, area, neighborhood, central_air, garage, pool, fireplace_count
        enriched = self._enrich_features(raw_features)
        df = self._dict_to_df(enriched)

        model = self.registry.load_model("knn_retrieval")
        neighbor_ids, distances = model.query_neighbors(df, k=k)
        if not neighbor_ids or len(neighbor_ids[0]) == 0:
            return []

        ids_to_fetch = neighbor_ids[0]
        dist_map = dict(zip(ids_to_fetch, distances[0]))

        # Query database for raw listing details
        raw_listings = (
            db.query(RawListing)
            .filter(RawListing.external_id.in_(ids_to_fetch))
            .order_by(RawListing.scraped_at.desc())
            .all()
        )

        fetched_dict = {}
        for rl in raw_listings:
            if rl.external_id not in fetched_dict:
                fetched_dict[rl.external_id] = {
                    "external_id": rl.external_id,
                    "title": rl.title,
                    "price": rl.price,
                    "location": rl.location,
                    "bedrooms": rl.bedrooms,
                    "area": rl.area,
                    "amenities": rl.amenities,
                    "description_text": rl.description_text,
                    "distance": float(dist_map.get(rl.external_id, 0.0)),
                }

        result = []
        for ext_id in ids_to_fetch:
            if ext_id in fetched_dict:
                result.append(fetched_dict[ext_id])

        return result
