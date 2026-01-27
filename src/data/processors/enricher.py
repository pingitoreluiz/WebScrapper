"""
Data enrichment processor

Enriches product data with additional information.
"""

from typing import List

from src.backend.core.models import ProductInDB, RawProduct, EnrichedProduct
from src.scrapers.components.product_enricher import ProductEnricher
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataEnricher:
    """
    Enriches product data
    
    Features:
    - Chip brand detection
    - Manufacturer detection
    - Model extraction
    - Batch processing
    """
    
    def __init__(self):
        self.enricher = ProductEnricher()
    
    def enrich_product(self, raw_product: RawProduct) -> EnrichedProduct:
        """
        Enrich a single product
        
        Args:
            raw_product: Raw product data
            
        Returns:
            Enriched product with chip_brand, manufacturer, model
        """
        chip_brand, manufacturer, model = self.enricher.enrich(
            raw_product.title,
            str(raw_product.url)
        )
        
        enriched = EnrichedProduct(
            title=raw_product.title,
            price=raw_product.price,
            url=raw_product.url,
            store=raw_product.store,
            chip_brand=chip_brand,
            manufacturer=manufacturer,
            model=model
        )
        
        logger.debug(
            "product_enriched",
            title=raw_product.title[:50],
            chip=chip_brand.value,
            manufacturer=manufacturer,
            model=model
        )
        
        return enriched
    
    def enrich_batch(self, raw_products: List[RawProduct]) -> List[EnrichedProduct]:
        """
        Enrich a batch of products
        
        Args:
            raw_products: List of raw products
            
        Returns:
            List of enriched products
        """
        logger.info("enriching_batch", count=len(raw_products))
        
        enriched_products = []
        
        for raw in raw_products:
            try:
                enriched = self.enrich_product(raw)
                enriched_products.append(enriched)
            except Exception as e:
                logger.error(
                    "enrichment_failed",
                    title=raw.title[:50] if raw.title else None,
                    error=str(e)
                )
                # Skip failed enrichments
                continue
        
        logger.info(
            "batch_enriched",
            input=len(raw_products),
            output=len(enriched_products),
            failed=len(raw_products) - len(enriched_products)
        )
        
        return enriched_products
    
    def get_enrichment_stats(self, enriched_products: List[EnrichedProduct]) -> dict:
        """
        Get enrichment statistics
        
        Args:
            enriched_products: List of enriched products
            
        Returns:
            Dictionary with enrichment stats
        """
        stats = {
            "total": len(enriched_products),
            "by_chip_brand": {},
            "by_manufacturer": {},
            "unknown_models": 0
        }
        
        for product in enriched_products:
            # Count by chip brand
            chip = product.chip_brand.value
            stats["by_chip_brand"][chip] = stats["by_chip_brand"].get(chip, 0) + 1
            
            # Count by manufacturer
            mfr = product.manufacturer
            stats["by_manufacturer"][mfr] = stats["by_manufacturer"].get(mfr, 0) + 1
            
            # Count unknown models
            if product.model == "Desconhecido":
                stats["unknown_models"] += 1
        
        return stats
