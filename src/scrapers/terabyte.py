from typing import Optional
from .base import BaseScraper
from .models import StoreSelectors, SelectorSet
import asyncio
import random

class TerabyteScraper(BaseScraper):
    def get_store_name(self) -> str:
        return "TerabyteShop"

    def get_selectors(self) -> StoreSelectors:
        return StoreSelectors(
            product_card=SelectorSet(
                selectors=[
                    "div.product-item",
                    "div[class*='product-item']",
                    "div.pbox"
                ],
                description="Container do produto"
            ),
            title=SelectorSet(
                selectors=[
                    "a.prod-name",
                    "a[class*='prod-name']",
                    "h2",
                    "div.product-item__name" # Sometimes used in newer layouts
                ],
                description="Título do produto"
            ),
            price=SelectorSet(
                selectors=[
                    "div.product-item__new-price",
                    "div.prod-new-price",
                    "span.prod-new-price",
                    "div[class*='new-price']"
                ],
                description="Preço a vista"
            ),
            link=SelectorSet(
                selectors=[
                    "a.prod-name", 
                    "a.product-item__name",
                    "a[href*='produto']"
                ],
                description="Link do produto"
            ),
            availability=SelectorSet(
                selectors=[
                    "div.tbt_esgotado",
                    "div.indisponivel",
                    "div[class*='esgotado']"
                ],
                description="Indicador de indisponibilidade"
            )
        )
    
    def build_url(self, page: int) -> str:
        base_url = "https://www.terabyteshop.com.br/hardware/placas-de-video"
        if page == 1:
            return base_url
        return f"{base_url}?pagina={page}"

    async def _load_page(self, url: str) -> None:
        """Override to add specific scrolling and waiting logic for Terabyte"""
        await super()._load_page(url)
        
        # Terabyte checks for bot behavior, adding some human-like scrolling
        try:
            # Random scroll down
            await self.page.evaluate("window.scrollBy(0, 300)")
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Wait for products
            await self.page.wait_for_selector("div.product-item", timeout=10000)
            
            # Scroll to bottom to trigger lazy loading if any
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
        except Exception as e:
            self.logger.warning("error_during_page_load_scroll", error=str(e))

    async def extract_price(self, element) -> Optional[tuple[str, float]]:
        """Custom extraction for Terabyte which has specific price formatting"""
        selectors = self.get_selectors()
        
        # Try finding the price element
        for selector in selectors.price:
            try:
                price_el = element.locator(selector).first
                if await price_el.count() > 0:
                    text = await price_el.inner_text()
                    # Terabyte format often: "R$ 1.234,56" inside a div
                    if "R$" in text:
                        # Clean up "à vista" or other text
                        prices = text.replace("R$", "").replace(".", "").replace(",", ".").split()
                        # Usually the last number is the price if there are multiple or extra text
                        # But safely, let's find the float pattern
                        import re
                        matches = re.findall(r'[\d\.]+', text.replace("R$", "").replace(".", "").replace(",", "."))
                        if matches:
                            val = float(matches[0])
                            return text.strip(), val
            except:
                continue
        
        return None
