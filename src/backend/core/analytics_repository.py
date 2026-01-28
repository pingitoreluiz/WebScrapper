"""
Analytics Repository

Handles complex aggregation queries for the analytics dashboard.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy import func, desc, cast, Date
from sqlalchemy.orm import Session

from .database_models import Product, ScraperRun
from .models import AnalyticsHistoryPoint, AnalyticsStoreComparison, Store


class AnalyticsRepository:
    """Repository for Analytics operations"""

    def __init__(self, session: Session):
        self.session = session

    def get_price_history(self, days: int = 30) -> List[AnalyticsHistoryPoint]:
        """
        Get daily price average for the last N days.
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # SQLite/PostgreSQL compatible date stripping
        # Grouping by date component of scraped_at
        stats = (
            self.session.query(
                func.date(Product.scraped_at).label("date"),
                func.avg(Product.price_value).label("avg_price"),
                func.min(Product.price_value).label("min_price"),
            )
            .filter(Product.scraped_at >= cutoff_date)
            .filter(Product.price_value > 0)
            .group_by(func.date(Product.scraped_at))
            .order_by(func.date(Product.scraped_at))
            .all()
        )

        return [
            AnalyticsHistoryPoint(
                date=str(stat.date),
                average_price=float(stat.avg_price or 0.0),
                min_price=float(stat.min_price or 0.0),
            )
            for stat in stats
        ]

    def get_store_comparison(self) -> List[AnalyticsStoreComparison]:
        """
        Get comparison stats between stores (avg price, count, cheapest item).
        """
        stats = (
            self.session.query(
                Product.store,
                func.count(Product.id).label("count"),
                func.avg(Product.price_value).label("avg_price"),
                func.min(Product.price_value).label("min_price"),
            )
            .filter(Product.price_value > 0)
            .group_by(Product.store)
            .all()
        )

        return [
            AnalyticsStoreComparison(
                store=Store(stat.store),
                product_count=stat.count,
                average_price=float(stat.avg_price or 0.0),
                cheapest_product_price=float(stat.min_price or 0.0),
            )
            for stat in stats
        ]
