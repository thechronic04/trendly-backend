import re
from typing import List, Dict

class EntityExtractor:
    """
    Simulated AI/NLP service to identify product entities from trend signals.
    In a production scenario, this would call an LLM (OpenAI/Gemini) 
    or use spaCy/NLTK for Named Entity Recognition.
    """
    
    # Simple pattern mapping for mock extraction
    PATTERNS = {
        "makeup": ["lipstick", "lip oil", "blush", "highlighter", "foundation", "gloss", "mascara"],
        "fashion": ["hoodie", "jacket", "denim", "skirt", "blazer", "dress", "tote"],
        "skincare": ["serum", "cleanser", "moisturizer", "spf", "toner", "oil"],
        "accessories": ["sunglasses", "belt", "hair clip", "jewelry", "bag"]
    }

    @staticmethod
    def extract(text: str) -> List[Dict[str, str]]:
        """
        Identify products and categories from raw text.
        """
        extracted = []
        text_lower = text.lower()
        
        for category, keywords in EntityExtractor.PATTERNS.items():
            for kw in keywords:
                if kw in text_lower:
                    extracted.append({
                        "name": kw.title(),
                        "category": category
                    })
        
        # If no specific patterns match, try to infer or use the phrase as an entity
        if not extracted:
            # Fallback for generic phrases
            words = text.split()
            if words:
                extracted.append({
                    "name": text.title(),
                    "category": "fashion"  # Default
                })
                
        return extracted

# Singleton instance
entity_extractor = EntityExtractor()
