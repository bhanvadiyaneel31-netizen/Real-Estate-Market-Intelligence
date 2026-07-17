"""
Core scheduler service for executing periodic rescrape and retrain runs in the background.
"""

import logging
import re
import time
from datetime import datetime
from fastapi import FastAPI
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import FeaturedListing
from app.scraper.scraper import AmesSandboxScraper
from app.etl.pipeline import ETLPipeline
from app.ml.trainer import ModelTrainer

logger = logging.getLogger("app.core.scheduler")

# Instantiate a single background scheduler instance
scheduler = BackgroundScheduler()


def get_next_feature_version(db: Session) -> str:
    """
    Scan the database for existing FeaturedListing records, extract the maximum
    1.0.<patch> version, and return the incremented patch version string.
    Defaults to '1.0.1' if no records match.
    """
    try:
        versions = db.query(FeaturedListing.feature_set_version).distinct().all()
        version_strings = [v[0] for v in versions]
    except Exception as e:
        logger.error(f"Error querying distinct featured versions: {e}")
        version_strings = []

    patches = []
    for vs in version_strings:
        match = re.match(r"^1\.0\.(\d+)$", vs)
        if match:
            patches.append(int(match.group(1)))

    if not patches:
        return "1.0.1"

    next_patch = max(patches) + 1
    return f"1.0.{next_patch}"


def run_periodic_rescrape_and_retrain() -> None:
    """
    Background job that executes a periodic crawler crawl, runs the ETL pipeline,
    and retrains all 10 models on the newly generated dataset version.
    """
    start_time = time.time()
    logger.info("Scheduler task 'run_periodic_rescrape_and_retrain' triggered.")
    
    db: Session = SessionLocal()
    try:
        # 1. Determine new feature set version to avoid database collisions
        new_version = get_next_feature_version(db)
        logger.info(f"Targeting new feature set version for this run: {new_version}")

        # 2. Run Crawler Scraping Phase (with connection error safety)
        logger.info(f"Scraper Phase: Querying sandbox at {settings.sandbox_url}...")
        scraper = AmesSandboxScraper(base_url=settings.sandbox_url, delay_seconds=0.1)
        
        try:
            # Scrape up to 50 listings during periodic updates
            listings = scraper.scrape_listings(limit=50)
            if listings:
                saved_count = scraper.save_raw_listings(db, listings)
                logger.info(f"Scraper completed. Found: {len(listings)}, Saved to DB: {saved_count}")
            else:
                logger.warning("Scraper returned zero listings. Check if sandbox server is active.")
        except Exception as se:
            logger.warning(
                f"Scraper phase encountered an error: {se}. "
                f"Proceeding with ETL and training on existing raw listings in database."
            )

        # 3. Run ETL/Cleaning Phase
        logger.info(f"ETL Phase: Cleaning and engineering features for version {new_version}...")
        pipeline = ETLPipeline(db, feature_set_version=new_version)
        cleaned_count = pipeline.run()
        logger.info(f"ETL completed. Featured listings saved: {cleaned_count}")

        if cleaned_count == 0:
            logger.error("No featured listings cleaned or generated. Aborting ML retraining phase.")
            return

        # 4. Run Model Training Phase
        logger.info(f"ML Phase: Retraining all 10 models on version {new_version}...")
        trainer = ModelTrainer(db)
        elapsed_train, metrics = trainer.train_all(feature_set_version=new_version)

        # Log training completion details
        elapsed_total = time.time() - start_time
        logger.info(
            f"Scheduled run for version {new_version} completed successfully in {elapsed_total:.2f}s! "
            f"Trained {len(metrics)} models. "
            f"Metrics summary: {metrics}"
        )

    except Exception as e:
        logger.error(f"Critical failure in periodic scheduler job: {e}", exc_info=True)
    finally:
        db.close()


def setup_scheduler(app: FastAPI) -> None:
    """
    Setup, start, and register clean shutdown triggers for the background scheduler
    if settings.scheduler_enabled is configured to True.
    """
    if not settings.scheduler_enabled:
        logger.info("Background Scheduler is disabled (gated by settings.scheduler_enabled).")
        return

    logger.info("Initializing Background Scheduler...")
    
    # Add periodic rescrape and retrain job
    # Runs at the configured interval in hours
    scheduler.add_job(
        run_periodic_rescrape_and_retrain,
        trigger="interval",
        hours=settings.scheduler_interval_hours,
        id="rescrape_and_retrain_job",
        replace_existing=True,
    )

    # Start the scheduler
    scheduler.start()
    logger.info(
        f"Background Scheduler started successfully. "
        f"Rescrape and Retrain job registered to run every {settings.scheduler_interval_hours} hour(s)."
    )
