import random

class ProductMatcher:
    \"\"\"
    SECTION 5 — PRODUCT MATCHING
    Matches abstract product entities to real ecommerce database links.
    \"\"\"
    
    # Mocking external API responses (e.g Amazon/Shopify lookup)
    AFFILIATE_RESOURCES = [
        {"image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&q=80", "price": 45.99, "link": "https://www.bonkerscorner.com/"},
        {"image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&q=80", "price": 18.50, "link": "https://www.nykaa.com/"},
        {"image": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=800&q=80", "price": 60.00, "link": "https://hermod.in/"}
    ]
    
    @staticmethod
    def match_product(product_name: str, category: str = "fashion") -> dict:
        resource = random.choice(ProductMatcher.AFFILIATE_RESOURCES)
        
        # In a real app we'd determine category dynamically, mocking it here
        is_makeup = "oil" in product_name.lower() or "makeup" in product_name.lower() or "gloss" in product_name.lower() or "blush" in product_name.lower() or "serum" in product_name.lower()
        determined_cat = "makeup" if is_makeup else "fashion"
        
        return {
            "product_name": product_name.title(),
            "category": determined_cat,
            "image_url": resource["image"],
            "price": resource["price"],
            "affiliate_link": resource["link"],
            "source_platform": "Amazon" if resource["link"].startswith("https://amzn") else "Shopify/Brand Site"
        }

product_matcher = ProductMatcher()
