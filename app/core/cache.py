"""
app/core/cache.py
-----------------
Dual-protocol caching layer.
Automatically detects and uses Upstash REST if credentials are provided,
otherwise falls back to standard Redis (TCP).
"""

import json
import logging
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Async wrapper that supports both Redis TCP and Upstash REST."""

    def __init__(self) -> None:
        self.client: Any = None
        self.mode: str = "OFF"
        self.enabled: bool = False
        
        # Try to initialize Upstash REST first (Best for Serverless)
        if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
            try:
                from upstash_redis.asyncio import Redis as UpstashRedis
                self.client = UpstashRedis(
                    url=settings.UPSTASH_REDIS_REST_URL,
                    token=settings.UPSTASH_REDIS_REST_TOKEN
                )
                self.mode = "UPSTASH_REST"
                self.enabled = True
                logger.info("Cache initialized via Upstash REST mode.")
            except ImportError:
                logger.warning("upstash-redis not installed. Falling back to TCP.")
            except Exception as e:
                logger.warning(f"Upstash REST initialization failed: {e}")

        # Fallback to standard Redis TCP
        if not self.enabled:
            try:
                import redis.asyncio as redis
                self.client = redis.from_url(
                    settings.REDIS_CONNECTION_URL,
                    decode_responses=True,
                )
                self.mode = "REDIS_TCP"
                self.enabled = True
                logger.info(f"Cache initialized via Redis TCP mode ({settings.REDIS_HOST}).")
            except Exception as e:
                logger.warning(f"Redis TCP initialization failed: {e}. Caching disabled.")
                self.enabled = False

    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        try:
            # Both clients have similar async get() methods
            raw = await self.client.get(key)
            if raw is None:
                return None
            # Standard redis returns str, Upstash REST might return dict/list directly depending on config
            return json.loads(raw) if isinstance(raw, str) else raw
        except Exception as exc:
            logger.warning(f"Cache GET failed ({exc}).")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self.enabled:
            return False
        try:
            val_str = json.dumps(value, default=str)
            await self.client.set(key, val_str, ex=ttl)
            return True
        except Exception as exc:
            logger.warning(f"Cache SET failed ({exc}).")
            return False

    async def invalidate(self, key_pattern: str) -> bool:
        if not self.enabled:
            return False
        try:
            # Note: Upstash REST 'keys' and 'delete' work similarly
            keys = await self.client.keys(key_pattern)
            if keys:
                await self.client.delete(*keys)
            return True
        except Exception as exc:
            logger.warning(f"Cache INVALIDATE failed ({exc}).")
            return False

# Global instance
cache_manager = CacheManager()
