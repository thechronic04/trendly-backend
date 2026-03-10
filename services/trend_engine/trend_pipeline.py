from typing import List, Dict
from .trend_collector import trend_collector
from .trend_scorer import trend_scorer
from .trend_classifier import trend_classifier
from ..ai.entity_extractor import entity_extractor
from ..ai.trend_insight_generator import trend_insight_generator
from ..affiliate.link_generator import generate_affiliate_link
import models

class TrendPipeline:
    """
    Main orchestrator for the Trend Intelligence Engine.
    """
    async def run_pipeline(self, db_session):
        """
        End-to-end execution of the discovery process.
        """
        # 1. Collect signals
        aggregated_signals = await trend_collector.collect_all()
        
        results = []
        for signal in aggregated_signals:
            phrase = signal["keyword"]
            
            # 2. Extract Entities via AI
            entities = entity_extractor.extract(phrase)
            
            for entity in entities:
                product_name = entity["name"]
                
                # 3. Classify Product
                category = trend_classifier.classify(product_name, entity["category"])
                
                # 4. Calculate Trend Score
                score = trend_scorer.calculate(
                    signal["signals"]["search_growth"],
                    signal["signals"]["mention_count"],
                    signal["signals"]["rank_signal"]
                )
                
                # 5. Filter (Threshold >= 60)
                if score < 60:
                    continue
                
                # 6. Enrich with AI Insights
                insight = trend_insight_generator.generate(product_name, category)
                
                # 7. Prepare for persistence
                results.append({
                    "product_name": product_name,
                    "category": category,
                    "trend_score": score,
                    "growth_metric": signal["signals"]["search_growth"] * 100,
                    "ai_insight": insight,
                    "sources": signal["sources"],
                    "image_url": f"https://api.dicebear.com/7.x/identicon/svg?seed={product_name}", # placeholder
                    "affiliate_link": generate_affiliate_link(product_name, category)
                })
        
        # 8. Persist to Database
        for res in results:
            # Check for existing product to avoid duplicates (UPSERT)
            existing = db_session.query(models.TrendingProduct).filter(
                models.TrendingProduct.product_name == res["product_name"]
            ).first()
            
            if existing:
                existing.trend_score = res["trend_score"]
                existing.ai_insight = res["ai_insight"]
                existing.sources = res["sources"]
                existing.affiliate_link = res["affiliate_link"]
            else:
                db_trending = models.TrendingProduct(**res)
                db_session.add(db_trending)
        
        db_session.commit()
        return results

# Singleton
trend_pipeline = TrendPipeline()
