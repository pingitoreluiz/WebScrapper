
import asyncio
import httpx
import sys
import os
from sqlalchemy import create_engine, text

# Add src to path
sys.path.append(os.getcwd())

from src.backend.core.config import get_config

async def verify_flow():
    print("Starting End-to-End Verification")
    
    # 1. Check Initial DB State
    config = get_config()
    engine = create_engine(config.database.url)
    
    with engine.connect() as conn:
        initial_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        print(f"Initial Product Count: {initial_count}")

    # 2. Trigger Scraper via API
    api_url = "http://localhost:8000/api/v1/scrapers/run"
    payload = {
        "stores": ["Terabyte"], # Use Terabyte as it was reliable in testing
        "headless": True,
        "max_pages": 1
    }
    
    print(f"Triggering API: {api_url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                print(f"API Success: Run ID {data.get('run_id')}")
            else:
                print(f"API Failed: {response.text}")
                return
    except Exception as e:
        print(f"API Connection Error: {e}")
        return

    # 3. Wait for execution
    print("Waiting for scraper to finish (60s)...")
    await asyncio.sleep(60)

    # 4. Check Final DB State
    with engine.connect() as conn:
        final_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        print(f"Final Product Count: {final_count}")
        
    diff = final_count - initial_count
    if diff > 0:
        print(f"SUCCESS: {diff} new products saved!")
    elif initial_count > 0 and diff == 0:
        print("WARNING: No new products, but DB was not empty. Scraper might have updated existing ones.")
    else:
        print("FAILURE: No products saved.")

if __name__ == "__main__":
    asyncio.run(verify_flow())
