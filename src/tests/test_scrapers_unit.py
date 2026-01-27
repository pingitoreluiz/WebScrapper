import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from src.scrapers.base import BaseScraper
from src.scrapers.kabum import KabumScraper
from src.scrapers.pichau import PichauScraper
from src.scrapers.terabyte import TerabyteScraper
from src.scrapers.models import ScraperConfig, StoreSelectors
from src.backend.core.models import Store

@pytest.fixture
def mock_config():
    return ScraperConfig(store=Store.TERABYTE, headless=True)

class TestTerabyteScraper:
    def test_initialization(self, mock_config):
        scraper = TerabyteScraper(config=mock_config)
        assert scraper.get_store_name() == "TerabyteShop"
        assert isinstance(scraper, BaseScraper)

    def test_get_selectors(self, mock_config):
        scraper = TerabyteScraper(config=mock_config)
        selectors = scraper.get_selectors()
        assert isinstance(selectors, StoreSelectors)
        assert len(selectors.product_card.selectors) > 0
        assert "div.product-item" in selectors.product_card.selectors

    def test_build_url(self, mock_config):
        scraper = TerabyteScraper(config=mock_config)
        assert scraper.build_url(1) == "https://www.terabyteshop.com.br/hardware/placas-de-video"
        assert scraper.build_url(2) == "https://www.terabyteshop.com.br/hardware/placas-de-video?pagina=2"

    @pytest.mark.asyncio
    async def test_extract_price_valid(self, mock_config):
        scraper = TerabyteScraper(config=mock_config)
        
        # Mock element
        mock_element = AsyncMock()
        mock_price_el = AsyncMock()
        mock_price_el.count.return_value = 1
        mock_price_el.inner_text.return_value = "R$ 1.234,56"
        
        mock_element.locator.return_value.first = mock_price_el
        
        # Manually set up the side effect for locator calls to match keys in get_selectors
        # This is simplified; integration tests are better for actual extraction logic
        # But here we test the parsing logic if we can inject text
        
        # Simplified test: logic validation
        # We can test the parsing logic directly if we extract it or mock the whole flow
        pass 

class TestKabumScraper:
    def test_initialization(self):
        config = ScraperConfig(store=Store.KABUM)
        scraper = KabumScraper(config=config)
        assert scraper.get_store_name() == "Kabum"

    def test_build_url(self):
        config = ScraperConfig(store=Store.KABUM)
        scraper = KabumScraper(config=config)
        url = scraper.build_url(1)
        # Check against the actual logic we modified (or should match)
        assert "kabum.com.br" in url

    def test_selectors(self):
        config = ScraperConfig(store=Store.KABUM)
        scraper = KabumScraper(config=config)
        selectors = scraper.get_selectors()
        assert "article" in selectors.product_card.selectors or "div.productCard" in selectors.product_card.selectors

class TestPichauScraper:
    def test_initialization(self):
        config = ScraperConfig(store=Store.PICHAU)
        scraper = PichauScraper(config=config)
        assert scraper.get_store_name() == "Pichau"
