import os, random, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

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

# Speed Insights middleware
class SpeedInsightsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        if response.status_code == 200 and "text/html" in response.headers.get("content-type", ""):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            try:
                html = body.decode("utf-8")
                script = '''
<script>
  window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
'''
                if "</body>" in html:
                    html = html.replace("</body>", f"{script}</body>")
                elif "</html>" in html:
                    html = html.replace("</html>", f"{script}</html>")
                
                return Response(
                    content=html.encode("utf-8"),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            except (UnicodeDecodeError, AttributeError):
                pass
        
        return response

app = FastAPI(title="Trendly AI API", version="2.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "")
allowed_origins = [FRONTEND_URL, "https://trendly-frontend.vercel.app"] if FRONTEND_URL else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add Speed Insights middleware
app.add_middleware(SpeedInsightsMiddleware)

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
