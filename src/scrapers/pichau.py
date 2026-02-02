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
                    "a[class*='product-card']",
                ],
                description="Container do produto",
            ),
            title=SelectorSet(
                selectors=[
                    "h2",
                    "a[data-cy*='product-name']",
                    "div[class*='name']",
                    "h2[class*='MuiTypography']",
                ],
                description="Título do produto",
            ),
            price=SelectorSet(
                selectors=["div[class*='price']", "div[class*='Price']"],
                description="Preço (contém a vista e parcelado)",
            ),
            link=SelectorSet(
                selectors=[
                    "a[data-cy*='product-link']",
                    "a[data-cy*='product-name']",
                    "a[href*='/hardware/']",
                    "a",
                    "xpath=.",
                    "xpath=parent::a",
                    "xpath=ancestor::a",
                ],
                description="Link do produto",
            ),
            availability=SelectorSet(
                selectors=[
                    "p:has-text('Indisponível')",
                    "button:disabled",
                    "div:has-text('Esgotado')",
                ],
                description="Indicador de indisponibilidade",
            ),
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
                    text = await element.inner_text()

                    import re

                    # Find all R$ like values
                    matches = re.findall(r"R\$\s*([\d\.,]+)", text)
                    if matches:
                        valid_values = []
                        for m in matches:
                            try:
                                # Smart parsing for US (1,234.56) vs BR (1.234,56) formats
                                clean_val = 0.0
                                if "," in m and "." in m:
                                    if m.rfind(".") > m.rfind(","):
                                        # US Format (comma then dot) -> "26,999.99"
                                        clean_val = float(m.replace(",", ""))
                                    else:
                                        # BR Format (dot then comma) -> "26.999,99"
                                        clean_val = float(
                                            m.replace(".", "").replace(",", ".")
                                        )
                                elif "," in m:
                                    # Assume BR decimal -> "1234,56"
                                    clean_val = float(m.replace(",", "."))
                                else:
                                    # Assume plain number -> "1234.56" or "1234"
                                    clean_val = float(m)

                                if clean_val > 100:  # Sanity check
                                    valid_values.append(clean_val)
                            except:
                                continue

                        if valid_values:
                            # Heuristic: Pichau often includes the "12x" installment value (e.g. 529.41)
                            # alongside the full price (e.g. 5399.99).
                            # We want the lowest price that IS NOT an installment.

                            max_val = max(valid_values)
                            # Installments are typically ~1/10th or 1/12th of the max price.
                            # We filter out anything smaller than 20% of the maximum detected value.
                            real_prices = [
                                v for v in valid_values if v > (max_val * 0.2)
                            ]

                            if real_prices:
                                best_price = min(real_prices)
                            else:
                                # Fallback if filtering removed everything (unlikely)
                                best_price = min(valid_values)

                            # Convert back to BR format string for display
                            price_formatted = (
                                f"R$ {best_price:,.2f}".replace(",", "X")
                                .replace(".", ",")
                                .replace("X", ".")
                            )
                            return price_formatted, best_price
                        else:
                            self.logger.warning(
                                "pichau_price_parse_failed",
                                text_snippet=text[:100],
                                matches=matches,
                            )

                else:
                    pass  # Selector didn't match
            except Exception as e:
                self.logger.error("pichau_price_error", error=str(e))
                continue

        return None

    async def _load_page(self, url: str) -> None:
        """Override to check for maintenance pages"""
        await super()._load_page(url)

        # Check for specific maintenance title
        try:
            title = await self.page.title()
            if "Site em Manutenção" in title or "Pru Pru" in title:
                self.logger.warning("site_maintenance_detected", url=url)
                from .exceptions import PageLoadError

                raise PageLoadError(url, "Site running maintenance")
        except Exception:
            raise
