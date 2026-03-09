import os
import random
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models

app = FastAPI(title="Trendly AI B2C API", version="1.0.0")

# --- CORS CONFIGURATION ---
# In development: FRONTEND_URL is not set, so we allow all origins.
# In production: set FRONTEND_URL in Railway env vars to your Vercel URL,
# e.g. "https://trendly.vercel.app" — this locks down the API properly.
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

allowed_origins = (
    [FRONTEND_URL] if FRONTEND_URL else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Allow Vercel Analytics headers
)


# --- DB DEPENDENCY ---
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- STARTUP: Auto-create tables and seed if DB is empty ---
@app.on_event("startup")
def on_startup():
    models.init_db()
    _auto_seed()


def _auto_seed():
    """Seeds the database on first boot if no products exist."""
    db = models.SessionLocal()
    try:
        count = db.query(models.Product).count()
        if count == 0:
            print("Empty database detected — running auto-seed...")
            from seed_products import seed
            seed()
            print("Auto-seed complete.")
    finally:
        db.close()


# --- ROUTES ---

@app.get("/")
def read_root():
    return {"message": "Welcome to Trendly AI - B2C Fashion & Makeup Trend Predictor"}


@app.get("/health")
def health_check():
    """Railway uses this endpoint to confirm the service is alive."""
    return {"status": "ok"}


@app.get("/api/trends")
def get_trending_products(db: Session = Depends(get_db)):
    """Fetch currently trending products."""
    products = db.query(models.Product).filter(models.Product.is_trending_now == True).all()
    return {"trending": products}


@app.get("/api/predictions")
def get_predicted_trends(db: Session = Depends(get_db)):
    """Fetch products predicted to trend next month."""
    products = db.query(models.Product).filter(models.Product.predicted_next_month == True).all()
    return {"predicted_next_month": products}


@app.get("/api/products")
def get_all_products(db: Session = Depends(get_db)):
    """Get full product catalog."""
    return db.query(models.Product).all()


@app.get("/api/ai/analyze-trend")
def analyze_trend(keyword: str):
    """Mock AI endpoint — simulates an ML trend score for any keyword."""
    score = random.uniform(50.0, 99.9)
    momentum = random.choice(["Rising Fast", "Peaking", "Declining", "Emerging Feature"])

    return {
        "keyword": keyword,
        "ai_trend_score": round(score, 1),
        "momentum": momentum,
        "recommendation": "Promote heavily via affiliate ads" if score > 85 else "Monitor",
    }
