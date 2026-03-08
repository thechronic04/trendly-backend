import os
import random
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- DATABASE ---
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Use pg8000 (pure Python) — psycopg2 doesn't work on Vercel serverless
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    description = Column(String)
    price = Column(Float)
    currency = Column(String, default="USD")
    category = Column(String)
    sub_category = Column(String)
    collection = Column(String)
    image_url = Column(String)
    affiliate_link = Column(String)
    trend_score = Column(Float, default=0.0)
    is_trending_now = Column(Boolean, default=False)
    predicted_next_month = Column(Boolean, default=False)
    momentum = Column(String)

# --- APP ---
app = FastAPI(title="Trendly AI API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "")
allowed_origins = [FRONTEND_URL] if FRONTEND_URL else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Trendly AI API is live!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/api/trends")
def get_trending(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_trending_now == True).all()
    return {"trending": products}

@app.get("/api/predictions")
def get_predictions(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.predicted_next_month == True).all()
    return {"predicted_next_month": products}

@app.get("/api/ai/analyze-trend")
def analyze_trend(keyword: str):
    score = random.uniform(50.0, 99.9)
    momentum = random.choice(["Rising Fast", "Peaking", "Declining", "Emerging"])
    return {
        "keyword": keyword,
        "ai_trend_score": round(score, 1),
        "momentum": momentum,
        "recommendation": "Promote heavily" if score > 85 else "Monitor",
    }
