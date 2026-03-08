import os
import random
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- SUPABASE REST API CONFIG ---
SUPABASE_URL = "https://yzpodrfyssnmxbqzeuwk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6cG9kcmZ5c3NubXhicXpldXdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5NjU5OTMsImV4cCI6MjA4ODU0MTk5M30.2fIlXmAK4SiwPfLe8kBQrHyLvAq5lDoop42l-HXKWyM"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def query_supabase(table: str, filters: dict = None):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    if filters:
        for key, value in filters.items():
            url += f"&{key}=eq.{value}"
    with httpx.Client() as client:
        response = client.get(url, headers=HEADERS)
        return response.json()

app = FastAPI(title="Trendly AI API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "")
allowed_origins = [FRONTEND_URL] if FRONTEND_URL else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Trendly AI API is live! ✅"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/products")
def get_all_products():
    return query_supabase("products")

@app.get("/api/trends")
def get_trending():
    products = query_supabase("products", {"is_trending_now": "true"})
    return {"trending": products}

@app.get("/api/predictions")
def get_predictions():
    products = query_supabase("products", {"predicted_next_month": "true"})
    return {"predicted_next_month": products}

@app.get("/api/ai/analyze-trend")
def analyze_trend(keyword: str):
    score = random.uniform(50.0, 99.9)
    momentum = random.choice(["Rising Fast", "Peaking", "Declining", "Emerging"])
    return {
        "keyword": keyword,
        "ai_trend_score": round(score, 1),
        "momentum": momentum,
        "recommendation": "Promote heavily" if score > 85 else "Monitor",
    }
