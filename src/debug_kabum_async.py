import asyncio
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.scrapers.kabum import KabumScraper
from src.scrapers.models import ScraperConfig
from src.backend.core.models import Store
from src.utils.logger import configure_logging

async def main():
    configure_logging(log_level="DEBUG", json_logs=False)
    
    config = ScraperConfig(
        store=Store.KABUM,
        headless=True,
        max_pages=1
    )
    
    scraper = KabumScraper(config)
    
    print("🚀 Starting Kabum Scraper (Async Debug)...")
    metrics = await scraper.run()
    
    print("\n📊 Metrics:")
    print(metrics.to_dict())

if __name__ == "__main__":
    asyncio.run(main())
