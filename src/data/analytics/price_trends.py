"""
Price trends analytics

Analyzes price trends and patterns.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from statistics import mean, median, stdev
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.backend.core.database_models import Product
from src.backend.core.models import ChipBrand, Store
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PriceTrendsAnalyzer:
    """
    Analyzes price trends
    
    Features:
    - Moving averages
    - Price statistics
    - Trend detection
    - Outlier detection
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_price_statistics(
        self,
        chip_brand: Optional[ChipBrand] = None,
        store: Optional[Store] = None,
        days: int = 30
    ) -> Dict:
        """
        Get price statistics
        
        Args:
            chip_brand: Optional filter by chip brand
            store: Optional filter by store
            days: Number of days to analyze
            
        Returns:
            Dictionary with price statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = self.db.query(Product).filter(Product.created_at >= cutoff_date)
        
        if chip_brand:
            query = query.filter(Product.chip_brand == chip_brand.value)
        
        if store:
            query = query.filter(Product.store == store.value)
        
        products = query.all()
        
        if not products:
            return {
                "count": 0,
                "mean": None,
                "median": None,
                "std_dev": None,
                "min": None,
                "max": None
            }
        
        prices = [float(p.price_value) for p in products]
        
        stats = {
            "count": len(prices),
            "mean": round(mean(prices), 2),
            "median": round(median(prices), 2),
            "min": round(min(prices), 2),
            "max": round(max(prices), 2)
        }
        
        if len(prices) > 1:
            stats["std_dev"] = round(stdev(prices), 2)
        else:
            stats["std_dev"] = 0.0
        
        logger.info("price_statistics_calculated", **stats)
        
        return stats
    
    def get_moving_average(
        self,
        chip_brand: ChipBrand,
        window_days: int = 7
    ) -> List[Dict]:
        """
        Calculate moving average for a chip brand
        
        Args:
            chip_brand: Chip brand to analyze
            window_days: Window size in days
            
        Returns:
            List of {date, average_price} dictionaries
        """
        # Get products from last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        
        products = self.db.query(Product).filter(
            Product.chip_brand == chip_brand.value,
            Product.created_at >= cutoff_date
        ).order_by(Product.created_at).all()
        
        if not products:
            return []
        
        # Group by date
        prices_by_date = {}
        for product in products:
            date_key = product.created_at.date()
            if date_key not in prices_by_date:
                prices_by_date[date_key] = []
            prices_by_date[date_key].append(float(product.price_value))
        
        # Calculate daily averages
        daily_averages = [
            {"date": date, "average": mean(prices)}
            for date, prices in sorted(prices_by_date.items())
        ]
        
        # Calculate moving average
        moving_averages = []
        for i in range(len(daily_averages)):
            window_start = max(0, i - window_days + 1)
            window_data = daily_averages[window_start:i+1]
            window_avg = mean([d["average"] for d in window_data])
            
            moving_averages.append({
                "date": daily_averages[i]["date"].isoformat(),
                "average_price": round(window_avg, 2),
                "daily_average": round(daily_averages[i]["average"], 2)
            })
        
        return moving_averages
    
    def detect_outliers(
        self,
        chip_brand: Optional[ChipBrand] = None,
        threshold_std_devs: float = 2.0
    ) -> List[Dict]:
        """
        Detect price outliers
        
        Args:
            chip_brand: Optional filter by chip brand
            threshold_std_devs: Number of standard deviations for outlier detection
            
        Returns:
            List of outlier products
        """
        query = self.db.query(Product)
        
        if chip_brand:
            query = query.filter(Product.chip_brand == chip_brand.value)
        
        products = query.all()
        
        if len(products) < 3:
            return []
        
        prices = [float(p.price_value) for p in products]
        avg = mean(prices)
        std = stdev(prices)
        
        outliers = []
        for product in products:
            price = float(product.price_value)
            z_score = abs((price - avg) / std) if std > 0 else 0
            
            if z_score > threshold_std_devs:
                outliers.append({
                    "id": product.id,
                    "title": product.title,
                    "price": price,
                    "z_score": round(z_score, 2),
                    "deviation": round(price - avg, 2)
                })
        
        logger.info("outliers_detected", count=len(outliers), threshold=threshold_std_devs)
        
        return outliers
    
    def get_price_trend(
        self,
        chip_brand: ChipBrand,
        days: int = 30
    ) -> str:
        """
        Determine price trend direction
        
        Args:
            chip_brand: Chip brand to analyze
            days: Number of days to analyze
            
        Returns:
            "increasing", "decreasing", or "stable"
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        products = self.db.query(Product).filter(
            Product.chip_brand == chip_brand.value,
            Product.created_at >= cutoff_date
        ).order_by(Product.created_at).all()
        
        if len(products) < 10:
            return "insufficient_data"
        
        # Split into first half and second half
        mid = len(products) // 2
        first_half = products[:mid]
        second_half = products[mid:]
        
        first_avg = mean([float(p.price_value) for p in first_half])
        second_avg = mean([float(p.price_value) for p in second_half])
        
        change_percent = ((second_avg - first_avg) / first_avg) * 100
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
