from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.sql_models import TrendingProduct
from app.schemas.pydantic_schemas import TrendingProductResponse

router = APIRouter()

# --- Cache Infrastructure ---
_cache: Dict[str, Any] = {}
CACHE_TTL = 300 # 5 minutes

def _is_cache_valid(key: str) -> bool:
    if key not in _cache:
        return False
    entry = _cache[key]
    return (datetime.utcnow().timestamp() - entry["timestamp"]) < CACHE_TTL

@router.get("/trending", response_model=List[TrendingProductResponse])
async def get_trending_products(
    db: AsyncSession = Depends(get_db), 
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None
):
    """
    Main Discovery Feed: Returns high-confidence trending items.
    Optimized with memory caching for high concurrency.
    """
    cache_key = f"trending_{category}_{limit}"
    if _is_cache_valid(cache_key):
        return _cache[cache_key]["data"]

    try:
        query = select(TrendingProduct).order_by(TrendingProduct.trend_score.desc()).limit(limit)
        
        if category and category != 'all':
            query = query.where(TrendingProduct.category == category)
        
        result = await db.execute(query)
        products = result.scalars().all()
        
        # Ensure deep analytics is mocked if missing to prevent frontend crashes
        for p in products:
            if not p.analytics_json:
                p.analytics_json = {
                    "engagement_graph": [10, 20, 15, 25, 30, 25, 40],
                    "social_mentions": f"{round(p.trend_score * 1.2, 1)}K",
                    "top_regions": ["Global"],
                    "sentiment_score": int(p.trend_score)
                }

        _cache[cache_key] = {"data": products, "timestamp": datetime.utcnow().timestamp()}
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", response_model=TrendingProductResponse)
async def get_product_detail(product_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch deep-dive analytics for a single piece."""
    query = select(TrendingProduct).where(TrendingProduct.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Mock data for analytics if not present
    if not product.analytics_json:
         product.analytics_json = {
            "engagement_graph": [15, 25, 35, 45, 55, 65, 75],
            "social_mentions": "82.4K",
            "top_regions": ["Global"],
            "sentiment_score": 85
        }
    return product

@router.get("/sync-trends")
async def trigger_trend_sync(db: AsyncSession = Depends(get_db)):
    """
    Automated endpoint to trigger the AI Trend Discovery Pipeline.
    Used by Vercel Cron or external schedulers.
    """
    from app.services.trends.trend_pipeline import trend_pipeline
    results = await trend_pipeline.run_pipeline(db)
    # Clear cache since data changed
    _cache.clear()
    return {"message": f"Successfully processed {len(results)} viral trends.", "status": "success"}
