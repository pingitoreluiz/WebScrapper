"""Tests for DataCleaner."""

import pytest
from decimal import Decimal
from datetime import datetime

from src.data.processors.cleaner import DataCleaner
from src.backend.core.models import ProductInDB, Price


class TestDataCleaner:
    """Test suite for DataCleaner."""

    def test_clean_price(self):
        """Test price cleaning."""
        price = Price(raw="R$  1.500,00  ", value=Decimal("1500.00"), currency="BRL")

        cleaned = DataCleaner.clean_price(price)

        assert cleaned.raw == "R$ 1.500,00"
        assert cleaned.value == Decimal("1500.00")
        assert cleaned.currency == "BRL"

    def test_clean_text_removes_whitespace(self):
        """Test text cleaning removes extra whitespace."""
        text = "RTX   4070    Ti"

        cleaned = DataCleaner.clean_text(text)

        assert cleaned == "RTX 4070 Ti"

    def test_clean_text_fixes_encoding(self):
        """Test text cleaning fixes encoding issues."""
        text = "PlacaÃ§Ã£o"

        cleaned = DataCleaner.clean_text(text)

        assert "ç" in cleaned or "ã" in cleaned

    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        assert DataCleaner.clean_text("") == ""
        assert DataCleaner.clean_text(None) is None

    def test_standardize_manufacturer_asus(self):
        """Test manufacturer standardization for ASUS."""
        assert DataCleaner.standardize_manufacturer("ASUS") == "ASUS"
        assert DataCleaner.standardize_manufacturer("asus") == "ASUS"
        assert DataCleaner.standardize_manufacturer("AZUS") == "ASUS"

    def test_standardize_manufacturer_msi(self):
        """Test manufacturer standardization for MSI."""
        assert DataCleaner.standardize_manufacturer("MSI") == "MSI"
        assert DataCleaner.standardize_manufacturer("M.S.I") == "MSI"

    def test_standardize_manufacturer_gigabyte(self):
        """Test manufacturer standardization for Gigabyte."""
        assert DataCleaner.standardize_manufacturer("GIGABYTE") == "GIGABYTE"
        assert DataCleaner.standardize_manufacturer("GIGA BYTE") == "GIGABYTE"
        assert DataCleaner.standardize_manufacturer("GBT") == "GIGABYTE"

    def test_standardize_manufacturer_unknown(self):
        """Test manufacturer standardization for unknown brand."""
        result = DataCleaner.standardize_manufacturer("UnknownBrand")
        assert result == "UnknownBrand"

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        products = [
            ProductInDB(
                id=1,
                title="Product 1",
                price=Price(raw="R$ 100", value=Decimal("100"), currency="BRL"),
                url="https://example.com/1",
                store="Pichau",
                chip_brand="NVIDIA",
                manufacturer="ASUS",
                model="RTX 4070",
                scraped_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            ProductInDB(
                id=2,
                title="Product 1 Duplicate",
                price=Price(raw="R$ 100", value=Decimal("100"), currency="BRL"),
                url="https://example.com/1",  # Same URL
                store="Pichau",
                chip_brand="NVIDIA",
                manufacturer="ASUS",
                model="RTX 4070",
                scraped_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            ProductInDB(
                id=3,
                title="Product 2",
                price=Price(raw="R$ 200", value=Decimal("200"), currency="BRL"),
                url="https://example.com/2",
                store="Kabum",
                chip_brand="AMD",
                manufacturer="MSI",
                model="RX 7800",
                scraped_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]

        unique = DataCleaner.remove_duplicates(products)

        assert len(unique) == 2
        assert str(unique[0].url) == "https://example.com/1"
        assert str(unique[1].url) == "https://example.com/2"

    def test_remove_duplicates_no_duplicates(self):
        """Test duplicate removal with no duplicates."""
        products = [
            ProductInDB(
                id=1,
                title="Product 1",
                price=Price(raw="R$ 100", value=Decimal("100"), currency="BRL"),
                url="https://example.com/1",
                store="Pichau",
                chip_brand="NVIDIA",
                manufacturer="ASUS",
                model="RTX 4070",
                scraped_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        ]

        unique = DataCleaner.remove_duplicates(products)

        assert len(unique) == 1

    def test_clean_batch(self):
        """Test batch cleaning."""
        products = [
            ProductInDB(
                id=1,
                title="RTX   4070",
                price=Price(raw="R$  100  ", value=Decimal("100"), currency="BRL"),
                url="https://example.com/1",
                store="Pichau",
                chip_brand="NVIDIA",
                manufacturer="asus",
                model="RTX 4070",
                scraped_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        ]

        cleaned = DataCleaner.clean_batch(products)

        assert len(cleaned) == 1
        assert cleaned[0].title == "RTX 4070"
        assert cleaned[0].manufacturer == "ASUS"
