"""Tests for ProductEnricher components."""

import pytest

from src.scrapers.components.product_enricher import (
    ChipBrandDetector,
    ManufacturerDetector,
    ModelExtractor,
    ProductEnricher,
)
from src.backend.core.models import ChipBrand


class TestChipBrandDetector:
    """Test suite for ChipBrandDetector."""

    def test_detect_nvidia_rtx(self):
        """Test detecting NVIDIA from RTX keyword."""
        result = ChipBrandDetector.detect("Placa de Vídeo RTX 4090")
        assert result == ChipBrand.NVIDIA

    def test_detect_nvidia_gtx(self):
        """Test detecting NVIDIA from GTX keyword."""
        result = ChipBrandDetector.detect("GeForce GTX 1660")
        assert result == ChipBrand.NVIDIA

    def test_detect_nvidia_geforce(self):
        """Test detecting NVIDIA from GeForce keyword."""
        result = ChipBrandDetector.detect("NVIDIA GeForce")
        assert result == ChipBrand.NVIDIA

    def test_detect_amd_radeon(self):
        """Test detecting AMD from Radeon keyword."""
        result = ChipBrandDetector.detect("AMD Radeon RX 7900")
        assert result == ChipBrand.AMD

    def test_detect_amd_rx(self):
        """Test detecting AMD from RX keyword."""
        result = ChipBrandDetector.detect("Placa RX 6800 XT")
        assert result == ChipBrand.AMD

    def test_detect_intel_arc(self):
        """Test detecting Intel from Arc keyword."""
        result = ChipBrandDetector.detect("Intel Arc A770")
        assert result == ChipBrand.INTEL

    def test_detect_other(self):
        """Test detecting OTHER for unknown brands."""
        result = ChipBrandDetector.detect("Generic Video Card")
        assert result == ChipBrand.OTHER


class TestManufacturerDetector:
    """Test suite for ManufacturerDetector."""

    def test_detect_from_title(self):
        """Test detecting manufacturer from title."""
        result = ManufacturerDetector.detect("ASUS ROG RTX 4090")
        assert result == "ASUS"

    def test_detect_msi_from_title(self):
        """Test detecting MSI from title."""
        result = ManufacturerDetector.detect("MSI Gaming RTX 4070")
        assert result == "MSI"

    def test_detect_gigabyte_from_title(self):
        """Test detecting Gigabyte from title."""
        result = ManufacturerDetector.detect("Gigabyte AORUS RTX 4080")
        assert result == "GIGABYTE"

    def test_detect_from_url(self):
        """Test detecting manufacturer from URL."""
        result = ManufacturerDetector.detect(
            "Placa de Vídeo", "https://example.com/asus-rtx-4090"
        )
        assert result == "ASUS"

    def test_detect_generic(self):
        """Test detecting generic manufacturer."""
        result = ManufacturerDetector.detect("Placa de Vídeo RTX 4090")
        assert result == "Genérica/Outra"


class TestModelExtractor:
    """Test suite for ModelExtractor."""

    def test_extract_nvidia_rtx(self):
        """Test extracting NVIDIA RTX model."""
        result = ModelExtractor.extract("ASUS RTX 4090")
        assert result == "RTX 4090"

    def test_extract_nvidia_rtx_ti(self):
        """Test extracting NVIDIA RTX Ti model."""
        result = ModelExtractor.extract("MSI RTX 4070 Ti")
        assert result == "RTX 4070 TI"

    def test_extract_nvidia_rtx_super(self):
        """Test extracting NVIDIA RTX Super model."""
        result = ModelExtractor.extract("RTX 4060 Super")
        assert result == "RTX 4060 SUPER"

    def test_extract_nvidia_gtx(self):
        """Test extracting NVIDIA GTX model."""
        result = ModelExtractor.extract("GTX 1660")
        assert result == "GTX 1660"

    def test_extract_amd_rx(self):
        """Test extracting AMD RX model."""
        result = ModelExtractor.extract("RX 7900")
        assert result == "RX 7900"

    def test_extract_amd_rx_xt(self):
        """Test extracting AMD RX XT model."""
        result = ModelExtractor.extract("RX 7800 XT")
        assert result == "RX 7800 XT"

    def test_extract_amd_rx_xtx(self):
        """Test extracting AMD RX XTX model."""
        result = ModelExtractor.extract("RX 7900 XTX")
        assert result == "RX 7900 XTX"

    def test_extract_intel_arc(self):
        """Test extracting Intel Arc model."""
        result = ModelExtractor.extract("Intel Arc A770")
        assert result == "ARC A770"

    def test_extract_unknown(self):
        """Test extracting unknown model."""
        result = ModelExtractor.extract("Generic Video Card")
        assert result == "Desconhecido"


class TestProductEnricher:
    """Test suite for ProductEnricher."""

    def test_enrich_nvidia_product(self):
        """Test enriching NVIDIA product."""
        enricher = ProductEnricher()

        chip, manufacturer, model = enricher.enrich("ASUS ROG RTX 4090")

        assert chip == ChipBrand.NVIDIA
        assert manufacturer == "ASUS"
        assert model == "RTX 4090"

    def test_enrich_amd_product(self):
        """Test enriching AMD product."""
        enricher = ProductEnricher()

        chip, manufacturer, model = enricher.enrich("MSI RX 7900 XT")

        assert chip == ChipBrand.AMD
        assert manufacturer == "MSI"
        assert model == "RX 7900 XT"

    def test_enrich_with_url(self):
        """Test enriching with URL hint."""
        enricher = ProductEnricher()

        chip, manufacturer, model = enricher.enrich(
            "Placa de Vídeo RTX 4070", "https://example.com/gigabyte-rtx-4070"
        )

        assert chip == ChipBrand.NVIDIA
        assert manufacturer == "GIGABYTE"
        assert model == "RTX 4070"

    def test_enrich_generic_product(self):
        """Test enriching generic product."""
        enricher = ProductEnricher()

        chip, manufacturer, model = enricher.enrich("Generic Video Card")

        assert chip == ChipBrand.OTHER
        assert manufacturer == "Genérica/Outra"
        assert model == "Desconhecido"
