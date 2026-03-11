import asyncio
import os
import sys
import httpx
from datetime import datetime

# Add the backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app.db.session import AsyncSessionLocal, engine
from app.models.sql_models import Base
from services.trend_engine.trend_pipeline import trend_pipeline

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def daily_update():
    print(f"[{datetime.now().isoformat()}] Initializing database...")
    await init_db()
    print(f"[{datetime.now().isoformat()}] Starting daily trend update...")
    
    async with AsyncSessionLocal() as db:
        try:
            results = await trend_pipeline.run_pipeline(db)
            print(f"Successfully processed {len(results)} trending products.")
            
            # Optional: Trigger site rebuild if on Vercel/Netlify
            webhook = os.getenv("BUILD_WEBHOOK_URL")
            if webhook:
                print("Triggering site rebuild...")
                async with httpx.AsyncClient() as client:
                    await client.post(webhook)
                
        except Exception as e:
            print(f"Error during daily update: {e}")
            await db.rollback()
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(daily_update())
