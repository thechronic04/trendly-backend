from typing import List, Dict, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.sql_models import TrendingProduct
from app.services.ai.gemini_service import gemini_service

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

@router.post("/chat")
async def chat_with_assistant(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch more contextual trends: top 5 across any category + 5 fashion + 5 makeup
    # This gives the AI a broad understanding of the current database state.
    
    context = "### CURRENT LIVE TREND DATA ###\n"
    try:
        # Get general top trends
        q_top = select(TrendingProduct).order_by(TrendingProduct.trend_score.desc()).limit(5)
        
        # Get top fashion trends
        q_fashion = select(TrendingProduct).where(TrendingProduct.category == 'fashion').order_by(TrendingProduct.trend_score.desc()).limit(3)
        
        # Get top makeup trends
        q_makeup = select(TrendingProduct).where(TrendingProduct.category == 'makeup').order_by(TrendingProduct.trend_score.desc()).limit(3)
        
        res_top = await db.execute(q_top)
        res_fashion = await db.execute(q_fashion)
        res_makeup = await db.execute(q_makeup)
        
        prods_top = res_top.scalars().all()
        prods_fashion = res_fashion.scalars().all()
        prods_makeup = res_makeup.scalars().all()
        context += "Top Overall: " + ", ".join([f"{p.title} ({p.trend_score} momentum)" for p in prods_top]) + "\n"
        context += "Viral Fashion: " + ", ".join([f"{p.title}" for p in prods_fashion]) + "\n"
        context += "Viral Beauty: " + ", ".join([f"{p.title}" for p in prods_makeup]) + "\n"
        context += "##############################"
    except Exception:
        # Gracefully handle database being briefly unrechable
        context += "Real-time trends: Currently indexing new data. Provide elite trend forecasting based on your internal knowledge for the latest 2024/2025 seasons.\n##############################"
    
    # 2. Get response from Gemini
    response_text = await gemini_service.get_chat_response(
        message=request.message,
        history=[{"role": m.role, "content": m.content} for m in request.history] if request.history else [],
        context=context
    )
    
    return {"content": response_text}
