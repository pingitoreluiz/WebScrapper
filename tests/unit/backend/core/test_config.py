"""Tests for config module."""

import pytest
from src.backend.core.config import (
    AppConfig,
    get_config,
    reload_config,
    KNOWN_MANUFACTURERS,
    STORE_URLS,
)


class TestAppConfig:
    """Test suite for AppConfig configuration."""

    def test_config_creation(self):
        """Test creating AppConfig instance."""
        config = AppConfig()

        assert config is not None
        assert hasattr(config, "database")
        assert hasattr(config, "api")
        assert hasattr(config, "scraper")

    def test_config_database(self):
        """Test database configuration."""
        config = AppConfig()

        assert config.database.url is not None
        assert isinstance(config.database.url, str)
        assert config.database.pool_size > 0

    def test_config_api(self):
        """Test API configuration."""
        config = AppConfig()

        assert isinstance(config.api.host, str)
        assert isinstance(config.api.port, int)
        assert config.api.port > 0

    def test_config_scraper(self):
        """Test scraper configuration."""
        config = AppConfig()

        assert config.scraper.max_concurrent >= 1
        assert config.scraper.timeout > 0
        assert config.scraper.min_price > 0
        assert config.scraper.max_price > config.scraper.min_price

    def test_get_config_singleton(self):
        """Test get_config returns singleton."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reload_config(self):
        """Test reload_config creates new instance."""
        config1 = get_config()
        config2 = reload_config()

        # Should be different instances after reload
        assert isinstance(config2, AppConfig)

    def test_known_manufacturers_list(self):
        """Test KNOWN_MANUFACTURERS constant."""
        assert isinstance(KNOWN_MANUFACTURERS, list)
        assert len(KNOWN_MANUFACTURERS) > 0

        # Check for common manufacturers
        assert "ASUS" in KNOWN_MANUFACTURERS
        assert "MSI" in KNOWN_MANUFACTURERS
        assert "GIGABYTE" in KNOWN_MANUFACTURERS

    def test_known_manufacturers_uppercase(self):
        """Test that manufacturers are uppercase."""
        for manufacturer in KNOWN_MANUFACTURERS:
            assert manufacturer == manufacturer.upper()

    def test_store_urls(self):
        """Test STORE_URLS configuration."""
        assert isinstance(STORE_URLS, dict)
        assert "pichau" in STORE_URLS
        assert "kabum" in STORE_URLS
        assert "terabyte" in STORE_URLS
