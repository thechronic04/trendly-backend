"""
Vercel Speed Insights integration for FastAPI.

This module provides functionality to inject Vercel Speed Insights tracking
into HTML responses, particularly for FastAPI's auto-generated documentation pages.
"""

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable


# Speed Insights script template
SPEED_INSIGHTS_SCRIPT = """
<script>
  window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
"""


class SpeedInsightsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject Vercel Speed Insights script into HTML responses.
    
    This middleware automatically adds the Speed Insights tracking script
    to any HTML response before the closing </body> tag.
    """
    
    async def dispatch(self, request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Only inject into HTML responses
        if (
            response.status_code == 200
            and "text/html" in response.headers.get("content-type", "")
        ):
            # Read the response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Decode and inject the script
            try:
                html = body.decode("utf-8")
                
                # Inject before closing </body> tag if it exists
                if "</body>" in html:
                    html = html.replace("</body>", f"{SPEED_INSIGHTS_SCRIPT}</body>")
                # Otherwise inject before closing </html> tag
                elif "</html>" in html:
                    html = html.replace("</html>", f"{SPEED_INSIGHTS_SCRIPT}</html>")
                
                # Create new response with modified body
                return Response(
                    content=html.encode("utf-8"),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            except (UnicodeDecodeError, AttributeError):
                # If we can't decode or modify, return original response
                pass
        
        return response


def get_speed_insights_html() -> str:
    """
    Get the Speed Insights HTML script tags.
    
    Returns:
        str: The HTML script tags for Speed Insights
    """
    return SPEED_INSIGHTS_SCRIPT


def setup_speed_insights(app: FastAPI, enable: bool = True) -> None:
    """
    Configure Speed Insights for a FastAPI application.
    
    This function customizes the Swagger UI and ReDoc HTML to include
    the Speed Insights tracking script.
    
    Args:
        app: The FastAPI application instance
        enable: Whether to enable Speed Insights (default: True)
    """
    if not enable:
        return
    
    # Add middleware to inject Speed Insights into HTML responses
    app.add_middleware(SpeedInsightsMiddleware)
    
    # Custom Swagger UI HTML
    def custom_swagger_ui_html():
        from fastapi.openapi.docs import get_swagger_ui_html
        
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )
    
    # Custom ReDoc HTML
    def custom_redoc_html():
        from fastapi.openapi.docs import get_redoc_html
        
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        )
    
    # Note: The middleware will automatically inject Speed Insights into these HTML responses
    print("✅ Vercel Speed Insights enabled for FastAPI application")
