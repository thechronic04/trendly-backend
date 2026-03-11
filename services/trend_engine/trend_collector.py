from typing import List, Dict
from .trend_sources import ShopStyleAdapter, SephoraAdapter, EtsyAdapter, AmazonBeautyAdapter

class TrendCollector:
    """
    Orchestrates adapters to collect trending products across categories.
    """
    def __init__(self):
        self.adapters = [
            ShopStyleAdapter(),
            SephoraAdapter(),
            EtsyAdapter(),
            AmazonBeautyAdapter()
        ]

    async def collect_products(self) -> List[Dict]:
        """
        Call each adapter to get trending products.
        """
        all_products = []
        for adapter in self.adapters:
            try:
                products = await adapter.fetch_products()
                all_products.extend(products)
            except Exception as e:
                print(f"Error fetching from {adapter.__class__.__name__}: {e}")
        
        return all_products

# Singleton
trend_collector = TrendCollector()
