"""
Feature engineering module for real estate listings.
"""

import logging
import re
from typing import Any, Set
import pandas as pd

logger = logging.getLogger("app.etl.feature_engineer")


class PropertyFeatureEngineer:
    """
    Feature Engineer class responsible for extracting features like price_per_sqft,
    amenity flags, text features, and the neighborhood-relative target variable.
    """

    def __init__(self, luxury_keywords: Set[str] = None) -> None:
        """
        Initialize PropertyFeatureEngineer with a set of luxury keywords.
        """
        if luxury_keywords is None:
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
        else:
            self.luxury_keywords = luxury_keywords

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineers features for a cleaned listings DataFrame.

        Args:
            df (pd.DataFrame): Cleaned listings DataFrame.

        Returns:
            pd.DataFrame: DataFrame with engineered features.
        """
        if df.empty:
            return df

        # Copy to avoid modifying original df
        df = df.copy()

        # 1. price_per_sqft
        df["price_per_sqft"] = df["price"] / df["area"]

        # 2. Extract amenities flags
        df["has_central_air"] = df["amenities"].apply(self._check_central_air)
        df["has_garage"] = df["amenities"].apply(self._check_garage)
        df["has_pool"] = df["amenities"].apply(self._check_pool)
        df["fireplace_count"] = df["amenities"].apply(self._extract_fireplaces)

        # 3. Extract text features
        df["description_length"] = df["description_text"].apply(
            lambda x: len(str(x)) if pd.notna(x) else 0
        )
        df["has_luxury_keywords"] = df["description_text"].apply(self._check_luxury_keywords)

        # 4. Compute target proxy: is_below_market_value
        # For each neighborhood, calculate the median price of all listings in that neighborhood.
        # Fall back to city-wide median if a neighborhood has fewer than 5 listings.
        city_median = df["price"].median()

        # Calculate count and median per neighborhood
        group_stats = df.groupby("neighborhood")["price"].agg(["count", "median"])

        # Define target median using fallback if count < 5
        group_stats["target_median"] = group_stats.apply(
            lambda r: city_median if r["count"] < 5 else r["median"], axis=1
        )

        # Map the target threshold medians back to the listings DataFrame
        target_medians = df["neighborhood"].map(group_stats["target_median"])
        df["is_below_market_value"] = (df["price"] < target_medians).astype(int)

        return df

    def _check_central_air(self, val: Any) -> int:
        if pd.isna(val) or not val:
            return 0
        return 1 if "central air" in str(val).lower() else 0

    def _check_garage(self, val: Any) -> int:
        if pd.isna(val) or not val:
            return 0
        return 1 if "garage" in str(val).lower() else 0

    def _check_pool(self, val: Any) -> int:
        if pd.isna(val) or not val:
            return 0
        return 1 if "pool" in str(val).lower() else 0

    def _extract_fireplaces(self, val: Any) -> int:
        if pd.isna(val) or not val:
            return 0
        val_str = str(val).lower()
        match = re.search(r"(\d+)\s+fireplace", val_str)
        if match:
            return int(match.group(1))
        if "fireplace" in val_str:
            return 1
        return 0

    def _check_luxury_keywords(self, val: Any) -> int:
        if pd.isna(val) or not val:
            return 0
        val_lower = str(val).lower()
        for word in self.luxury_keywords:
            if word in val_lower:
                return 1
        return 0
