"""
run_trend_engine.py - Standalone script to execute the AI Trend Discovery Pipeline.
This initializes the database, runs the full pipeline, and reports results.

Usage:
    cd backend
    python scripts/run_trend_engine.py
"""
import asyncio
import sys
import os
import io

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add backend root to sys.path for app module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine, AsyncSessionLocal
from app.models.sql_models import Base, TrendingProduct
from app.services.trends.trend_pipeline import trend_pipeline
from sqlalchemy import select, func


async def run_discovery():
    """Execute the full Trend Intelligence Engine discovery pipeline."""
    print("=" * 60)
    print("[ROCKET] Trendly.Ai -- Trend Intelligence Engine")
    print("=" * 60)
    print()

    # 1. Initialize database tables
    print("[WRENCH] Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("   [OK] Database tables ready\n")

    # 2. Run the pipeline
    async with AsyncSessionLocal() as db:
        try:
            results = await trend_pipeline.run_pipeline(db)
            print(f"\n[DONE] Discovery complete! Discovered {len(results)} trending items.\n")

            # 3. Report results
            if results:
                print("=" * 60)
                print("[CHART] DISCOVERY RESULTS")
                print("=" * 60)
                print(f"{'Product':<35} {'Category':<15} {'Score':<8} {'Growth':<10}")
                print("-" * 68)
                for r in sorted(results, key=lambda x: x["trend_score"], reverse=True):
                    print(f"{r['product_name']:<35} {r['category']:<15} {r['trend_score']:<8} {r['growth_metric']:<10}")
                print()

            # 4. Verify database population
            count_result = await db.execute(select(func.count(TrendingProduct.id)))
            total_count = count_result.scalar()
            print(f"[DB] Total items in trending_products table: {total_count}")

            # 5. Show top 5 from database
            top_result = await db.execute(
                select(TrendingProduct)
                .order_by(TrendingProduct.trend_score.desc())
                .limit(5)
            )
            top_products = top_result.scalars().all()
            if top_products:
                print("\n[TROPHY] TOP 5 FROM DATABASE:")
                print(f"{'ID':<6} {'Product':<35} {'Score':<8} {'Sources'}")
                print("-" * 70)
                for p in top_products:
                    sources = ", ".join(p.sources) if p.sources else "N/A"
                    print(f"{p.id:<6} {p.product_name:<35} {p.trend_score:<8} {sources}")

        except Exception as e:
            print(f"\n[ERROR] Error in Trend Engine: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("[OK] Pipeline execution complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_discovery())
