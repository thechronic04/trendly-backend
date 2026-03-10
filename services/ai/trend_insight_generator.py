import random

class TrendInsightGenerator:
    """
    Simulated AI service to generate short explanations for trend momentum.
    """
    
    TEMPLATES = [
        "{product} is surging due to viral {platform} tutorials and rising searches for {category} aesthetics.",
        "We're seeing heavy engagement for {product} from influencers in Tier 1 cities.",
        "{product} has crossed the 80% momentum threshold, driven by recent {category} week highlights.",
        "Rising search volume for {product} indicates it will peak in the next 14 days.",
        "Social hashtag analysis shows {product} is a top choice for '{category} core' styles."
    ]

    @staticmethod
    def generate(product_name: str, category: str) -> str:
        """
        Generate a compelling AI insight for the product.
        """
        template = random.choice(TrendInsightGenerator.TEMPLATES)
        platform = random.choice(["TikTok", "Instagram", "Pinterest", "YouTube"])
        
        return template.format(
            product=product_name,
            platform=platform,
            category=category
        )

# Singleton instance
trend_insight_generator = TrendInsightGenerator()
