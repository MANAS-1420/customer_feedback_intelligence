import streamlit as st
from transformers import pipeline
import google.generativeai as genai

# BERT Model Caching
@st.cache_resource(show_spinner="Initializing Neural Engine...")
def get_bert_pipeline():
    return pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def bert_sentiment(text: str):
    try:
        model = get_bert_pipeline()
        res = model(text[:512])[0]
        rating = int(res["label"].split()[0])
        score = float(res["score"])
        if rating <= 2: return 0, score
        if rating == 3: return 1, score
        return 2, score
    except: return 1, 0.5

# Gemini AI Executive Summary
genai.configure(api_key="AIzaSyAm2_CCjgqGcOPgPwb64hyP71BAnZD45bU")

@st.cache_data(ttl=3600)
def generate_ai_summary(df_subset):
    """Generates a high-level business summary using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        context = df_subset[['Review', 'sentiment_label', 'primary_aspect_label']].to_string()
        prompt = f"Analyze these customer reviews and provide a 3-bullet point executive summary for a manager. Focus on the biggest problem, the main sentiment, and one actionable recommendation: \n\n{context}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Summary unavailable: {str(e)}"
