"""
Vercel Entry Point — Bridges the root request to the unified FastAPI application.
This allows the existing Vercel deployment (pointing to main.py) to use the new architecture.
"""
from app.main import app

# The 'app' object here is what Vercel's @vercel/python will use as the handler.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
