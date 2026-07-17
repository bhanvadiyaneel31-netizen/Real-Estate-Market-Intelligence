"""
FastAPI router containing model metrics endpoints.
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from app.ml.registry import ModelRegistry

logger = logging.getLogger("app.api.metrics")
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def get_model_metrics(version: str = "latest") -> Dict[str, Any]:
    """
    Retrieve performance metrics, training timestamps, and versions for all trained models.
    Supports query parameter `version` ('latest', 'all', or a specific version string).
    """
    try:
        registry = ModelRegistry()
        if version == "all":
            return registry.get_all_metrics()
        elif version == "latest":
            return registry.get_latest_metrics()
        else:
            all_metrics = registry.get_all_metrics()
            if version not in all_metrics:
                raise HTTPException(
                    status_code=404, detail=f"Metrics for version '{version}' not found."
                )
            return all_metrics[version]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving model metrics: {e}")
        raise HTTPException(
            status_code=500, detail="Unexpected error retrieving model metrics."
        )

