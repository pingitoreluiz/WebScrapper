"""Tests for ScraperRun entity."""

import pytest
from datetime import datetime, timedelta

from src.scrapers.domain.entities.scraper_run import ScraperRun
from src.scrapers.domain.entities.product import Product
from src.scrapers.domain.value_objects.price import Price
from src.scrapers.domain.value_objects.url import ProductUrl


class TestScraperRun:
    """Test suite for ScraperRun entity."""

    def test_create_scraper_run_with_valid_data(self):
        """Test creating a scraper run with valid data."""
        run = ScraperRun(store="Pichau")

        assert run.store == "Pichau"
        assert run.products_found == 0
        assert run.products_saved == 0
        assert run.success is False
        assert run.is_running() is True

    def test_scraper_run_store_cannot_be_empty(self):
        """Test that store name cannot be empty."""
        with pytest.raises(ValueError, match="Store name cannot be empty"):
            ScraperRun(store="")

        with pytest.raises(ValueError, match="Store name cannot be empty"):
            ScraperRun(store="   ")

    def test_start_scraper_run(self):
        """Test starting a scraper run."""
        run = ScraperRun(store="Pichau")
        original_time = run.started_at

        run.start()

        assert run.started_at >= original_time
        assert run.finished_at is None
        assert run.success is False

    def test_finish_successfully(self):
        """Test finishing scraper run successfully."""
        run = ScraperRun(store="Pichau")
        run.start()

        run.finish_successfully()

        assert run.finished_at is not None
        assert run.success is True
        assert run.error_message is None
        assert run.execution_time > 0

    def test_finish_with_error(self):
        """Test finishing scraper run with error."""
        run = ScraperRun(store="Pichau")
        run.start()

        error_msg = "Connection timeout"
        run.finish_with_error(error_msg)

        assert run.finished_at is not None
        assert run.success is False
        assert run.error_message == error_msg
        assert run.execution_time > 0

    def test_increment_products_found(self):
        """Test incrementing products found counter."""
        run = ScraperRun(store="Pichau")

        run.increment_products_found()
        assert run.products_found == 1

        run.increment_products_found(5)
        assert run.products_found == 6

    def test_increment_products_saved(self):
        """Test incrementing products saved counter."""
        run = ScraperRun(store="Pichau")

        run.increment_products_saved()
        assert run.products_saved == 1

        run.increment_products_saved(3)
        assert run.products_saved == 4

    def test_increment_products_skipped(self):
        """Test incrementing products skipped counter."""
        run = ScraperRun(store="Pichau")

        run.increment_products_skipped()
        assert run.products_skipped == 1

        run.increment_products_skipped(2)
        assert run.products_skipped == 3

    def test_increment_pages_scraped(self):
        """Test incrementing pages scraped counter."""
        run = ScraperRun(store="Pichau")

        run.increment_pages_scraped()
        assert run.pages_scraped == 1

        run.increment_pages_scraped(4)
        assert run.pages_scraped == 5

    def test_increment_errors(self):
        """Test incrementing errors counter."""
        run = ScraperRun(store="Pichau")

        run.increment_errors()
        assert run.errors == 1

        run.increment_errors(2)
        assert run.errors == 3

    def test_increment_captchas(self):
        """Test incrementing CAPTCHAs counter."""
        run = ScraperRun(store="Pichau")

        run.increment_captchas()
        assert run.captchas_detected == 1

        run.increment_captchas(3)
        assert run.captchas_detected == 4

    def test_add_product(self):
        """Test adding product to run."""
        run = ScraperRun(store="Pichau")

        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")
        product = Product(title="Test", price=price, url=url, store="Pichau")

        run.add_product(product)

        assert len(run.products) == 1
        assert run.products[0] == product
        assert run.products_found == 1

    def test_add_duplicate_product(self):
        """Test that duplicate products are not added."""
        run = ScraperRun(store="Pichau")

        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")
        product = Product(title="Test", price=price, url=url, store="Pichau")

        run.add_product(product)
        run.add_product(product)  # Try to add same product again

        assert len(run.products) == 1  # Should still be 1
        assert run.products_found == 1  # Only counted once

    def test_is_running(self):
        """Test checking if run is running."""
        run = ScraperRun(store="Pichau")

        assert run.is_running() is True

        run.finish_successfully()
        assert run.is_running() is False

    def test_get_success_rate(self):
        """Test calculating success rate."""
        run = ScraperRun(store="Pichau")

        # No products found
        assert run.get_success_rate() == 0.0

        # 8 saved out of 10 found
        run.products_found = 10
        run.products_saved = 8
        assert run.get_success_rate() == 80.0

        # All saved
        run.products_saved = 10
        assert run.get_success_rate() == 100.0

    def test_validation_negative_execution_time(self):
        """Test that negative execution time is invalid."""
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            ScraperRun(store="Pichau", execution_time=-1.0)

    def test_validation_negative_products_found(self):
        """Test that negative products found is invalid."""
        with pytest.raises(ValueError, match="Products found cannot be negative"):
            ScraperRun(store="Pichau", products_found=-1)

    def test_validation_negative_products_saved(self):
        """Test that negative products saved is invalid."""
        with pytest.raises(ValueError, match="Products saved cannot be negative"):
            ScraperRun(store="Pichau", products_saved=-1)

    def test_validation_saved_exceeds_found(self):
        """Test that saved cannot exceed found."""
        with pytest.raises(
            ValueError, match="Products saved cannot exceed products found"
        ):
            ScraperRun(store="Pichau", products_found=5, products_saved=10)

    def test_scraper_run_equality(self):
        """Test scraper run equality based on ID."""
        run1 = ScraperRun(store="Pichau")
        run2 = ScraperRun(store="Pichau")

        assert run1 != run2  # Different IDs
        assert run1 == run1  # Same instance

    def test_scraper_run_hash(self):
        """Test scraper run can be used in sets/dicts."""
        run1 = ScraperRun(store="Pichau")
        run2 = ScraperRun(store="Kabum")

        run_set = {run1, run2}
        assert len(run_set) == 2

    def test_repr(self):
        """Test string representation."""
        run = ScraperRun(store="Pichau")
        run.products_found = 10
        run.products_saved = 8

        repr_str = repr(run)
        assert "Pichau" in repr_str
        assert "running" in repr_str
        assert "8/10" in repr_str
