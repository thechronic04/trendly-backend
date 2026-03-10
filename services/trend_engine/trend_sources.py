import datetime
import random
from typing import List, Dict

class TrendSourceAdapter:
    """Base adapter class for trend signals."""
    async def fetch_signals(self) -> List[Dict]:
        raise NotImplementedError

class GoogleTrendsAdapter(TrendSourceAdapter):
    """Adapter for Google Trends signals."""
    async def fetch_signals(self) -> List[Dict]:
        # Simulated signals for makeup and fashion
        keywords = [
            "lip oil", "oversized hoodie", "clean girl makeup", 
            "vintage leather jacket", "niacinamide serum", "baggy denim"
        ]
        signals = []
        for kw in keywords:
            signals.append({
                "keyword": kw,
                "source": "google_trends",
                "metric": {
                    "search_volume": random.randint(50000, 150000),
                    "growth_rate": random.uniform(0.1, 0.9)
                },
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        return signals

class PinterestTrendsAdapter(TrendSourceAdapter):
    """Adapter for Pinterest trending searches."""
    async def fetch_signals(self) -> List[Dict]:
        keywords = ["coquette aesthetic", "balletcore", "strawberry makeup", "quiet luxury"]
        signals = []
        for kw in keywords:
            signals.append({
                "keyword": kw,
                "source": "pinterest",
                "metric": {
                    "saves": random.randint(10000, 50000),
                    "growth_rate": random.uniform(0.2, 0.8)
                },
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        return signals

class EcommerceBestSellerAdapter(TrendSourceAdapter):
    """Adapter for Amazon/Ecommerce best sellers."""
    async def fetch_signals(self) -> List[Dict]:
        keywords = ["matte lipstick", "puffy tote bag", "claw clip", "hydrocolloid patches"]
        signals = []
        for kw in keywords:
            signals.append({
                "keyword": kw,
                "source": "ecommerce_bestseller",
                "metric": {
                    "sales_rank": random.randint(1, 100),
                    "review_velocity": random.uniform(0.5, 2.0)
                },
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        return signals
