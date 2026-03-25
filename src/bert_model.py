import streamlit as st
from transformers import pipeline
import google.generativeai as genai

@st.cache_resource(show_spinner=False)
def get_bert_pipeline():
    try:
        return pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    except Exception:
        return None

def bert_sentiment(text: str):
    model = get_bert_pipeline()
    if not model:
        return 1, 0.5 # Default to neutral if model fails to load
    try:
        res = model(text[:512])[0]
        rating = int(res["label"].split()[0])
        score = float(res["score"])
        if rating <= 2: return 0, score # Negative
        if rating == 3: return 1, score # Neutral
        return 2, score # Positive
    except Exception: 
        return 1, 0.5

@st.cache_data(ttl=3600)
def generate_ai_summary(df_subset):
    """Generates a high-level business summary using Gemini."""
    try:
        # Utilizing Streamlit secrets if available, else fallback
        api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyAm2_CCjgqGcOPgPwb64hyP71BAnZD45bU")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        context = df_subset[['sentiment_label', 'primary_aspect_label']].to_string()
        prompt = f"Analyze these customer review classifications and provide a 3-bullet point executive summary for a manager. Focus on the biggest problem, the main sentiment, and one actionable recommendation. Be concise and professional: \n\n{context}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "AI Summary is currently unavailable. Please check API configuration or connection."
