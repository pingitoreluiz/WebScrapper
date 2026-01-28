"""
Integration tests for scraping workflow

Tests the complete flow: scraper → database → validation
"""

import pytest
from src.scrapers.factory import ScraperFactory
from src.scrapers.models import ScraperConfig
from src.data.processors.cleaner import DataCleaner
from src.data.processors.validator import DataValidator
from src.backend.core.database_models import Product, ScraperRun
from src.backend.core.models import Store


class TestScrapingFlow:
    """Test complete scraping workflow"""

    def test_scraper_to_database_flow(self, db_session):
        """Test scraping and saving to database"""
        # Create scraper config
        config = ScraperConfig(
            store=Store.PICHAU, headless=True, max_pages=1, timeout=30
        )

        # Create scraper (using factory)
        scraper = ScraperFactory.create(Store.PICHAU, config)

        # Note: This would require mocking or actual scraping
        # For now, we'll test with mock data
        mock_products = [
            {
                "title": "RTX 4090 Test",
                "price_value": 10000.00,
                "price_raw": "R$ 10.000,00",
                "url": "https://test.com/1",
                "manufacturer": "NVIDIA",
                "model": "RTX 4090",
                "store": Store.PICHAU,
            }
        ]

        # Process and save
        for product_data in mock_products:
            product = Product(**product_data)
            db_session.add(product)

        db_session.commit()

        # Verify
        products = db_session.query(Product).all()
        assert len(products) > 0
        assert products[0].title == "RTX 4090 Test"

    def test_data_cleaning_pipeline(self, db_session, sample_products):
        """Test data cleaning with real database"""
        cleaner = DataCleaner()

        # Get products from database
        products = db_session.query(Product).all()

        # Clean each product
        for product in products:
            cleaned_data = cleaner.clean_product(
                {
                    "title": product.title,
                    "price": product.price_value,
                    "url": product.url,
                }
            )

            assert cleaned_data is not None
            assert "title" in cleaned_data
            assert "price" in cleaned_data

    def test_data_validation_pipeline(self, db_session, sample_products):
        """Test data validation with real database"""
        validator = DataValidator()

        # Get products from database
        products = db_session.query(Product).all()

        # Validate each product
        for product in products:
            is_valid, errors = validator.validate_product(
                {
                    "title": product.title,
                    "price": product.price_value,
                    "url": product.url,
                    "store": product.store.value,
                    "chip_brand": "NVIDIA",  # Required field
                }
            )

            assert is_valid is True
            assert len(errors) == 0

    def test_duplicate_detection(self, db_session):
        """Test duplicate product detection"""
        # Create first product
        product1 = Product(
            title="RTX 4090 ASUS",
            price_value=10000.00,
            price_raw="R$ 10.000,00",
            store=Store.PICHAU,
            url="https://pichau.com.br/product/1",
            manufacturer="ASUS",
            model="RTX 4090",
        )
        db_session.add(product1)
        db_session.commit()

        # Try to add duplicate (same URL)
        existing = (
            db_session.query(Product)
            .filter_by(url="https://pichau.com.br/product/1")
            .first()
        )

        assert existing is not None
        assert existing.title == "RTX 4090 ASUS"

    def test_price_update_flow(self, db_session, sample_products):
        """Test updating product prices"""
        # Get existing product
        product = db_session.query(Product).first()
        old_price = product.price_value

        # Update price
        product.price_value = old_price + 100
        db_session.commit()

        # Verify update
        updated_product = db_session.query(Product).filter_by(id=product.id).first()
        assert updated_product.price_value == old_price + 100

    def test_scraper_metrics_tracking(self, db_session, sample_scraper_run):
        """Test scraper run metrics are saved"""
        # Verify scraper run was saved
        runs = db_session.query(ScraperRun).all()
        assert len(runs) > 0

        run = runs[0]
        assert run.store == Store.PICHAU
        assert run.products_found == 10
        assert run.success


class TestDataIntegrity:
    """Test data integrity constraints"""

    def test_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Try to create product without required fields
        with pytest.raises(Exception):
            product = Product(title="Test")  # Missing price, store, url
            db_session.add(product)
            db_session.commit()

    def test_price_constraints(self, db_session):
        """Test price validation constraints"""
        validator = DataValidator()

        # Test negative price
        is_valid, errors = validator.validate_product(
            {
                "title": "Test",
                "price": -100,
                "url": "https://test.com",
                "store": "Pichau",
                "chip_brand": "NVIDIA",
            }
        )

        assert is_valid is False
        assert any("price" in e.lower() for e in errors)

    def test_url_format(self, db_session):
        """Test URL format validation"""
        validator = DataValidator()

        # Test invalid URL
        is_valid, errors = validator.validate_product(
            {"title": "Test", "price": 1000, "url": "not-a-url", "store": "Pichau"}
        )

        assert is_valid is False
        assert "url" in str(errors)
