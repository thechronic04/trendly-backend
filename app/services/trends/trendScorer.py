"""
Trend Scorer — Weighted scoring algorithm for product trend signals.
Formula: 0.4 * Growth + 0.3 * Mentions + 0.2 * Ranking + 0.1 * Recency
Normalizes all scores to a 0-100 scale.
"""
import math
import time
from typing import Optional


class TrendScorer:
    """
    Implements the weighted scoring algorithm:
      TrendScore = 0.4 * normalizedGrowth
                 + 0.3 * normalizedMentions
                 + 0.2 * normalizedRanking
                 + 0.1 * recencyWeight

    All inputs are normalized to 0-100 before weight application.
    """

    # Weight constants
    W_GROWTH = 0.4
    W_MENTIONS = 0.3
    W_RANKING = 0.2
    W_RECENCY = 0.1

    @staticmethod
    def calculate(
        search_growth: float,
        mention_count: int,
        rank_signal: float,
        signal_age_hours: Optional[float] = None
    ) -> float:
        """
        Calculate a normalized trend score from 0 to 100.

        Args:
            search_growth: Growth rate (0.0 to 1.0+, capped at 1.0)
            mention_count: Social/search mentions (1 to ~1M)
            rank_signal: Ecommerce ranking signal (0.0 to 1.0)
            signal_age_hours: How old the signal is in hours (default: fresh = 0)

        Returns:
            Float trend score from 0 to 100, rounded to 1 decimal.
        """
        # 1. Normalize Growth (input 0.0–1.0 → 0–100)
        norm_growth = min(1.0, max(0.0, search_growth)) * 100

        # 2. Normalize Mentions (logarithmic scale for large ranges)
        # log10(1) = 0, log10(1M) = 6 → normalized to 0–100
        norm_mentions = min(1.0, math.log10(max(1, mention_count)) / 6) * 100

        # 3. Normalize Ranking Signal (input 0.0–1.0 → 0–100)
        norm_ranking = min(1.0, max(0.0, rank_signal)) * 100

        # 4. Calculate Recency Weight
        # Fresh signals (< 6 hours) get score 90-100
        # Older signals decay gradually
        if signal_age_hours is None:
            recency_score = 95.0  # Assume fresh
        else:
            # Exponential decay: half-life of 48 hours
            decay = math.exp(-0.015 * max(0, signal_age_hours))
            recency_score = decay * 100

        # 5. Apply Weights
        score = (
            TrendScorer.W_GROWTH * norm_growth
            + TrendScorer.W_MENTIONS * norm_mentions
            + TrendScorer.W_RANKING * norm_ranking
            + TrendScorer.W_RECENCY * recency_score
        )

        return round(min(100.0, max(0.0, score)), 1)

    @staticmethod
    def calculate_from_signals(signals: dict) -> dict:
        """
        Convenience method: calculates score from a signals dict.
        Returns a full result dict with score and formatted growth metric.
        """
        growth = signals.get("search_growth", 0.5)
        mentions = signals.get("mention_count", 1000)
        rank = signals.get("rank_signal", 0.5)

        score = TrendScorer.calculate(growth, mentions, rank)
        growth_pct = round(growth * 100)

        return {
            "trend_score": score,
            "growth_metric": f"+{growth_pct}%",
            "growth_raw": growth
        }


# Singleton
trend_scorer = TrendScorer()
