"""
ScraperRun repository interface.

Defines the contract for scraper run persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..entities.scraper_run import ScraperRun


class ScraperRunRepository(ABC):
    """
    Repository interface for ScraperRun persistence.

    This is a domain interface that will be implemented by infrastructure.
    """

    @abstractmethod
    def save(self, scraper_run: ScraperRun) -> ScraperRun:
        """
        Save a scraper run (create or update).

        Args:
            scraper_run: ScraperRun entity to save

        Returns:
            Saved scraper run
        """
        pass

    @abstractmethod
    def find_by_id(self, run_id: UUID) -> Optional[ScraperRun]:
        """
        Find a scraper run by its ID.

        Args:
            run_id: ScraperRun UUID

        Returns:
            ScraperRun if found, None otherwise
        """
        pass

    @abstractmethod
    def find_recent(
        self, store: Optional[str] = None, limit: int = 10
    ) -> List[ScraperRun]:
        """
        Find recent scraper runs.

        Args:
            store: Filter by store name (optional)
            limit: Maximum number of results

        Returns:
            List of recent scraper runs (newest first)
        """
        pass

    @abstractmethod
    def find_by_date_range(
        self, start_date: datetime, end_date: datetime, store: Optional[str] = None
    ) -> List[ScraperRun]:
        """
        Find scraper runs within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            store: Filter by store name (optional)

        Returns:
            List of scraper runs
        """
        pass

    @abstractmethod
    def count(self, store: Optional[str] = None, success_only: bool = False) -> int:
        """
        Count scraper runs.

        Args:
            store: Filter by store name (optional)
            success_only: Only count successful runs

        Returns:
            Number of scraper runs
        """
        pass
