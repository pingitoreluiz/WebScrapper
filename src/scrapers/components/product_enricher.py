"""
Product data enrichment

Detects chip brand, manufacturer, and model from product titles and URLs.
"""

import re
from typing import Tuple, Optional

from ...backend.core.models import ChipBrand
from ...backend.core.config import KNOWN_MANUFACTURERS
from ...utils.logger import get_logger

logger = get_logger(__name__)


class ChipBrandDetector:
    """Detects GPU chip brand (NVIDIA, AMD, INTEL)"""

    # Keywords for each brand
    NVIDIA_KEYWORDS = ["GEFORCE", "RTX", "GTX", "NVIDIA"]
    AMD_KEYWORDS = ["RADEON", "RX", "AMD"]
    INTEL_KEYWORDS = ["ARC", "INTEL"]

    @staticmethod
    def detect(title: str) -> ChipBrand:
        """
        Detect chip brand from product title

        Args:
            title: Product title

        Returns:
            ChipBrand enum value
        """
        title_upper = title.upper()

        # Check NVIDIA
        if any(keyword in title_upper for keyword in ChipBrandDetector.NVIDIA_KEYWORDS):
            return ChipBrand.NVIDIA

        # Check AMD
        if any(keyword in title_upper for keyword in ChipBrandDetector.AMD_KEYWORDS):
            return ChipBrand.AMD

        # Check Intel
        if any(keyword in title_upper for keyword in ChipBrandDetector.INTEL_KEYWORDS):
            return ChipBrand.INTEL

        return ChipBrand.OTHER


class ManufacturerDetector:
    """Detects product manufacturer (ASUS, MSI, etc.)"""

    @staticmethod
    def detect(title: str, url: str = "") -> str:
        """
        Detect manufacturer from title and URL

        Args:
            title: Product title
            url: Product URL (optional, for additional hints)

        Returns:
            Manufacturer name or "Genérica/Outra"
        """
        title_upper = title.upper()
        url_lower = url.lower()

        # Try title first
        for manufacturer in KNOWN_MANUFACTURERS:
            if manufacturer in title_upper:
                return manufacturer

        # Try URL (pattern: /manufacturer-product or -manufacturer-)
        if url_lower:
            for manufacturer in KNOWN_MANUFACTURERS:
                manufacturer_lower = manufacturer.lower()
                if (
                    f"-{manufacturer_lower}-" in url_lower
                    or f"/{manufacturer_lower}-" in url_lower
                ):
                    return manufacturer

        return "Genérica/Outra"


class ModelExtractor:
    """Extracts GPU model from product title"""

    # Regex patterns for different brands
    NVIDIA_PATTERN = r"(RTX|GTX)\s*(\d{3,4})\s*(TI|SUPER)?"
    AMD_PATTERN = r"(RX)\s*(\d{3,4})\s*(XTX|XT|GRE)?"  # XTX must come before XT
    INTEL_PATTERN = r"(ARC)\s*(A\d{3})"

    @staticmethod
    def extract(title: str) -> str:
        """
        Extract GPU model from title

        Args:
            title: Product title

        Returns:
            Model string (e.g., "RTX 4090", "RX 7900 XT") or "Desconhecido"
        """
        title_upper = title.upper()

        # Try NVIDIA pattern
        match = re.search(ModelExtractor.NVIDIA_PATTERN, title_upper)
        if match:
            series, number, suffix = match.groups()
            model = f"{series} {number}"
            if suffix:
                model += f" {suffix}"
            return model

        # Try AMD pattern
        match = re.search(ModelExtractor.AMD_PATTERN, title_upper)
        if match:
            series, number, suffix = match.groups()
            model = f"{series} {number}"
            if suffix:
                model += f" {suffix}"
            return model

        # Try Intel pattern
        match = re.search(ModelExtractor.INTEL_PATTERN, title_upper)
        if match:
            series, number = match.groups()
            return f"{series} {number}"

        return "Desconhecido"


class ProductEnricher:
    """
    Complete product enrichment

    Combines all detectors to enrich product data.
    """

    def __init__(self):
        self.chip_detector = ChipBrandDetector()
        self.manufacturer_detector = ManufacturerDetector()
        self.model_extractor = ModelExtractor()

    def enrich(self, title: str, url: str = "") -> Tuple[ChipBrand, str, str]:
        """
        Enrich product with chip brand, manufacturer, and model

        Args:
            title: Product title
            url: Product URL (optional)

        Returns:
            Tuple of (chip_brand, manufacturer, model)

        Example:
            >>> enricher = ProductEnricher()
            >>> enricher.enrich("Placa de Vídeo ASUS ROG RTX 4090")
            (ChipBrand.NVIDIA, "ASUS", "RTX 4090")
        """
        chip_brand = self.chip_detector.detect(title)
        manufacturer = self.manufacturer_detector.detect(title, url)
        model = self.model_extractor.extract(title)

        logger.debug(
            "product_enriched",
            title=title[:50],
            chip=chip_brand.value,
            manufacturer=manufacturer,
            model=model,
        )

        return (chip_brand, manufacturer, model)
