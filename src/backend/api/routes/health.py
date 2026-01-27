"""
Health check endpoints

Provides application health and status information.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.database import get_db
from ...core.repository import ProductRepository
from ....utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns basic application status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check
    
    Includes database connectivity and statistics.
    """
    try:
        # Check database
        repo = ProductRepository(db)
        stats = repo.get_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "database": {
                "status": "connected",
                "total_products": stats["total_products"],
                "latest_scrape": stats["latest_scrape"]
            }
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "database": {
                "status": "error",
                "error": str(e)
            }
        }
