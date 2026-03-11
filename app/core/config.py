import os
from pydantic_settings import BaseSettings
from typing import List, Optional

# --- SCALABILITY INFRASTRUCTURE: CLOUD CONFIGURATION ---

class Settings(BaseSettings):
    """
    Main Backend Configuration using Environment Variables.
    Enforces 'Cloud-Native/12-Factor' principle.
    """
    # System Info
    PROJECT_NAME: str = "Trendly.Ai Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "trendly-ai-prod-key-7728786271")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALLOWED_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "https://trendly.ai",
        "https://trendly-frontend-rwu8.vercel.app",
        "https://trendly-frontend-rwu8-thechronic04s-projects.vercel.app",
        "http://localhost:5173"
    ]    

    # Relational Database (SQLite for local, switch to PostgreSQL for Production)
    # Automatically converts postgres:// to postgresql+asyncpg:// for cloud compatibility
    _raw_db_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./trendly.db")

    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self._raw_db_url.startswith("postgres://"):
            return self._raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self._raw_db_url.startswith("postgresql://"):
            return self._raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self._raw_db_url
    
    # Event Database (MongoDB)
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    
    # Cache & Worker (Redis)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    
    # AI Engine Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    RE_TRAINING_INTERVAL_DAYS: int = 7
    ML_MODEL_PATH: str = "/app/ml/models/recommender.joblib"
    
    # Enterprise-Level Security Features
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_IP_PROTECTION: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"

# Instantiate global settings
settings = Settings()
