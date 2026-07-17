"""
Regression models for Ames Housing price estimation.
"""

from typing import Dict
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor

from app.ml.models.base import BaseAppModel


class BaseRegressionModel(BaseAppModel):
    """
    Base class for regression models predicting property prices.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize the base regression model.
        """
        super().__init__(feature_set_version)
        self.target_col = "price"
        self.features = [
            "bedrooms",
            "area",
            "neighborhood",
            "has_central_air",
            "has_garage",
            "has_pool",
            "fireplace_count",
        ]


    def fit(self, df_train: pd.DataFrame) -> None:
        """
        Train the regression model.
        """
        X = df_train[self.features]
        y = df_train[self.target_col]
        self.pipeline.fit(X, y)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict values using the trained pipeline.
        """
        X = df[self.features]
        return self.pipeline.predict(X)

    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance on the test set.
        """
        X_test = df_test[self.features]
        y_test = df_test[self.target_col]
        preds = self.pipeline.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        return {"rmse": float(rmse), "r2": float(r2)}


class LinearRegressionModel(BaseRegressionModel):
    """
    Multiple Linear Regression wrapper.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize LinearRegressionModel with OneHotEncoder preprocessor.
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
            steps=[("preprocessor", preprocessor), ("regressor", LinearRegression())]
        )


class RidgeRegressionModel(BaseRegressionModel):
    """
    Ridge Regression wrapper with L2 regularization.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize RidgeRegressionModel with standard scale preprocessor.
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
            steps=[("preprocessor", preprocessor), ("regressor", Ridge(alpha=1.0))]
        )


class LassoRegressionModel(BaseRegressionModel):
    """
    Lasso Regression wrapper with L1 regularization (feature selection).
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize LassoRegressionModel with standard scale preprocessor.
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
                ("regressor", Lasso(alpha=1.0, max_iter=2000)),
            ]
        )


class RandomForestRegressionModel(BaseRegressionModel):
    """
    Random Forest Regressor wrapper.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize RandomForestRegressionModel with OrdinalEncoder.
        """
        super().__init__(feature_set_version)
        numeric_features = [f for f in self.features if f != "neighborhood"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                (
                    "cat",
                    OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                    ["neighborhood"],
                ),
            ]
        )
        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "regressor",
                    RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
                ),
            ]
        )


class XGBoostRegressionModel(BaseRegressionModel):
    """
    Gradient Boosted Trees wrapper using XGBoost.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize XGBoostRegressionModel.
        """
        super().__init__(feature_set_version)
        numeric_features = [f for f in self.features if f != "neighborhood"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                (
                    "cat",
                    OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                    ["neighborhood"],
                ),
            ]
        )
        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "regressor",
                    XGBRegressor(
                        n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
                    ),
                ),
            ]
        )


class DecisionTreeRegressionModel(BaseRegressionModel):
    """
    Decision Tree Regressor wrapper for explainable price factors.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize DecisionTreeRegressionModel.
        """
        super().__init__(feature_set_version)
        numeric_features = [f for f in self.features if f != "neighborhood"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                (
                    "cat",
                    OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                    ["neighborhood"],
                ),
            ]
        )
        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", DecisionTreeRegressor(max_depth=5, random_state=42)),
            ]
        )

    def explain_prediction(self, df_input: pd.DataFrame) -> list:
        """
        Explain the decision path of a single property listing.
        Traces the split nodes from root to leaf and computes local feature contributions.

        Returns:
            list: List of dicts, e.g. [{"feature": str, "impact": float}] sorted by absolute impact.
        """
        # Preprocess features
        X_trans = self.pipeline.named_steps["preprocessor"].transform(df_input)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()

        x = X_trans[0]

        dt = self.pipeline.named_steps["regressor"]
        left = dt.tree_.children_left
        right = dt.tree_.children_right
        features = dt.tree_.feature
        thresholds = dt.tree_.threshold
        values = dt.tree_.value.squeeze()

        # Mapping from index in preprocessor output to raw feature name
        numeric_features = [f for f in self.features if f != "neighborhood"]
        features_mapping = numeric_features + ["neighborhood"]

        contributions = {}
        node = 0
        while left[node] != -1:  # Not a leaf
            feat_idx = features[node]
            val_current = values[node]

            # Go left or right
            if x[feat_idx] <= thresholds[node]:
                next_node = left[node]
            else:
                next_node = right[node]

            val_next = values[next_node]
            diff = float(val_next - val_current)

            feat_name = features_mapping[feat_idx]
            contributions[feat_name] = contributions.get(feat_name, 0.0) + diff
            node = next_node

        # Sort by absolute impact descending
        sorted_contribs = sorted(
            contributions.items(), key=lambda item: abs(item[1]), reverse=True
        )
        return [{"feature": k, "impact": v} for k, v in sorted_contribs]

