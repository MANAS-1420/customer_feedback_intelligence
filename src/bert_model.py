# src/bert_model.py
import streamlit as st
from transformers import pipeline
import google.generativeai as genai

@st.cache_resource(show_spinner=False)
def load_sentiment_model():
    try:
        return pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    except Exception:
        return None

def get_bert_sentiment(text: str):
    model = load_sentiment_model()
    if not model or not text.strip(): return "neutral", 0.0
    try:
        result = model(text[:512])[0]
        stars = int(result['label'].split()[0])
        if stars <= 2: return "negative", result['score']
        if stars == 3: return "neutral", result['score']
        return "positive", result['score']
    except Exception: 
        return "neutral", 0.0

@st.cache_data(ttl=3600)
def generate_ai_summary(df_subset):
    try:
        genai.configure(api_key="AIzaSyAm2_CCjgqGcOPgPwb64hyP71BAnZD45bU")
        
        context = df_subset[['sentiment_label', 'primary_aspect_label', 'subcategory_label', 'priority_label']].to_string()
        prompt = f"Analyze these classified customer reviews. Provide a 3-bullet executive summary. Focus on the main problem category, the general sentiment, and one actionable recommendation for the business: \n\n{context}"
        
        # SMART FALLBACK: Tries latest flash, then falls back to stable pro
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
            
    except Exception as e:
        return f"AI Summary unavailable: {str(e)}"
