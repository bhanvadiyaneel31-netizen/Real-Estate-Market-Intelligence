"""
Trainer class for orchestrating the training and evaluation of all machine learning models.
"""

from datetime import datetime
import logging
import time
from typing import Dict, Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from app.db.models import FeaturedListing, RawListing
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
from app.ml.registry import ModelRegistry

logger = logging.getLogger("app.ml.trainer")


class ModelTrainer:
    """
    Orchestrates data loading, train/test splitting, fitting, evaluating,
    and registering all 10 models.
    """

    def __init__(self, db: Session, registry: ModelRegistry = None) -> None:
        """
        Initialize the trainer.
        """
        self.db = db
        self.registry = registry if registry is not None else ModelRegistry()

    def load_data(self, feature_set_version: str) -> pd.DataFrame:
        """
        Load clean/featured listings and join with raw description text.
        """
        featured = (
            self.db.query(FeaturedListing)
            .filter(FeaturedListing.feature_set_version == feature_set_version)
            .all()
        )
        if not featured:
            return pd.DataFrame()

        # Query raw descriptions, order by scraped_at desc to deduplicate in memory
        raw_sub = (
            self.db.query(RawListing.external_id, RawListing.description_text)
            .order_by(RawListing.scraped_at.desc())
            .all()
        )

        raw_desc = {}
        for ext_id, desc in raw_sub:
            if ext_id not in raw_desc:
                raw_desc[ext_id] = desc

        data = []
        for f in featured:
            data.append(
                {
                    "external_id": f.external_id,
                    "price": f.price,
                    "bedrooms": f.bedrooms,
                    "area": f.area,
                    "neighborhood": f.neighborhood,
                    "has_central_air": f.has_central_air,
                    "has_garage": f.has_garage,
                    "has_pool": f.has_pool,
                    "fireplace_count": f.fireplace_count,
                    "price_per_sqft": f.price_per_sqft,
                    "description_length": f.description_length,
                    "has_luxury_keywords": f.has_luxury_keywords,
                    "is_below_market_value": f.is_below_market_value,
                    "description_text": raw_desc.get(f.external_id, ""),
                }
            )

        return pd.DataFrame(data)

    def train_all(self, feature_set_version: str = "1.0.0") -> Tuple[float, Dict[str, Dict[str, float]]]:
        """
        Perform stratified train/test split, train all 10 models, evaluate, and save artifacts.

        Returns:
            Tuple[float, dict]: Elapsed time in seconds and test metrics dictionary.
        """
        start_time = time.time()
        df = self.load_data(feature_set_version)
        if df.empty:
            raise ValueError(f"No featured listings found for version: {feature_set_version}")

        # 80/20 stratified split based on binary class target
        df_train, df_test = train_test_split(
            df, test_size=0.2, random_state=42, stratify=df["is_below_market_value"]
        )

        logger.info(
            f"Loaded {len(df)} listings. Train size: {len(df_train)}, Test size: {len(df_test)}."
        )

        # Instantiate all 10 models
        models = {
            "linear_regression": LinearRegressionModel(feature_set_version),
            "ridge_regression": RidgeRegressionModel(feature_set_version),
            "lasso_regression": LassoRegressionModel(feature_set_version),
            "random_forest_regression": RandomForestRegressionModel(feature_set_version),
            "xgboost_regression": XGBoostRegressionModel(feature_set_version),
            "decision_tree_regression": DecisionTreeRegressionModel(feature_set_version),
            "logistic_classification": LogisticRegressionModel(feature_set_version),
            "svm_classification": SVMPriceTierModel(feature_set_version),
            "naive_bayes_text": NaiveBayesTextModel(feature_set_version),
            "knn_retrieval": KNNRetrievalModel(feature_set_version),
        }

        metrics_summary = {}
        for name, model in models.items():
            model_start = time.time()
            logger.info(f"Fitting model: {name}...")
            try:
                # Fit model
                model.fit(df_train)
                model.trained_at = datetime.utcnow().isoformat()

                # Evaluate on held-out test split
                eval_metrics = model.evaluate(df_test)
                metrics_summary[name] = eval_metrics

                # Persist artifact & metrics
                self.registry.save_model(name, model, eval_metrics)

                logger.info(
                    f"Finished {name} in {time.time() - model_start:.2f}s. Metrics: {eval_metrics}"
                )
            except Exception as e:
                logger.error(f"Failed to fit or evaluate model '{name}': {e}", exc_info=True)

        elapsed = time.time() - start_time
        return elapsed, metrics_summary

