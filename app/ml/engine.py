import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Union, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# --- 1. AI PROCESSING ENGINE: TREND SCORING ---

def calculate_trend_score(
    engagement: int, 
    mentions: int, 
    sentiment: float, 
    decay_hours: int = 24
) -> float:
    """
    Core AI Trend Scoring Algorithm for 'Neural Discovery'.
    Weights: Engagement (40%), Mentions (30%), Sentiment (30%) with Time Decay.
    """
    # Normalize inputs to 0.0 - 1.0 (Mock normalization logic)
    norm_engagement = min(engagement / 100000, 1.0)
    norm_mentions = min(mentions / 50000, 1.0)
    norm_sentiment = min(sentiment / 100, 1.0)
    
    # Calculate weighted score (0.0 - 1.0 range)
    base_score = (norm_engagement * 0.4) + (norm_mentions * 0.3) + (norm_sentiment * 0.3)
    
    # Apply Time Decay (Exponential Decay: score * e^(-lambda * t))
    decay_rate = 0.05
    final_score = base_score * np.exp(-decay_rate * decay_hours)
    
    # Scale to 0 - 99.9 for the UI
    return round(max(10.0, final_score * 100), 1)


# --- 2. RECOMMENDATION SYSTEM: CONTENT-BASED FILTERING ---

class ContentRecommender:
    """
    Production-ready content-based recommendation logic.
    Uses TF-IDF + Cosine Similarity on product descriptions/tags.
    In production: Trained model is serialized to 'models/recommender.joblib'
    """
    def __init__(self, metadata_df: pd.DataFrame):
        self.df = metadata_df
        self.tfidf = TfidfVectorizer(stop_words='english')
        # Combine relevant metadata into a single string for vectorization
        self.df['description_soup'] = self.df['category'] + " " + self.df['brand'] + " " + self.df['name']
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['description_soup'])
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)

    def get_recommendations(self, product_id: int, top_n: int = 5) -> List[int]:
        """Returns IDs of top matching products based on content similarity."""
        try:
            idx = self.df.index[self.df['id'] == product_id].tolist()[0]
            sim_scores = list(enumerate(self.cosine_sim[idx]))
            # Sort by highest similarity, skip the item itself (index 0)
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
            product_indices = [i[0] for i in sim_scores]
            return self.df['id'].iloc[product_indices].tolist()
        except (IndexError, KeyError):
            return []


# --- 3. ML MODEL PIPELINE & STORAGE ---

def save_trained_model(model: Any, filename: str):
    """Serializes a trained scikit-learn model for server consumption."""
    model_dir = "app/ml/models"
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, filename))

def load_trained_model(filename: str) -> Optional[Any]:
    """Deserializes a model from storage for serving predictions."""
    model_path = os.path.join("app/ml/models", filename)
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None
