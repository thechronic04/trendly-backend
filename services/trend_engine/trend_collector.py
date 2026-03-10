from typing import List, Dict
from .trend_sources import GoogleTrendsAdapter, PinterestTrendsAdapter, EcommerceBestSellerAdapter

class TrendCollector:
    """
    Orchestrates adapters to collect and aggregate trend signals.
    """
    def __init__(self):
        self.adapters = [
            GoogleTrendsAdapter(),
            PinterestTrendsAdapter(),
            EcommerceBestSellerAdapter()
        ]

    async def collect_all(self) -> List[Dict]:
        """
        Call each adapter, normalize, and aggregate signals by keyword.
        """
        all_raw_signals = []
        for adapter in self.adapters:
            signals = await adapter.fetch_signals()
            all_raw_signals.extend(signals)
        
        # Aggregate logic
        aggregated = {}
        for signal in all_raw_signals:
            kw = signal["keyword"].lower()
            if kw not in aggregated:
                aggregated[kw] = {
                    "keyword": kw,
                    "sources": [signal["source"]],
                    "signals": {
                        "search_growth": signal["metric"].get("growth_rate", 0),
                        "mention_count": signal["metric"].get("saves", signal["metric"].get("search_volume", 0)),
                        "rank_signal": 1.0 / signal["metric"].get("sales_rank", 100) if "sales_rank" in signal["metric"] else 0
                    }
                }
            else:
                aggregated[kw]["sources"].append(signal["source"])
                # Take max growth for simplicity
                aggregated[kw]["signals"]["search_growth"] = max(
                    aggregated[kw]["signals"]["search_growth"], 
                    signal["metric"].get("growth_rate", 0)
                )
        
        return list(aggregated.values())

# Singleton
trend_collector = TrendCollector()
