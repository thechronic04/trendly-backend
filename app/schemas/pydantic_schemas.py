import uuid
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# --- AUTH SYTEM: USER SCHEMAS (SIGNUP / LOGIN) ---

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # Password integrity enforcement

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    role_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# --- DISCOVERY & ANALYTICS: PRODUCT SCHEMAS ---

class ProductAnalytics(BaseModel):
    engagement_graph: List[int]
    social_mentions: str
    top_regions: List[str]
    sentiment_score: int

class ProductBase(BaseModel):
    name: str
    brand: str
    price: float
    category: str
    sub_category: str
    image_url: str
    affiliate_link: str

class ProductResponse(ProductBase):
    id: int
    trend_score: float
    predicted_next_month: bool
    analytics: Optional[ProductAnalytics] = None
    
    class Config:
        from_attributes = True


# --- TRACKER & REPORTING: EVENT SCHEMAS ---

class EventLog(BaseModel):
    user_id: str = "guest"
    event_type: str  # e.g., 'CLICK', 'VIEW', 'SHARE'
    product_id: int
    session_id: str
    metadata: Dict[str, Any] = None


class SystemPerformance(BaseModel):
    """Used for 'System Performance Analytics' reports."""
    cpu_usage: float
    memory_usage: float
    request_latency_ms: float
    active_users: int
    timestamp: datetime = datetime.utcnow()
