from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.analytics_repository import AnalyticsRepository
from ...core.models import AnalyticsHistoryPoint, AnalyticsStoreComparison

router = APIRouter()


@router.get("/history", response_model=List[AnalyticsHistoryPoint])
async def get_price_history(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Get daily price history for the last N days.
    Useful for line charts.
    """
    repo = AnalyticsRepository(db)
    return repo.get_price_history(days)


@router.get("/comparison", response_model=List[AnalyticsStoreComparison])
async def get_store_comparison(
    db: Session = Depends(get_db)
):
    """
    Get comparison statistics between stores.
    Useful for bar charts.
    """
    repo = AnalyticsRepository(db)
    return repo.get_store_comparison()
