import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sql_models import User
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.pydantic_schemas import Token, UserCreate, UserResponse

router = APIRouter()

# --- AUTH MODULE: SECURE IDENTITY MANAGEMENT ---

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and returns a JWT access token.
    """
    # 1. Fetch user from database
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # 2. Verify identity
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 3. Generate token
    # We include the role in the token for easy RBAC on the frontend (secondary check)
    access_token = create_access_token(data={"sub": user.email, "role": "USER"})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": "USER" # Defaulting to USER for now; can be expanded for ADMIN
    }

@router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registers a new trendly explorer."""
    # 1. Check if user already exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )

    # 2. Create new user record
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        role_id=3, # Default: USER
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user
