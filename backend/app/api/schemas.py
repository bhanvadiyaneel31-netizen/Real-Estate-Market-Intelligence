"""
Pydantic schemas defining request and response payloads for the API.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """
    Input features for running price predictions and classification.
    """

    bedrooms: int = Field(..., description="Number of bedrooms", ge=0)
    area: float = Field(..., description="Total living area in square feet", gt=0)
    neighborhood: str = Field(..., description="Neighborhood name (raw string)")
    has_central_air: int = Field(
        ..., description="Presence of central air conditioning (0 or 1)", ge=0, le=1
    )
    has_garage: int = Field(..., description="Presence of a garage (0 or 1)", ge=0, le=1)
    has_pool: int = Field(..., description="Presence of a pool (0 or 1)", ge=0, le=1)
    fireplace_count: int = Field(..., description="Number of fireplaces", ge=0)
    description_text: Optional[str] = Field(
        "", description="Optional property description text for TF-IDF NB model"
    )


class FeatureFactor(BaseModel):
    """
    Representation of a single feature attribution/driver for price predictions.
    """

    feature: str = Field(..., description="Name of the attribute")
    impact: float = Field(..., description="Attributed price impact ($ deviation)")


class PredictResponse(BaseModel):
    """
    Consolidated price and classification prediction outputs.
    """

    estimated_price: float = Field(..., description="Estimated numerical property price")
    confidence: float = Field(..., description="Confidence score between 0.50 and 0.98")
    proxy_explainability_factors: List[FeatureFactor] = Field(
        ...,
        description="Local price drivers explaining the estimate via a Decision Tree proxy",
    )
    is_below_market_value: bool = Field(
        ..., description="True if the property is priced below its neighborhood median"
    )
    price_tier: str = Field(
        ..., description="Estimated price tier of the property (Low, Medium, High)"
    )
    models_used: Dict[str, str] = Field(
        ..., description="Names of the specific registry models used for each task"
    )


class SimilarPropertiesRequest(PredictRequest):
    """
    Request inputs for comparative similar property lookup.
    """

    k: Optional[int] = Field(5, description="Number of neighbors to retrieve", gt=0)


class ComparableProperty(BaseModel):
    """
    Representation of a matching similar listing retrieved from DB.
    """

    external_id: str
    title: str
    price: str
    location: str
    bedrooms: str
    area: str
    amenities: Optional[str] = None
    description_text: Optional[str] = None
    distance: float


class SimilarPropertiesResponse(BaseModel):
    """
    Output payload containing top comparable listings.
    """

    similar_properties: List[ComparableProperty]
    model_used: str


class NeighborhoodTrend(BaseModel):
    """
    Aggregated market statistics for a single neighborhood.
    """

    neighborhood: str
    median_price: float
    median_price_per_sqft: float
    total_listings: int


class MarketTrendsResponse(BaseModel):
    """
    Aggregated market metrics across neighborhoods.
    """

    feature_set_version: str
    neighborhood_trends: List[NeighborhoodTrend]
