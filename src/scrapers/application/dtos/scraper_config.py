"""
ScraperConfig DTO - Configuration for scraper execution.

This DTO is used to pass configuration from the API/CLI to the application layer.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ScraperConfigDTO:
    """
    DTO for scraper configuration.

    This is a simple data structure for transferring configuration data.

    Attributes:
        store: Store name to scrape
        headless: Run browser in headless mode
        max_pages: Maximum number of pages to scrape
        timeout: Page load timeout in milliseconds
        user_agent: Custom user agent (optional)
        viewport: Browser viewport size
    """

    store: str
    headless: bool = True
    max_pages: int = 20
    timeout: int = 30000
    user_agent: Optional[str] = None
    viewport: Optional[Dict[str, int]] = None

    def __post_init__(self):
        """Set default viewport if not provided."""
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}

    def validate(self) -> None:
        """
        Validate DTO data.

        Raises:
            ValueError: If validation fails
        """
        if not self.store or not self.store.strip():
            raise ValueError("Store name cannot be empty")

        if self.max_pages <= 0:
            raise ValueError("Max pages must be positive")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
