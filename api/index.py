import os, random, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

SUPABASE_URL = "https://yzpodrfyssnmxbqzeuwk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6cG9kcmZ5c3NubXhicXpldXdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5NjU5OTMsImV4cCI6MjA4ODU0MTk5M30.2fIlXmAK4SiwPfLe8kBQrHyLvAq5lDoop42l-HXKWyM"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def query_supabase(table, filters=None, order=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    if filters:
        for key, value in filters.items():
            url += f"&{key}=eq.{value}"
    if order:
        url += f"&order={order}"
    with httpx.Client() as client:
        resp = client.get(url, headers=HEADERS)
        return resp.json()

app = FastAPI(title="Trendly AI API", version="2.0.0")

allowed_origins = [
    "https://trendly-frontend-rwu8.vercel.app",
    "https://trendly-frontend.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "Trendly AI API v2 is live! ✅"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/products")
def get_all_products():
    products = query_supabase("products", order="trend_score.desc")
    return products

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    url = f"{SUPABASE_URL}/rest/v1/products?id=eq.{product_id}&select=*"
    with httpx.Client() as client:
        resp = client.get(url, headers=HEADERS)
        data = resp.json()
        return data[0] if data else {"error": "Not found"}

@app.get("/api/products/category/{category}")
def get_by_category(category: str):
    products = query_supabase("products", {"category": category}, order="trend_score.desc")
    return products

@app.get("/api/trends")
def get_trending():
    url = f"{SUPABASE_URL}/rest/v1/products?is_trending_now=eq.true&select=*&order=trend_score.desc"
    with httpx.Client() as client:
        resp = client.get(url, headers=HEADERS)
        return {"trending": resp.json()}

@app.get("/api/predictions")
def get_predictions():
    url = f"{SUPABASE_URL}/rest/v1/products?predicted_next_month=eq.true&select=*&order=trend_score.desc"
    with httpx.Client() as client:
        resp = client.get(url, headers=HEADERS)
        return {"predicted_next_month": resp.json()}

@app.get("/api/ai/analyze-trend")
def analyze_trend(keyword: str):
    score = round(random.uniform(50.0, 99.9), 1)
    momentums = ["Rising Fast", "Peaking", "Declining", "Emerging", "Viral"]
    return {
        "keyword": keyword,
        "ai_trend_score": score,
        "momentum": random.choice(momentums),
        "recommendation": "Promote heavily" if score > 85 else "Monitor closely",
        "predicted_surge": f"+{random.randint(10, 90)}% in next 7 days"
    }

# --- NEW: AI Trending Products Endpoints ---

@app.get("/api/trending-products")
def get_all_trending_products():
    products = query_supabase("trending_products", order="trend_score.desc")
    if isinstance(products, list):
        return products
    return []

@app.get("/api/trending-products/{category}")
def get_category_trending_products(category: str):
    products = query_supabase("trending_products", {"category": category}, order="trend_score.desc")
    if isinstance(products, list):
        return products
    return []
