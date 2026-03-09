from typing import List

class ProductExtractor:
    \"\"\"
    SECTION 3 — AI PRODUCT EXTRACTION
    Converts raw trend phrases into specific product categories/entities.
    \"\"\"
    
    # Mocking an AI model inference
    AI_KNOWLEDGE_BASE = {
        "clean girl makeup": ["lip gloss", "cream blush", "highlighter"],
        "oversized hoodie": ["streetwear hoodie", "fleece zip-up", "graphic hoodie"],
        "y2k cargo pants": ["parachute pants", "low-rise cargos", "denim cargo"],
        "lip oil": ["tinted lip oil", "plumping lip gloss"],
        "chunky sneakers": ["platform sneakers", "dad shoes"],
        "peptide serum": ["hyaluronic acid serum", "peptide moisturizer"]
    }
    
    @staticmethod
    def extract_products(trend_phrase: str) -> List[str]:
        # Returns mapped products or default generalized product
        return ProductExtractor.AI_KNOWLEDGE_BASE.get(trend_phrase.lower(), [f"{trend_phrase} style product"])

product_extractor = ProductExtractor()
