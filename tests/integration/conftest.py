"""
Integration test configuration and fixtures

Provides test database setup and common fixtures for integration tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.backend.core.database import Base
from src.backend.core.models import Store
from src.backend.core.database_models import Product, ScraperRun
from datetime import datetime


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    # Use in-memory SQLite for fast tests
    engine = create_engine(
        "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create database session for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_products(db_session):
    """Create sample products for testing"""
    from src.backend.core.models import Price

    products = [
        Product(
            title="NVIDIA RTX 4090 ASUS ROG",
            price_raw="R$ 10.000,00",
            price_value=10000.00,
            store=Store.PICHAU,
            url="https://pichau.com.br/product/1",
            chip_brand="NVIDIA",
            manufacturer="ASUS",
            model="RTX 4090",
            scraped_at=datetime.utcnow(),
        ),
        Product(
            title="AMD RX 7900 XTX Sapphire",
            price_raw="R$ 6.500,00",
            price_value=6500.00,
            store=Store.KABUM,
            url="https://kabum.com.br/product/2",
            chip_brand="AMD",
            manufacturer="Sapphire",
            model="RX 7900",
            scraped_at=datetime.utcnow(),
        ),
        Product(
            title="NVIDIA RTX 4080 MSI",
            price_raw="R$ 8.000,00",
            price_value=8000.00,
            store=Store.TERABYTE,
            url="https://terabyte.com.br/product/3",
            chip_brand="NVIDIA",
            manufacturer="MSI",
            model="RTX 4080",
            scraped_at=datetime.utcnow(),
        ),
    ]

    for product in products:
        db_session.add(product)
    db_session.commit()

    return products


@pytest.fixture
def sample_scraper_run(db_session):
    """Create sample scraper run for testing"""
    scraper_run = ScraperRun(
        store=Store.PICHAU,
        started_at=datetime.utcnow(),
        finished_at=datetime.utcnow(),
        products_found=10,
        products_saved=5,
        products_skipped=3,
        success=True,
        error_message=None,
    )

    db_session.add(scraper_run)
    db_session.commit()

    return scraper_run
