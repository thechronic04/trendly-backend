import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# --- DATABASE CONFIGURATION ---
# Reads DATABASE_URL from environment (injected by Railway/Render automatically).
# Falls back to local SQLite for development.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trendly.db")

# Railway & Render provide Postgres URLs starting with "postgres://"
# but SQLAlchemy requires "postgresql://" — this fixes that automatically.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs a special flag; PostgreSQL does not.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
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
    trend_score = Column(Float, default=0.0)  # AI Predicted trend score out of 100
    is_trending_now = Column(Boolean, default=False)
    predicted_next_month = Column(Boolean, default=False)
    momentum = Column(String)  # e.g., "+24% 7d"


def init_db():
    Base.metadata.create_all(bind=engine)
