from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, discovery, assistant
from app.core.config import settings

app = FastAPI(title="Trendly AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from app.db.session import init_db
    await init_db()

app.include_router(auth.router, prefix="/api/auth", tags=["Secure Auth"])
app.include_router(discovery.router, prefix="/api/discovery", tags=["Discovery Engine"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["AI Assistant"])

@app.get("/health")
async def health_check():
    return {"status": "online"}
