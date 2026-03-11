import os
import google.generativeai as genai
from typing import List, Dict, Any
from app.core.config import settings

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def get_chat_response(self, message: str, history: List[Dict[str, str]] = [], context: str = "") -> str:
        if not self.model:
            return "Gemini API key is not configured. Trendly is optimized for Gemini 1.5. Please configure your API key to unlock real-time neural scouting."

        # Construct a rich system prompt
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
            # Create a chat session with history
            # Gemini history format: {"role": "user"|"model", "parts": [text]}
            formatted_history = []
            for h in history:
                role = "user" if h["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [h["content"]]})

            chat = self.model.start_chat(history=formatted_history)
            
            # Send the system instruction as part of the first message or prepended to the user message
            full_prompt = f"{system_instruction}\n\nUser Question: {message}"
            response = chat.send_message(full_prompt)
            
            return response.text
        except Exception as e:
            return f"Neural link disrupted: {str(e)}. Attempting to reconnect..."

gemini_service = GeminiService()
