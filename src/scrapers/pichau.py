from typing import Optional
from .base import BaseScraper
from .models import StoreSelectors, SelectorSet
import asyncio
import random

class PichauScraper(BaseScraper):
    def get_store_name(self) -> str:
        return "Pichau"

    def get_selectors(self) -> StoreSelectors:
        return StoreSelectors(
            product_card=SelectorSet(
                selectors=[
                    "div.MuiCard-root",
                    "article[data-cy*='product']",
                    "div[class*='ProductCard']",
                    "a[class*='product-card']"
                ],
                description="Container do produto"
            ),
            title=SelectorSet(
                selectors=[
                    "h2",
                    "a[data-cy*='product-name']",
                    "div[class*='name']",
                    "h2[class*='MuiTypography']"
                ],
                description="Título do produto"
            ),
            price=SelectorSet(
                selectors=[
                    "div[class*='price']",
                    "div[class*='Price']"
                ],
                description="Preço (contém a vista e parcelado)"
            ),
            link=SelectorSet(
                selectors=[
                    "a",
                    "a[data-cy*='product-link']"
                ],
                description="Link do produto"
            ),
            availability=SelectorSet(
                selectors=[
                    "p:has-text('Indisponível')",
                    "button:disabled",
                    "div:has-text('Esgotado')"
                ],
                description="Indicador de indisponibilidade"
            )
        )
    
    def build_url(self, page: int) -> str:
        base_url = "https://www.pichau.com.br/hardware/placa-de-video"
        if page == 1:
            return base_url
        return f"{base_url}?page={page}"

    async def extract_price(self, element) -> Optional[tuple[str, float]]:
        """Custom extraction for Pichau which often lists 'de X por Y'"""
        selectors = self.get_selectors()
        
        for selector in selectors.price.selectors:
            try:
                # Pichau usually has multiple price elements (old, new, credit) in one div
                # Or multiple divs. We generally want the lowest valid price (PIX)
                price_div_locator = element.locator(selector)
                count = await price_div_locator.count()
                
                if count > 0:
                    # Strategy: Get all text from price area and parse numbers
                    text = await element.inner_text()
                    
                    import re
                    # Find all R$ like values
                    matches = re.findall(r'R\$\s*([\d\.,]+)', text)
                    if matches:
                        valid_values = []
                        for m in matches:
                            clean = m.replace(".", "").replace(",", ".")
                            try:
                                val = float(clean)
                                if val > 100: # Sanity check
                                    valid_values.append(val)
                            except:
                                continue
                        
                        if valid_values:
                            # Typically the lowest price is the cash/pix price
                            best_price = min(valid_values)
                            return f"R$ {best_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), best_price
            except:
                continue
        
        return None
