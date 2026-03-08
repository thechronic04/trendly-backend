import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List

# --- BEHAVIOR TRACKING (CLICKSTREAM ANALYSIS) ---

class ClickstreamTracker:
    """
    High-Frequency Event Tracking for 'User Behavior Analytics'.
    Uses Motor (Async MongoDB client) for high-performance logging.
    """
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.trendly_analytics
        self.events_collection = self.db.user_behavior_logs
        self.sessions_collection = self.db.user_sessions

    async def log_event(
        self, 
        user_id: str = "guest", 
        event_type_str: str = "VIEW", 
        product_id: int = 0, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Logs a user interaction and its context asynchronously.
        Index optimization: product_id + event_type + timestamp.
        """
        event_doc = {
            "user_id": user_id,
            "event_type": event_type_str,
            "product_id": product_id,
            "timestamp": datetime.utcnow(),
            "meta_data": metadata or {}
        }
        # Zero-blocking write to MongoDB
        result = await self.events_collection.insert_one(event_doc)
        return result.acknowledged

# --- USAGE ANALYTICS & AGGREGATION ---

    async def get_popular_products(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """
        Aggregates high-frequency events to identify top trending items.
        MapReduce / Aggregation Pipeline in MongoDB.
        """
        pipeline = [
            # 1. Filter events within 'last x hours'
            {"$match": {"timestamp": {"$gte": datetime.fromtimestamp(time.time() - (hours * 3600))}}},
            # 2. Group by product_id and count interactions
            {"$group": {"_id": "$product_id", "total_interactions": {"$sum": 1}}},
            # 3. Sort by popularity and limit results
            {"$sort": {"total_interactions": -1}},
            {"$limit": limit}
        ]
        cursor = self.events_collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

# --- SESSION TRACKING ---

    async def track_session_duration(self, session_id: str, duration: int):
        """Used for 'User Journey Tracking' and retention metrics."""
        await self.sessions_collection.update_one(
            {"session_id": session_id},
            {"$set": {"last_active": datetime.utcnow()}, "$inc": {"total_duration": duration}},
            upsert=True
        )
