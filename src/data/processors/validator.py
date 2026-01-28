"""
Data validation processor

Validates product data quality and integrity.
"""

from typing import List, Optional, Tuple, Any
from decimal import Decimal

from src.backend.core.models import ProductInDB, ChipBrand, Store
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Raised when validation fails"""

    pass


class DataValidator:
    """
    Validates product data

    Features:
    - Price range validation
    - URL validation
    - Required field validation
    - Data type validation
    """

    # Validation rules
    MIN_PRICE = 100.0
    MAX_PRICE = 50000.0
    MIN_TITLE_LENGTH = 10
    MAX_TITLE_LENGTH = 500

    @staticmethod
    def validate_price(price: Decimal) -> Tuple[bool, Optional[str]]:
        """
        Validate price is in acceptable range

        Args:
            price: Price value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if price is None:
            return False, "Price is None"

        price_float = float(price)

        if price_float < DataValidator.MIN_PRICE:
            return False, f"Price {price_float} below minimum {DataValidator.MIN_PRICE}"

        if price_float > DataValidator.MAX_PRICE:
            return False, f"Price {price_float} above maximum {DataValidator.MAX_PRICE}"

        return True, None

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is empty"

        if not url.startswith("http"):
            return False, f"URL must start with http: {url}"

        if len(url) < 10:
            return False, f"URL too short: {url}"

        return True, None

    @staticmethod
    def validate_title(title: str) -> Tuple[bool, Optional[str]]:
        """
        Validate product title

        Args:
            title: Title to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not title:
            return False, "Title is empty"

        if len(title) < DataValidator.MIN_TITLE_LENGTH:
            return False, f"Title too short ({len(title)} chars): {title[:50]}"

        if len(title) > DataValidator.MAX_TITLE_LENGTH:
            return False, f"Title too long ({len(title)} chars)"

        return True, None

    @staticmethod
    def validate_required_fields(product: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate all required fields are present

        Args:
            product: Product to validate (object or dict)

        Returns:
            Tuple of (is_valid, error_message)
        """

        def _get_field(obj, name):
            if isinstance(obj, dict):
                return obj.get(name)
            return getattr(obj, name, None)

        required_fields = {
            "title": _get_field(product, "title"),
            "price": _get_field(product, "price"),
            "url": _get_field(product, "url"),
            "store": _get_field(product, "store"),
            "chip_brand": _get_field(product, "chip_brand"),
        }

        for field_name, field_value in required_fields.items():
            if field_value is None:
                return False, f"Required field '{field_name}' is None"

        return True, None

    @staticmethod
    def validate_product(product: Any, strict: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate a product

        Args:
            product: Product to validate (object or dict)
            strict: If True, raise exception on validation failure

        Returns:
            Tuple of (is_valid, list_of_errors)

        Raises:
            ValidationError: If strict=True and validation fails
        """

        def _get_field(obj, name):
            if isinstance(obj, dict):
                return obj.get(name)
            return getattr(obj, name, None)

        errors = []

        # Validate required fields
        valid, error = DataValidator.validate_required_fields(product)
        if not valid:
            errors.append(error)

        # Get fields safely
        title = _get_field(product, "title")
        price_val = _get_field(product, "price")
        # Handle Price object or direct value
        if hasattr(price_val, "value"):
            price_val = price_val.value

        url = _get_field(product, "url")

        # Validate title
        if title:
            valid, error = DataValidator.validate_title(title)
            if not valid:
                errors.append(error)

        # Validate price
        if price_val is not None:
            valid, error = DataValidator.validate_price(price_val)
            if not valid:
                errors.append(error)

        # Validate URL
        if url:
            valid, error = DataValidator.validate_url(str(url))
            if not valid:
                errors.append(error)

        is_valid = len(errors) == 0

        if not is_valid:
            logger.debug(
                "validation_failed",
                # product_id might not exist on dict
                product_id=_get_field(product, "id"),
                errors=errors,
            )

            if strict:
                raise ValidationError(f"Product validation failed: {'; '.join(errors)}")

        return is_valid, errors

    @staticmethod
    def validate_batch(
        products: List[ProductInDB], remove_invalid: bool = True
    ) -> Tuple[List[ProductInDB], List[ProductInDB]]:
        """
        Validate a batch of products

        Args:
            products: List of products to validate
            remove_invalid: If True, remove invalid products

        Returns:
            Tuple of (valid_products, invalid_products)
        """
        logger.info("validating_batch", count=len(products))

        valid_products = []
        invalid_products = []

        for product in products:
            is_valid, errors = DataValidator.validate_product(product)

            if is_valid:
                valid_products.append(product)
            else:
                invalid_products.append(product)
                logger.warning(
                    "invalid_product",
                    product_id=product.id,
                    title=product.title[:50] if product.title else None,
                    errors=errors,
                )

        logger.info(
            "batch_validated",
            total=len(products),
            valid=len(valid_products),
            invalid=len(invalid_products),
        )

        if remove_invalid:
            return valid_products, invalid_products
        else:
            return products, []

    @staticmethod
    def get_validation_stats(products: List[ProductInDB]) -> dict:
        """
        Get validation statistics for a batch

        Args:
            products: List of products

        Returns:
            Dictionary with validation stats
        """
        stats = {"total": len(products), "valid": 0, "invalid": 0, "errors_by_type": {}}

        for product in products:
            is_valid, errors = DataValidator.validate_product(product)

            if is_valid:
                stats["valid"] += 1
            else:
                stats["invalid"] += 1
                for error in errors:
                    # Categorize error
                    if "price" in error.lower():
                        category = "price_errors"
                    elif "url" in error.lower():
                        category = "url_errors"
                    elif "title" in error.lower():
                        category = "title_errors"
                    else:
                        category = "other_errors"

                    stats["errors_by_type"][category] = (
                        stats["errors_by_type"].get(category, 0) + 1
                    )

        return stats
