"""
Market insights analytics

Provides market analysis and insights.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter

from src.backend.core.database_models import Product
from src.backend.core.models import ChipBrand, Store
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MarketInsightsAnalyzer:
    """
    Analyzes market insights
    
    Features:
    - Store comparison
    - Brand distribution
    - Manufacturer analysis
    - Best value products
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def compare_stores(self, chip_brand: Optional[ChipBrand] = None) -> List[Dict]:
        """
        Compare prices across stores
        
        Args:
            chip_brand: Optional filter by chip brand
            
        Returns:
            List of store comparisons
        """
        query = self.db.query(
            Product.store,
            func.count(Product.id).label('product_count'),
            func.avg(Product.price_value).label('avg_price'),
            func.min(Product.price_value).label('min_price'),
            func.max(Product.price_value).label('max_price')
        )
        
        if chip_brand:
            query = query.filter(Product.chip_brand == chip_brand.value)
        
        results = query.group_by(Product.store).all()
        
        comparisons = [
            {
                "store": row.store,
                "product_count": row.product_count,
                "avg_price": round(float(row.avg_price), 2),
                "min_price": round(float(row.min_price), 2),
                "max_price": round(float(row.max_price), 2)
            }
            for row in results
        ]
        
        logger.info("stores_compared", count=len(comparisons))
        
        return comparisons
    
    def get_brand_distribution(self) -> Dict[str, int]:
        """
        Get distribution of products by chip brand
        
        Returns:
            Dictionary of {brand: count}
        """
        results = self.db.query(
            Product.chip_brand,
            func.count(Product.id).label('count')
        ).group_by(Product.chip_brand).all()
        
        distribution = {row.chip_brand: row.count for row in results}
        
        logger.info("brand_distribution_calculated", **distribution)
        
        return distribution
    
    def get_manufacturer_analysis(self, chip_brand: Optional[ChipBrand] = None) -> List[Dict]:
        """
        Analyze products by manufacturer
        
        Args:
            chip_brand: Optional filter by chip brand
            
        Returns:
            List of manufacturer statistics
        """
        query = self.db.query(
            Product.manufacturer,
            func.count(Product.id).label('product_count'),
            func.avg(Product.price_value).label('avg_price'),
            func.min(Product.price_value).label('min_price')
        )
        
        if chip_brand:
            query = query.filter(Product.chip_brand == chip_brand.value)
        
        results = query.group_by(Product.manufacturer).all()
        
        analysis = [
            {
                "manufacturer": row.manufacturer,
                "product_count": row.product_count,
                "avg_price": round(float(row.avg_price), 2),
                "min_price": round(float(row.min_price), 2)
            }
            for row in results
        ]
        
        # Sort by product count
        analysis.sort(key=lambda x: x["product_count"], reverse=True)
        
        return analysis
    
    def get_best_value_products(
        self,
        chip_brand: Optional[ChipBrand] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find best value products (lowest price per performance tier)
        
        Args:
            chip_brand: Optional filter by chip brand
            limit: Number of products to return
            
        Returns:
            List of best value products
        """
        query = self.db.query(Product).order_by(Product.price_value.asc())
        
        if chip_brand:
            query = query.filter(Product.chip_brand == chip_brand.value)
        
        products = query.limit(limit).all()
        
        best_values = [
            {
                "id": p.id,
                "title": p.title,
                "price": float(p.price_value),
                "store": p.store,
                "manufacturer": p.manufacturer,
                "model": p.model
            }
            for p in products
        ]
        
        return best_values
    
    def get_market_summary(self) -> Dict:
        """
        Get overall market summary
        
        Returns:
            Dictionary with market summary
        """
        total_products = self.db.query(func.count(Product.id)).scalar()
        
        avg_price = self.db.query(func.avg(Product.price_value)).scalar()
        
        brand_dist = self.get_brand_distribution()
        
        store_count = self.db.query(func.count(func.distinct(Product.store))).scalar()
        
        summary = {
            "total_products": total_products,
            "average_price": round(float(avg_price), 2) if avg_price else 0,
            "brand_distribution": brand_dist,
            "stores_tracked": store_count,
            "most_common_brand": max(brand_dist, key=brand_dist.get) if brand_dist else None
        }
        
        logger.info("market_summary_generated")
        
        return summary
