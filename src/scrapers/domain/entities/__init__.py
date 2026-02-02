"""
Domain entities package.

Entities are objects with unique identity that run through time.
They contain business logic and are independent of infrastructure.
"""

from .product import Product
from .scraper_run import ScraperRun

__all__ = ["Product", "ScraperRun"]
