import random
from typing import List, Dict
from .trend_collector import trend_collector
from ..ai.trend_insight_generator import trend_insight_generator
from ..affiliate.link_generator import get_affiliate_links
from app.models.sql_models import TrendingProduct

class TrendPipeline:
    """
    Main orchestrator for the Trend Intelligence Engine.
    """
    async def run_pipeline(self, db_session):
        """
        End-to-end execution of the discovery process for trending products.
        """
        # 1. Collect Trending Products
        products = await trend_collector.collect_products()
        
        results = []
        for p in products:
            # 2. Enrich with AI Insights
            insight = trend_insight_generator.generate(p["title"], p["category"])
            
            # 3. Generate Multiple Affiliate Links
            # Note: asin and flipkart_id would normally come from the source data
            affiliate_links = get_affiliate_links(
                p["title"], 
                p["category"], 
                asin=p.get("asin"), 
                flipkart_id=p.get("flipkart_id")
            )
            
            # 4. Normalize and prepare for persistence
            product_data = {
                "title": p["title"],
                "category": p["category"],
                "brand": p.get("brand", ""),
                "description": p.get("description", ""),
                "price": p.get("price", 0.0),
                "image_url": p.get("image_url", ""),
                "affiliate_links": affiliate_links,
                "trend_score": random.uniform(70, 98), # Products in this feed are already trending
                "growth_metric": random.uniform(15, 45),
                "ai_insight": insight,
                "sources": [p.get("source", "aggregator")]
            }
            results.append(product_data)
        
        # 5. Persist to Database (UPSERT by title)
        from sqlalchemy import select
        for res in results:
            stmt = select(TrendingProduct).where(TrendingProduct.title == res["title"])
            result = await db_session.execute(stmt)
            existing = result.scalars().first()
            
            if existing:
                existing.trend_score = res["trend_score"]
                existing.ai_insight = res["ai_insight"]
                existing.affiliate_links = res["affiliate_links"]
                existing.price = res["price"]
                existing.description = res["description"]
            else:
                db_trending = TrendingProduct(**res)
                db_session.add(db_trending)
        
        await db_session.commit()
        return results

# Singleton
trend_pipeline = TrendPipeline()
