"""
Main application entry point for the FastAPI backend.
"""

import logging
from typing import Dict
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging

# Initialize and configure logging
setup_logging()
logger = logging.getLogger("app.main")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for the Real Estate Market Intelligence Platform",
    version="1.0.0",
)

# CORS middleware configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.api.predict import router as predict_router
from app.api.similar import router as similar_router
from app.api.trends import router as trends_router
from app.api.metrics import router as metrics_router

app.include_router(predict_router, prefix="/api/predict", tags=["Prediction"])
app.include_router(similar_router, prefix="/api/similar-properties", tags=["Comparables"])
app.include_router(trends_router, prefix="/api/market-trend", tags=["Market Trends"])
app.include_router(metrics_router, prefix="/api/model-metrics", tags=["Model Comparison"])


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Verify the service is up and running.

    Returns:
        Dict[str, str]: Status payload indicating health.
    """
    logger.info("Health check endpoint queried.")
    return {"status": "healthy"}


# Startup and Shutdown Lifecycle Hooks
from app.core.scheduler import setup_scheduler, scheduler

@app.on_event("startup")
def on_startup() -> None:
    logger.info("FastAPI backend application starting up...")
    setup_scheduler(app)


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("FastAPI backend application shutting down...")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler background thread terminated successfully.")


