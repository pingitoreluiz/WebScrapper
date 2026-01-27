import asyncio
import sys
import os
from pathlib import Path

# Add src to python path for direct execution
sys.path.append(str(Path(__file__).parent.parent))

from src.scrapers.terabyte import TerabyteScraper
from src.utils.logger import get_logger
from src.scrapers.models import ScraperConfig
from src.backend.core.models import Store

logger = get_logger("debug_terabyte")

async def main():
    print("🚀 Starting Terabyte Scraper (Async Debug)...")
    
    # Initialize scraper
    config = ScraperConfig(store=Store.TERABYTE, headless=True)
    scraper = TerabyteScraper(config=config)
    
    try:
        # Run scraping
        metrics = await scraper.run()
        
        print("\n📊 Metrics:")
        print(metrics.__dict__)
        
        if metrics.error:
            print(f"❌ Error: {metrics.error}")
            sys.exit(1)
            
        if metrics.products_found == 0:
            print("❌ No products found!")
            sys.exit(1)
            
        print("✅ Success!")
        
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        raise
    finally:
        if scraper.browser:
            await scraper.browser.close()

if __name__ == "__main__":
    asyncio.run(main())
