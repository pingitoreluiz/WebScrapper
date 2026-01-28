"""
Unit tests for scraper components

Tests the reusable scraper components.
"""

import pytest
from decimal import Decimal

from src.scrapers.components.data_extractor import DataExtractor
from src.scrapers.components.product_enricher import (
    ChipBrandDetector,
    ManufacturerDetector,
    ModelExtractor,
    ProductEnricher,
)
from src.scrapers.components.selector_cache import SelectorCache
from src.backend.core.models import ChipBrand


class TestDataExtractor:
    """Test DataExtractor utility methods"""

    def test_clean_price_brazilian_format(self):
        """Test cleaning Brazilian price format"""
        assert DataExtractor.clean_price("R$ 2.500,99") == 2500.99
        assert DataExtractor.clean_price("R$ 1.234,56") == 1234.56
        assert DataExtractor.clean_price("R$ 999,00") == 999.0

    def test_clean_price_without_currency(self):
        """Test cleaning price without R$ symbol"""
        assert DataExtractor.clean_price("2.500,99") == 2500.99
        assert DataExtractor.clean_price("1234,56") == 1234.56

    def test_clean_price_invalid(self):
        """Test cleaning invalid price returns None"""
        assert DataExtractor.clean_price("invalid") is None
        assert DataExtractor.clean_price("") is None

    def test_extract_price_from_text(self):
        """Test extracting price from text"""
        text = "Produto custa R$ 2.500,99 à vista"
        result = DataExtractor.extract_price_from_text(text)

        assert result is not None
        raw, value = result
        assert "R$ 2.500,99" in raw
        assert value == 2500.99

    def test_extract_price_multiple_prices(self):
        """Test extracting first valid price from multiple"""
        text = "De R$ 3.000,00 por R$ 2.500,99 em 12x"
        result = DataExtractor.extract_price_from_text(text)

        assert result is not None
        _, value = result
        # Should get first price in valid range
        assert 100 <= value <= 50000

    def test_contains_keywords_case_insensitive(self):
        """Test keyword checking (case insensitive)"""
        text = "Produto INDISPONÍVEL no momento"
        keywords = ["indisponível", "esgotado"]

        assert DataExtractor.contains_keywords(text, keywords) is True

    def test_contains_keywords_not_found(self):
        """Test keyword checking when not found"""
        text = "Produto disponível"
        keywords = ["indisponível", "esgotado"]

        assert DataExtractor.contains_keywords(text, keywords) is False

    def test_extract_number(self):
        """Test extracting number from text"""
        assert DataExtractor.extract_number("Página 5 de 10") == 5
        assert DataExtractor.extract_number("Total: 123 produtos") == 123
        assert DataExtractor.extract_number("Sem números") is None


class TestChipBrandDetector:
    """Test ChipBrandDetector"""

    def test_detect_nvidia(self):
        """Test detecting NVIDIA GPUs"""
        assert ChipBrandDetector.detect("GeForce RTX 4090") == ChipBrand.NVIDIA
        assert ChipBrandDetector.detect("GTX 1660 Super") == ChipBrand.NVIDIA
        assert ChipBrandDetector.detect("NVIDIA RTX 3080") == ChipBrand.NVIDIA

    def test_detect_amd(self):
        """Test detecting AMD GPUs"""
        assert ChipBrandDetector.detect("Radeon RX 7900 XT") == ChipBrand.AMD
        assert ChipBrandDetector.detect("AMD RX 6800") == ChipBrand.AMD

    def test_detect_intel(self):
        """Test detecting Intel GPUs"""
        assert ChipBrandDetector.detect("Intel ARC A770") == ChipBrand.INTEL
        assert ChipBrandDetector.detect("ARC A750") == ChipBrand.INTEL

    def test_detect_other(self):
        """Test detecting unknown brand"""
        assert ChipBrandDetector.detect("Placa de Vídeo Genérica") == ChipBrand.OTHER


class TestManufacturerDetector:
    """Test ManufacturerDetector"""

    def test_detect_from_title(self):
        """Test detecting manufacturer from title"""
        assert ManufacturerDetector.detect("ASUS ROG RTX 4090") == "ASUS"
        assert ManufacturerDetector.detect("MSI Gaming X RTX 4080") == "MSI"
        assert ManufacturerDetector.detect("GIGABYTE Eagle RX 7900") == "GIGABYTE"

    def test_detect_from_url(self):
        """Test detecting manufacturer from URL"""
        url = "https://pichau.com.br/asus-rog-strix-rtx-4090"
        assert ManufacturerDetector.detect("Placa RTX 4090", url) == "ASUS"

    def test_detect_generic(self):
        """Test detecting generic/unknown manufacturer"""
        assert (
            ManufacturerDetector.detect("Placa de Vídeo RTX 4090") == "Genérica/Outra"
        )


class TestModelExtractor:
    """Test ModelExtractor"""

    def test_extract_nvidia_rtx(self):
        """Test extracting NVIDIA RTX models"""
        assert ModelExtractor.extract("RTX 4090 24GB") == "RTX 4090"
        assert ModelExtractor.extract("RTX 4080 SUPER") == "RTX 4080 SUPER"
        assert ModelExtractor.extract("RTX 3060 TI") == "RTX 3060 TI"

    def test_extract_nvidia_gtx(self):
        """Test extracting NVIDIA GTX models"""
        assert ModelExtractor.extract("GTX 1660 SUPER") == "GTX 1660 SUPER"
        assert ModelExtractor.extract("GTX 1050 TI") == "GTX 1050 TI"

    def test_extract_amd(self):
        """Test extracting AMD models"""
        assert ModelExtractor.extract("RX 7900 XT") == "RX 7900 XT"
        assert ModelExtractor.extract("RX 6800 XTX") == "RX 6800 XTX"
        assert ModelExtractor.extract("RX 580 GRE") == "RX 580 GRE"

    def test_extract_intel(self):
        """Test extracting Intel models"""
        assert ModelExtractor.extract("ARC A770 16GB") == "ARC A770"
        assert ModelExtractor.extract("Intel ARC A750") == "ARC A750"

    def test_extract_unknown(self):
        """Test extracting unknown model"""
        assert ModelExtractor.extract("Placa Genérica") == "Desconhecido"


class TestProductEnricher:
    """Test complete ProductEnricher"""

    def test_enrich_nvidia_product(self):
        """Test enriching NVIDIA product"""
        enricher = ProductEnricher()
        chip, mfr, model = enricher.enrich(
            "Placa de Vídeo ASUS ROG RTX 4090 24GB",
            "https://pichau.com.br/asus-rog-rtx-4090",
        )

        assert chip == ChipBrand.NVIDIA
        assert mfr == "ASUS"
        assert model == "RTX 4090"

    def test_enrich_amd_product(self):
        """Test enriching AMD product"""
        enricher = ProductEnricher()
        chip, mfr, model = enricher.enrich("MSI Radeon RX 7900 XT Gaming", "")

        assert chip == ChipBrand.AMD
        assert mfr == "MSI"
        assert model == "RX 7900 XT"

    def test_enrich_intel_product(self):
        """Test enriching Intel product"""
        enricher = ProductEnricher()
        chip, mfr, model = enricher.enrich("GIGABYTE Intel ARC A770 16GB")

        assert chip == ChipBrand.INTEL
        assert mfr == "GIGABYTE"
        assert model == "ARC A770"


class TestSelectorCache:
    """Test SelectorCache"""

    def test_cache_miss_then_hit(self):
        """Test cache miss followed by hit"""
        cache = SelectorCache()

        # First call - cache miss
        selectors = ["div.price", "span.price"]
        result1 = cache.get("price", selectors)
        assert result1 in selectors

        # Second call - cache hit
        result2 = cache.get("price", selectors)
        assert result2 == result1

        # Check stats
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_manual_set(self):
        """Test manually setting cache"""
        cache = SelectorCache()

        cache.set("title", "h2.product-title")
        result = cache.get("title", ["h1", "h2", "h3"])

        assert result == "h2.product-title"

    def test_clear_cache(self):
        """Test clearing cache"""
        cache = SelectorCache()

        cache.set("price", "div.price")
        cache.clear()

        stats = cache.get_stats()
        assert stats["cached_selectors"] == 0
        assert stats["hits"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
