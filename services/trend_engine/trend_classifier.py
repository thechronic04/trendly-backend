from typing import Dict

class TrendClassifier:
    """
    Maps products to supported categories: fashion, makeup, skincare, accessories.
    """
    @staticmethod
    def classify(product_name: str, category: str = None) -> str:
        """
        Refine or assign category.
        """
        if category:
            return category
            
        name = product_name.lower()
        if any(w in name for w in ["lip", "blush", "foundation", "palette", "liner", "gloss"]):
            return "makeup"
        if any(w in name for w in ["hoodie", "jacket", "denim", "skirt", "blazer", "dress", "tote"]):
            return "fashion"
        if any(w in name for w in ["serum", "cleanser", "moisturizer", "spf", "toner"]):
            return "skincare"
        if any(w in name for w in ["sunglasses", "belt", "hair clip", "jewelry", "bag"]):
            return "accessories"
            
        return "fashion" # Default

# Singleton
trend_classifier = TrendClassifier()
