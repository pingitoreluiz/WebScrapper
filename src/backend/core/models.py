"""
Data models using Pydantic for validation

Defines DTOs (Data Transfer Objects) and Value Objects for the application.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, HttpUrl, Field, field_validator


class ChipBrand(str, Enum):
    """GPU Chip manufacturers"""

    NVIDIA = "NVIDIA"
    AMD = "AMD"
    INTEL = "INTEL"
    OTHER = "Outros"


class Store(str, Enum):
    """Supported stores"""

    PICHAU = "Pichau"
    KABUM = "Kabum"
    TERABYTE = "Terabyte"


class Price(BaseModel):
    """
    Value object for prices with validation

    Attributes:
        raw: Original price string (e.g., "R$ 2.500,00")
        value: Numeric value as Decimal
        currency: Currency code (default: BRL)
    """

    raw: str
    value: Decimal
    currency: str = "BRL"

    @classmethod
    def from_string(cls, price_str: str) -> "Price":
        """
        Create Price from Brazilian format string

        Args:
            price_str: Price string like "R$ 2.500,00"

        Returns:
            Price instance

        Example:
            >>> price = Price.from_string("R$ 1.234,56")
            >>> price.value
            Decimal('1234.56')
        """
        # Remove R$, convert thousands separator and decimal separator
        cleaned = price_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return cls(raw=price_str, value=Decimal(cleaned))

    @field_validator("value")
    @classmethod
    def validate_price_range(cls, v: Decimal) -> Decimal:
        """Validate price is within reasonable range"""
        if v < 100 or v > 50000:
            raise ValueError(f"Price {v} out of valid range (100-50000)")
        return v

    def __str__(self) -> str:
        return self.raw

    def __float__(self) -> float:
        return float(self.value)


class RawProduct(BaseModel):
    """
    Raw product data extracted from scraping (before enrichment)

    Attributes:
        title: Product title/name
        price: Product price
        url: Product URL
        store: Store name
    """

    title: str = Field(..., min_length=5, max_length=500)
    price: Price
    url: HttpUrl
    store: Store

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty or just whitespace"""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    model_config = {"frozen": False}


class EnrichedProduct(RawProduct):
    """
    Product with enriched metadata

    Adds chip brand, manufacturer, and model information to raw product.
    """

    chip_brand: ChipBrand
    manufacturer: str = Field(..., min_length=2, max_length=100)
    model: str = Field(..., min_length=2, max_length=100)
    scraped_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": False}


class ProductInDB(EnrichedProduct):
    """
    Product as stored in database

    Adds database-specific fields like ID and timestamps.
    """

    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    """
    Product response for API

    Simplified view of product for API responses.
    """

    id: int
    title: str
    price: float
    price_formatted: str
    chip_brand: ChipBrand
    manufacturer: str
    model: str
    store: Store
    url: str
    scraped_at: datetime

    @classmethod
    def from_db_model(cls, product: ProductInDB) -> "ProductResponse":
        """Create API response from database model"""
        return cls(
            id=product.id or 0,
            title=product.title,
            price=float(product.price.value),
            price_formatted=product.price.raw,
            chip_brand=product.chip_brand,
            manufacturer=product.manufacturer,
            model=product.model,
            store=product.store,
            url=str(product.url),
            scraped_at=product.scraped_at,
        )

    model_config = {"from_attributes": True}


class ScraperMetrics(BaseModel):
    """
    Metrics collected during scraper execution

    Tracks performance and results of scraping operations.
    """

    store: Store
    pages_scraped: int = 0
    products_found: int = 0
    products_saved: int = 0
    products_skipped: int = 0
    errors: int = 0
    captchas_detected: int = 0
    unavailable_count: int = 0
    execution_time: float = 0.0
    started_at: datetime = Field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    def success_rate(self) -> float:
        """Calculate success rate (saved/found)"""
        if self.products_found == 0:
            return 0.0
        return (self.products_saved / self.products_found) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            "store": self.store.value,
            "pages_scraped": self.pages_scraped,
            "products_found": self.products_found,
            "products_saved": self.products_saved,
            "products_skipped": self.products_skipped,
            "errors": self.errors,
            "captchas_detected": self.captchas_detected,
            "unavailable_count": self.unavailable_count,
            "execution_time": round(self.execution_time, 2),
            "success_rate": round(self.success_rate(), 2),
        }


class ScraperRun(BaseModel):
    """
    Scraper run details
    """

    id: int
    store: Store
    products_saved: int
    execution_time: float
    success: bool
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScraperRunRequest(BaseModel):
    """Request to run a scraper"""

    stores: list[Store] = Field(default=[Store.PICHAU, Store.KABUM, Store.TERABYTE])
    headless: bool = True
    max_pages: Optional[int] = None


class ScraperRunResponse(BaseModel):
    """Response from scraper execution"""

    success: bool
    message: str
    metrics: list[ScraperMetrics]
    total_products_saved: int
    total_execution_time: float


class PriceHistoryPoint(BaseModel):
    """Single point in price history"""

    date: datetime
    price: float
    store: Store


class ProductSearchQuery(BaseModel):
    """Product search query parameters"""

    query: Optional[str] = None
    chip_brand: Optional[ChipBrand] = None
    manufacturer: Optional[str] = None
    store: Optional[Store] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="price", pattern="^(price|date|title)$")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$")


class AnalyticsHistoryPoint(BaseModel):
    """
    Data point for price history chart.
    """

    date: str  # ISO Format YYYY-MM-DD
    average_price: float
    min_price: float


class AnalyticsStoreComparison(BaseModel):
    """
    Data point for store comparison chart.
    """

    store: Store
    product_count: int
    average_price: float
    cheapest_product_price: float
