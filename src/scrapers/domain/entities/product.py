"""
Product entity - Core domain object representing a GPU product.

This is a pure domain entity with business logic and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ..value_objects.price import Price
from ..value_objects.url import ProductUrl


@dataclass
class Product:
    """
    Product entity representing a GPU product from a store.
    
    This is the core domain entity with identity and business rules.
    
    Attributes:
        id: Unique identifier
        title: Product title/name
        price: Current price (value object)
        url: Product URL (value object)
        store: Store name (e.g., "Pichau", "Kabum")
        chip_brand: GPU chip brand (e.g., "NVIDIA", "AMD")
        manufacturer: Card manufacturer (e.g., "ASUS", "MSI")
        model: GPU model (e.g., "RTX 4070")
        available: Whether product is in stock
        scraped_at: When this data was scraped
        created_at: When this product was first discovered
        updated_at: When this product was last updated
    """
    
    # Core attributes (required)
    title: str
    price: Price
    url: ProductUrl
    store: str
    
    # Identity (has default)
    id: UUID = field(default_factory=uuid4)
    
    # Optional attributes
    chip_brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    available: bool = True
    
    # Timestamps
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate product after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate product business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if not self.title or not self.title.strip():
            raise ValueError("Product title cannot be empty")
        
        if len(self.title) > 500:
            raise ValueError("Product title too long (max 500 chars)")
        
        if not self.store or not self.store.strip():
            raise ValueError("Product store cannot be empty")
        
        # Price and URL are validated by their value objects
    
    def update_price(self, new_price: Price) -> None:
        """
        Update product price.
        
        Args:
            new_price: New price value object
        """
        if new_price != self.price:
            self.price = new_price
            self.updated_at = datetime.utcnow()
    
    def mark_unavailable(self) -> None:
        """Mark product as unavailable."""
        if self.available:
            self.available = False
            self.updated_at = datetime.utcnow()
    
    def mark_available(self) -> None:
        """Mark product as available."""
        if not self.available:
            self.available = True
            self.updated_at = datetime.utcnow()
    
    def is_gpu(self) -> bool:
        """
        Check if this product is a GPU.
        
        Returns:
            True if product has chip_brand set
        """
        return self.chip_brand is not None
    
    def get_display_name(self) -> str:
        """
        Get a formatted display name for the product.
        
        Returns:
            Formatted product name
        """
        parts = []
        
        if self.manufacturer:
            parts.append(self.manufacturer)
        
        if self.chip_brand:
            parts.append(self.chip_brand)
        
        if self.model:
            parts.append(self.model)
        
        if parts:
            return " ".join(parts)
        
        return self.title
    
    def __eq__(self, other) -> bool:
        """Products are equal if they have the same ID."""
        if not isinstance(other, Product):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Product(id={self.id}, title='{self.title[:30]}...', "
            f"price={self.price}, store='{self.store}')"
        )
