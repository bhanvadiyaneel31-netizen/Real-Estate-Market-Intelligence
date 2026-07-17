"""
K-Nearest Neighbors model for similar property retrieval.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors

from app.ml.models.base import BaseAppModel


class KNNRetrievalModel(BaseAppModel):
    """
    Unsupervised K-Nearest Neighbors wrapper for similar property retrieval.
    """

    def __init__(self, feature_set_version: str = "1.0.0") -> None:
        """
        Initialize the KNN model.
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
        self.external_ids: List[str] = []

        numeric_features = [f for f in self.features if f != "neighborhood"]
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), ["neighborhood"]),
            ]
        )
        self.estimator = NearestNeighbors(n_neighbors=5, metric="euclidean")

    def fit(self, df_train: pd.DataFrame) -> None:
        """
        Fits preprocessor and NearestNeighbors model, storing training external_ids.
        """
        self.external_ids = list(df_train["external_id"].astype(str))
        X = df_train[self.features]
        X_trans = self.preprocessor.fit_transform(X)
        # Convert sparse matrix output from OneHotEncoder to dense if necessary
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()
        self.estimator.fit(X_trans)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Dummy predict method for abstract class.
        Returns external_ids of the 1st nearest neighbor for each query.
        """
        indices, _ = self.query_neighbors(df, k=1)
        return np.array([idx[0] if len(idx) > 0 else "" for idx in indices])

    def query_neighbors(self, df_query: pd.DataFrame, k: int = 5) -> Tuple[List[List[str]], np.ndarray]:
        """
        Query k nearest neighbors for listings in df_query.

        Returns:
            Tuple[List[List[str]], np.ndarray]: Lists of neighboring external_ids and distance matrix.
        """
        X = df_query[self.features]
        X_trans = self.preprocessor.transform(X)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()

        distances, indices = self.estimator.kneighbors(X_trans, n_neighbors=k)

        neighbor_ids = []
        for row in indices:
            row_ids = [self.external_ids[idx] for idx in row]
            neighbor_ids.append(row_ids)

        return neighbor_ids, distances

    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate KNN by finding average neighbor distance for the test set.
        """
        _, distances = self.query_neighbors(df_test, k=5)
        mean_dist = np.mean(distances)
        return {"mean_neighbor_distance": float(mean_dist)}
