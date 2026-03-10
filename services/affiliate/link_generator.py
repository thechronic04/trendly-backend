import urllib.parse
import random

def generate_affiliate_link(product_name: str, category: str) -> str:
    """
    Generates an affiliate search URL for Indian e-commerce platforms based on product category.
    Supports: Nykaa, Myntra, Ajio, Amazon India, Plum Goodness, Mamaearth.
    """
    query = urllib.parse.quote_plus(product_name)
    product_lower = product_name.lower()

    # Pre-defined Tracking IDs (Replace with actual affiliate tags in production)
    AMAZON_IN_TAG = "trendlyai-21"
    
    # Logic for Skincare & Makeup
    if category in ["skincare", "makeup"]:
        if "plum" in product_lower:
            # Plum Goodness format
            return f"https://plumgoodness.com/search?q={query}&type=product"
        elif "mamaearth" in product_lower:
            # Mamaearth format
            return f"https://mamaearth.in/search?q={query}"
        else:
            # Default to Nykaa for beauty
            return f"https://www.nykaa.com/search/result/?q={query}"

    # Logic for Fashion & Accessories
    elif category in ["fashion", "clothing", "accessories"]:
        # Randomly distribute traffic between Myntra and Ajio
        choice = random.choice(["myntra", "ajio"])
        if choice == "myntra":
            return f"https://www.myntra.com/{query}"
        else:
            return f"https://www.ajio.com/search/?text={query}"

    # Default Fallback (Amazon India)
    else:
        return f"https://www.amazon.in/s?k={query}&tag={AMAZON_IN_TAG}"
