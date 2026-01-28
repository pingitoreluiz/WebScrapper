"""
Scraper Scheduler

Automated scraping execution using APScheduler.
"""

from typing import Optional, List, Callable
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .factory import ScraperFactory
from .models import ScraperConfig
from src.backend.core.models import Store, ScraperMetrics
from src.backend.core.database import get_db_session
from src.backend.core.repository import ScraperRunRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperScheduler:
    """
    Scheduler for automated scraper execution

    Features:
    - Cron-based scheduling
    - Concurrent execution control
    - Metrics persistence
    - Callback support
    """

    def __init__(self, max_concurrent: int = 1):
        """
        Initialize scheduler

        Args:
            max_concurrent: Maximum concurrent scraper executions
        """
        self.scheduler = BackgroundScheduler()
        self.max_concurrent = max_concurrent
        self.running_jobs = 0
        self.callbacks: List[Callable[[ScraperMetrics], None]] = []

    def add_callback(self, callback: Callable[[ScraperMetrics], None]) -> None:
        """
        Add callback to be called after each scraper run

        Args:
            callback: Function that receives ScraperMetrics
        """
        self.callbacks.append(callback)
        logger.debug("callback_added", callback_name=callback.__name__)

    def schedule_store(
        self,
        store: Store,
        cron_expression: str,
        config: Optional[ScraperConfig] = None,
        job_id: Optional[str] = None,
    ) -> str:
        """
        Schedule a store scraper

        Args:
            store: Store to scrape
            cron_expression: Cron expression (e.g., "0 */6 * * *" for every 6 hours)
            config: Optional scraper configuration
            job_id: Optional job ID (defaults to store name)

        Returns:
            Job ID

        Example:
            >>> scheduler.schedule_store(
            ...     Store.PICHAU,
            ...     "0 */6 * * *",  # Every 6 hours
            ...     ScraperConfig(headless=True, max_pages=10)
            ... )
        """
        job_id = job_id or f"scraper_{store.value.lower()}"

        # Create trigger from cron expression
        trigger = CronTrigger.from_crontab(cron_expression)

        # Add job
        self.scheduler.add_job(
            func=self._run_scraper,
            trigger=trigger,
            args=[store, config],
            id=job_id,
            name=f"Scraper: {store.value}",
            replace_existing=True,
        )

        logger.info(
            "scraper_scheduled", store=store.value, cron=cron_expression, job_id=job_id
        )

        return job_id

    def schedule_all_stores(
        self,
        cron_expression: str,
        config_overrides: Optional[dict[Store, ScraperConfig]] = None,
    ) -> List[str]:
        """
        Schedule all registered stores

        Args:
            cron_expression: Cron expression for all stores
            config_overrides: Optional store-specific configs

        Returns:
            List of job IDs
        """
        from .factory import ScraperRegistry

        job_ids = []
        config_overrides = config_overrides or {}

        for store in ScraperRegistry.list_stores():
            config = config_overrides.get(store)
            job_id = self.schedule_store(store, cron_expression, config)
            job_ids.append(job_id)

        logger.info("all_stores_scheduled", count=len(job_ids))

        return job_ids

    async def run_now(
        self, store: Store, config: Optional[ScraperConfig] = None
    ) -> ScraperMetrics:
        """
        Run a scraper immediately (blocking)

        Args:
            store: Store to scrape
            config: Optional configuration

        Returns:
            ScraperMetrics from execution
        """
        logger.info("running_scraper_now", store=store.value)
        return await self._run_scraper(store, config)

    def start(self) -> None:
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("scheduler_started")

    def stop(self, wait: bool = True) -> None:
        """
        Stop the scheduler

        Args:
            wait: Wait for running jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("scheduler_stopped")

    def get_jobs(self) -> List[dict]:
        """
        Get all scheduled jobs

        Returns:
            List of job information dicts
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time,
                    "trigger": str(job.trigger),
                }
            )
        return jobs

    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job

        Args:
            job_id: Job ID to remove

        Returns:
            True if removed, False if not found
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info("job_removed", job_id=job_id)
            return True
        except:
            logger.warning("job_not_found", job_id=job_id)
            return False

    async def _run_scraper(
        self, store: Store, config: Optional[ScraperConfig] = None
    ) -> ScraperMetrics:
        """
        Internal method to run a scraper

        Handles concurrency control, execution, and metrics persistence.
        """
        # Check concurrency limit
        if self.running_jobs >= self.max_concurrent:
            logger.warning(
                "max_concurrent_reached",
                running=self.running_jobs,
                max=self.max_concurrent,
            )
            # Return empty metrics
            return ScraperMetrics(store=store)

        self.running_jobs += 1

        try:
            # Create and run scraper
            scraper = ScraperFactory.create(store, config)
            metrics = await scraper.run()

            # Persist metrics to database
            self._save_metrics(metrics)

            # Call callbacks
            for callback in self.callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    logger.error(
                        "callback_failed", callback=callback.__name__, error=str(e)
                    )

            return metrics

        except Exception as e:
            logger.error(
                "scraper_execution_failed",
                store=store.value,
                error=str(e),
                exc_info=True,
            )
            return ScraperMetrics(store=store)

        finally:
            self.running_jobs -= 1

    def _save_metrics(self, metrics: ScraperMetrics) -> None:
        """Save metrics to database"""
        try:
            with get_db_session() as session:
                repo = ScraperRunRepository(session)
                run_id = repo.create(metrics)
                logger.info("metrics_saved", run_id=run_id, store=metrics.store.value)
        except Exception as e:
            logger.error("metrics_save_failed", error=str(e))


# Global scheduler instance
_scheduler: Optional[ScraperScheduler] = None


def get_scheduler() -> ScraperScheduler:
    """
    Get global scheduler instance (singleton)

    Returns:
        ScraperScheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = ScraperScheduler()
    return _scheduler
