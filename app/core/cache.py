"""
app/core/cache.py
-----------------
Distributed caching layer backed by Redis (async).

* Uses `settings.REDIS_CONNECTION_URL` which supports:
    - Full redis:// / rediss:// URL  (Redis Cloud, Upstash, etc.)
    - Plain hostname fallback          (local dev: "localhost")
* Fails **openly**: if Redis is unavailable the `enabled` flag is set to
  False and every cache call becomes a no-op, so the app still works.
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: redis.Redis = redis.from_url(
    settings.REDIS_CONNECTION_URL,
    decode_responses=True,
)


class CacheManager:
    """Async Redis wrapper with graceful degradation."""

    def __init__(self, client: redis.Redis) -> None:
        self.client = client
        self.enabled = True

    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        try:
            raw = await self.client.get(key)
            return json.loads(raw) if raw is not None else None
        except Exception as exc:
            logger.warning("Redis GET failed (%s) – caching disabled.", exc)
            self.enabled = False
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self.enabled:
            return False
        try:
            await self.client.set(key, json.dumps(value, default=str), ex=ttl)
            return True
        except Exception as exc:
            logger.warning("Redis SET failed (%s) – caching disabled.", exc)
            self.enabled = False
            return False

    async def invalidate(self, key_pattern: str) -> bool:
        """Delete all keys matching a glob-style pattern (e.g. 'trendly:trending:*')."""
        if not self.enabled:
            return False
        try:
            keys = await self.client.keys(key_pattern)
            if keys:
                await self.client.delete(*keys)
            return True
        except Exception as exc:
            logger.warning("Redis INVALIDATE failed (%s) – caching disabled.", exc)
            self.enabled = False
            return False


cache_manager = CacheManager(redis_client)
