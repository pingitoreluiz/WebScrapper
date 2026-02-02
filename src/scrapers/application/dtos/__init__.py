"""
DTOs (Data Transfer Objects) package.

DTOs are simple data structures used to transfer data between layers.
They have no business logic, only data and validation.
"""

from .scraper_config import ScraperConfigDTO
from .extraction_result import ExtractionResultDTO
from .scraper_metrics import ScraperMetricsDTO

__all__ = ["ScraperConfigDTO", "ExtractionResultDTO", "ScraperMetricsDTO"]
