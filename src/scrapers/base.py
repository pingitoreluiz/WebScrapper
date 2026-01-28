"""
Abstract base scraper using Template Method Pattern

Defines the interface and common behavior for all store scrapers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Generator
from datetime import datetime
import time

from playwright.async_api import Page, async_playwright, Playwright
from playwright_stealth import stealth_async
from fake_useragent import UserAgent
import random
import asyncio

from .models import ScraperConfig, StoreSelectors, ExtractionResult
from .exceptions import CaptchaDetected, PageLoadError, MaxRetriesExceeded
from ..backend.core.models import (
    ScraperMetrics,
    EnrichedProduct,
    RawProduct,
    Store,
    Price,
)
from ..utils.logger import get_logger


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers

    Implements Template Method Pattern:
    - run() defines the algorithm skeleton
    - Subclasses implement specific steps

    Attributes:
        config: Scraper configuration
        metrics: Execution metrics
        logger: Structured logger
    """

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.metrics = ScraperMetrics(store=config.store)
        self.logger = get_logger(f"{__name__}.{self.get_store_name()}")

        # Browser state
        self.playwright: Optional[Playwright] = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None

    # ==================== Abstract Methods (must be implemented) ====================

    @abstractmethod
    def get_store_name(self) -> str:
        """Return the store name (e.g., 'Pichau')"""
        pass

    @abstractmethod
    def get_selectors(self) -> StoreSelectors:
        """Return the CSS selectors for this store"""
        pass

    @abstractmethod
    def build_url(self, page: int) -> str:
        """Build the URL for a specific page number"""
        pass

    @abstractmethod
    def extract_price(self, element) -> Optional[tuple[str, float]]:
        """
        Extract price from product element

        Returns:
            Tuple of (raw_price_string, numeric_value) or None
        """
        pass

    # ==================== Template Method ====================

    async def run(self) -> ScraperMetrics:
        """
        Main execution method (Template Method)

        Defines the scraping algorithm:
        1. Setup browser
        2. Scrape pages until done
        3. Cleanup
        4. Return metrics

        Returns:
            ScraperMetrics with execution results
        """
        self.metrics.started_at = datetime.now()
        self.logger.info("scraper_started", store=self.get_store_name())

        try:
            # Setup phase
            await self._setup_browser()

            # Scraping phase
            page_num = 1
            while self._should_continue(page_num):
                try:
                    await self._scrape_page(page_num)
                    page_num += 1
                except CaptchaDetected as e:
                    self.logger.warning("captcha_detected", message=str(e))
                    self.metrics.captchas_detected += 1
                    break
                except PageLoadError as e:
                    self.logger.error("page_load_error", url=e.url, message=str(e))
                    self.metrics.errors += 1
                    # Continue to next page
                    page_num += 1
                except Exception as e:
                    self.logger.error(
                        "unexpected_error", page=page_num, error=str(e), exc_info=True
                    )
                    self.metrics.errors += 1
                    # Stop on unexpected errors
                    break

        except Exception as e:
            self.logger.error("scraper_failed", error=str(e), exc_info=True)
            self.metrics.errors += 1

        finally:
            # Cleanup phase
            await self._cleanup_browser()

            # Finalize metrics
            self.metrics.finished_at = datetime.now()
            if self.metrics.started_at and self.metrics.finished_at:
                self.metrics.execution_time = (
                    self.metrics.finished_at - self.metrics.started_at
                ).total_seconds()

            self.logger.info("scraper_finished", **self.metrics.to_dict())

        return self.metrics

    # ==================== Hook Methods (can be overridden) ====================

    def _should_continue(self, page_num: int) -> bool:
        """
        Determine if scraping should continue

        Can be overridden by subclasses for custom logic.
        """
        # Stop if max pages reached
        if page_num > self.config.max_pages:
            self.logger.info("max_pages_reached", page=page_num)
            return False

        # Stop if too many errors
        if self.metrics.errors >= 3:
            self.logger.warning("too_many_errors", errors=self.metrics.errors)
            return False

        return True

    def _validate_extraction(self, result: ExtractionResult) -> bool:
        """
        Validate extracted data

        Can be overridden for store-specific validation.
        """
        # Validate
        if not result.is_valid():
            return False

        # Price range validation
        if result.price_value:
            if result.price_value < 100 or result.price_value > 50000:
                self.logger.debug(
                    "price_out_of_range",
                    price=result.price_value,
                    title=result.title[:50] if result.title else None,
                )
                return False

        return True

    # ==================== Helper Methods ====================

    async def _setup_browser(self) -> None:
        """Initialize browser with anti-detection"""
        from .components.browser_manager import BrowserManager

        self.logger.debug("setting_up_browser")

        # This will be implemented in browser_manager component
        # For now, basic setup
        self.playwright = await async_playwright().start()

        # Configure browser with stealth args
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--hide-scrollbars",
            "--mute-audio",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-component-extensions-with-background-pages",
            "--disable-extensions",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--enable-features=NetworkService,NetworkServiceInProcess",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--start-maximized",
        ]

        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless, args=args
        )

        # Generate random user agent
        ua = UserAgent()
        user_agent = ua.random

        self.context = await self.browser.new_context(
            viewport=self.config.viewport,
            user_agent=user_agent,
            locale="pt-BR",
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
        )

        # Add init scripts to evade detection
        await self.context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self.page = await self.context.new_page()

        # Apply stealth
        await stealth_async(self.page)

        self.page.set_default_timeout(self.config.timeout)

        self.logger.debug("browser_ready", user_agent=user_agent)

    async def _cleanup_browser(self) -> None:
        """Cleanup browser resources"""
        self.logger.debug("cleaning_up_browser")

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        self.logger.debug("browser_closed")

    async def _scrape_page(self, page_num: int) -> None:
        """
        Scrape a single page

        Args:
            page_num: Page number to scrape
        """
        url = self.build_url(page_num)
        self.logger.info("scraping_page", page=page_num, url=url)

        # Load page
        await self._load_page(url)

        # Check for CAPTCHA
        if await self._check_captcha():
            raise CaptchaDetected()

        # Extract products
        products = await self._extract_products()

        self.logger.info("products_found", page=page_num, count=len(products))
        self.metrics.pages_scraped += 1
        self.metrics.products_found += len(products)

        # Process each product
        for product in products:
            if await self._process_product(product):
                self.metrics.products_saved += 1
            else:
                self.metrics.products_skipped += 1

    async def _load_page(self, url: str) -> None:
        """Load a page with retry logic"""
        if not self.page:
            raise BrowserError("Page not initialized")

        try:
            # Add random initial delay
            await asyncio.sleep(random.uniform(2.0, 5.0))

            response = await self.page.goto(
                url, wait_until="domcontentloaded", timeout=self.config.timeout
            )

            if not response:
                raise PageLoadError(f"No response from {url}")

            # Simulate human behavior
            await self._simulate_human_behavior()

            return True
            time.sleep(1)  # Brief pause for dynamic content
        except Exception as e:
            raise PageLoadError(url, str(e))

    async def _simulate_human_behavior(self):
        """Simulate human-like mouse movements and scrolling"""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 1000)
                y = random.randint(100, 800)
                await self.page.mouse.move(x, y, steps=random.randint(5, 20))
                await asyncio.sleep(random.uniform(0.1, 0.5))

            # Natural scrolling
            total_height = await self.page.evaluate("document.body.scrollHeight")
            viewport_height = await self.page.evaluate("window.innerHeight")

            # Scroll down just a bit to trigger lazy loading and look natural
            scroll_amount = random.randint(300, 700)
            steps = random.randint(5, 15)

            for i in range(steps):
                y_pos = (scroll_amount / steps) * (i + 1)
                await self.page.keyboard.press("ArrowDown")
                await asyncio.sleep(random.uniform(0.05, 0.2))

            # Random pause after scrolling
            await asyncio.sleep(random.uniform(1.0, 3.0))

            # Move mouse to a random element if possible
            try:
                # Try to hover over a random link or distinct element to trigger hover effects
                elements = await self.page.query_selector_all("a, button, img")
                if elements:
                    element = random.choice(elements[:10])  # Pick from first few
                    box = await element.bounding_box()
                    if box:
                        await self.page.mouse.move(
                            box["x"] + box["width"] / 2,
                            box["y"] + box["height"] / 2,
                            steps=random.randint(10, 25),
                        )
            except Exception:
                pass  # Ignore if hovering fails

        except Exception as e:
            self.logger.warning("human_simulation_failed", error=str(e))

    async def _check_captcha(self) -> bool:
        """Check if CAPTCHA is present"""
        if not self.page:
            return False

        # Check title
        title = await self.page.title()
        title = title.lower()
        captcha_keywords = ["captcha", "cloudflare", "just a moment", "verify"]

        return any(keyword in title for keyword in captcha_keywords)

    async def _extract_products(self) -> List:
        """Extract product elements from page"""
        if not self.page:
            return []

        selectors = self.get_selectors()

        # Try each product card selector
        for selector in selectors.product_card:
            try:
                elements = await self.page.locator(selector).all()
                if len(elements) > 5:  # Reasonable number of products
                    self.logger.debug(
                        "using_selector", selector=selector, count=len(elements)
                    )
                    return elements
            except:
                continue

        self.logger.warning("no_products_found")

        # Debugging: Log page title and content snippet
        try:
            title = await self.page.title()
            content = await self.page.content()
            body_text = await self.page.inner_text("body")
            self.logger.warning(
                "page_debug_info",
                title=title,
                body_snippet=body_text[:500] if body_text else "Empty body",
                html_length=len(content),
            )

            # Save full HTML for inspection
            import os

            debug_path = "/app/data/debug_failed_page.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.warning(f"Saved debug HTML to {debug_path}")
        except Exception as e:
            self.logger.error("debug_logging_failed", error=str(e))

        return []

    async def _process_product(self, element) -> bool:
        """
        Process a single product element

        Returns:
            True if product was saved, False otherwise
        """
        try:
            # Extract data
            result = await self._extract_product_data(element)

            # Validate
            if not self._validate_extraction(result):
                return False

            # Enrich and Save to Database
            from ..backend.core.database import get_db_session
            from ..backend.core.repository import ProductRepository
            from .components.product_enricher import ProductEnricher
            from ..backend.core.models import EnrichedProduct, Price, ChipBrand, Store

            enricher = ProductEnricher()
            chip, manufact, model = enricher.enrich(result.title, result.url)

            # Map scraper name to Store enum
            store_name = self.get_store_name()
            store_enum = None

            # Helper to match store names to Enum values
            # Normalize to uppercase for comparison
            normalized_name = store_name.upper()

            if "TERABYTE" in normalized_name:
                store_enum = Store.TERABYTE
            elif "KABUM" in normalized_name:
                store_enum = Store.KABUM
            elif "PICHAU" in normalized_name:
                store_enum = Store.PICHAU
            else:
                # Fallback to direct value (capitalized)
                try:
                    store_enum = Store(store_name.capitalize())
                except ValueError:
                    self.logger.error("invalid_store_name", name=store_name)
                    return False

            enriched_product = EnrichedProduct(
                title=result.title,
                price=Price(raw=result.price_raw, value=result.price_value),
                url=result.url,
                store=store_enum,
                chip_brand=chip,
                manufacturer=manufact,
                model=model,
                scraped_at=datetime.now(),
            )

            with get_db_session() as session:
                repo = ProductRepository(session)
                saved_product = repo.create(enriched_product)

                self.logger.info(
                    "product_saved",
                    id=saved_product.id,
                    title=saved_product.title[:30],
                    price=float(saved_product.price.value),
                )

            return True

        except Exception as e:
            self.logger.error("extraction_saving_failed", error=str(e), exc_info=True)
            return False

    async def _extract_product_data(self, element) -> ExtractionResult:
        """Extract all data from a product element"""
        result = ExtractionResult()

        selectors = self.get_selectors()

        # Extract title
        result.title = await self._extract_text(element, selectors.title)

        # Extract price (store-specific)
        price_data = await self.extract_price(element)
        if price_data:
            result.price_raw, result.price_value = price_data

        # Extract URL
        result.url = await self._extract_link(element, selectors.link)

        # Check availability (if selector provided)
        if selectors.availability:
            result.available = await self._check_availability(
                element, selectors.availability
            )

        return result

    async def _extract_text(self, element, selector_set: List[str]) -> Optional[str]:
        """Extract text using selector set with fallbacks"""
        for selector in selector_set:
            try:
                el = element.locator(selector).first
                count = await el.count()
                if count:
                    text = await el.inner_text()
                    text = text.strip()
                    if text:
                        return text
            except:
                continue
        return None

    async def _extract_link(self, element, selector_set: List[str]) -> Optional[str]:
        """Extract link/URL from element"""
        for selector in selector_set:
            try:
                el = element.locator(selector).first
                count = await el.count()
                if count:
                    href = await el.get_attribute("href")
                    if href:
                        # Make absolute URL if needed
                        if not href.startswith("http"):
                            base_url = self.page.url if self.page else ""
                            # Simple URL joining (can be improved)
                            href = (
                                f"https://{self.get_store_name().lower()}.com.br{href}"
                            )
                        return href
            except:
                continue
        return None

    async def _check_availability(self, element, selector_set: List[str]) -> bool:
        """Check if product is available"""
        text = await element.inner_text()
        text = text.lower()
        unavailable_keywords = ["indisponível", "esgotado", "avise-me", "out of stock"]
        return not any(keyword in text for keyword in unavailable_keywords)
