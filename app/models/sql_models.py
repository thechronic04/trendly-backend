import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, Numeric, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID

# --- RELATIONAL DATA MANAGEMENT (POSTGRESQL) ---

Base = declarative_base()

class Role(Base):
    """
    Role-Based Access Control (RBAC) definitions.
    Initial: 1: ADMIN, 2: ANALYST, 3: USER
    """
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    users = relationship("User", back_populates="role")

class User(Base):
    """
    Master User Record with Secure Authentication hooks.
    Primary identifier: email (Unique).
    """
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")


# --- DATA MANAGEMENT: PRODUCT TREND DATA ---

class Product(Base):
    """
    Store for high-fidelity product metadata and pre-computed AI trends.
    Uses Postgres JSONB for flexible 'analytics_json'.
    """
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), index=True)
    price = Column(Numeric(10, 2))
    category = Column(String(50), index=True)
    sub_category = Column(String(50))
    
    # AI Trend Score (fluctuates via 'Trendalyzer' logic)
    trend_score = Column(Float, default=50.0)
    predicted_next_month = Column(Boolean, default=False)
    
    # Store complex metadata objects: engagement_graph, top_regions, etc.
    analytics_json = Column(JSON)
    
    affiliate_link = Column(String(2048))
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- DATA VALIDATION & INDEX OPTIMIZATION ---

# 1. Indexing Strategy:
#   - User.email: Fast login lookups.
#   - Product.brand/category: Landing page filter speed.
#   - Product.trend_score: Sorting 'What's Trending' feed.

# 2. Schema management (Alembic) would go here in a full stack.
