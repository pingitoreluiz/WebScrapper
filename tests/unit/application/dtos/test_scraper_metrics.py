"""Tests for ScraperMetrics DTO."""

import pytest
from datetime import datetime

from src.scrapers.application.dtos.scraper_metrics import ScraperMetricsDTO


class TestScraperMetricsDTO:
    """Test suite for ScraperMetricsDTO."""

    def test_create_metrics_with_required_fields(self):
        """Test creating metrics with required fields."""
        started = datetime.utcnow()
        metrics = ScraperMetricsDTO(store="Pichau", started_at=started)

        assert metrics.store == "Pichau"
        assert metrics.started_at == started
        assert metrics.finished_at is None
        assert metrics.execution_time == 0.0
        assert metrics.products_found == 0
        assert metrics.products_saved == 0
        assert metrics.success is False

    def test_create_metrics_with_all_fields(self):
        """Test creating metrics with all fields."""
        started = datetime(2024, 1, 1, 10, 0, 0)
        finished = datetime(2024, 1, 1, 10, 5, 30)

        metrics = ScraperMetricsDTO(
            store="Kabum",
            started_at=started,
            finished_at=finished,
            execution_time=330.5,
            products_found=100,
            products_saved=95,
            products_skipped=5,
            pages_scraped=10,
            errors=2,
            captchas_detected=1,
            success=True,
            error_message=None,
        )

        assert metrics.store == "Kabum"
        assert metrics.started_at == started
        assert metrics.finished_at == finished
        assert metrics.execution_time == 330.5
        assert metrics.products_found == 100
        assert metrics.products_saved == 95
        assert metrics.products_skipped == 5
        assert metrics.pages_scraped == 10
        assert metrics.errors == 2
        assert metrics.captchas_detected == 1
        assert metrics.success is True
        assert metrics.error_message is None

    def test_get_success_rate_no_products(self):
        """Test success rate when no products found."""
        metrics = ScraperMetricsDTO(store="Pichau", started_at=datetime.utcnow())

        assert metrics.get_success_rate() == 0.0

    def test_get_success_rate_all_saved(self):
        """Test success rate when all products saved."""
        metrics = ScraperMetricsDTO(
            store="Pichau",
            started_at=datetime.utcnow(),
            products_found=100,
            products_saved=100,
        )

        assert metrics.get_success_rate() == 100.0

    def test_get_success_rate_partial(self):
        """Test success rate with partial save."""
        metrics = ScraperMetricsDTO(
            store="Pichau",
            started_at=datetime.utcnow(),
            products_found=100,
            products_saved=80,
        )

        assert metrics.get_success_rate() == 80.0

    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        started = datetime(2024, 1, 1, 10, 0, 0)
        finished = datetime(2024, 1, 1, 10, 5, 0)

        metrics = ScraperMetricsDTO(
            store="Pichau",
            started_at=started,
            finished_at=finished,
            execution_time=300.0,
            products_found=50,
            products_saved=45,
            products_skipped=5,
            pages_scraped=5,
            errors=1,
            captchas_detected=0,
            success=True,
        )

        result = metrics.to_dict()

        assert result["store"] == "Pichau"
        assert result["started_at"] == started.isoformat()
        assert result["finished_at"] == finished.isoformat()
        assert result["execution_time"] == 300.0
        assert result["products_found"] == 50
        assert result["products_saved"] == 45
        assert result["products_skipped"] == 5
        assert result["pages_scraped"] == 5
        assert result["errors"] == 1
        assert result["captchas_detected"] == 0
        assert result["success"] is True
        assert result["error_message"] is None
        assert result["success_rate"] == 90.0

    def test_to_dict_with_error(self):
        """Test converting failed metrics to dictionary."""
        started = datetime(2024, 1, 1, 10, 0, 0)

        metrics = ScraperMetricsDTO(
            store="Pichau",
            started_at=started,
            success=False,
            error_message="Connection timeout",
        )

        result = metrics.to_dict()

        assert result["success"] is False
        assert result["error_message"] == "Connection timeout"
