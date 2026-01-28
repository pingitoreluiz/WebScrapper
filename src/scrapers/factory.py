"""
Scraper Factory Pattern

Provides dynamic scraper creation and registration.
"""

from typing import Dict, Type, Optional, List
from enum import Enum

from .base import BaseScraper
from .models import ScraperConfig
from ..backend.core.models import Store
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperRegistry:
    """
    Registry for scraper classes

    Allows dynamic registration and retrieval of scrapers.
    """

    _scrapers: Dict[Store, Type[BaseScraper]] = {}

    @classmethod
    def register(cls, store: Store, scraper_class: Type[BaseScraper]) -> None:
        """
        Register a scraper class for a store

        Args:
            store: Store enum value
            scraper_class: Scraper class (must inherit from BaseScraper)
        """
        if not issubclass(scraper_class, BaseScraper):
            raise TypeError(f"{scraper_class} must inherit from BaseScraper")

        cls._scrapers[store] = scraper_class
        logger.debug(
            "scraper_registered", store=store.value, class_name=scraper_class.__name__
        )

    @classmethod
    def get(cls, store: Store) -> Optional[Type[BaseScraper]]:
        """Get scraper class for a store"""
        return cls._scrapers.get(store)

    @classmethod
    def get_all(cls) -> Dict[Store, Type[BaseScraper]]:
        """Get all registered scrapers"""
        return cls._scrapers.copy()

    @classmethod
    def list_stores(cls) -> List[Store]:
        """List all registered stores"""
        return list(cls._scrapers.keys())


class ScraperFactory:
    """
    Factory for creating scraper instances

    Provides a clean interface for scraper creation.
    """

    @staticmethod
    def create(store: Store, config: Optional[ScraperConfig] = None) -> BaseScraper:
        """
        Create a scraper instance for a store

        Args:
            store: Store to scrape
            config: Optional scraper configuration

        Returns:
            Configured scraper instance

        Raises:
            ValueError: If store is not registered
        """
        scraper_class = ScraperRegistry.get(store)

        if scraper_class is None:
            available = [s.value for s in ScraperRegistry.list_stores()]
            raise ValueError(
                f"No scraper registered for {store.value}. "
                f"Available: {', '.join(available)}"
            )

        # Create config if not provided
        if config is None:
            config = ScraperConfig(store=store)

        logger.info(
            "creating_scraper", store=store.value, class_name=scraper_class.__name__
        )

        return scraper_class(config)

    @staticmethod
    def create_all(
        config_overrides: Optional[Dict[Store, ScraperConfig]] = None,
    ) -> List[BaseScraper]:
        """
        Create scrapers for all registered stores

        Args:
            config_overrides: Optional dict of store-specific configs

        Returns:
            List of scraper instances
        """
        scrapers = []
        config_overrides = config_overrides or {}

        for store in ScraperRegistry.list_stores():
            config = config_overrides.get(store)
            scraper = ScraperFactory.create(store, config)
            scrapers.append(scraper)

        logger.info("created_all_scrapers", count=len(scrapers))

        return scrapers


def register_default_scrapers() -> None:
    """
    Register all default scrapers

    This should be called during application initialization.
    """
    # Import scrapers here to avoid circular imports
    from .pichau import PichauScraper
    from .kabum import KabumScraper
    from .terabyte import TerabyteScraper

    ScraperRegistry.register(Store.PICHAU, PichauScraper)
    ScraperRegistry.register(Store.KABUM, KabumScraper)
    ScraperRegistry.register(Store.TERABYTE, TerabyteScraper)

    logger.info("default_scrapers_registered", count=len(ScraperRegistry.list_stores()))


# Auto-register on module import
register_default_scrapers()
