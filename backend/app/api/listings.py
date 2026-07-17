"""
FastAPI router containing endpoints for querying and filtering cleaned listings.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import FeaturedListing
from app.db.session import get_db
from app.api.schemas import NeighborhoodTrend  # We can re-use schemas or define custom

logger = logging.getLogger("app.api.listings")
router = APIRouter()


@router.get("/")
def get_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    neighborhood: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_area: Optional[float] = Query(None),
    max_area: Optional[float] = Query(None),
    is_below_market_value: Optional[int] = Query(None, ge=0, le=1),
    version: str = Query("latest"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retrieve and filter featured listings for the Listing Explorer dashboard view.
    """
    # Logical validation checks
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400, detail="min_price cannot be greater than max_price."
        )
    if min_area is not None and max_area is not None and min_area > max_area:
        raise HTTPException(
            status_code=400, detail="min_area cannot be greater than max_area."
        )

    try:
        # 1. Determine active version if "latest" requested
        if version == "latest":
            max_version_row = db.query(func.max(FeaturedListing.feature_set_version)).scalar()
            active_version = max_version_row if max_version_row else "1.0.0"
        else:
            active_version = version

        # 2. Build Query
        query = db.query(FeaturedListing).filter(FeaturedListing.feature_set_version == active_version)

        # Apply filters
        if neighborhood:
            query = query.filter(FeaturedListing.neighborhood.ilike(f"%{neighborhood}%"))
        if min_price is not None:
            query = query.filter(FeaturedListing.price >= min_price)
        if max_price is not None:
            query = query.filter(FeaturedListing.price <= max_price)
        if min_area is not None:
            query = query.filter(FeaturedListing.area >= min_area)
        if max_area is not None:
            query = query.filter(FeaturedListing.area <= max_area)
        if is_below_market_value is not None:
            query = query.filter(FeaturedListing.is_below_market_value == is_below_market_value)

        # 3. Calculate total counts for pagination
        total = query.count()

        # 4. Paginate and fetch
        offset = (page - 1) * limit
        results = query.order_by(FeaturedListing.price.asc()).offset(offset).limit(limit).all()

        listings_list = []
        for l in results:
            listings_list.append({
                "id": l.id,
                "external_id": l.external_id,
                "price": l.price,
                "bedrooms": l.bedrooms,
                "area": l.area,
                "neighborhood": l.neighborhood,
                "has_central_air": l.has_central_air,
                "has_garage": l.has_garage,
                "has_pool": l.has_pool,
                "fireplace_count": l.fireplace_count,
                "price_per_sqft": l.price_per_sqft,
                "is_below_market_value": bool(l.is_below_market_value),
                "feature_set_version": l.feature_set_version,
            })

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "feature_set_version": active_version,
            "listings": listings_list,
        }

    except Exception as e:
        logger.error(f"Error querying listings in get_listings router: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected listings retrieval error."
        )
