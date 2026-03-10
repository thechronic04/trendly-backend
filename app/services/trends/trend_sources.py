"""
Trend Sources — Adapter Pattern implementation for multi-platform signal collection.
Each adapter normalizes signals into a unified format:
  { keyword, source, search_volume, growth_rate }
"""
import datetime
import random
from typing import List, Dict
from abc import ABC, abstractmethod


class TrendSignal:
    """Unified trend signal object."""
    def __init__(self, keyword: str, source: str, search_volume: int, growth_rate: float):
        self.keyword = keyword
        self.source = source
        self.search_volume = search_volume
        self.growth_rate = growth_rate
        self.timestamp = datetime.datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            "keyword": self.keyword,
            "source": self.source,
            "search_volume": self.search_volume,
            "growth_rate": self.growth_rate,
            "timestamp": self.timestamp
        }


class TrendSourceAdapter(ABC):
    """Base adapter class — all adapters must implement fetch_signals()."""
    @abstractmethod
    async def fetch_signals(self) -> List[Dict]:
        raise NotImplementedError


class GoogleTrendsAdapter(TrendSourceAdapter):
    """
    Adapter for Google Trends signals.
    In production: uses pytrends or Google Trends API.
    Currently: simulated with realistic fashion/beauty trend data.
    """
    TREND_KEYWORDS = [
        "lip oil", "oversized hoodie", "clean girl makeup",
        "vintage leather jacket", "niacinamide serum", "baggy denim",
        "coquette aesthetic", "quiet luxury blazer", "strawberry makeup",
        "korean skincare routine", "maxi skirt", "chunky gold jewelry"
    ]

    async def fetch_signals(self) -> List[Dict]:
        signals = []
        for kw in self.TREND_KEYWORDS:
            signal = TrendSignal(
                keyword=kw,
                source="google_trends",
                search_volume=random.randint(30000, 200000),
                growth_rate=round(random.uniform(0.10, 0.95), 2)
            )
            signals.append(signal.to_dict())
        return signals


class PinterestAdapter(TrendSourceAdapter):
    """
    Adapter for Pinterest trending searches.
    In production: uses Pinterest Trends API or web scraping.
    """
    TREND_KEYWORDS = [
        "coquette aesthetic", "balletcore", "strawberry makeup",
        "quiet luxury", "mob wife aesthetic", "coastal grandmother",
        "clean girl nails", "soft glam makeup", "pearl accessories"
    ]

    async def fetch_signals(self) -> List[Dict]:
        signals = []
        for kw in self.TREND_KEYWORDS:
            signal = TrendSignal(
                keyword=kw,
                source="pinterest",
                search_volume=random.randint(10000, 80000),
                growth_rate=round(random.uniform(0.15, 0.85), 2)
            )
            signals.append(signal.to_dict())
        return signals


class EcommerceAdapter(TrendSourceAdapter):
    """
    Adapter for e-commerce bestseller lists (Amazon, Nykaa, Myntra, etc.).
    In production: scrapes bestseller/movers-and-shakers pages.
    """
    TREND_KEYWORDS = [
        "matte lipstick", "puffy tote bag", "claw clip",
        "hydrocolloid patches", "retinol serum", "platform sneakers",
        "silk pillowcase", "oversized sunglasses", "peptide moisturizer"
    ]

    async def fetch_signals(self) -> List[Dict]:
        signals = []
        for kw in self.TREND_KEYWORDS:
            # E-commerce signals use sales rank instead of search volume
            sales_rank = random.randint(1, 100)
            signal = TrendSignal(
                keyword=kw,
                source="ecommerce_bestseller",
                search_volume=random.randint(5000, 60000),
                growth_rate=round(1.0 / max(1, sales_rank), 4)
            )
            signals.append(signal.to_dict())
        return signals
