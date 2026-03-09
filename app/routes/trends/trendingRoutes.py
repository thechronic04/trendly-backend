from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.sql_models import TrendingProduct

router = APIRouter()

# In-memory simple cache for Section 14
cache = {}

@router.get("/trending-products")
async def get_all_trending_products(db: AsyncSession = Depends(get_db)):
    if "all" in cache:
        return cache["all"]
        
    result = await db.execute(select(TrendingProduct).order_by(TrendingProduct.trend_score.desc()).limit(20))
    products = result.scalars().all()
    cache["all"] = products
    return products

@router.get("/trending-products/{category}")
async def get_category_trending_products(category: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"cat_{category}"
    if cache_key in cache:
        return cache[cache_key]
        
    result = await db.execute(
        select(TrendingProduct)
        .where(TrendingProduct.category == category)
        .order_by(TrendingProduct.trend_score.desc())
        .limit(20)
    )
    products = result.scalars().all()
    cache[cache_key] = products
    return products
