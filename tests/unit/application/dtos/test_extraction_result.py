"""Tests for ExtractionResult DTO."""

import pytest

from src.scrapers.application.dtos.extraction_result import ExtractionResultDTO


class TestExtractionResultDTO:
    """Test suite for ExtractionResultDTO."""

    def test_create_empty_result(self):
        """Test creating empty extraction result."""
        result = ExtractionResultDTO()

        assert result.title is None
        assert result.price_raw is None
        assert result.price_value is None
        assert result.url is None
        assert result.available is True
        assert result.extra_data == {}

    def test_create_complete_result(self):
        """Test creating complete extraction result."""
        result = ExtractionResultDTO(
            title="RTX 4070",
            price_raw="R$ 2.500,00",
            price_value=2500.0,
            url="https://example.com/product/1",
            available=True,
            extra_data={"chip_brand": "NVIDIA"},
        )

        assert result.title == "RTX 4070"
        assert result.price_raw == "R$ 2.500,00"
        assert result.price_value == 2500.0
        assert result.url == "https://example.com/product/1"
        assert result.available is True
        assert result.extra_data == {"chip_brand": "NVIDIA"}

    def test_is_valid_with_complete_data(self):
        """Test is_valid returns True for complete data."""
        result = ExtractionResultDTO(
            title="Product",
            price_raw="R$ 100,00",
            price_value=100.0,
            url="https://example.com/product",
        )

        assert result.is_valid() is True

    def test_is_valid_missing_title(self):
        """Test is_valid returns False when title is missing."""
        result = ExtractionResultDTO(
            price_raw="R$ 100,00", price_value=100.0, url="https://example.com/product"
        )

        assert result.is_valid() is False

    def test_is_valid_empty_title(self):
        """Test is_valid returns False when title is empty."""
        result = ExtractionResultDTO(
            title="   ",
            price_raw="R$ 100,00",
            price_value=100.0,
            url="https://example.com/product",
        )

        assert result.is_valid() is False

    def test_is_valid_missing_price_raw(self):
        """Test is_valid returns False when price_raw is missing."""
        result = ExtractionResultDTO(
            title="Product", price_value=100.0, url="https://example.com/product"
        )

        assert result.is_valid() is False

    def test_is_valid_missing_price_value(self):
        """Test is_valid returns False when price_value is missing."""
        result = ExtractionResultDTO(
            title="Product", price_raw="R$ 100,00", url="https://example.com/product"
        )

        assert result.is_valid() is False

    def test_is_valid_zero_price_value(self):
        """Test is_valid returns False when price_value is zero."""
        result = ExtractionResultDTO(
            title="Product",
            price_raw="R$ 0,00",
            price_value=0.0,
            url="https://example.com/product",
        )

        assert result.is_valid() is False

    def test_is_valid_negative_price_value(self):
        """Test is_valid returns False when price_value is negative."""
        result = ExtractionResultDTO(
            title="Product",
            price_raw="R$ -100,00",
            price_value=-100.0,
            url="https://example.com/product",
        )

        assert result.is_valid() is False

    def test_is_valid_missing_url(self):
        """Test is_valid returns False when URL is missing."""
        result = ExtractionResultDTO(
            title="Product", price_raw="R$ 100,00", price_value=100.0
        )

        assert result.is_valid() is False

    def test_get_missing_fields_all_present(self):
        """Test get_missing_fields returns empty list when all fields present."""
        result = ExtractionResultDTO(
            title="Product",
            price_raw="R$ 100,00",
            price_value=100.0,
            url="https://example.com/product",
        )

        missing = result.get_missing_fields()
        assert missing == []

    def test_get_missing_fields_title_missing(self):
        """Test get_missing_fields includes title when missing."""
        result = ExtractionResultDTO(
            price_raw="R$ 100,00", price_value=100.0, url="https://example.com/product"
        )

        missing = result.get_missing_fields()
        assert "title" in missing

    def test_get_missing_fields_multiple_missing(self):
        """Test get_missing_fields returns all missing fields."""
        result = ExtractionResultDTO()

        missing = result.get_missing_fields()
        assert "title" in missing
        assert "price_raw" in missing
        assert "price_value" in missing
        assert "url" in missing
        assert len(missing) == 4
