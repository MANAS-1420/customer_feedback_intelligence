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
        # UPDATED API KEY
        genai.configure(api_key="AIzaSyBz6_6-r-aFQGKzmCXw_spwexoQFMmk3jM")
        
        context = df_subset[['sentiment_label', 'primary_aspect_label', 'subcategory_label', 'priority_label']].to_string()
        prompt = f"Analyze these classified customer reviews. Provide a 3-bullet executive summary. Focus on the main problem category, the general sentiment, and one actionable recommendation for the business: \n\n{context}"
        
        # DYNAMIC MODEL FINDER: Ask the API exactly what models are available
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                
        if not available_models:
            return "AI Summary unavailable: No generative models accessible with this API key."
            
        # Prioritize 'flash' (fastest) or 'pro', otherwise just pick the first available text model
        target_model = available_models[0]
        for m_name in available_models:
            if 'flash' in m_name.lower():
                target_model = m_name
                break
            elif 'pro' in m_name.lower() and 'vision' not in m_name.lower():
                target_model = m_name

        # Generate using the dynamically found model
        model = genai.GenerativeModel(target_model)
        response = model.generate_content(prompt)
        return response.text
            
    except Exception as e:
        return f"AI Summary unavailable. Diagnostics: {str(e)}"
