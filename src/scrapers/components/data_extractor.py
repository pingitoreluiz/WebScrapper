"""
Generic data extraction utilities

Provides reusable methods for extracting data from page elements.
"""

from typing import Optional, List
from decimal import Decimal
import re

from ..models import SelectorSet
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataExtractor:
    """
    Generic data extraction methods

    Provides static methods for common extraction patterns.
    """

    @staticmethod
    def extract_text(element, selectors: SelectorSet) -> Optional[str]:
        """
        Extract text using selector set with fallbacks

        Args:
            element: Playwright element
            selectors: SelectorSet to try

        Returns:
            Extracted text or None
        """
        for selector in selectors:
            try:
                el = element.locator(selector).first
                if el.count():
                    text = el.inner_text().strip()
                    if text:
                        return text
            except Exception as e:
                logger.debug("selector_failed", selector=selector, error=str(e))
                continue

        return None

    @staticmethod
    def extract_attribute(
        element, selectors: SelectorSet, attribute: str
    ) -> Optional[str]:
        """
        Extract attribute value using selector set

        Args:
            element: Playwright element
            selectors: SelectorSet to try
            attribute: Attribute name (e.g., 'href', 'src')

        Returns:
            Attribute value or None
        """
        for selector in selectors:
            try:
                el = element.locator(selector).first
                if el.count():
                    value = el.get_attribute(attribute)
                    if value:
                        return value
            except Exception as e:
                logger.debug(
                    "attribute_extraction_failed", selector=selector, error=str(e)
                )
                continue

        return None

    @staticmethod
    def extract_link(
        element, selectors: SelectorSet, base_url: str = ""
    ) -> Optional[str]:
        """
        Extract and normalize URL

        Args:
            element: Playwright element
            selectors: SelectorSet to try
            base_url: Base URL for relative links

        Returns:
            Absolute URL or None
        """
        href = DataExtractor.extract_attribute(element, selectors, "href")

        if not href:
            return None

        # Make absolute if relative
        if href.startswith("/") and base_url:
            href = base_url.rstrip("/") + href
        elif not href.startswith("http"):
            href = f"{base_url}/{href.lstrip('/')}"

        return href

    @staticmethod
    def clean_price(price_str: str) -> Optional[float]:
        """
        Clean and convert Brazilian price format to float

        Args:
            price_str: Price string (e.g., "R$ 2.500,99")

        Returns:
            Float value or None

        Examples:
            >>> DataExtractor.clean_price("R$ 2.500,99")
            2500.99
            >>> DataExtractor.clean_price("1.234,56")
            1234.56
        """
        try:
            # Remove currency symbol and spaces
            cleaned = price_str.replace("R$", "").replace(" ", "").strip()

            # Convert Brazilian format: 1.234,56 -> 1234.56
            cleaned = cleaned.replace(".", "").replace(",", ".")

            return float(cleaned)
        except (ValueError, AttributeError) as e:
            logger.debug("price_cleaning_failed", price=price_str, error=str(e))
            return None

    @staticmethod
    def extract_price_from_text(
        text: str, pattern: Optional[str] = None
    ) -> Optional[tuple[str, float]]:
        """
        Extract price from text using regex

        Args:
            text: Text containing price
            pattern: Custom regex pattern (optional)

        Returns:
            Tuple of (raw_string, numeric_value) or None
        """
        if pattern:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(0)
                price_val = DataExtractor.clean_price(price_str)
                if price_val:
                    return (price_str, price_val)

        # Default pattern: R$ followed by numbers
        matches = re.findall(r"R\$\s*[\d.,]+", text)

        for match in matches:
            price_val = DataExtractor.clean_price(match)
            if price_val and 100 <= price_val <= 50000:  # Reasonable range
                return (match, price_val)

        return None

    @staticmethod
    def contains_keywords(
        text: str, keywords: List[str], case_sensitive: bool = False
    ) -> bool:
        """
        Check if text contains any of the keywords

        Args:
            text: Text to search
            keywords: List of keywords
            case_sensitive: Whether search is case-sensitive

        Returns:
            True if any keyword found
        """
        if not case_sensitive:
            text = text.lower()
            keywords = [k.lower() for k in keywords]

        return any(keyword in text for keyword in keywords)

    @staticmethod
    def extract_number(text: str) -> Optional[int]:
        """
        Extract first number from text

        Args:
            text: Text containing number

        Returns:
            Integer or None
        """
        match = re.search(r"\d+", text)
        return int(match.group(0)) if match else None
