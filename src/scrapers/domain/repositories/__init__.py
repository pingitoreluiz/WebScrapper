"""
Repository interfaces package.

Repositories define contracts for persistence without implementation details.
These are interfaces (abstract base classes) that infrastructure will implement.
"""

from .product_repository import ProductRepository
from .scraper_run_repository import ScraperRunRepository

__all__ = ["ProductRepository", "ScraperRunRepository"]
