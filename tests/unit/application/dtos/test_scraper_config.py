"""Tests for ScraperConfig DTO."""

import pytest

from src.scrapers.application.dtos.scraper_config import ScraperConfigDTO


class TestScraperConfigDTO:
    """Test suite for ScraperConfigDTO."""

    def test_create_config_with_defaults(self):
        """Test creating config with default values."""
        config = ScraperConfigDTO(store="Pichau")

        assert config.store == "Pichau"
        assert config.headless is True
        assert config.max_pages == 20
        assert config.timeout == 30000
        assert config.user_agent is None
        assert config.viewport == {"width": 1920, "height": 1080}

    def test_create_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = ScraperConfigDTO(
            store="Kabum",
            headless=False,
            max_pages=10,
            timeout=60000,
            user_agent="Custom Agent",
            viewport={"width": 1280, "height": 720},
        )

        assert config.store == "Kabum"
        assert config.headless is False
        assert config.max_pages == 10
        assert config.timeout == 60000
        assert config.user_agent == "Custom Agent"
        assert config.viewport == {"width": 1280, "height": 720}

    def test_validate_valid_config(self):
        """Test validating a valid config."""
        config = ScraperConfigDTO(store="Pichau")

        # Should not raise
        config.validate()

    def test_validate_empty_store(self):
        """Test that empty store fails validation."""
        config = ScraperConfigDTO(store="")

        with pytest.raises(ValueError, match="Store name cannot be empty"):
            config.validate()

    def test_validate_whitespace_store(self):
        """Test that whitespace-only store fails validation."""
        config = ScraperConfigDTO(store="   ")

        with pytest.raises(ValueError, match="Store name cannot be empty"):
            config.validate()

    def test_validate_negative_max_pages(self):
        """Test that negative max_pages fails validation."""
        config = ScraperConfigDTO(store="Pichau", max_pages=-1)

        with pytest.raises(ValueError, match="Max pages must be positive"):
            config.validate()

    def test_validate_zero_max_pages(self):
        """Test that zero max_pages fails validation."""
        config = ScraperConfigDTO(store="Pichau", max_pages=0)

        with pytest.raises(ValueError, match="Max pages must be positive"):
            config.validate()

    def test_validate_negative_timeout(self):
        """Test that negative timeout fails validation."""
        config = ScraperConfigDTO(store="Pichau", timeout=-1000)

        with pytest.raises(ValueError, match="Timeout must be positive"):
            config.validate()

    def test_validate_zero_timeout(self):
        """Test that zero timeout fails validation."""
        config = ScraperConfigDTO(store="Pichau", timeout=0)

        with pytest.raises(ValueError, match="Timeout must be positive"):
            config.validate()
