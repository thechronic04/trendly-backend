import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.models.sql_models import TrendingProduct
from app.services.trends.trendCollector import trend_collector
from app.services.ai.productExtractor import product_extractor
from app.services.trends.trendScorer import trend_scorer
from app.services.trends.productMatcher import product_matcher
from sqlalchemy.orm import Session
import asyncio

class TrendUpdateJob:
    \"\"\"
    SECTION 7 — TREND UPDATE JOB
    Scheduled job to run the pipeline
    \"\"\"
    
    @staticmethod
    async def run_pipeline():
        print("Starting Trend Update Pipeline...")
        
        # 1. Collect trend phrases
        trend_phrases = trend_collector.collect_trends()
        print(f"Collected {len(trend_phrases)} trend phrases: {trend_phrases}")
        
        async with AsyncSessionLocal() as db:
            for phrase in trend_phrases:
                # 2. Extract product entities using AI
                products = product_extractor.extract_products(phrase)
                
                for product_name in products:
                    # 3. Score products using trendScorer
                    scored_data = trend_scorer.calculateTrendScore(product_name)
                    
                    # 4. Match them to ecommerce listings
                    matched_data = product_matcher.match_product(product_name)
                    
                    # 5. Store results in trending_products
                    insight = f"AI Insight: {product_name} is surging based on recent {phrase} spikes."
                    
                    new_trend = TrendingProduct(
                        product_name=matched_data["product_name"],
                        category=matched_data["category"],
                        trend_score=scored_data["trendScore"],
                        growth_metric=scored_data["growth_metric"],
                        image_url=matched_data["image_url"],
                        affiliate_link=matched_data["affiliate_link"],
                        source_platform=matched_data["source_platform"],
                        ai_insight=insight
                    )
                    
                    db.add(new_trend)
            
            await db.commit()
            print("Trend Pipeline Sync Complete!")

if __name__ == "__main__":
    # Simulate cron execution
    asyncio.run(TrendUpdateJob.run_pipeline())
