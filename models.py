from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import uuid

DATABASE_URL = "sqlite:///./trendly.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    currency = Column(String, default="USD")
    category = Column(String, index=True)  # 'clothing' or 'makeup'
    sub_category = Column(String, index=True)
    collection = Column(String, index=True)
    image_url = Column(String)
    affiliate_link = Column(String)
    trend_score = Column(Float, default=0.0) # AI Predicted trend score out of 100
    is_trending_now = Column(Boolean, default=False)
    predicted_next_month = Column(Boolean, default=False)
    momentum = Column(String) # e.g., "+24% 7d"

class TrendingProduct(Base):
    """
    Table for the discovery engine results.
    """
    __tablename__ = "trending_products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    category = Column(String, index=True) # fashion|makeup|accessories|skincare
    brand = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)
    affiliate_links = Column(JSON) # Store dict of networks: links
    trend_score = Column(Float, index=True)
    growth_metric = Column(Float)
    ai_insight = Column(String)
    sources = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
