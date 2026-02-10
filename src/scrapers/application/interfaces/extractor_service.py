"""
ExtractorService interface - Contract for data extraction.

This interface defines what the application layer needs from an extractor service.
Each store will have its own implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from ..dtos.extraction_result import ExtractionResultDTO


class ExtractorService(ABC):
    """
    Interface for product data extraction.

    This abstracts away store-specific extraction logic from the application layer.
    Each store (Pichau, Kabum, etc.) will implement this interface.
    """

    @abstractmethod
    def get_store_name(self) -> str:
        """
        Get the store name this extractor handles.

        Returns:
            Store name (e.g., "Pichau", "Kabum")
        """
        pass

    @abstractmethod
    def build_url(self, page: int) -> str:
        """
        Build the URL for a specific page number.

        Args:
            page: Page number (1-indexed)

        Returns:
            Full URL for the page
        """
        pass

    @abstractmethod
    async def extract_products(self, page_content: Any) -> List[ExtractionResultDTO]:
        """
        Extract products from page content.

        Args:
            page_content: Page content (HTML, elements, etc.)

        Returns:
            List of extraction results
        """
        pass

    @abstractmethod
    async def extract_product_data(self, product_element: Any) -> ExtractionResultDTO:
        """
        Extract data from a single product element.

        Args:
            product_element: Product element to extract from

        Returns:
            Extraction result DTO
        """
        pass

    @abstractmethod
    def should_continue(self, page_num: int, products_found: int) -> bool:
        """
        Determine if scraping should continue.

        Args:
            page_num: Current page number
            products_found: Number of products found so far

        Returns:
            True if should continue scraping
        """
        pass
