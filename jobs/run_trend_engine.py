import asyncio
import sys
import os

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import models
from services.trend_engine.trend_pipeline import trend_pipeline

async def run_discovery():
    print("Starting Trend Intelligence Engine Discovery...")
    db = models.SessionLocal()
    try:
        # 1. Initialize DB tables if they don't exist
        models.init_db()
        
        # 2. Run Pipeline
        results = await trend_pipeline.run_pipeline(db)
        print(f"Discovery complete. Discovered {len(results)} trending items.")
        
        # 3. Cleanup old trends (older than 7 days)
        from datetime import datetime, timedelta
        threshold = datetime.utcnow() - timedelta(days=7)
        deleted = db.query(models.TrendingProduct).filter(models.TrendingProduct.created_at < threshold).delete()
        if deleted:
            print(f"Removed {deleted} expired trends.")
            db.commit()
            
    except Exception as e:
        print(f"Error in Trend Engine: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_discovery())
