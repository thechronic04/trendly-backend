import asyncio
import sys
import os
from decimal import Decimal

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.sql_models import Product

async def seed():
    print("Seeding AI-Curated Product Data to Trendly.Ai Database...")
    
    products_data = [
        {
            "name": "Oversized Vintage Leather Moto Jacket",
            "brand": "AllSaints",
            "price": Decimal("24999.00"),
            "category": "clothing",
            "sub_category": "Outerwear",
            "trend_score": 95.8,
            "predicted_next_month": True,
            "affiliate_link": "https://www.allsaints.com/",
            "analytics_json": {
                "engagement_graph": [40, 55, 45, 70, 85, 95, 92],
                "social_mentions": "124.5K",
                "top_regions": ["New York", "London", "Tokyo"],
                "sentiment_score": 92
            }
        },
        {
            "name": "Oversized Streetwear Hoodie",
            "brand": "Bonkers",
            "price": Decimal("1599.00"),
            "category": "clothing",
            "sub_category": "Knitwear",
            "trend_score": 98.4,
            "predicted_next_month": True,
            "affiliate_link": "https://www.bonkerscorner.com/",
            "analytics_json": {
                "engagement_graph": [20, 35, 55, 80, 95, 98, 99],
                "social_mentions": "256.2K",
                "top_regions": ["Los Angeles", "Milan", "Shanghai"],
                "sentiment_score": 96
            }
        },
        {
            "name": "Soft Pinch Liquid Blush",
            "brand": "Nykaa",
            "price": Decimal("2499.00"),
            "category": "makeup",
            "sub_category": "Tops",
            "trend_score": 98.2,
            "predicted_next_month": True,
            "affiliate_link": "https://www.nykaa.com/",
            "analytics_json": {
                "engagement_graph": [40, 50, 60, 70, 80, 90, 98],
                "social_mentions": "182.4K",
                "top_regions": ["Los Angeles", "London", "Sydney"],
                "sentiment_score": 94
            }
        },
        {
            "name": "Asymmetric Satin Slip Midi",
            "brand": "Zara",
            "price": Decimal("3499.00"),
            "category": "clothing",
            "sub_category": "Tops",
            "trend_score": 89.5,
            "predicted_next_month": True,
            "affiliate_link": "https://www.zara.com/",
            "analytics_json": {
                "engagement_graph": [50, 45, 60, 55, 75, 85, 89],
                "social_mentions": "64.3K",
                "top_regions": ["Paris", "Tokyo", "Milan"],
                "sentiment_score": 91
            }
        }
    ]

    async with AsyncSessionLocal() as db:
        for p_data in products_data:
            # Check if product already exists
            from sqlalchemy import select
            q = select(Product).filter(Product.name == p_data["name"])
            result = await db.execute(q)
            if result.scalars().first():
                continue
                
            product = Product(**p_data)
            db.add(product)
        
        await db.commit()
    
    print("Done: Database seeded with high-fidelity production data.")

if __name__ == "__main__":
    asyncio.run(seed())
