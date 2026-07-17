"""
Classification models for Ames Housing analysis and prediction.
"""

from typing import Dict
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score

from app.ml.models.base import BaseAppModel


class BaseClassificationModel(BaseAppModel):
    """
    Base class for classification models.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize the base classification model.
        """
        super().__init__(feature_set_version)
        self.features = [
            "bedrooms",
            "area",
            "neighborhood",
            "has_central_air",
            "has_garage",
            "has_pool",
            "fireplace_count",
        ]
        self.target_col = "is_below_market_value"


    def fit(self, df_train: pd.DataFrame) -> None:
        """
        Train the classification model.
        """
        X = df_train[self.features]
        y = df_train[self.target_col]
        self.pipeline.fit(X, y)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict classes using the trained pipeline.
        """
        X = df[self.features]
        return self.pipeline.predict(X)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict probability scores.
        """
        X = df[self.features]
        return self.pipeline.predict_proba(X)

    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate classification metrics on the test set.
        """
        X_test = df_test[self.features]
        y_test = df_test[self.target_col]
        preds = self.pipeline.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="binary")
        return {"accuracy": float(acc), "f1": float(f1)}


class LogisticRegressionModel(BaseClassificationModel):
    """
    Logistic Regression wrapper for binary classification of is_below_market_value.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize LogisticRegressionModel with scaling and one-hot encoding.
        """
        super().__init__(feature_set_version)
        numeric_features = [f for f in self.features if f != "neighborhood"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), ["neighborhood"]),
            ]
        )
        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", LogisticRegression(random_state=42, max_iter=1000)),
            ]
        )


class SVMPriceTierModel(BaseAppModel):
    """
    Support Vector Machine wrapper for price tier classification (multiclass).
    Tiers are dynamically calculated from training set price tertiles.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize SVMPriceTierModel.
        """
        super().__init__(feature_set_version)
        self.features = [
            "bedrooms",
            "area",
            "neighborhood",
            "has_central_air",
            "has_garage",
            "has_pool",
            "fireplace_count",
        ]

        self.target_col = "price"  # Price is the source for classification
        self.t33 = 0.0
        self.t66 = 0.0

        numeric_features = [f for f in self.features if f != "neighborhood"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), ["neighborhood"]),
            ]
        )
        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", SVC(C=1.0, kernel="rbf", probability=True, random_state=42)),
            ]
        )

    def _map_price_to_tier(self, price: float) -> str:
        """
        Map float price to tier based on stored thresholds.
        """
        if price < self.t33:
            return "Low"
        elif price <= self.t66:
            return "Medium"
        else:
            return "High"

    def fit(self, df_train: pd.DataFrame) -> None:
        """
        Calculate thresholds from train split, map targets, and train SVM.
        """
        prices = df_train[self.target_col].dropna()
        self.t33 = float(np.percentile(prices, 33.3))
        self.t66 = float(np.percentile(prices, 66.6))

        X = df_train[self.features]
        y = df_train[self.target_col].apply(self._map_price_to_tier)
        self.pipeline.fit(X, y)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict price tier strings ("Low", "Medium", "High").
        """
        X = df[self.features]
        return self.pipeline.predict(X)

    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate multiclass performance.
        """
        X_test = df_test[self.features]
        y_test = df_test[self.target_col].apply(self._map_price_to_tier)
        preds = self.pipeline.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1_w = f1_score(y_test, preds, average="weighted")
        return {"accuracy": float(acc), "f1_weighted": float(f1_w)}


class NaiveBayesTextModel(BaseAppModel):
    """
    Multinomial Naive Bayes model for classifying is_below_market_value using description_text.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize NaiveBayesTextModel with TF-IDF Vectorizer.
        """
        super().__init__(feature_set_version)
        self.target_col = "is_below_market_value"
        self.text_col = "description_text"

        self.pipeline = Pipeline(
            steps=[
                ("vectorizer", TfidfVectorizer(max_features=500, stop_words="english")),
                ("classifier", MultinomialNB()),
            ]
        )

    def fit(self, df_train: pd.DataFrame) -> None:
        """
        Train Naive Bayes model using description text.
        """
        # Fill missing text values with empty string
        X = df_train[self.text_col].fillna("").astype(str)
        y = df_train[self.target_col]
        self.pipeline.fit(X, y)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict target class based on description text.
        """
        X = df[self.text_col].fillna("").astype(str)
        return self.pipeline.predict(X)

    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate on test set text.
        """
        X_test = df_test[self.text_col].fillna("").astype(str)
        y_test = df_test[self.target_col]
        preds = self.pipeline.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="binary")
        return {"accuracy": float(acc), "f1": float(f1)}
