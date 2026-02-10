"""
ExtractionResult DTO - Result of extracting product data.

This DTO carries extracted data from infrastructure to application layer.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict


@dataclass
class ExtractionResultDTO:
    """
    DTO for product extraction results.

    Carries raw extracted data before domain entity creation.

    Attributes:
        title: Product title
        price_raw: Raw price string
        price_value: Numeric price value
        url: Product URL
        available: Whether product is available
        extra_data: Additional extracted data
    """

    title: Optional[str] = None
    price_raw: Optional[str] = None
    price_value: Optional[float] = None
    url: Optional[str] = None
    available: bool = True
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """
        Check if extraction has minimum required data.

        Returns:
            True if has title, price, and URL
        """
        return all(
            [
                self.title and self.title.strip(),
                self.price_raw and self.price_raw.strip(),
                self.price_value and self.price_value > 0,
                self.url and self.url.strip(),
            ]
        )

    def get_missing_fields(self) -> list[str]:
        """
        Get list of missing required fields.

        Returns:
            List of field names that are missing
        """
        missing = []

        if not self.title or not self.title.strip():
            missing.append("title")

        if not self.price_raw or not self.price_raw.strip():
            missing.append("price_raw")

        if not self.price_value or self.price_value <= 0:
            missing.append("price_value")

        if not self.url or not self.url.strip():
            missing.append("url")

        return missing
