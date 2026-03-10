"""
Trend Pipeline — End-to-end orchestrator for the AI Discovery Engine.
Flow: Collect → Extract → Classify → Score → Enrich → Persist
"""
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.trends.trend_sources import (
    GoogleTrendsAdapter, PinterestAdapter, EcommerceAdapter
)
from app.services.trends.trendScorer import trend_scorer
from app.services.ai.entity_extractor import entity_extractor
from app.services.ai.trend_insight_generator import trend_insight_generator
from app.models.sql_models import TrendingProduct


class TrendPipeline:
    """
    Main orchestrator for the Trend Intelligence Engine.
    Orchestrates: Collect → Extract → Classify → Score → Enrich → Persist.
    """

    def __init__(self):
        self.adapters = [
            GoogleTrendsAdapter(),
            PinterestAdapter(),
            EcommerceAdapter()
        ]
        self.SCORE_THRESHOLD = 40  # Minimum score to persist

    async def _collect_signals(self) -> List[Dict]:
        """
        Step 1: Collect raw signals from all adapters.
        Aggregates by keyword, combining source information.
        """
        all_signals = []
        for adapter in self.adapters:
            signals = await adapter.fetch_signals()
            all_signals.extend(signals)

        # Aggregate by keyword
        aggregated = {}
        for signal in all_signals:
            kw = signal["keyword"].lower()
            if kw not in aggregated:
                aggregated[kw] = {
                    "keyword": kw,
                    "sources": [signal["source"]],
                    "signals": {
                        "search_growth": signal.get("growth_rate", 0),
                        "mention_count": signal.get("search_volume", 0),
                        "rank_signal": 0.0
                    }
                }
            else:
                aggregated[kw]["sources"].append(signal["source"])
                # Take the max growth for multi-source keywords
                aggregated[kw]["signals"]["search_growth"] = max(
                    aggregated[kw]["signals"]["search_growth"],
                    signal.get("growth_rate", 0)
                )
                # Sum mention counts
                aggregated[kw]["signals"]["mention_count"] += signal.get("search_volume", 0)
                # E-commerce rank signal
                if signal["source"] == "ecommerce_bestseller":
                    aggregated[kw]["signals"]["rank_signal"] = max(
                        aggregated[kw]["signals"]["rank_signal"],
                        signal.get("growth_rate", 0)
                    )

        return list(aggregated.values())

    def _extract_entities(self, phrase: str) -> List[Dict[str, str]]:
        """Step 2: Extract product entities from a raw trend phrase."""
        return entity_extractor.extract(phrase)

    def _classify(self, entity: Dict[str, str]) -> str:
        """Step 3: Classify/confirm the product category."""
        # The entity extractor already provides category
        return entity.get("category", "fashion")

    def _score(self, signals: Dict) -> Dict:
        """Step 4: Calculate trend score using weighted formula."""
        return trend_scorer.calculate_from_signals(signals)

    def _enrich(self, product_name: str, category: str) -> str:
        """Step 5: Generate AI insight text."""
        return trend_insight_generator.generate(product_name, category)

    def _generate_affiliate_link(self, product_name: str, category: str) -> str:
        """Generate affiliate links based on product/category."""
        import urllib.parse
        query = urllib.parse.quote_plus(product_name)

        if category in ["skincare", "makeup"]:
            return f"https://www.nykaa.com/search/result/?q={query}"
        elif category in ["fashion", "clothing"]:
            return f"https://www.myntra.com/{query}"
        elif category == "accessories":
            return f"https://www.ajio.com/search/?text={query}"
        else:
            return f"https://www.amazon.in/s?k={query}&tag=trendlyai-21"

    async def run_pipeline(self, db: AsyncSession) -> List[Dict]:
        """
        End-to-end pipeline execution:
        Collect → Extract → Classify → Score → Enrich → Persist
        """
        print("[COLLECT] Step 1: Collecting signals from all adapters...")
        aggregated_signals = await self._collect_signals()
        print(f"   [OK] Aggregated {len(aggregated_signals)} unique trend phrases")

        results = []

        for signal in aggregated_signals:
            phrase = signal["keyword"]

            # Step 2: Extract product entities
            entities = self._extract_entities(phrase)

            for entity in entities:
                product_name = entity["name"]

                # Step 3: Classify
                category = self._classify(entity)

                # Step 4: Score
                score_result = self._score(signal["signals"])
                score = score_result["trend_score"]

                # Filter low-scoring items
                if score < self.SCORE_THRESHOLD:
                    continue

                # Step 5: Enrich with AI insight
                insight = self._enrich(product_name, category)

                # Step 6: Prepare result
                results.append({
                    "product_name": product_name,
                    "category": category,
                    "trend_score": score,
                    "growth_metric": score_result["growth_metric"],
                    "ai_insight": insight,
                    "sources": list(set(signal["sources"])),
                    "image_url": f"https://source.unsplash.com/400x400/?{product_name.lower().replace(' ', ',')}",
                    "affiliate_link": self._generate_affiliate_link(product_name, category)
                })

        print(f"[AI] Step 2-5: Extracted & scored {len(results)} products (threshold >= {self.SCORE_THRESHOLD})")

        # Step 7: Persist to database (UPSERT pattern)
        print("[SAVE] Step 6: Persisting to database...")
        persisted_count = 0
        for res in results:
            # Check for existing product → update instead of duplicate
            stmt = select(TrendingProduct).where(
                TrendingProduct.product_name == res["product_name"]
            )
            existing_result = await db.execute(stmt)
            existing = existing_result.scalar_one_or_none()

            if existing:
                existing.trend_score = res["trend_score"]
                existing.growth_metric = res["growth_metric"]
                existing.ai_insight = res["ai_insight"]
                existing.sources = res["sources"]
                existing.affiliate_link = res["affiliate_link"]
                existing.image_url = res["image_url"]
                existing.created_at = datetime.utcnow()
            else:
                db_trending = TrendingProduct(
                    product_name=res["product_name"],
                    category=res["category"],
                    trend_score=res["trend_score"],
                    growth_metric=res["growth_metric"],
                    image_url=res["image_url"],
                    affiliate_link=res["affiliate_link"],
                    ai_insight=res["ai_insight"],
                    sources=res["sources"],
                    source_platform=", ".join(res["sources"])
                )
                db.add(db_trending)
                persisted_count += 1

        await db.commit()
        print(f"   [OK] Persisted {persisted_count} new items, updated {len(results) - persisted_count} existing")

        # Step 8: Cleanup expired trends (> 7 days)
        threshold = datetime.utcnow() - timedelta(days=7)
        cleanup_stmt = delete(TrendingProduct).where(
            TrendingProduct.created_at < threshold
        )
        cleanup_result = await db.execute(cleanup_stmt)
        if cleanup_result.rowcount > 0:
            await db.commit()
            print(f"[CLEANUP] Cleaned up {cleanup_result.rowcount} expired trends")

        return results


# Singleton
trend_pipeline = TrendPipeline()
