"""
FastAPI router containing prediction endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.api.schemas import PredictRequest, PredictResponse
from app.ml.predictor import Predictor

logger = logging.getLogger("app.api.predict")
router = APIRouter()


@router.post("/", response_model=PredictResponse)
def run_predict(payload: PredictRequest) -> PredictResponse:
    """
    Run property price estimation, below-market classification, price-tiering,
    and decision-tree proxy explainability factors.
    """
    try:
        predictor = Predictor()
        # run_all_predictions accepts dictionary of features
        pred_res, models_used = predictor.run_all_predictions(payload.model_dump())
        return PredictResponse(
            estimated_price=pred_res["estimated_price"],
            confidence=pred_res["confidence"],
            proxy_explainability_factors=pred_res["proxy_explainability_factors"],
            is_below_market_value=pred_res["is_below_market_value"],
            price_tier=pred_res["price_tier"],
            models_used=models_used,
        )
    except FileNotFoundError as fnf:
        logger.error(f"Model loading error: {fnf}")
        raise HTTPException(
            status_code=404,
            detail=f"Model files not found. Please run training pipeline first: {fnf}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in run_predict endpoint: {e}")
        raise HTTPException(status_code=500, detail="Unexpected prediction error occurred.")
