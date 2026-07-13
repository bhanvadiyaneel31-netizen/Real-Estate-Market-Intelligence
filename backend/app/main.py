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


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Verify the service is up and running.

    Returns:
        Dict[str, str]: Status payload indicating health.
    """
    logger.info("Health check endpoint queried.")
    return {"status": "healthy"}
