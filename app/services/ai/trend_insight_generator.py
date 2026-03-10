"""
Trend Insight Generator — Simulated AI service for generating contextual product insights.
In production, this would call an LLM API for richer, context-aware text.
"""
import random
from functools import lru_cache


class TrendInsightGenerator:
    """
    Generates short, compelling AI-powered explanations of why a product is trending.
    Uses template-based generation with randomized platform and style references.
    """

    TEMPLATES = [
        "{product} is surging due to viral {platform} tutorials and rising interest in {category} aesthetics.",
        "We're detecting heavy engagement for {product} from top-tier influencers in {region} markets.",
        "{product} has crossed the 80% momentum threshold, driven by recent {category} week highlights.",
        "Rising search volume for {product} indicates it will peak within the next 14 days.",
        "Social hashtag analysis shows {product} is a breakout favorite for '{category} core' trends.",
        "Neural analysis: {product} saw a +{growth}% spike on {platform} this week — strong buy signal.",
        "{product} is trending across {platform} and Google Shopping, with a {growth}% growth in saves.",
        "AI detects {product} crossing viral threshold on {platform} — {category} category heating up.",
        "Cross-platform momentum for {product}: trending on {platform}, Pinterest, and e-commerce bestseller lists.",
        "{product} is gaining traction in {region} — predicted to go mainstream within 2 weeks."
    ]

    PLATFORMS = ["TikTok", "Instagram", "Pinterest", "YouTube Shorts", "Reddit"]
    REGIONS = [
        "New York", "London", "Tokyo", "Seoul", "Paris",
        "Mumbai", "Los Angeles", "Berlin", "Milan", "Sydney"
    ]

    @staticmethod
    @lru_cache(maxsize=128)
    def generate(product_name: str, category: str) -> str:
        """
        Generate a compelling, contextual AI insight for the product.
        Cached per (product_name, category) to avoid regeneration.
        """
        template = random.choice(TrendInsightGenerator.TEMPLATES)
        platform = random.choice(TrendInsightGenerator.PLATFORMS)
        region = random.choice(TrendInsightGenerator.REGIONS)
        growth = random.randint(15, 85)

        return template.format(
            product=product_name,
            platform=platform,
            category=category,
            region=region,
            growth=growth
        )

    @staticmethod
    def clear_cache():
        """Clear the insight cache for fresh generation."""
        TrendInsightGenerator.generate.cache_clear()


# Singleton instance
trend_insight_generator = TrendInsightGenerator()
