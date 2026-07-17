"""
FastAPI router containing market trends and neighborhood aggregations.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from sqlalchemy.orm import Session
from app.api.schemas import MarketTrendsResponse, NeighborhoodTrend
from app.db.models import FeaturedListing
from app.db.session import get_db

logger = logging.getLogger("app.api.trends")
router = APIRouter()


@router.get("/", response_model=MarketTrendsResponse)
def get_market_trends(
    version: str = "1.0.0", db: Session = Depends(get_db)
) -> MarketTrendsResponse:
    """
    Get aggregated market statistics (median price, price per sqft, and listing count)
    grouped by neighborhood for the specified feature set version.
    """
    try:
        listings = (
            db.query(FeaturedListing)
            .filter(FeaturedListing.feature_set_version == version)
            .all()
        )
        if not listings:
            return MarketTrendsResponse(
                feature_set_version=version, neighborhood_trends=[]
            )

        # Build DataFrame for pandas aggregation (SQLite lacks native median function)
        data = [
            {
                "neighborhood": l.neighborhood,
                "price": l.price,
                "price_per_sqft": l.price_per_sqft,
            }
            for l in listings
        ]
        df = pd.DataFrame(data)

        agg = (
            df.groupby("neighborhood")
            .agg(
                total_listings=("price", "count"),
                median_price=("price", "median"),
                median_price_per_sqft=("price_per_sqft", "median"),
            )
            .reset_index()
        )

        trends = []
        for _, row in agg.iterrows():
            trends.append(
                NeighborhoodTrend(
                    neighborhood=str(row["neighborhood"]),
                    median_price=float(row["median_price"]),
                    median_price_per_sqft=float(row["median_price_per_sqft"]),
                    total_listings=int(row["total_listings"]),
                )
            )

        return MarketTrendsResponse(
            feature_set_version=version, neighborhood_trends=trends
        )
    except Exception as e:
        logger.error(f"Unexpected error in market trends endpoint: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected error fetching market trends."
        )
