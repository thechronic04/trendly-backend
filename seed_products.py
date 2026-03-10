import models

def seed():
    # Initialize Database
    models.init_db()
    db = models.SessionLocal()

    # Clear existing data just in case
    db.query(models.Product).delete()
    
    products_data = [
        {
            "name": "Oversized Vintage Leather Moto Jacket",
            "brand": "AllSaints",
            "description": "Authentic 90s inspired distressed leather. Predicted to explode next month.",
            "price": 24999.00,
            "category": "clothing",
            "sub_category": "Outerwear",
            "collection": "New In",
            "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80",
            "affiliate_link": "https://www.allsaints.com/",
            "trend_score": 95.8,
            "is_trending_now": True,
            "predicted_next_month": True,
            "momentum": "+24% 7d"
        },
        {
            "name": "Premium Cotton Oxford Shirt",
            "brand": "The Bear House",
            "description": "Premium breathable cotton. A staple for the 'Quiet Luxury' enthusiast.",
            "price": 2499.00,
            "category": "clothing",
            "sub_category": "Tops",
            "collection": "Ready to Wear",
            "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&q=80",
            "affiliate_link": "https://thebearhouse.com/",
            "trend_score": 87.5,
            "is_trending_now": True,
            "predicted_next_month": False,
            "momentum": "Steady"
        },
        {
            "name": "Urban Minimalist Tech Shorts",
            "brand": "Hermod",
            "description": "Lightweight tech fabrics for the urban explorer.",
            "price": 1899.00,
            "category": "clothing",
            "sub_category": "Denim",
            "collection": "Urban Street",
            "image_url": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=800&q=80",
            "affiliate_link": "https://hermod.in/",
            "trend_score": 91.2,
            "is_trending_now": True,
            "predicted_next_month": True,
            "momentum": "+15% 7d"
        },
        {
            "name": "Oversized Streetwear Hoodie",
            "brand": "Bonkers",
            "description": "High-density cotton hoodie with a viral silhouette.",
            "price": 1599.00,
            "category": "clothing",
            "sub_category": "Knitwear",
            "collection": "New In",
            "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800&q=80",
            "affiliate_link": "https://www.bonkerscorner.com/",
            "trend_score": 98.4,
            "is_trending_now": True,
            "predicted_next_month": True,
            "momentum": "+64% 7d"
        },
        {
            "name": "Soft Pinch Liquid Blush",
            "brand": "Nykaa",
            "description": "Insanely pigmented and viral blush. A staple for the 'Clean Girl' aesthetic.",
            "price": 2499.00,
            "category": "makeup",
            "sub_category": "Tops",
            "collection": "Self Care",
            "image_url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&q=80",
            "affiliate_link": "https://www.nykaa.com/",
            "trend_score": 98.2,
            "is_trending_now": True,
            "predicted_next_month": True,
            "momentum": "+45% 7d"
        },
        {
            "name": "Cherry Glow Lip Oil",
            "brand": "Nykaa",
            "description": "High-shine luxury lip oil matching the upcoming cherry red fashion trend.",
            "price": 4200.00,
            "category": "makeup",
            "sub_category": "Jewelry",
            "collection": "Essentials",
            "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&q=80",
            "affiliate_link": "https://www.nykaa.com/",
            "trend_score": 99.1,
            "is_trending_now": True,
            "predicted_next_month": True,
            "momentum": "+80% 7d"
        }
    ]

    for p_data in products_data:
        product = models.Product(**p_data)
        db.add(product)
    
    db.commit()
    print("Database seeded with 6 AI-curated authentic products successfully.")

if __name__ == "__main__":
    seed()
