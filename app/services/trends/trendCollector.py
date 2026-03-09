from typing import List

class TrendCollector:
    \"\"\"
    SECTION 2 — TREND COLLECTION SERVICE
    Gathers trend signals from external sources.
    Outputs a list of raw trend phrases.
    \"\"\"
    
    @staticmethod
    def collect_trends() -> List[str]:
        # Simulated responses mimicking Google Trends, Hashtags, Best Sellers
        return [
            "oversized hoodie",
            "lip oil",
            "y2k cargo pants",
            "clean girl makeup",
            "chunky sneakers",
            "peptide serum"
        ]

trend_collector = TrendCollector()
