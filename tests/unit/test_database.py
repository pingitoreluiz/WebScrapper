"""
Unit tests for database layer

Tests models, repository, and database operations.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from src.backend.core.models import Price, RawProduct, EnrichedProduct, ChipBrand, Store
from src.backend.core.database import create_tables, get_db_session
from src.backend.core.repository import ProductRepository


class TestPriceModel:
    """Test Price value object"""
    
    def test_price_from_string(self):
        """Test creating Price from Brazilian format string"""
        price = Price.from_string("R$ 2.500,99")
        
        assert price.raw == "R$ 2.500,99"
        assert price.value == Decimal("2500.99")
        assert price.currency == "BRL"
    
    def test_price_validation_min(self):
        """Test price minimum validation"""
        with pytest.raises(ValueError, match="out of valid range"):
            Price(raw="R$ 50,00", value=Decimal("50"))
    
    def test_price_validation_max(self):
        """Test price maximum validation"""
        with pytest.raises(ValueError, match="out of valid range"):
            Price(raw="R$ 100.000,00", value=Decimal("100000"))
    
    def test_price_float_conversion(self):
        """Test converting price to float"""
        price = Price.from_string("R$ 1.234,56")
        assert float(price) == 1234.56


class TestProductModels:
    """Test product models"""
    
    def test_raw_product_creation(self):
        """Test creating RawProduct"""
        product = RawProduct(
            title="Placa de Vídeo NVIDIA GeForce RTX 4090",
            price=Price.from_string("R$ 12.000,00"),
            url="https://example.com/product/123",
            store=Store.PICHAU
        )
        
        assert product.title == "Placa de Vídeo NVIDIA GeForce RTX 4090"
        assert product.store == Store.PICHAU
        assert float(product.price) == 12000.0
    
    def test_enriched_product_creation(self):
        """Test creating EnrichedProduct"""
        product = EnrichedProduct(
            title="Placa de Vídeo ASUS ROG RTX 4090",
            price=Price.from_string("R$ 12.000,00"),
            url="https://example.com/product/123",
            store=Store.PICHAU,
            chip_brand=ChipBrand.NVIDIA,
            manufacturer="ASUS",
            model="RTX 4090"
        )
        
        assert product.chip_brand == ChipBrand.NVIDIA
        assert product.manufacturer == "ASUS"
        assert product.model == "RTX 4090"
        assert isinstance(product.scraped_at, datetime)


@pytest.fixture
def db_session():
    """Fixture to provide database session for tests"""
    # Create tables
    create_tables()
    
    # Provide session
    with get_db_session() as session:
        yield session
        # Cleanup happens automatically


class TestProductRepository:
    """Test ProductRepository"""
    
    def test_create_product(self, db_session):
        """Test creating a product"""
        repo = ProductRepository(db_session)
        
        product = EnrichedProduct(
            title="Placa de Vídeo MSI RTX 4080",
            price=Price.from_string("R$ 8.500,00"),
            url="https://example.com/product/456",
            store=Store.KABUM,
            chip_brand=ChipBrand.NVIDIA,
            manufacturer="MSI",
            model="RTX 4080"
        )
        
        saved = repo.create(product)
        
        assert saved.id is not None
        assert saved.title == product.title
        assert float(saved.price.value) == 8500.0
    
    def test_create_duplicate_url_updates(self, db_session):
        """Test that creating product with existing URL updates it"""
        repo = ProductRepository(db_session)
        
        # Create first product
        product1 = EnrichedProduct(
            title="Product V1",
            price=Price.from_string("R$ 1.000,00"),
            url="https://example.com/product/789",
            store=Store.PICHAU,
            chip_brand=ChipBrand.NVIDIA,
            manufacturer="ASUS",
            model="RTX 4070"
        )
        
        saved1 = repo.create(product1)
        first_id = saved1.id
        
        # Create second product with same URL but different price
        product2 = EnrichedProduct(
            title="Product V2",
            price=Price.from_string("R$ 900,00"),
            url="https://example.com/product/789",  # Same URL
            store=Store.PICHAU,
            chip_brand=ChipBrand.NVIDIA,
            manufacturer="ASUS",
            model="RTX 4070"
        )
        
        saved2 = repo.create(product2)
        
        # Should have same ID (updated, not created)
        assert saved2.id == first_id
        assert saved2.title == "Product V2"
        assert float(saved2.price.value) == 900.0
    
    def test_get_best_deals(self, db_session):
        """Test getting best deals"""
        repo = ProductRepository(db_session)
        
        # Create multiple products
        products = [
            EnrichedProduct(
                title=f"Product {i}",
                price=Price.from_string(f"R$ {1000 + i * 100},00"),
                url=f"https://example.com/product/{i}",
                store=Store.PICHAU,
                chip_brand=ChipBrand.NVIDIA,
                manufacturer="ASUS",
                model="RTX 4070"
            )
            for i in range(5)
        ]
        
        for p in products:
            repo.create(p)
        
        # Get best deals
        best = repo.get_best_deals(limit=3)
        
        assert len(best) == 3
        assert float(best[0].price.value) == 1000.0  # Lowest price first
        assert float(best[1].price.value) == 1100.0
        assert float(best[2].price.value) == 1200.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
