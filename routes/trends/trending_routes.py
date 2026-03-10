from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models

router = APIRouter(prefix="/api/trending-products", tags=["trends"])

def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_trending_all(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    min_score: float = Query(60.0, ge=0)
):
    """
    Fetch all discovered trends ranked by trend score.
    """
    trends = db.query(models.TrendingProduct).filter(
        models.TrendingProduct.trend_score >= min_score
    ).order_by(models.TrendingProduct.trend_score.desc()).offset(offset).limit(limit).all()
    
    return {"data": trends}

@router.get("/fashion")
def get_trending_fashion(db: Session = Depends(get_db)):
    trends = db.query(models.TrendingProduct).filter(
        models.TrendingProduct.category == "fashion"
    ).order_by(models.TrendingProduct.trend_score.desc()).limit(10).all()
    return {"data": trends}

@router.get("/makeup")
def get_trending_makeup(db: Session = Depends(get_db)):
    trends = db.query(models.TrendingProduct).filter(
        models.TrendingProduct.category == "makeup"
    ).order_by(models.TrendingProduct.trend_score.desc()).limit(10).all()
    return {"data": trends}

@router.get("/skincare")
def get_trending_skincare(db: Session = Depends(get_db)):
    trends = db.query(models.TrendingProduct).filter(
        models.TrendingProduct.category == "skincare"
    ).order_by(models.TrendingProduct.trend_score.desc()).limit(10).all()
    return {"data": trends}

from fastapi import Header, HTTPException
import os
from services.trend_engine.trend_pipeline import trend_pipeline

@router.get("/cron/sync-trends")
async def trigger_trend_sync(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Vercel Cron Job endpoint to automatically run the AI pipeline.
    Secured by Vercel's Cron Secret environment variable.
    """
    CRON_SECRET = os.getenv("CRON_SECRET")
    
    # Allow testing without a secret locally, but enforce it securely in production
    if CRON_SECRET:
        if not authorization or authorization != f"Bearer {CRON_SECRET}":
            raise HTTPException(status_code=401, detail="Unauthorized Actions")

    # Run the Pipeline
    results = await trend_pipeline.run_pipeline(db)
    return {"message": f"Successfully processed {len(results)} viral trends.", "status": "success"}
