"""
ScraperRun entity - Aggregate root for a scraping execution.

Represents a single execution of a scraper with metrics and results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from .product import Product


@dataclass
class ScraperRun:
    """
    ScraperRun entity representing a single scraper execution.
    
    This is an aggregate root that manages the lifecycle of a scraping run.
    
    Attributes:
        id: Unique identifier
        store: Store name being scraped
        started_at: When scraping started
        finished_at: When scraping finished (None if still running)
        execution_time: Total execution time in seconds
        products_found: Number of products found
        products_saved: Number of products saved
        products_skipped: Number of products skipped
        pages_scraped: Number of pages scraped
        errors: Number of errors encountered
        captchas_detected: Number of CAPTCHAs detected
        success: Whether the run completed successfully
        error_message: Error message if failed
        products: List of products scraped (optional)
    """
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    
    # Core attributes
    store: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    # Completion info
    finished_at: Optional[datetime] = None
    execution_time: float = 0.0
    
    # Metrics
    products_found: int = 0
    products_saved: int = 0
    products_skipped: int = 0
    pages_scraped: int = 0
    errors: int = 0
    captchas_detected: int = 0
    
    # Status
    success: bool = False
    error_message: Optional[str] = None
    
    # Products (optional, for in-memory aggregation)
    products: List[Product] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate scraper run after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate scraper run business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if not self.store or not self.store.strip():
            raise ValueError("Store name cannot be empty")
        
        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")
        
        if self.products_found < 0:
            raise ValueError("Products found cannot be negative")
        
        if self.products_saved < 0:
            raise ValueError("Products saved cannot be negative")
        
        if self.products_saved > self.products_found:
            raise ValueError("Products saved cannot exceed products found")
    
    def start(self) -> None:
        """Mark the scraper run as started."""
        self.started_at = datetime.utcnow()
        self.finished_at = None
        self.success = False
    
    def finish_successfully(self) -> None:
        """Mark the scraper run as successfully completed."""
        self.finished_at = datetime.utcnow()
        self.execution_time = (self.finished_at - self.started_at).total_seconds()
        self.success = True
        self.error_message = None
    
    def finish_with_error(self, error_message: str) -> None:
        """
        Mark the scraper run as failed.
        
        Args:
            error_message: Description of the error
        """
        self.finished_at = datetime.utcnow()
        self.execution_time = (self.finished_at - self.started_at).total_seconds()
        self.success = False
        self.error_message = error_message
    
    def increment_products_found(self, count: int = 1) -> None:
        """Increment the products found counter."""
        self.products_found += count
    
    def increment_products_saved(self, count: int = 1) -> None:
        """Increment the products saved counter."""
        self.products_saved += count
    
    def increment_products_skipped(self, count: int = 1) -> None:
        """Increment the products skipped counter."""
        self.products_skipped += count
    
    def increment_pages_scraped(self, count: int = 1) -> None:
        """Increment the pages scraped counter."""
        self.pages_scraped += count
    
    def increment_errors(self, count: int = 1) -> None:
        """Increment the errors counter."""
        self.errors += count
    
    def increment_captchas(self, count: int = 1) -> None:
        """Increment the CAPTCHAs detected counter."""
        self.captchas_detected += count
    
    def add_product(self, product: Product) -> None:
        """
        Add a product to this run.
        
        Args:
            product: Product entity to add
        """
        if product not in self.products:
            self.products.append(product)
            self.increment_products_found()
    
    def is_running(self) -> bool:
        """Check if the scraper run is currently running."""
        return self.finished_at is None
    
    def get_success_rate(self) -> float:
        """
        Calculate the success rate (saved / found).
        
        Returns:
            Success rate as percentage (0-100)
        """
        if self.products_found == 0:
            return 0.0
        return (self.products_saved / self.products_found) * 100
    
    def __eq__(self, other) -> bool:
        """Scraper runs are equal if they have the same ID."""
        if not isinstance(other, ScraperRun):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        status = "running" if self.is_running() else ("success" if self.success else "failed")
        return (
            f"ScraperRun(id={self.id}, store='{self.store}', "
            f"status={status}, products={self.products_saved}/{self.products_found})"
        )
