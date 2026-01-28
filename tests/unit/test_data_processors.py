"""
Unit tests for data processors

Tests data cleaning, validation, and enrichment.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.data.processors import (
    DataCleaner,
    DataValidator,
    DataEnricher,
    ValidationError,
)
from src.backend.core.models import ProductInDB, RawProduct, Price, Store, ChipBrand


@pytest.fixture
def sample_product():
    """Sample product for testing"""
    return ProductInDB(
        id=1,
        title="Placa de Vídeo ASUS ROG RTX 4090 24GB",
        price=Price(raw="R$ 12.000,00", value=Decimal("12000.00")),
        url="https://pichau.com.br/produto/123",
        store=Store.PICHAU,
        chip_brand=ChipBrand.NVIDIA,
        manufacturer="ASUS",
        model="RTX 4090",
        scraped_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestDataCleaner:
    """Test DataCleaner"""

    def test_clean_price(self):
        """Test price cleaning"""
        price = Price(raw="R$  12.000,00  ", value=Decimal("12000.123"))
        cleaned = DataCleaner.clean_price(price)

        assert cleaned.raw == "R$ 12.000,00"
        assert cleaned.value == Decimal("12000.12")

    def test_clean_text(self):
        """Test text cleaning"""
        text = "  Placa   de   Vídeo  "
        cleaned = DataCleaner.clean_text(text)

        assert cleaned == "Placa de Vídeo"

    def test_clean_text_encoding(self):
        """Test encoding fix"""
        text = "PlacaÃ§Ã£o"
        cleaned = DataCleaner.clean_text(text)

        assert "ç" in cleaned or "ã" in cleaned  # Should fix encoding

    def test_standardize_manufacturer(self):
        """Test manufacturer standardization"""
        assert DataCleaner.standardize_manufacturer("AZUS") == "ASUS"
        assert DataCleaner.standardize_manufacturer("M.S.I") == "MSI"
        assert DataCleaner.standardize_manufacturer("GIGA BYTE") == "GIGABYTE"
        assert DataCleaner.standardize_manufacturer("Unknown") == "Unknown"

    def test_clean_product(self, sample_product):
        """Test cleaning full product"""
        # Add some dirty data
        sample_product.title = "  Placa   RTX  "
        sample_product.manufacturer = "AZUS"

        cleaned = DataCleaner.clean_product(sample_product)

        assert cleaned.title == "Placa RTX"
        assert cleaned.manufacturer == "ASUS"

    def test_remove_duplicates(self, sample_product):
        """Test duplicate removal"""
        products = [sample_product, sample_product]  # Same URL

        unique = DataCleaner.remove_duplicates(products)

        assert len(unique) == 1


class TestDataValidator:
    """Test DataValidator"""

    def test_validate_price_valid(self):
        """Test valid price"""
        valid, error = DataValidator.validate_price(Decimal("5000.00"))

        assert valid is True
        assert error is None

    def test_validate_price_too_low(self):
        """Test price below minimum"""
        valid, error = DataValidator.validate_price(Decimal("50.00"))

        assert valid is False
        assert "below minimum" in error

    def test_validate_price_too_high(self):
        """Test price above maximum"""
        valid, error = DataValidator.validate_price(Decimal("100000.00"))

        assert valid is False
        assert "above maximum" in error

    def test_validate_url_valid(self):
        """Test valid URL"""
        valid, error = DataValidator.validate_url("https://example.com/product")

        assert valid is True
        assert error is None

    def test_validate_url_invalid(self):
        """Test invalid URL"""
        valid, error = DataValidator.validate_url("not-a-url")

        assert valid is False
        assert "must start with http" in error

    def test_validate_title_valid(self):
        """Test valid title"""
        valid, error = DataValidator.validate_title("Placa de Vídeo RTX 4090")

        assert valid is True
        assert error is None

    def test_validate_title_too_short(self):
        """Test title too short"""
        valid, error = DataValidator.validate_title("RTX")

        assert valid is False
        assert "too short" in error

    def test_validate_product_valid(self, sample_product):
        """Test valid product"""
        valid, errors = DataValidator.validate_product(sample_product)

        assert valid is True
        assert len(errors) == 0

    def test_validate_product_invalid_price(self, sample_product):
        """Test product with invalid price"""
        # Bypass Pydantic validation by using model_copy
        sample_product.price.value = Decimal("50.00")  # Too low

        valid, errors = DataValidator.validate_product(sample_product)

        assert valid is False
        assert any("price" in e.lower() for e in errors)

    def test_validate_batch(self, sample_product):
        """Test batch validation"""
        # Create fully valid product first
        invalid_product = ProductInDB(
            id=2,
            title="Valid Product Title Here",  # Valid
            price=Price(raw="R$ 1000,00", value=Decimal("1000.00")),  # Valid initially
            url="https://valid-url.com/product",  # Valid
            store=Store.PICHAU,
            chip_brand=ChipBrand.NVIDIA,
            manufacturer="Test",
            model="Test",
            scraped_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Now modify to invalid price (bypasses Pydantic, tests DataValidator)
        invalid_product.price.value = Decimal("10.00")

        valid_products, invalid_products = DataValidator.validate_batch(
            [sample_product, invalid_product]
        )

        assert len(valid_products) == 1
        assert len(invalid_products) == 1


class TestDataEnricher:
    """Test DataEnricher"""

    def test_enrich_product(self):
        """Test product enrichment"""
        enricher = DataEnricher()

        raw = RawProduct(
            title="Placa de Vídeo MSI GeForce RTX 4080",
            price=Price(raw="R$ 8.000,00", value=Decimal("8000.00")),
            url="https://kabum.com.br/produto/123",
            store=Store.KABUM,
        )

        enriched = enricher.enrich_product(raw)

        assert enriched.chip_brand == ChipBrand.NVIDIA
        assert enriched.manufacturer == "MSI"
        assert "RTX 4080" in enriched.model

    def test_enrich_batch(self):
        """Test batch enrichment"""
        enricher = DataEnricher()

        raw_products = [
            RawProduct(
                title="ASUS RTX 4090",
                price=Price(raw="R$ 12000", value=Decimal("12000")),
                url="https://test.com/1",
                store=Store.PICHAU,
            ),
            RawProduct(
                title="AMD RX 7900 XT",
                price=Price(raw="R$ 6000", value=Decimal("6000")),
                url="https://test.com/2",
                store=Store.KABUM,
            ),
        ]

        enriched = enricher.enrich_batch(raw_products)

        assert len(enriched) == 2
        assert enriched[0].chip_brand == ChipBrand.NVIDIA
        assert enriched[1].chip_brand == ChipBrand.AMD


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
