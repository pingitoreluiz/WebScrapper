"""
Repository pattern for database operations

Provides clean abstraction over database queries.
"""

import csv
import json
import os
from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session

from .database_models import Product, ScraperRun
from .models import (
    EnrichedProduct,
    ProductInDB,
    ProductSearchQuery,
    ScraperMetrics,
    ChipBrand,
    Store,
    Price,
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


class ProductRepository:
    """Repository for Product database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, product: EnrichedProduct) -> ProductInDB:
        """
        Create a new product or update if URL already exists

        Args:
            product: EnrichedProduct to save

        Returns:
            ProductInDB with database ID
        """
        # Check if product already exists by URL
        existing = (
            self.session.query(Product).filter(Product.url == str(product.url)).first()
        )

        if existing:
            # Update existing product
            existing.title = product.title
            existing.price_raw = product.price.raw
            existing.price_value = float(product.price.value)
            existing.chip_brand = product.chip_brand.value
            existing.manufacturer = product.manufacturer
            existing.model = product.model
            existing.scraped_at = product.scraped_at
            existing.updated_at = datetime.now()

            self.session.flush()
            logger.debug(
                "product_updated", product_id=existing.id, url=str(product.url)
            )

            return self._to_product_in_db(existing)
        else:
            # Create new product
            db_product = Product(
                title=product.title,
                price_raw=product.price.raw,
                price_value=float(product.price.value),
                chip_brand=product.chip_brand.value,
                manufacturer=product.manufacturer,
                model=product.model,
                url=str(product.url),
                store=product.store.value,
                scraped_at=product.scraped_at,
            )

            self.session.add(db_product)
            self.session.flush()

            logger.debug(
                "product_created", product_id=db_product.id, url=str(product.url)
            )

            return self._to_product_in_db(db_product)

    def get_by_id(self, product_id: int) -> Optional[ProductInDB]:
        """Get product by ID"""
        product = self.session.query(Product).filter(Product.id == product_id).first()
        return self._to_product_in_db(product) if product else None

    def get_all(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ProductInDB]:
        """
        Get all products with optional pagination

        Args:
            limit: Maximum number of products to return (None for all)
            offset: Number of products to skip

        Returns:
            List of ProductInDB ordered by scraped_at descending
        """
        query = self.session.query(Product).order_by(desc(Product.scraped_at))

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        products = query.all()
        return [self._to_product_in_db(p) for p in products]

    def search(self, query: ProductSearchQuery) -> List[ProductInDB]:
        """
        Search products with filters

        Args:
            query: Search query parameters

        Returns:
            List of matching products
        """
        q = self.session.query(Product)

        # Apply filters
        if query.query:
            search_term = f"%{query.query}%"
            q = q.filter(
                (Product.title.like(search_term))
                | (Product.model.like(search_term))
                | (Product.manufacturer.like(search_term))
            )

        if query.chip_brand:
            q = q.filter(Product.chip_brand == query.chip_brand.value)

        if query.manufacturer:
            q = q.filter(Product.manufacturer.like(f"%{query.manufacturer}%"))

        if query.store:
            q = q.filter(Product.store == query.store.value)

        if query.min_price is not None:
            q = q.filter(Product.price_value >= query.min_price)

        if query.max_price is not None:
            q = q.filter(Product.price_value <= query.max_price)

        # Apply sorting
        if query.sort_by == "price":
            order_col = Product.price_value
        elif query.sort_by == "date":
            order_col = Product.scraped_at
        else:  # title
            order_col = Product.title

        if query.sort_order == "desc":
            q = q.order_by(desc(order_col))
        else:
            q = q.order_by(asc(order_col))

        # Apply pagination
        q = q.limit(query.limit).offset(query.offset)

        products = q.all()
        return [self._to_product_in_db(p) for p in products]

    def get_best_deals(
        self, limit: int = 10, chip_brand: Optional[ChipBrand] = None
    ) -> List[ProductInDB]:
        """
        Get best deals (lowest prices)

        Args:
            limit: Number of results
            chip_brand: Filter by chip brand

        Returns:
            List of products with best prices
        """
        q = self.session.query(Product).filter(Product.price_value > 0)

        if chip_brand:
            q = q.filter(Product.chip_brand == chip_brand.value)

        q = q.order_by(asc(Product.price_value)).limit(limit)

        products = q.all()
        return [self._to_product_in_db(p) for p in products]

    def get_stats(self) -> dict:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        total = self.session.query(func.count(Product.id)).scalar()

        by_store = (
            self.session.query(Product.store, func.count(Product.id))
            .group_by(Product.store)
            .all()
        )

        by_chip = (
            self.session.query(Product.chip_brand, func.count(Product.id))
            .group_by(Product.chip_brand)
            .all()
        )

        avg_price = (
            self.session.query(func.avg(Product.price_value))
            .filter(Product.price_value > 0)
            .scalar()
        )

        min_price = (
            self.session.query(func.min(Product.price_value))
            .filter(Product.price_value > 0)
            .scalar()
        )

        max_price = (
            self.session.query(func.max(Product.price_value))
            .filter(Product.price_value > 0)
            .scalar()
        )

        latest_scrape = self.session.query(func.max(Product.scraped_at)).scalar()

        best_deals_count = (
            self.session.query(func.count(Product.id))
            .filter(Product.price_value > 0)
            .scalar()
        )

        return {
            "total_products": total or 0,
            "by_store": dict(by_store) if by_store else {},
            "by_chip_brand": dict(by_chip) if by_chip else {},
            "average_price": float(avg_price) if avg_price else 0.0,
            "best_deals_count": best_deals_count or 0,
            "min_price": float(min_price) if min_price else 0.0,
            "max_price": float(max_price) if max_price else 0.0,
            "latest_scrape": latest_scrape.isoformat() if latest_scrape else None,
        }

    def delete_old_products(self, days: int = 30) -> int:
        """
        Delete products older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted products
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        count = (
            self.session.query(Product)
            .filter(Product.scraped_at < cutoff_date)
            .delete()
        )

        logger.info("old_products_deleted", count=count, days=days)

        return count

    def _get_data_dir(self) -> str:
        """Get the data directory for exports"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(base_dir)))
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def export_to_csv(self, output_file: Optional[str] = None) -> str:
        """
        Export all products to CSV

        Args:
            output_file: Output file path (optional, auto-generated if None)

        Returns:
            Path to the generated file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self._get_data_dir(), f"export_{timestamp}.csv")

        products = (
            self.session.query(Product)
            .order_by(Product.store, Product.price_value)
            .all()
        )

        column_names = [
            "id",
            "title",
            "price_raw",
            "price_value",
            "chip_brand",
            "manufacturer",
            "model",
            "url",
            "store",
            "scraped_at",
            "created_at",
            "updated_at",
        ]

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            for p in products:
                writer.writerow(
                    [
                        p.id,
                        p.title,
                        p.price_raw,
                        p.price_value,
                        p.chip_brand,
                        p.manufacturer,
                        p.model,
                        p.url,
                        p.store,
                        p.scraped_at.isoformat() if p.scraped_at else None,
                        p.created_at.isoformat() if p.created_at else None,
                        p.updated_at.isoformat() if p.updated_at else None,
                    ]
                )

        logger.info("products_exported_csv", file=output_file, count=len(products))
        return output_file

    def export_to_json(self, output_file: Optional[str] = None) -> str:
        """
        Export all products to JSON

        Args:
            output_file: Output file path (optional, auto-generated if None)

        Returns:
            Path to the generated file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self._get_data_dir(), f"export_{timestamp}.json")

        products = (
            self.session.query(Product)
            .order_by(Product.store, Product.price_value)
            .all()
        )

        data = []
        for p in products:
            data.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "price_raw": p.price_raw,
                    "price_value": p.price_value,
                    "chip_brand": p.chip_brand,
                    "manufacturer": p.manufacturer,
                    "model": p.model,
                    "url": p.url,
                    "store": p.store,
                    "scraped_at": p.scraped_at.isoformat() if p.scraped_at else None,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                }
            )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("products_exported_json", file=output_file, count=len(products))
        return output_file

    def _to_product_in_db(self, product: Product) -> ProductInDB:
        """Convert SQLAlchemy model to Pydantic model"""
        return ProductInDB(
            id=product.id,
            title=product.title,
            price=Price(raw=product.price_raw, value=product.price_value),
            url=product.url,
            store=Store(product.store),
            chip_brand=ChipBrand(product.chip_brand),
            manufacturer=product.manufacturer,
            model=product.model,
            scraped_at=product.scraped_at,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )


class ScraperRunRepository:
    """Repository for ScraperRun database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, metrics: ScraperMetrics) -> int:
        """
        Create a scraper run record

        Args:
            metrics: ScraperMetrics from execution

        Returns:
            ID of created record
        """
        run = ScraperRun(
            store=metrics.store.value,
            pages_scraped=metrics.pages_scraped,
            products_found=metrics.products_found,
            products_saved=metrics.products_saved,
            products_skipped=metrics.products_skipped,
            errors=metrics.errors,
            captchas_detected=metrics.captchas_detected,
            execution_time=metrics.execution_time,
            started_at=metrics.started_at,
            finished_at=metrics.finished_at,
            success=metrics.errors == 0,
        )

        self.session.add(run)
        self.session.flush()

        logger.info("scraper_run_recorded", run_id=run.id, store=metrics.store.value)

        return run.id

    def get_recent_runs(self, limit: int = 10) -> List[ScraperRun]:
        """Get recent scraper runs"""
        return (
            self.session.query(ScraperRun)
            .order_by(desc(ScraperRun.started_at))
            .limit(limit)
            .all()
        )

    def get_run_stats(self, days: int = 7) -> dict:
        """
        Get scraper run statistics for the last N days

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        total_runs = (
            self.session.query(func.count(ScraperRun.id))
            .filter(ScraperRun.started_at >= cutoff_date)
            .scalar()
        )

        successful_runs = (
            self.session.query(func.count(ScraperRun.id))
            .filter(ScraperRun.started_at >= cutoff_date, ScraperRun.success == True)
            .scalar()
        )

        total_products = (
            self.session.query(func.sum(ScraperRun.products_saved))
            .filter(ScraperRun.started_at >= cutoff_date)
            .scalar()
        )

        avg_execution_time = (
            self.session.query(func.avg(ScraperRun.execution_time))
            .filter(ScraperRun.started_at >= cutoff_date)
            .scalar()
        )

        return {
            "total_runs": total_runs or 0,
            "successful_runs": successful_runs or 0,
            "total_products_scraped": total_products or 0,
            "avg_execution_time": (
                float(avg_execution_time) if avg_execution_time else 0.0
            ),
            "success_rate": (successful_runs / total_runs * 100) if total_runs else 0.0,
        }
