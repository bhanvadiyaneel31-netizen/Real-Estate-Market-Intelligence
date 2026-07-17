"""
FastAPI router containing comparative similar property retrieval endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import SimilarPropertiesRequest, SimilarPropertiesResponse, ComparableProperty
from app.db.session import get_db
from app.ml.predictor import Predictor

logger = logging.getLogger("app.api.similar")
router = APIRouter()


@router.post("/", response_model=SimilarPropertiesResponse)
def get_similar_properties(
    payload: SimilarPropertiesRequest, db: Session = Depends(get_db)
) -> SimilarPropertiesResponse:
    """
    Query KNN index for comparable listings and fetch matching detail records.
    """
    try:
        predictor = Predictor()
        # Retrieve similar listings
        raw_results = predictor.get_similar_properties(
            db, payload.model_dump(), k=payload.k
        )

        similar_props = []
        for prop in raw_results:
            similar_props.append(
                ComparableProperty(
                    external_id=prop["external_id"],
                    title=prop["title"],
                    price=prop["price"],
                    location=prop["location"],
                    bedrooms=prop["bedrooms"],
                    area=prop["area"],
                    amenities=prop.get("amenities"),
                    description_text=prop.get("description_text"),
                    distance=prop["distance"],
                )
            )

        return SimilarPropertiesResponse(
            similar_properties=similar_props, model_used="knn_retrieval"
        )
    except FileNotFoundError as fnf:
        logger.error(f"Model loading error: {fnf}")
        raise HTTPException(
            status_code=404,
            detail=f"KNN model file not found. Please run training pipeline first: {fnf}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in similar properties endpoint: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected retrieval error occurred."
        )
