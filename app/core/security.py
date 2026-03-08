import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Union, Any

# --- JWT & Security Configuration ---

# Use high-entropy keys in production via environment variables.
JWT_SECRET = os.getenv("JWT_SECRET", "trendly-ai-super-secret-key-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Initialize Bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 schema for dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --- 1. AUTHENTICATION (USER SIGNUP / LOGIN) ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure Bcrypt hash of a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token with user metadata."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# --- 2. AUTHORIZATION (RBAC) ---

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodes the JWT and returns the current user.
    In production, this would fetch from the PostgreSQL 'users' table.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
        return {"email": email, "role": role}
    except Exception:
        raise credentials_exception

def check_role(required_role: str):
    """
    Decorator dependency for Role-Based Access Control (RBAC).
    Usage: Depends(check_role('ADMIN'))
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role and current_user["role"] != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role."
            )
        return current_user
    return role_checker


# --- 3. SECURITY PROTECTIONS ---

# Example Rate Limiting Implementation logic (would use Redis in production)
# In code: from fastapi_limiter import FastAPILimiter
# @app.post("/api/v1/tracker/event", dependencies=[Depends(RateLimiter(times=5, seconds=1))])
