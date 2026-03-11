import os
import httpx
import asyncio
from typing import List, Dict

class ProductSourceAdapter:
    """Base adapter class for trending products."""
    async def fetch_products(self) -> List[Dict]:
        raise NotImplementedError

class ShopStyleAdapter(ProductSourceAdapter):
    """Adapter for ShopStyle (Fashion)."""
    async def fetch_products(self) -> List[Dict]:
        api_key = os.getenv("SHOPSTYLE_API_KEY")
        if not api_key:
            # Fallback to simulated trending fashion
            return [{
                "id": "ss1", "title": "Oversized Cashmere Sweater", "brand": "Everlane",
                "image_url": "https://picsum.photos/seed/fashion1/400/600", "price": 120.0,
                "description": "Luxurious oversized sweater.", "category": "fashion"
            }]
        
        url = "https://api.shopstyle.com/api/v2/products"
        params = {"cat": "women", "sort": "trending", "limit": 100, "api_key": api_key}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            products = resp.json().get("products", [])
        return [{
            "id": str(p["id"]), "title": p["name"], "brand": p.get("brand", {}).get("name", ""),
            "image_url": p["image"]["sizes"]["Large"]["url"], "price": p["price"],
            "description": p.get("description", ""), "category": "fashion"
        } for p in products]

class SephoraAdapter(ProductSourceAdapter):
    """Adapter for Sephora (Makeup)."""
    async def fetch_products(self) -> List[Dict]:
        # Sephora API is often restricted, usually requires scraping or partner access
        return [{
            "id": "sep1", "title": "Gloss Bomb Universal Lip Luminizer", "brand": "Fenty Beauty",
            "image_url": "https://picsum.photos/seed/makeup1/400/600", "price": 21.0,
            "description": "The ultimate gotta-have-it lip gloss.", "category": "makeup"
        }]

class EtsyAdapter(ProductSourceAdapter):
    """Adapter for Etsy (Accessories)."""
    async def fetch_products(self) -> List[Dict]:
        api_key = os.getenv("ETSY_API_KEY")
        if not api_key:
            return [{
                "id": "etsy1", "title": "Personalized Gold Name Necklace", "brand": "CustomJewels",
                "image_url": "https://picsum.photos/seed/acc1/400/600", "price": 45.0,
                "description": "Handmade personalized necklace.", "category": "accessories"
            }]
        # Etsy API logic here...
        return []

class AmazonBeautyAdapter(ProductSourceAdapter):
    """Adapter for Amazon Beauty (Skincare)."""
    async def fetch_products(self) -> List[Dict]:
        # PA-API logic or scraping
        return [{
            "id": "amz1", "title": "CeraVe Hydrating Facial Cleanser", "brand": "CeraVe",
            "image_url": "https://picsum.photos/seed/skin1/400/600", "price": 15.99,
            "description": "Daily face wash with hyaluronic acid.", "category": "skincare"
        }]
