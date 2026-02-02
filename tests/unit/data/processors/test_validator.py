"""Tests for DataValidator."""

import pytest
from decimal import Decimal
from datetime import datetime

from src.data.processors.validator import DataValidator, ValidationError
from src.backend.core.models import ProductInDB, Price


class TestDataValidator:
    """Test suite for DataValidator."""
    
    def test_validate_price_valid(self):
        """Test price validation with valid price."""
        is_valid, error = DataValidator.validate_price(Decimal("1500.00"))
        
        assert is_valid is True
        assert error is None
    
    def test_validate_price_too_low(self):
        """Test price validation with price too low."""
        is_valid, error = DataValidator.validate_price(Decimal("50.00"))
        
        assert is_valid is False
        assert "below minimum" in error or "too low" in error.lower()
    
    def test_validate_price_too_high(self):
        """Test price validation with price too high."""
        is_valid, error = DataValidator.validate_price(Decimal("60000.00"))
        
        assert is_valid is False
        assert "above maximum" in error or "too high" in error.lower()
    
    def test_validate_url_valid_https(self):
        """Test URL validation with valid HTTPS URL."""
        is_valid, error = DataValidator.validate_url("https://example.com/product")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_url_valid_http(self):
        """Test URL validation with valid HTTP URL."""
        is_valid, error = DataValidator.validate_url("http://example.com/product")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URL."""
        is_valid, error = DataValidator.validate_url("not-a-url")
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_title_valid(self):
        """Test title validation with valid title."""
        is_valid, error = DataValidator.validate_title("RTX 4070 Ti")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_title_empty(self):
        """Test title validation with empty title."""
        is_valid, error = DataValidator.validate_title("")
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_title_too_short(self):
        """Test title validation with too short title."""
        is_valid, error = DataValidator.validate_title("RT")
        
        assert is_valid is False
        assert "short" in error.lower()
    
    def test_validate_product_valid(self):
        """Test product validation with valid product."""
        product = ProductInDB(
            id=1,
            title="RTX 4070 Ti",
            price=Price(raw="R$ 2500", value=Decimal("2500"), currency="BRL"),
            url="https://example.com/product",
            store="Pichau",
            chip_brand="NVIDIA",
            manufacturer="ASUS",
            model="RTX 4070",
            scraped_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        is_valid, errors = DataValidator.validate_product(product)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_product_invalid_url(self):
        """Test product validation with invalid URL."""
        product = ProductInDB(
            id=1,
            title="RTX 4070 Ti",
            price=Price(raw="R$ 2500", value=Decimal("2500"), currency="BRL"),
            url="https://example.com/product",  # Valid for creation
            store="Pichau",
            chip_brand="NVIDIA",
            manufacturer="ASUS",
            model="RTX 4070",
            scraped_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Manually set invalid URL after creation to test validation
        product.url = "not-a-valid-url"
        
        is_valid, errors = DataValidator.validate_product(product)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_title_strict_mode(self):
        """Test title validation in strict mode."""
        # Test with too short title directly
        is_valid, error = DataValidator.validate_title("RT")
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_batch(self):
        """Test batch validation."""
        product1 = ProductInDB(
            id=1,
            title="RTX 4070 Ti",
            price=Price(raw="R$ 2500", value=Decimal("2500"), currency="BRL"),
            url="https://example.com/1",
            store="Pichau",
            chip_brand="NVIDIA",
            manufacturer="ASUS",
            model="RTX 4070",
            scraped_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        product2 = ProductInDB(
            id=2,
            title="RX 7800 XT",
            price=Price(raw="R$ 3000", value=Decimal("3000"), currency="BRL"),
            url="https://example.com/2",
            store="Kabum",
            chip_brand="AMD",
            manufacturer="MSI",
            model="RX 7800",
            scraped_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Make one invalid by changing URL after creation
        product2.url = "invalid-url"
        
        products = [product1, product2]
        
        valid, invalid = DataValidator.validate_batch(products, remove_invalid=True)
        
        assert len(valid) == 1
        assert len(invalid) == 1
    
    def test_get_validation_stats(self):
        """Test getting validation statistics."""
        products = [
            ProductInDB(
                id=1,
                title="RTX 4070 Ti",
                price=Price(raw="R$ 2500", value=Decimal("2500"), currency="BRL"),
                url="https://example.com/1",
                store="Pichau",
                chip_brand="NVIDIA",
                manufacturer="ASUS",
                model="RTX 4070",
                scraped_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        stats = DataValidator.get_validation_stats(products)
        
        assert stats["total"] == 1
        assert "valid" in stats
        assert "invalid" in stats
