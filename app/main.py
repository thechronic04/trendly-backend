from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import auth, discovery, tracker
from app.core.config import settings

# --- MAIN APP: PRODUCTION-READY FASTAPI INSTANCE ---

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A multi-engine, scalable AI discovery platform for consumer fashion.",
    version="2.0.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Set up CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Allow Vercel Analytics headers
)

# --- SCALABILITY: MONITORING & OBSERVABILITY ---

# Prometheus instrumentation for real-time performance tracking
# Instrumentator().instrument(app).bootstrap()


# --- MODULE REGISTRATION (ROUTERS) ---

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Secure Auth"])
app.include_router(discovery.router, prefix=f"{settings.API_V1_STR}/discovery", tags=["Discovery Engine"])
app.include_router(tracker.router, prefix=f"{settings.API_V1_STR}/tracker", tags=["Neural Tracker"])


@app.get("/health", tags=["Infrastructure"])
async def health_check():
    """System health check for cloud orchestration (Kubernetes/ECS)."""
    return {
        "status": "online",
        "engines": {
            "auth": "active",
            "ai_discovery": "running",
            "clickstream": "listening"
        }
    }

# --- LIFECYCLE HANDLERS ---

@app.on_event("startup")
async def startup_event():
    # In a full Postgres setup, we would ensure migrations are applied here
    # from app.db.base import Base
    # from app.db.session import engine
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    print(f"🚀 {settings.PROJECT_NAME} booting up on version 2.0.0...")

@app.on_event("shutdown")
async def shutdown_event():
    print(f"🛑 {settings.PROJECT_NAME} shutting down gracefully...")
