import streamlit as st
from transformers import pipeline

@st.cache_resource(show_spinner="Loading AI Sentiment Model...")
def get_sentiment_model():
    """
    Loads and caches the BERT model. 
    @st.cache_resource ensures the model stays in memory across 
    different user interactions/reruns.
    """
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
        return sentiment_pipeline
    except Exception as e:
        st.error(f"Error loading BERT model: {e}")
        return None

def bert_sentiment(text: str):
    """
    Analyzes text and returns a sentiment ID (0, 1, 2) and confidence score.
    Mapping:
    1-2 Stars -> 0 (Negative)
    3 Stars   -> 1 (Neutral)
    4-5 Stars -> 2 (Positive)
    """
    if not text or len(text.strip()) == 0:
        return 1, 0.0

    try:
        model = get_sentiment_model()
        if model is None:
            return 1, 0.5  # Default to neutral if model fails
            
        # BERT has a 512 token limit; we truncate safely
        result = model(text[:512])[0]
        label = result["label"]  # Format: "1 star", "5 stars", etc.
        score = float(result["score"])

        # Extract numerical rating from label string
        rating = int(label.split()[0])

        if rating <= 2:
            return 0, score
        elif rating == 3:
            return 1, score
        else:
            return 2, score
            
    except Exception:
        # Fallback to neutral on any unexpected error
        return 1, 0.50
