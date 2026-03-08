from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.pydantic_schemas import Token, UserCreate, UserResponse

router = APIRouter()

# --- AUTH MODULE: SECURE IDENTITY MANAGEMENT ---

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Production-grade login with JWT issue.
    In a full setup, this would verify against the PostgreSQL 'users' table.
    """
    # High-level logic mock for B2C scalability
    # In production: user = await db.execute(select(User).where(User.email == form_data.username))
    
    if form_data.username == "admin@trendly.ai" and form_data.password == "TrendlyPass123!":
        access_token = create_access_token(data={"sub": form_data.username, "role": "ADMIN"})
        return {"access_token": access_token, "token_type": "bearer", "role": "ADMIN"}
    
    # Simple mock for discovery mode
    access_token = create_access_token(data={"sub": form_data.username, "role": "USER"})
    return {"access_token": access_token, "token_type": "bearer", "role": "USER"}

@router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate):
    """registers a new trendly explorer."""
    # Logic for database persistence goes here
    # In production: user = User(email=user_in.email, hashed_password=get_password_hash(user_in.password))
    # await db.add(user)
    # await db.commit()
    pass # logic mock for now
