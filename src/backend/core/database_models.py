"""
Database models using SQLAlchemy ORM

Defines database tables and relationships.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Integer, DateTime, Index, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .models import ChipBrand, Store


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


class Product(Base):
    """
    Product table - stores scraped product information

    Attributes:
        id: Primary key
        title: Product title/name
        price_raw: Original price string (e.g., "R$ 2.500,00")
        price_value: Numeric price value for queries
        chip_brand: GPU chip manufacturer (NVIDIA, AMD, INTEL)
        manufacturer: Product manufacturer (ASUS, MSI, etc.)
        model: GPU model (RTX 4090, RX 7900 XT, etc.)
        url: Product URL (unique)
        store: Store name
        scraped_at: When the product was scraped
        created_at: When the record was created
        updated_at: When the record was last updated
    """

    __tablename__ = "products"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Product information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    price_raw: Mapped[str] = mapped_column(String(50), nullable=False)
    price_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Enriched metadata
    chip_brand: Mapped[str] = mapped_column(
        SQLEnum(ChipBrand, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ChipBrand.OTHER.value,
    )
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Source information
    url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    store: Mapped[str] = mapped_column(
        SQLEnum(Store, values_callable=lambda x: [e.value for e in x]), nullable=False
    )

    # Timestamps
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_store", "store"),
        Index("idx_chip_brand", "chip_brand"),
        Index("idx_manufacturer", "manufacturer"),
        Index("idx_model", "model"),
        Index("idx_price_value", "price_value"),
        Index("idx_scraped_at", "scraped_at"),
        Index("idx_url", "url", unique=True),
        Index("idx_store_price", "store", "price_value"),
        Index("idx_chip_price", "chip_brand", "price_value"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title='{self.title[:30]}...', price={self.price_value}, store={self.store})>"


class ScraperRun(Base):
    """
    Scraper execution history

    Tracks each scraper run with metrics and results.
    """

    __tablename__ = "scraper_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store: Mapped[str] = mapped_column(
        SQLEnum(Store, values_callable=lambda x: [e.value for e in x]), nullable=False
    )

    # Metrics
    pages_scraped: Mapped[int] = mapped_column(Integer, default=0)
    products_found: Mapped[int] = mapped_column(Integer, default=0)
    products_saved: Mapped[int] = mapped_column(Integer, default=0)
    products_skipped: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    captchas_detected: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    execution_time: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Status
    success: Mapped[bool] = mapped_column(
        Integer, default=False
    )  # SQLite uses INTEGER for BOOLEAN
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        Index("idx_run_store", "store"),
        Index("idx_run_started_at", "started_at"),
        Index("idx_run_success", "success"),
    )

    def __init__(self, **kwargs):
        if "completed_at" in kwargs:
            kwargs["finished_at"] = kwargs.pop("completed_at")
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<ScraperRun(id={self.id}, store={self.store}, saved={self.products_saved}, time={self.execution_time:.2f}s)>"
