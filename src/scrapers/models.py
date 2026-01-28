"""
Scraper-specific models and data structures

Defines models used specifically by scrapers, separate from backend core models.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime

from ..backend.core.models import Store


@dataclass
class ScraperConfig:
    """
    Configuration for a scraper instance

    Attributes:
        store: Store name
        headless: Run browser in headless mode
        max_pages: Maximum pages to scrape
        timeout: Page timeout in milliseconds
        user_agent: User agent string (optional, will use random if None)
        viewport: Browser viewport size
    """

    store: Optional[Store] = None
    headless: bool = True
    max_pages: int = 20
    timeout: int = 30000
    user_agent: Optional[str] = None
    viewport: Optional[Dict[str, int]] = None

    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}


@dataclass
class BrowserConfig:
    """Browser-specific configuration"""

    headless: bool = True
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = field(
        default_factory=lambda: {"width": 1920, "height": 1080}
    )
    timezone_id: str = "America/Sao_Paulo"
    latitude: float = -23.5505
    longitude: float = -46.6333
    locale: str = "pt-BR"

    # Anti-detection settings
    remove_webdriver_flag: bool = True
    inject_chrome_object: bool = True
    randomize_plugins: bool = True


@dataclass
class SelectorSet:
    """
    Set of CSS selectors for a specific element type

    Attributes:
        selectors: List of selectors to try (in order)
        description: Human-readable description
    """

    selectors: List[str]
    description: str = ""

    def __iter__(self):
        return iter(self.selectors)

    def __len__(self):
        return len(self.selectors)

    def __getitem__(self, index):
        return self.selectors[index]


class StoreSelectors:
    """
    Container for all selectors needed by a store scraper

    Each store should define these selector sets.
    """

    def __init__(
        self,
        product_card: SelectorSet,
        title: SelectorSet,
        price: SelectorSet,
        link: SelectorSet,
        availability: Optional[SelectorSet] = None,
        next_page: Optional[SelectorSet] = None,
    ):
        self.product_card = product_card
        self.title = title
        self.price = price
        self.link = link
        self.availability = availability
        self.next_page = next_page

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format"""
        return {
            "product_card": self.product_card.selectors,
            "title": self.title.selectors,
            "price": self.price.selectors,
            "link": self.link.selectors,
            "availability": self.availability.selectors if self.availability else [],
            "next_page": self.next_page.selectors if self.next_page else [],
        }


@dataclass
class ExtractionResult:
    """
    Result of extracting data from a product element

    Attributes:
        title: Product title
        price_raw: Raw price string
        price_value: Numeric price value
        url: Product URL
        available: Whether product is available
        extra_data: Any additional data extracted
    """

    title: Optional[str] = None
    price_raw: Optional[str] = None
    price_value: Optional[float] = None
    url: Optional[str] = None
    available: bool = True
    extra_data: Dict[str, any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if extraction has minimum required data"""
        return all(
            [
                self.title,
                self.price_raw,
                self.price_value and self.price_value > 0,
                self.url,
            ]
        )

    def __repr__(self) -> str:
        return f"ExtractionResult(title='{self.title[:30] if self.title else None}...', price={self.price_value}, url='{self.url}')"
