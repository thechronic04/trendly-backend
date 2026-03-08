from fastapi import APIRouter, Depends, HTTPException
from app.tracker.events import ClickstreamTracker
from app.schemas.pydantic_schemas import EventLog
from typing import Dict, Any

router = APIRouter()

# --- BEHAVIOR ENGINE: CLICKSTREAM & ANALYTICS ---

# Initialize MongoDB tracker dependency logic
tracker = ClickstreamTracker()

@router.post("/event", status_code=201)
async def track_user_behavior(event: EventLog):
    """
    Production-safe asynchronous behavior logging.
    Ingests 'CLICK', 'VIEW', and 'CART' events to MongoDB.
    High-throughput: Minimal response latency.
    """
    success = await tracker.log_event(
        user_id=event.user_id,
        event_type_str=event.event_type,
        product_id=event.product_id,
        metadata=event.metadata
    )
    
    if not success:
        # In production: push to Redis/Kafka for later retry or fail-safe logic.
        print(f"CRITICAL: Event failed to log to Neural Tracker ID: {event.product_id}")
        
    return {"status": "event_ingested", "processed": success}

@router.get("/insights/hot-products")
async def get_realtime_hot_products(hours: int = 12):
    """Fetches high-velocity products according to current clickstream data."""
    # Data aggregation logic directly from MongoDB
    popular_items = await tracker.get_popular_products(hours=hours)
    return {"popular_products": popular_items}
