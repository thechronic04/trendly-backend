import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from google import genai
from app.core.config import settings

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            # We use the async client to prevent blocking the FastAPI event loop.
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-1.5-flash'
        else:
            self.client = None

    async def get_chat_response(self, message: str, history: List[Dict[str, str]] = [], context: str = "") -> str:
        if not self.client:
            return "Gemini API key is not configured. Trendly is optimized for Gemini 1.5. Please configure your API key to unlock real-time neural scouting."

        system_instruction = f"""
        You are 'Trendly's Neural Assistant', an elite AI trend scout. 
        Your personality: 
        - Analytical, forward-looking, and slightly exclusive. 
        - You speak like a high-end trend forecaster (WGSN style).
        - You use terms like 'saturation point', 'alpha users', 'velocity', 'engagement spikes', and 'cultural zeitgeist'.
        
        Your Mission:
        - Help users identify what's truly viral vs what's fading.
        - Give data-backed advice using the CURRENT LIVE TREND DATA provided.
        - If a user asks about a city (Milan, Paris, Tokyo), connect it to the current trends if possible.
        
        {context}
        """

        try:
            formatted_history = []
            for h in history:
                role = "user" if h["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [{"text": h["content"]}]})

            # For safety in async context, run in thread pool if needed, 
            # but usually for a single call it's fine unless high concurrency is needed.
            chat = self.client.aio.chats.create(
                model=self.model_id,
                history=formatted_history,
                config={'system_instruction': system_instruction}
            )
            
            response = await chat.send_message(message)
            return response.text
            
        except Exception as e:
            return f"Neural link disrupted: {str(e)}. Attempting to reconnect..."

gemini_service = GeminiService()
