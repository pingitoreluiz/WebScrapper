from typing import Optional, List
import re

from .base import BaseScraper
from .models import StoreSelectors, SelectorSet, ExtractionResult
from src.backend.core.models import Store


class KabumScraper(BaseScraper):
    def get_store_name(self) -> str:
        return "Kabum"

    async def _setup_browser(self) -> None:
        """Override to use Firefox which might bypass detection better"""
        from playwright.async_api import async_playwright

        # Stealth is for Chromium only usually

        self.logger.debug("setting_up_browser_firefox")
        self.playwright = await async_playwright().start()

        # Firefox args are different, usually fewer needed
        args = ["--kiosk"] if not self.config.headless else []

        self.browser = await self.playwright.firefox.launch(
            headless=self.config.headless, args=args
        )

        # Firefox UA
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"

        self.context = await self.browser.new_context(
            viewport=self.config.viewport,
            user_agent=user_agent,
            locale="pt-BR",
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
        )

        # Add basic headers
        await self.context.set_extra_http_headers(
            {
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/",
            }
        )

        await self.context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self.page = await self.context.new_page()
        # No stealth for Firefox

        self.page.set_default_timeout(self.config.timeout)

    async def _load_page(self, url: str) -> None:
        await super()._load_page(url)
        # Wait for skeletons to disappear (max 15s)
        try:
            self.logger.info("waiting_for_skeletons_to_detach")
            # Wait for at least one pulse element to detach, effectively waiting for grid load
            # Note: Checking for detachment of the grid container or specific skeleton items
            await self.page.wait_for_selector(
                "div.animate-pulse", state="detached", timeout=15000
            )
            self.logger.info("skeletons_detached", message="Content likely loaded")
        except Exception as e:
            self.logger.warning("timeout_waiting_for_skeletons", error=str(e))

    def get_selectors(self) -> StoreSelectors:
        return StoreSelectors(
            product_card=SelectorSet(
                selectors=[
                    "article",
                    "div.productCard",
                    "div[class*='productCard']",
                    "div[class*='product']",
                ],
                description="Product container",
            ),
            title=SelectorSet(
                selectors=["span.nameCard", "h2", "span[class*='name']"],
                description="Product title",
            ),
            price=SelectorSet(
                selectors=[
                    "span.priceCard",
                    "div[class*='price']",
                    "span[class*='finalPrice']",
                ],
                description="Product price",
            ),
            link=SelectorSet(selectors=["a"], description="Product link"),
            availability=SelectorSet(
                selectors=["div.unavailable", "div[class*='unavailable']"],
                description="Availability indicator",
            ),
        )

    def build_url(self, page: int) -> str:
        # Simplest URL for debugging
        if page == 1:
            return "https://www.kabum.com.br/hardware/placa-de-video-vga"
        return f"https://www.kabum.com.br/hardware/placa-de-video-vga?page_number={page}&page_size=20&sort=most_searched"

    async def extract_price(self, element) -> Optional[tuple[str, float]]:
        # This is handled by BaseScraper's default flow via _extract_text using selectors
        # But BaseScraper template calls self.extract_price(element) to get the tuple
        import re

        selectors = self.get_selectors()
        for selector in selectors.price:
            try:
                price_el = element.locator(selector).first
                if price_el:
                    text = await price_el.inner_text()
                    text = text.strip()
                    # Clean price
                    if "R$" in text:
                        clean_text = (
                            text.replace("R$", "")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )
                        val = float(clean_text)
                        return text, val
            except:
                continue

        # Fallback regex if needed, similar to legacy
        try:
            text = await element.inner_text()
            matches = re.findall(r"R\$\s*([\d.,]+)", text)
            if matches:
                clean = matches[0].replace(".", "").replace(",", ".")
                return f"R$ {matches[0]}", float(clean)
        except:
            pass

        return None
