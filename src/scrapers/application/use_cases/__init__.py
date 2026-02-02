"""
Use cases package.

Use cases contain application-specific business rules and orchestrate
the flow of data between entities and external services.
"""

from .scrape_store import ScrapeStoreUseCase

__all__ = ["ScrapeStoreUseCase"]
