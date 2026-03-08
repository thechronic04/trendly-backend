import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.db.session import engine
from app.models.sql_models import Base

async def init_db():
    print("Initializing Trendly.Ai Persistent Storage (SQLite)...")
    async with engine.begin() as conn:
        # Create all tables defined in sql_models.py
        await conn.run_sync(Base.metadata.create_all)
    print("Checkmark Database tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
