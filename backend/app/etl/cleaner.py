"""
Cleaner module for real estate listings data.
"""

import logging
import re
from typing import List, Dict, Any, Union, Optional
import pandas as pd
from app.db.models import RawListing

logger = logging.getLogger("app.etl.cleaner")


class PropertyCleaner:
    """
    Cleaner class responsible for type coercion, parsing raw string fields,
    handling missing values, and filtering outliers from raw scraped listings.
    """

    def __init__(
        self,
        price_min: float = 30000.0,
        price_max: float = 750000.0,
        area_min: float = 300.0,
        area_max: float = 5000.0,
    ) -> None:
        """
        Initialize PropertyCleaner with standard outlier thresholds.
        """
        self.price_min = price_min
        self.price_max = price_max
        self.area_min = area_min
        self.area_max = area_max

    def clean_listings(self, raw_listings: Union[List[RawListing], List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        Cleans a list of raw listings and returns a cleaned pandas DataFrame.

        Args:
            raw_listings: List of RawListing DB objects or dictionary representations.

        Returns:
            pd.DataFrame: Cleaned listings.
        """
        # Convert objects or dictionaries to a common list of dicts
        data_list = []
        for item in raw_listings:
            if isinstance(item, RawListing):
                data_list.append({
                    "external_id": item.external_id,
                    "title": item.title,
                    "price": item.price,
                    "location": item.location,
                    "bedrooms": item.bedrooms,
                    "area": item.area,
                    "amenities": item.amenities,
                    "description_text": item.description_text
                })
            elif isinstance(item, dict):
                data_list.append(item)
            else:
                logger.warning(f"Unsupported raw listing type: {type(item)}. Skipping.")

        if not data_list:
            logger.warning("No listings to clean.")
            return pd.DataFrame()

        df = pd.DataFrame(data_list)

        # 1. Parse and Clean Price
        df["price"] = df["price"].apply(self._parse_price)

        # 2. Parse and Clean Area
        df["area"] = df["area"].apply(self._parse_area)

        # 3. Parse and Clean Bedrooms
        df["bedrooms"] = df["bedrooms"].apply(self._parse_bedrooms)

        # 4. Parse and Extract Neighborhood
        df["neighborhood"] = df["location"].apply(self._parse_neighborhood)

        # 5. Drop Missing/Invalid Required Fields
        initial_len = len(df)
        df = df.dropna(subset=["external_id", "price", "area", "bedrooms", "neighborhood"])
        dropped_missing = initial_len - len(df)
        if dropped_missing > 0:
            logger.info(f"Dropped {dropped_missing} listings due to missing or unparseable required fields.")

        if df.empty:
            logger.warning("All listings dropped after cleaning required fields.")
            return df

        # Coerce types
        df["price"] = df["price"].astype(float)
        df["area"] = df["area"].astype(float)
        df["bedrooms"] = df["bedrooms"].astype(int)
        df["neighborhood"] = df["neighborhood"].astype(str)

        # 6. Outlier Filtering
        pre_outliers_len = len(df)
        df = df[
            (df["price"] >= self.price_min) & (df["price"] <= self.price_max) &
            (df["area"] >= self.area_min) & (df["area"] <= self.area_max) &
            (df["bedrooms"] >= 0) & (df["bedrooms"] <= 10)
        ]
        dropped_outliers = pre_outliers_len - len(df)
        if dropped_outliers > 0:
            logger.info(f"Dropped {dropped_outliers} listings as outliers.")

        return df

    def _parse_price(self, val: Any) -> Optional[float]:
        if val is None or pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return float(val)

        # String cleanup (remove $, commas, whitespace)
        cleaned = re.sub(r"[^\d.]", "", str(val))
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def _parse_area(self, val: Any) -> Optional[float]:
        if val is None or pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return float(val)

        # String cleanup (e.g. "1200 sqft", extract digits)
        cleaned = re.sub(r"[^\d.]", "", str(val))
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def _parse_bedrooms(self, val: Any) -> Optional[int]:
        if val is None or pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return int(val)

        # String cleanup (e.g. "3 BR", extract digits)
        cleaned = re.sub(r"[^\d]", "", str(val))
        try:
            return int(cleaned) if cleaned else None
        except ValueError:
            return None

    def _parse_neighborhood(self, val: Any) -> Optional[str]:
        if val is None or pd.isna(val):
            return None

        # Location format: "CollegeCreek, Ames, IA"
        # Take the first segment as neighborhood
        parts = str(val).split(",")
        if parts:
            neighborhood = parts[0].strip()
            return neighborhood if neighborhood else None
        return None
