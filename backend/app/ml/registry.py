"""
Model registry for loading, saving, and managing trained models and metrics.
"""

import json
import logging
import os
from typing import Any, Dict
from app.ml.models.base import BaseAppModel

logger = logging.getLogger("app.ml.registry")


class ModelRegistry:
    """
    ModelRegistry handles saving/loading model artifacts and maintaining the metrics.json log.
    """

    def __init__(self, base_dir: str = None) -> None:
        """
        Initialize ModelRegistry. If base_dir is None, defaults to app/ml/saved_models/.
        """
        if base_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.join(current_dir, "saved_models")
        else:
            self.base_dir = base_dir

        os.makedirs(self.base_dir, exist_ok=True)
        self.metrics_filepath = os.path.join(self.base_dir, "metrics.json")

    def save_model(
        self, model_name: str, model_obj: BaseAppModel, metrics: Dict[str, float]
    ) -> str:
        """
        Serialize model and update metrics in metrics.json.
        """
        filepath = os.path.join(self.base_dir, f"{model_name}.joblib")
        logger.info(f"Saving model {model_name} to {filepath}...")
        model_obj.save(filepath)

        # Load existing metrics
        all_metrics = self.get_all_metrics()

        # Handle legacy flat structure migration
        is_legacy = any(isinstance(v, dict) and "metrics" in v for v in all_metrics.values())
        if is_legacy:
            legacy_data = {k: v for k, v in all_metrics.items() if isinstance(v, dict) and "metrics" in v}
            all_metrics = {"1.0.0": legacy_data}

        version = model_obj.feature_set_version or "1.0.0"
        if version not in all_metrics:
            all_metrics[version] = {}

        all_metrics[version][model_name] = {
            "metrics": metrics,
            "trained_at": model_obj.trained_at,
            "feature_set_version": version,
        }

        # Write metrics
        try:
            with open(self.metrics_filepath, "w") as f:
                json.dump(all_metrics, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write metrics to {self.metrics_filepath}: {e}")

        return filepath

    def load_model(self, model_name: str) -> BaseAppModel:
        """
        Load model wrapper from registry.
        """
        filepath = os.path.join(self.base_dir, f"{model_name}.joblib")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file {filepath} not found.")
        logger.info(f"Loading model {model_name} from {filepath}...")
        return BaseAppModel.load(filepath)

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Read the consolidated metrics file.
        """
        if not os.path.exists(self.metrics_filepath):
            return {}
        try:
            with open(self.metrics_filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read metrics from {self.metrics_filepath}: {e}")
            return {}

    def get_latest_metrics(self) -> Dict[str, Any]:
        """
        Return the metrics of the latest trained version.
        """
        all_metrics = self.get_all_metrics()
        if not all_metrics:
            return {}

        # If it is legacy flat configuration
        is_nested = all(isinstance(v, dict) and not ("metrics" in v) for v in all_metrics.values())
        if not is_nested:
            return all_metrics

        latest_version = None
        latest_time = None
        for version, models in all_metrics.items():
            for model_name, model_info in models.items():
                trained_at = model_info.get("trained_at", "")
                if not latest_time or trained_at > latest_time:
                    latest_time = trained_at
                    latest_version = version

        if latest_version:
            return all_metrics[latest_version]

        sorted_versions = sorted(all_metrics.keys())
        if sorted_versions:
            return all_metrics[sorted_versions[-1]]

        return {}

