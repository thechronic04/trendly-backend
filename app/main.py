from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, discovery, assistant
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    from app.db.session import init_db
    try:
        await init_db()
    except Exception as e:
        print(f"Database init failed: {e}")
    yield

app = FastAPI(title="Trendly AI", lifespan=lifespan)

# Restore CORS Middleware for Frontend Accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Secure Auth"])
app.include_router(discovery.router, prefix="/api/discovery", tags=["Discovery Engine"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["AI Assistant"])

@app.get("/health")
async def health_check():
    return {"status": "online", "timestamp": settings.PROJECT_NAME}
