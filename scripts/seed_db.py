import sys
import os
from datetime import datetime
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.core.database import get_db_session, create_tables
from src.backend.core.repository import ProductRepository
from src.backend.core.models import EnrichedProduct, Price, Store, ChipBrand

def seed_database():
    """Seed database with valid sample data for E2E tests"""
    print("Seeding database...")
    create_tables()
    
    with get_db_session() as session:
        repo = ProductRepository(session)
        
        # Check if we already have data
        existing = repo.get_all(limit=1)
        if existing:
            print("Database already has data. Skipping seed.")
            return

        products = [
            EnrichedProduct(
                title="Placa de Vídeo ASUS ROG Strix GeForce RTX 4090 24GB",
                price=Price(raw="R$ 14.999,00", value=Decimal("14999.00")),
                url="https://www.pichau.com.br/placa-de-video-asus-rog-strix-geforce-rtx-4090-24gb-gddr6x-rog-strix-rtx4090-24g-gaming",
                store=Store.PICHAU,
                chip_brand=ChipBrand.NVIDIA,
                manufacturer="ASUS",
                model="RTX 4090",
                scraped_at=datetime.now()
            ),
            EnrichedProduct(
                title="Placa de Vídeo MSI GeForce RTX 4080 16GB VENTUS 3X",
                price=Price(raw="R$ 8.599,99", value=Decimal("8599.99")),
                url="https://www.kabum.com.br/produto/397782/placa-de-video-msi-geforce-rtx-4080-16gb-ventus-3x-oc-gddr6x",
                store=Store.KABUM,
                chip_brand=ChipBrand.NVIDIA,
                manufacturer="MSI",
                model="RTX 4080",
                scraped_at=datetime.now()
            ),
            EnrichedProduct(
                title="Placa de Vídeo Gigabyte Radeon RX 7900 XTX Gaming OC 24GB",
                price=Price(raw="R$ 7.299,00", value=Decimal("7299.00")),
                url="https://www.terabyteshop.com.br/produto/23456/placa-de-video-gigabyte-radeon-rx-7900-xtx-gaming-oc-24gb",
                store=Store.TERABYTE,
                chip_brand=ChipBrand.AMD,
                manufacturer="GIGABYTE",
                model="RX 7900 XTX",
                scraped_at=datetime.now()
            )
        ]
        
        for p in products:
            repo.create(p)
            print(f"Created product: {p.title[:30]}...")

    print("Database seeding completed.")

if __name__ == "__main__":
    seed_database()
