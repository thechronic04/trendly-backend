class TrendScorer:
    """
    Implements the weighted scoring algorithm:
    TrendScore = 0.4 * normalizedSearchGrowth 
               + 0.3 * normalizedSocialMentions 
               + 0.2 * ecommerceRankingSignal 
               + 0.1 * recencyWeight
    """
    
    @staticmethod
    def calculate(search_growth: float, mentions: int, rank_signal: float) -> float:
        """
        Calculate a normalized score from 0 to 100.
        """
        # 1. Normalize Search Growth (input is usually 0.1 to 1.0)
        norm_growth = min(1.0, search_growth) * 100
        
        # 2. Normalize Mentions (input is usually 5k to 150k)
        # Logarithmic scale to handle large ranges
        import math
        norm_mentions = min(1.0, math.log10(max(1, mentions)) / 6) * 100 # limit to 1M
        
        # 3. Ecommerce Signal (input is 0 to 1.0)
        norm_rank = min(1.0, rank_signal) * 100
        
        # 4. Apply Weights
        score = (0.4 * norm_growth) + (0.3 * norm_mentions) + (0.2 * norm_rank) + (0.1 * 90) # fixed recency weight for now
        
        return round(min(100.0, score), 1)

# Singleton
trend_scorer = TrendScorer()
