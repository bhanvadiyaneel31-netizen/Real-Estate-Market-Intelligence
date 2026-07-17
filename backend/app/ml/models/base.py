"""
Abstract base class defining the shared interface for all machine learning models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union
import joblib
import pandas as pd
import numpy as np


class BaseAppModel(ABC):
    """
    Abstract Base Class for all machine learning models in the platform.
    Ensures a consistent interface for training, prediction, evaluation, and serialization.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize the base model.
        """
        self.feature_set_version: str = feature_set_version
        self.trained_at: Union[str, None] = None
        self.pipeline: Any = None  # To hold the scikit-learn Pipeline (preprocessing + estimator)

    @abstractmethod
    def fit(self, df_train: pd.DataFrame) -> None:
        """
        Train the model using the training DataFrame.
        """
        pass

    @abstractmethod
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on the input DataFrame.
        """
        pass

    @abstractmethod
    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate the model on a test DataFrame and return a dict of metrics.
        """
        pass

    def save(self, filepath: str) -> None:
        """
        Serialize the model wrapper (including preprocessing pipeline) to a file.
        """
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "BaseAppModel":
        """
        Load a serialized model wrapper from a file.
        """
        model = joblib.load(filepath)
        return model
