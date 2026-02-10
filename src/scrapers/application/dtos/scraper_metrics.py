"""
ScraperMetrics DTO - Metrics from a scraper run.

This DTO carries metrics data from application to API/presentation layer.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScraperMetricsDTO:
    """
    DTO for scraper execution metrics.

    Carries metrics data for reporting and monitoring.

    Attributes:
        store: Store that was scraped
        started_at: When scraping started
        finished_at: When scraping finished
        execution_time: Total execution time in seconds
        products_found: Number of products found
        products_saved: Number of products saved
        products_skipped: Number of products skipped
        pages_scraped: Number of pages scraped
        errors: Number of errors encountered
        captchas_detected: Number of CAPTCHAs detected
        success: Whether the run completed successfully
        error_message: Error message if failed
    """

    store: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    execution_time: float = 0.0
    products_found: int = 0
    products_saved: int = 0
    products_skipped: int = 0
    pages_scraped: int = 0
    errors: int = 0
    captchas_detected: int = 0
    success: bool = False
    error_message: Optional[str] = None

    def get_success_rate(self) -> float:
        """
        Calculate success rate (saved / found).

        Returns:
            Success rate as percentage (0-100)
        """
        if self.products_found == 0:
            return 0.0
        return (self.products_saved / self.products_found) * 100

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "store": self.store,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "execution_time": self.execution_time,
            "products_found": self.products_found,
            "products_saved": self.products_saved,
            "products_skipped": self.products_skipped,
            "pages_scraped": self.pages_scraped,
            "errors": self.errors,
            "captchas_detected": self.captchas_detected,
            "success": self.success,
            "error_message": self.error_message,
            "success_rate": self.get_success_rate(),
        }
