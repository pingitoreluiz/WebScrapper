"""
Scraper API routes

Endpoints for triggering and monitoring scrapers.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.database import get_db, get_db_session
from ...core.repository import ScraperRunRepository
from ...core.models import (
    ScraperRunRequest,
    ScraperRunResponse,
    ScraperMetrics,
    Store,
    ScraperRun,
)
from ....scrapers.factory import ScraperFactory
from ....scrapers.scheduler import ScraperScheduler, get_scheduler
from ....utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


async def run_scrapers_background(
    stores: List[Store], headless: bool, max_pages: Optional[int] = None
):
    """
    Background task to run scrapers
    """
    logger.info("starting_background_scrape", stores=[s.value for s in stores])

    results = []

    # Run sequentially for now to avoid resource contention
    for store in stores:
        try:
            # Create scraper config
            from ....scrapers.models import ScraperConfig

            config = ScraperConfig(
                store=store,
                headless=headless,
                max_pages=max_pages or 5,  # Default to 5 pages if not specified
            )

            # Create and run scraper
            scraper = ScraperFactory.create(store, config)
            metrics = await scraper.run()

            # Save run metrics
            with get_db_session() as session:
                repo = ScraperRunRepository(session)
                repo.create(metrics)

            results.append(metrics)

        except Exception as e:
            logger.error(
                "scraper_run_failed", store=store.value, error=str(e), exc_info=True
            )

    logger.info("background_scrape_finished", count=len(results))


@router.post("/run", response_model=ScraperRunResponse)
async def run_scrapers(
    request: ScraperRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Trigger scraper execution

    Args:
        request: Scraper run configuration

    Returns:
        Status of invalidation
    """
    logger.info("received_scrape_request", stores=[s.value for s in request.stores])

    # Add to background tasks
    background_tasks.add_task(
        run_scrapers_background, request.stores, request.headless, request.max_pages
    )

    return ScraperRunResponse(
        success=True,
        message="Scrapers started in background",
        metrics=[],
        total_products_saved=0,
        total_execution_time=0,
    )


@router.get("/history", response_model=List[ScraperRun])
async def get_recent_runs(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent scraper runs"""
    repo = ScraperRunRepository(db)
    runs = repo.get_recent_runs(limit)
    return runs


@router.get("/metrics")
async def get_run_stats(days: int = 7, db: Session = Depends(get_db)):
    """Get scraper run statistics"""
    repo = ScraperRunRepository(db)
    return repo.get_run_stats(days)
