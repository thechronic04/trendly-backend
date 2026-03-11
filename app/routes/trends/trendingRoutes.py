"""
Trending Products API Routes — REST endpoints for the AI Discovery Engine.
Supports filtering by category (fashion, makeup, skincare, accessories).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.sql_models import TrendingProduct

router = APIRouter()

# --- Response Schema ---

class TrendingProductResponse(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    trend_score: Optional[float] = None
    growth_metric: Optional[str] = None
    image_url: Optional[str] = None
    affiliate_link: Optional[str] = None
    ai_insight: Optional[str] = None
    sources: Optional[list] = None
    source_platform: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- In-memory simple cache ---
_cache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _is_cache_valid(key: str) -> bool:
    if key not in _cache:
        return False
    cached_time = _cache[key].get("_cached_at", 0)
    return (datetime.utcnow().timestamp() - cached_time) < CACHE_TTL_SECONDS


# --- Endpoints ---

@router.get("/trending-products", response_model=List[TrendingProductResponse])
async def get_all_trending_products(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all trending products, sorted by trend score descending."""
    cache_key = f"all_{limit}"
    if _is_cache_valid(cache_key):
        return _cache[cache_key]["data"]

    result = await db.execute(
        select(TrendingProduct)
        .order_by(TrendingProduct.trend_score.desc())
        .limit(limit)
    )
    products = result.scalars().all()

    response = [TrendingProductResponse.model_validate(p) for p in products]
    _cache[cache_key] = {"data": response, "_cached_at": datetime.utcnow().timestamp()}
    return response


@router.get("/trending-products/{category}", response_model=List[TrendingProductResponse])
async def get_category_trending_products(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get trending products filtered by category."""
    cache_key = f"cat_{category}_{limit}"
    if _is_cache_valid(cache_key):
        return _cache[cache_key]["data"]

    result = await db.execute(
        select(TrendingProduct)
        .where(TrendingProduct.category == category)
        .order_by(TrendingProduct.trend_score.desc())
        .limit(limit)
    )
    products = result.scalars().all()

    response = [TrendingProductResponse.model_validate(p) for p in products]
    _cache[cache_key] = {"data": response, "_cached_at": datetime.utcnow().timestamp()}
    return response


@router.get("/trending-products/cron/sync-trends")
async def trigger_trend_sync(db: AsyncSession = Depends(get_db)):
    """
    Vercel Cron Job endpoint to automatically run the AI pipeline.
    This coordinates with the vercel.json configuration.
    """
    from app.services.trends.trend_pipeline import trend_pipeline
    results = await trend_pipeline.run_pipeline(db)
    return {"message": f"Successfully processed {len(results)} viral trends.", "status": "success"}


@router.post("/trending-products/refresh")
async def refresh_cache():

    """Clear the trending products cache to force fresh data on next request."""
    _cache.clear()
    return {"status": "cache_cleared", "message": "Next request will fetch fresh data."}
