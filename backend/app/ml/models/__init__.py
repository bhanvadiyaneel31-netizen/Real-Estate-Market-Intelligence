"""
Model classes package for regression, classification, and retrieval.
"""

from app.ml.models.base import BaseAppModel
from app.ml.models.regression import (
    LinearRegressionModel,
    RidgeRegressionModel,
    LassoRegressionModel,
    RandomForestRegressionModel,
    XGBoostRegressionModel,
    DecisionTreeRegressionModel,
)
from app.ml.models.classification import (
    LogisticRegressionModel,
    SVMPriceTierModel,
    NaiveBayesTextModel,
)
from app.ml.models.knn import KNNRetrievalModel

__all__ = [
    "BaseAppModel",
    "LinearRegressionModel",
    "RidgeRegressionModel",
    "LassoRegressionModel",
    "RandomForestRegressionModel",
    "XGBoostRegressionModel",
    "DecisionTreeRegressionModel",
    "LogisticRegressionModel",
    "SVMPriceTierModel",
    "NaiveBayesTextModel",
    "KNNRetrievalModel",
]
