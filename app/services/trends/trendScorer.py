import random

class TrendScorer:
    \"\"\"
    SECTION 4 — TREND SCORING ENGINE
    Calculates a normalized trend score based on simulated velocity.
    \"\"\"
    
    @staticmethod
    def calculateTrendScore(product_name: str, signals: dict = None) -> dict:
        # Simulate real-time API signals
        search_growth = signals.get('search_growth', random.randint(10, 100)) if signals else random.randint(10, 100)
        social_mentions = signals.get('social_mentions', random.randint(10, 100)) if signals else random.randint(10, 100)
        trend_velocity = signals.get('trend_velocity', random.randint(10, 100)) if signals else random.randint(10, 100)
        
        # Weighted formula matching Section 4 requirements
        score = (search_growth * 0.4) + (social_mentions * 0.3) + (trend_velocity * 0.3)
        normalized_score = min(max(int(score), 0), 100) # Clamp 0-100
        
        return {
            "product": product_name,
            "trendScore": normalized_score,
            "growth_metric": f"+{(search_growth)}%"
        }

trend_scorer = TrendScorer()
