"""
Product repository interface.

Defines the contract for product persistence without implementation details.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.product import Product
from ..value_objects.url import ProductUrl


class ProductRepository(ABC):
    """
    Repository interface for Product persistence.

    This is a domain interface that will be implemented by infrastructure.
    It defines what operations are needed without specifying how they work.
    """

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Save a product (create or update).

        Args:
            product: Product entity to save

        Returns:
            Saved product with any generated fields
        """
        pass

    @abstractmethod
    def find_by_id(self, product_id: UUID) -> Optional[Product]:
        """
        Find a product by its ID.

        Args:
            product_id: Product UUID

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_url(self, url: ProductUrl) -> Optional[Product]:
        """
        Find a product by its URL.

        Args:
            url: Product URL value object

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(
        self,
        store: Optional[str] = None,
        available_only: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Product]:
        """
        Find all products with optional filtering.

        Args:
            store: Filter by store name (optional)
            available_only: Only return available products
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of products
        """
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """
        Delete a product by ID.

        Args:
            product_id: Product UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def count(self, store: Optional[str] = None) -> int:
        """
        Count products.

        Args:
            store: Filter by store name (optional)

        Returns:
            Number of products
        """
        pass
