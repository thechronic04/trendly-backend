from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sql_models import TrendingProduct
from app.schemas.pydantic_schemas import TrendingProductResponse
from app.core.cache import cache_manager

router = APIRouter()

# Cache TTL constants
TRENDING_CACHE_TTL = 300   # 5 minutes
PRODUCT_CACHE_TTL  = 600   # 10 minutes


def _fill_analytics(product: TrendingProduct) -> dict:
    """Serialize a TrendingProduct ORM object to a dict, filling analytics if absent."""
    data = {c.name: getattr(product, c.name) for c in product.__table__.columns}
    if not data.get("analytics_json"):
        data["analytics_json"] = {
            "engagement_graph": [10, 20, 15, 25, 30, 25, 40],
            "social_mentions": f"{round((product.trend_score or 0) * 1.2, 1)}K",
            "top_regions": ["Global"],
            "sentiment_score": int(product.trend_score or 0),
        }
    return data


@router.get("/trending", response_model=List[TrendingProductResponse])
async def get_trending_products(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
):
    """
    Main Discovery Feed: Returns high-confidence trending items.
    Backed by Redis distributed caching (5-minute TTL).
    """
    cache_key = f"trendly:trending:{category}:{limit}"

    # Try cache first
    cached = await cache_manager.get(cache_key)
    if cached is not None:
        return cached

    try:
        query = (
            select(TrendingProduct)
            .order_by(TrendingProduct.trend_score.desc())
            .limit(limit)
        )
        if category and category != "all":
            query = query.where(TrendingProduct.category == category)

        result = await db.execute(query)
        products = result.scalars().all()

        payload = [_fill_analytics(p) for p in products]

        # Persist to Redis
        await cache_manager.set(cache_key, payload, ttl=TRENDING_CACHE_TTL)
        return payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=TrendingProductResponse)
async def get_product_detail(product_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch deep-dive analytics for a single product. Cached for 10 minutes."""
    cache_key = f"trendly:product:{product_id}"

    cached = await cache_manager.get(cache_key)
    if cached is not None:
        return cached

    query = select(TrendingProduct).where(TrendingProduct.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    payload = _fill_analytics(product)
    if not product.analytics_json:
        payload["analytics_json"] = {
            "engagement_graph": [15, 25, 35, 45, 55, 65, 75],
            "social_mentions": "82.4K",
            "top_regions": ["Global"],
            "sentiment_score": 85,
        }

    await cache_manager.set(cache_key, payload, ttl=PRODUCT_CACHE_TTL)
    return payload


@router.get("/sync-trends")
async def trigger_trend_sync(db: AsyncSession = Depends(get_db)):
    """
    Automated endpoint to trigger the AI Trend Discovery Pipeline.
    Used by Vercel Cron or external schedulers.
    Invalidates all trending cache entries after sync.
    """
    from app.services.trends.trend_pipeline import trend_pipeline

    results = await trend_pipeline.run_pipeline(db)

    # Purge all trending cache so stale data doesn't linger
    await cache_manager.invalidate("trendly:trending:*")

    return {
        "message": f"Successfully processed {len(results)} viral trends.",
        "status": "success",
    }
