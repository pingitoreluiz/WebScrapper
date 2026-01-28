"""
Product API routes

Endpoints for querying and managing product data.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.repository import ProductRepository
from ...core.models import (
    ProductResponse, ProductSearchQuery, ChipBrand, Store
)
from ....utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="price", pattern="^(price|date|title)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    chip_brand: Optional[ChipBrand] = None,
    store: Optional[Store] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    db: Session = Depends(get_db)
):
    """
    List products with pagination and filters
    
    Args:
        limit: Maximum number of results (1-1000)
        offset: Number of results to skip
        sort_by: Sort field (price, date, title)
        sort_order: Sort order (asc, desc)
        chip_brand: Filter by chip brand
        store: Filter by store
        min_price: Minimum price
        max_price: Maximum price
        
    Returns:
        List of products
    """
    repo = ProductRepository(db)
    
    query = ProductSearchQuery(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
        chip_brand=chip_brand,
        store=store,
        min_price=min_price,
        max_price=max_price
    )
    
    products = repo.search(query)
    
    logger.info("products_listed", count=len(products), limit=limit, offset=offset)
    
    return [ProductResponse.from_db_model(p) for p in products]


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    query: Optional[str] = Query(default=None, min_length=2),
    chip_brand: Optional[ChipBrand] = None,
    manufacturer: Optional[str] = None,
    store: Optional[Store] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="price", pattern="^(price|date|title)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Search products with filters
    
    Args:
        query: Search text (title, model, manufacturer)
        chip_brand: Filter by chip brand (NVIDIA, AMD, INTEL)
        manufacturer: Filter by manufacturer
        store: Filter by store
        min_price: Minimum price
        max_price: Maximum price
        limit: Maximum results
        offset: Results to skip
        sort_by: Sort field
        sort_order: Sort order
        
    Returns:
        List of matching products
    """
    repo = ProductRepository(db)
    
    search_query = ProductSearchQuery(
        query=query,
        chip_brand=chip_brand,
        manufacturer=manufacturer,
        store=store,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    products = repo.search(search_query)
    
    logger.info(
        "products_searched",
        query=query,
        filters={
            "chip_brand": chip_brand.value if chip_brand else None,
            "manufacturer": manufacturer,
            "store": store.value if store else None,
            "price_range": f"{min_price}-{max_price}" if min_price or max_price else None
        },
        count=len(products)
    )
    
    return [ProductResponse.from_db_model(p) for p in products]


@router.get("/best-deals", response_model=List[ProductResponse])
async def get_best_deals(
    limit: int = Query(default=10, ge=1, le=100),
    chip_brand: Optional[ChipBrand] = None,
    db: Session = Depends(get_db)
):
    """
    Get best deals (lowest prices)
    
    Args:
        limit: Number of deals to return
        chip_brand: Optional filter by chip brand
        
    Returns:
        List of products with best prices
    """
    repo = ProductRepository(db)
    
    products = repo.get_best_deals(limit=limit, chip_brand=chip_brand)
    
    logger.info(
        "best_deals_retrieved",
        limit=limit,
        chip_brand=chip_brand.value if chip_brand else None,
        count=len(products)
    )
    
    return [ProductResponse.from_db_model(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get product by ID
    
    Args:
        product_id: Product ID
        
    Returns:
        Product details
        
    Raises:
        HTTPException: 404 if product not found
    """
    repo = ProductRepository(db)
    
    product = repo.get_by_id(product_id)
    
    if not product:
        logger.warning("product_not_found", product_id=product_id)
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found"
        )
    
    logger.info("product_retrieved", product_id=product_id)
    
    return ProductResponse.from_db_model(product)


@router.get("/stats/overview")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get database statistics
    
    Returns:
        Statistics about products in database
    """
    repo = ProductRepository(db)
    
    stats = repo.get_stats()
    
    logger.info("stats_retrieved")
    
    return stats
