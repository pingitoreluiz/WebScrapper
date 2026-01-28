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
    engine = create_engine("sqlite:///:memory:", echo=False)
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
    products = [
        Product(
            title="NVIDIA RTX 4090 ASUS ROG",
            price=10000.00,
            store=Store.PICHAU,
            url="https://pichau.com.br/product/1",
            chip_brand="NVIDIA",
            manufacturer="ASUS",
            available=True,
            scraped_at=datetime.utcnow()
        ),
        Product(
            title="AMD RX 7900 XTX Sapphire",
            price=6500.00,
            store=Store.KABUM,
            url="https://kabum.com.br/product/2",
            chip_brand="AMD",
            manufacturer="Sapphire",
            available=True,
            scraped_at=datetime.utcnow()
        ),
        Product(
            title="NVIDIA RTX 4080 MSI",
            price=8000.00,
            store=Store.TERABYTE,
            url="https://terabyte.com.br/product/3",
            chip_brand="NVIDIA",
            manufacturer="MSI",
            available=False,
            scraped_at=datetime.utcnow()
        )
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
        completed_at=datetime.utcnow(),
        products_found=10,
        products_new=5,
        products_updated=3,
        success=True,
        error_message=None
    )
    
    db_session.add(scraper_run)
    db_session.commit()
    
    return scraper_run
