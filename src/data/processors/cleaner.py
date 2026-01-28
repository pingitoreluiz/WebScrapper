"""
Data cleaning processor

Normalizes and cleans product data.
"""

from typing import List, Optional
from decimal import Decimal
import re

from src.backend.core.models import ProductInDB, Price
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataCleaner:
    """
    Cleans and normalizes product data

    Features:
    - Price normalization
    - Text cleaning (encoding, whitespace)
    - Duplicate removal
    - Name standardization
    """

    @staticmethod
    def clean_price(price: Price) -> Price:
        """
        Normalize price data

        Args:
            price: Price object to clean

        Returns:
            Cleaned Price object
        """
        # Remove extra whitespace from raw price
        cleaned_raw = " ".join(price.raw.split())

        # Ensure value is properly rounded
        cleaned_value = round(float(price.value), 2)

        return Price(
            raw=cleaned_raw, value=Decimal(str(cleaned_value)), currency=price.currency
        )

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text field

        - Removes extra whitespace
        - Fixes encoding issues
        - Normalizes unicode

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return text

        # Remove extra whitespace
        cleaned = " ".join(text.split())

        # Fix common encoding issues
        replacements = {
            "Ã§": "ç",
            "Ã£": "ã",
            "Ã¡": "á",
            "Ã©": "é",
            "Ã­": "í",
            "Ã³": "ó",
            "Ãº": "ú",
        }

        for bad, good in replacements.items():
            cleaned = cleaned.replace(bad, good)

        return cleaned

    @staticmethod
    def standardize_manufacturer(manufacturer: str) -> str:
        """
        Standardize manufacturer names

        Args:
            manufacturer: Manufacturer name

        Returns:
            Standardized name
        """
        # Convert to uppercase for comparison
        upper = manufacturer.upper()

        # Standardization map
        standards = {
            "ASUS": ["ASUS", "AZUS"],
            "MSI": ["MSI", "M.S.I"],
            "GIGABYTE": ["GIGABYTE", "GIGA BYTE", "GBT"],
            "EVGA": ["EVGA", "E.V.G.A"],
            "ZOTAC": ["ZOTAC", "ZOTAX"],
            "GALAX": ["GALAX", "GALAXY"],
            "GAINWARD": ["GAINWARD", "GAIN WARD"],
            "PALIT": ["PALIT", "PALLIT"],
            "PNY": ["PNY", "P.N.Y"],
            "XFX": ["XFX", "X.F.X"],
        }

        for standard, variants in standards.items():
            if any(variant in upper for variant in variants):
                return standard

        return manufacturer

    @staticmethod
    def clean_product(product: ProductInDB) -> ProductInDB:
        """
        Clean all fields of a product

        Args:
            product: Product to clean (object or dict)

        Returns:
            Cleaned product
        """

        def _get_field(obj, name):
            if isinstance(obj, dict):
                return obj.get(name)
            return getattr(obj, name, None)

        title = _get_field(product, "title")
        price = _get_field(product, "price")
        url = _get_field(product, "url")
        manufacturer = _get_field(product, "manufacturer")

        cleaned_title = DataCleaner.clean_text(title)

        # Handle Price object or value
        cleaned_price = price
        if hasattr(price, "raw"):
            cleaned_price = DataCleaner.clean_price(price)

        cleaned_url = str(url).strip() if url else url
        cleaned_manufacturer = DataCleaner.standardize_manufacturer(manufacturer or "")

        if isinstance(product, dict):
            product_copy = product.copy()
            product_copy.update(
                {
                    "title": cleaned_title,
                    "price": cleaned_price,
                    "url": cleaned_url,
                    "manufacturer": cleaned_manufacturer,
                }
            )
            return product_copy

        return ProductInDB(
            id=product.id,
            title=cleaned_title,
            price=cleaned_price,
            url=cleaned_url,
            store=product.store,
            chip_brand=product.chip_brand,
            manufacturer=cleaned_manufacturer,
            model=product.model,
            scraped_at=product.scraped_at,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    @staticmethod
    def remove_duplicates(products: List[ProductInDB]) -> List[ProductInDB]:
        """
        Remove duplicate products based on URL

        Args:
            products: List of products

        Returns:
            List without duplicates
        """
        seen_urls = set()
        unique_products = []
        duplicates_removed = 0

        for product in products:
            if product.url not in seen_urls:
                seen_urls.add(product.url)
                unique_products.append(product)
            else:
                duplicates_removed += 1

        if duplicates_removed > 0:
            logger.info("duplicates_removed", count=duplicates_removed)

        return unique_products

    @staticmethod
    def clean_batch(products: List[ProductInDB]) -> List[ProductInDB]:
        """
        Clean a batch of products

        Args:
            products: List of products to clean

        Returns:
            List of cleaned products
        """
        logger.info("cleaning_batch", count=len(products))

        # Clean each product
        cleaned = [DataCleaner.clean_product(p) for p in products]

        # Remove duplicates
        cleaned = DataCleaner.remove_duplicates(cleaned)

        logger.info("batch_cleaned", original=len(products), cleaned=len(cleaned))

        return cleaned
