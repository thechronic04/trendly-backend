"""
AI Entity Extractor — NLP-based product entity extraction with LRU caching.
Isolates product names from raw trend phrases.
In production, this would call an LLM (GPT/Gemini) or use spaCy NER.
"""
import re
from typing import List, Dict
from functools import lru_cache


class EntityExtractor:
    """
    AI/NLP service to identify product entities from raw trend signals.
    Uses pattern matching with an extensible knowledge base, plus LRU caching
    to optimize repeated lookups.
    """

    # Product keyword patterns organized by category
    PATTERNS: Dict[str, List[str]] = {
        "makeup": [
            "lipstick", "lip oil", "lip gloss", "blush", "highlighter",
            "foundation", "gloss", "mascara", "concealer", "palette",
            "liner", "eyeshadow", "primer", "bronzer", "setting spray"
        ],
        "fashion": [
            "hoodie", "jacket", "denim", "skirt", "blazer", "dress",
            "tote", "cargo pants", "sneakers", "shorts", "shirt",
            "kurta", "lehenga", "saree", "co-ord"
        ],
        "skincare": [
            "serum", "cleanser", "moisturizer", "spf", "toner", "oil",
            "sunscreen", "retinol", "niacinamide", "hyaluronic",
            "peptide", "exfoliator", "face mask"
        ],
        "accessories": [
            "sunglasses", "belt", "hair clip", "jewelry", "bag",
            "watch", "scarf", "hat", "earring", "bracelet", "claw clip"
        ]
    }

    # Extended AI knowledge base — maps trend phrases to concrete products
    AI_KNOWLEDGE_BASE: Dict[str, List[Dict[str, str]]] = {
        "clean girl makeup": [
            {"name": "Cream Blush", "category": "makeup"},
            {"name": "Lip Gloss", "category": "makeup"},
            {"name": "Highlighter Stick", "category": "makeup"}
        ],
        "oversized hoodie": [
            {"name": "Streetwear Hoodie", "category": "fashion"},
            {"name": "Fleece Zip-Up", "category": "fashion"}
        ],
        "lip oil": [
            {"name": "Tinted Lip Oil", "category": "makeup"},
            {"name": "Cherry Glow Lip Oil", "category": "makeup"}
        ],
        "baggy denim": [
            {"name": "Wide Leg Jeans", "category": "fashion"},
            {"name": "Baggy Cargo Jeans", "category": "fashion"}
        ],
        "niacinamide serum": [
            {"name": "Niacinamide Serum", "category": "skincare"},
            {"name": "Pore-Minimizing Serum", "category": "skincare"}
        ],
        "vintage leather jacket": [
            {"name": "Vintage Leather Moto Jacket", "category": "fashion"}
        ],
        "coquette aesthetic": [
            {"name": "Ribbon Hair Clip", "category": "accessories"},
            {"name": "Lace Trim Dress", "category": "fashion"}
        ],
        "balletcore": [
            {"name": "Ballet Flats", "category": "fashion"},
            {"name": "Wrap Cardigan", "category": "fashion"}
        ],
        "strawberry makeup": [
            {"name": "Strawberry Blush", "category": "makeup"},
            {"name": "Berry Lip Tint", "category": "makeup"}
        ],
        "quiet luxury": [
            {"name": "Cashmere Knit Sweater", "category": "fashion"},
            {"name": "Minimalist Leather Bag", "category": "accessories"}
        ],
        "matte lipstick": [
            {"name": "Matte Lipstick", "category": "makeup"}
        ],
        "puffy tote bag": [
            {"name": "Puffy Tote Bag", "category": "accessories"}
        ],
        "claw clip": [
            {"name": "Claw Clip", "category": "accessories"}
        ],
        "hydrocolloid patches": [
            {"name": "Hydrocolloid Acne Patches", "category": "skincare"}
        ]
    }

    @staticmethod
    @lru_cache(maxsize=256)
    def _extract_cached(text: str) -> tuple:
        """
        Internal cached extraction — returns a tuple of (name, category) pairs.
        Uses tuple for hashability with lru_cache.
        """
        text_lower = text.lower().strip()

        # 1. Check the AI knowledge base first (exact/fuzzy phrase match)
        if text_lower in EntityExtractor.AI_KNOWLEDGE_BASE:
            results = EntityExtractor.AI_KNOWLEDGE_BASE[text_lower]
            return tuple((r["name"], r["category"]) for r in results)

        # 2. Fallback: pattern-matching against keyword lists
        extracted = []
        for category, keywords in EntityExtractor.PATTERNS.items():
            for kw in keywords:
                if kw in text_lower:
                    extracted.append((kw.title(), category))

        # 3. Fallback: use the phrase itself as an entity
        if not extracted:
            # Infer category from common terms
            inferred = "fashion"  # Default
            for category, keywords in EntityExtractor.PATTERNS.items():
                if any(kw in text_lower for kw in keywords):
                    inferred = category
                    break
            extracted.append((text.strip().title(), inferred))

        return tuple(extracted)

    @staticmethod
    def extract(text: str) -> List[Dict[str, str]]:
        """
        Public API: Extract product entities from a raw trend phrase.
        Returns list of {"name": ..., "category": ...} dicts.
        Results are cached via LRU for performance.
        """
        cached = EntityExtractor._extract_cached(text)
        return [{"name": name, "category": cat} for name, cat in cached]

    @staticmethod
    def cache_info():
        """Returns cache statistics for monitoring."""
        return EntityExtractor._extract_cached.cache_info()

    @staticmethod
    def clear_cache():
        """Clear the extraction cache."""
        EntityExtractor._extract_cached.cache_clear()


# Singleton instance
entity_extractor = EntityExtractor()
