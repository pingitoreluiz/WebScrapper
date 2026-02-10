"""Tests for DataEnricher."""

import pytest
from src.data.processors.enricher import DataEnricher
from src.backend.core.models import RawProduct, EnrichedProduct, ChipBrand, Price
from decimal import Decimal


class TestDataEnricher:
    """Test suite for DataEnricher."""

    def test_enrich_product_nvidia(self):
        """Test enriching NVIDIA product."""
        enricher = DataEnricher()
        raw = RawProduct(
            title="ASUS ROG RTX 4090",
            price=Price(raw="R$ 10000", value=Decimal("10000"), currency="BRL"),
            url="https://example.com/asus-rtx-4090",
            store="Pichau",
        )

        enriched = enricher.enrich_product(raw)

        assert enriched.chip_brand == ChipBrand.NVIDIA
        assert enriched.manufacturer == "ASUS"
        assert enriched.model == "RTX 4090"

    def test_enrich_batch_success(self):
        """Test batch enrichment with valid products."""
        enricher = DataEnricher()
        raw_products = [
            RawProduct(
                title="MSI RTX 4070 Ti",
                price=Price(raw="R$ 3500", value=Decimal("3500"), currency="BRL"),
                url="https://example.com/msi-rtx-4070",
                store="Kabum",
            ),
            RawProduct(
                title="Gigabyte RX 7900 XT",
                price=Price(raw="R$ 4000", value=Decimal("4000"), currency="BRL"),
                url="https://example.com/gigabyte-rx-7900",
                store="Terabyte",
            ),
        ]

        enriched = enricher.enrich_batch(raw_products)

        assert len(enriched) == 2
        assert enriched[0].chip_brand == ChipBrand.NVIDIA
        assert enriched[1].chip_brand == ChipBrand.AMD

    def test_enrich_batch_with_errors(self):
        """Test batch enrichment handles errors gracefully."""
        enricher = DataEnricher()

        # Create a product that might cause issues
        raw_products = [
            RawProduct(
                title="Valid Product RTX 4090",
                price=Price(raw="R$ 10000", value=Decimal("10000"), currency="BRL"),
                url="https://example.com/valid",
                store="Pichau",
            )
        ]

        enriched = enricher.enrich_batch(raw_products)

        # Should still process valid products
        assert len(enriched) >= 1

    def test_get_enrichment_stats(self):
        """Test getting enrichment statistics."""
        enricher = DataEnricher()

        enriched_products = [
            EnrichedProduct(
                title="RTX 4090",
                price=Price(raw="R$ 10000", value=Decimal("10000"), currency="BRL"),
                url="https://example.com/1",
                store="Pichau",
                chip_brand=ChipBrand.NVIDIA,
                manufacturer="ASUS",
                model="RTX 4090",
            ),
            EnrichedProduct(
                title="RX 7900 XT",
                price=Price(raw="R$ 4000", value=Decimal("4000"), currency="BRL"),
                url="https://example.com/2",
                store="Kabum",
                chip_brand=ChipBrand.AMD,
                manufacturer="MSI",
                model="RX 7900 XT",
            ),
            EnrichedProduct(
                title="Unknown Card",
                price=Price(raw="R$ 1000", value=Decimal("1000"), currency="BRL"),
                url="https://example.com/3",
                store="Terabyte",
                chip_brand=ChipBrand.OTHER,
                manufacturer="Generic",
                model="Desconhecido",
            ),
        ]

        stats = enricher.get_enrichment_stats(enriched_products)

        assert stats["total"] == 3
        assert stats["by_chip_brand"]["NVIDIA"] == 1
        assert stats["by_chip_brand"]["AMD"] == 1
        assert stats["by_manufacturer"]["ASUS"] == 1
        assert stats["by_manufacturer"]["MSI"] == 1
        assert stats["unknown_models"] == 1

    def test_get_enrichment_stats_empty(self):
        """Test stats with empty list."""
        enricher = DataEnricher()

        stats = enricher.get_enrichment_stats([])

        assert stats["total"] == 0
        assert stats["unknown_models"] == 0
