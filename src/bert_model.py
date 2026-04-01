# Inside src/bert_model.py

@st.cache_data(ttl=3600)
def generate_ai_summary(df_subset):
    try:
        # 🔒 SECURE WAY: Pulls the key from Streamlit Secrets, NOT from the code
        api_key = st.secrets["AIzaSyBz6_6-r-aFQGKzmCXw_spwexoQFMmk3jM"]
        genai.configure(api_key=api_key)
        
        context = df_subset[['sentiment_label', 'primary_aspect_label', 'subcategory_label', 'priority_label']].to_string()
        prompt = f"Analyze these classified customer reviews. Provide a 3-bullet executive summary. Focus on the main problem category, the general sentiment, and one actionable recommendation for the business: \n\n{context}"
        
        # DYNAMIC MODEL FINDER
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                
        if not available_models: return "AI Summary unavailable."
            
        target_model = available_models[0]
        for m_name in available_models:
            if 'flash' in m_name.lower():
                target_model = m_name
                break
            elif 'pro' in m_name.lower() and 'vision' not in m_name.lower():
                target_model = m_name

        model = genai.GenerativeModel(target_model)
        response = model.generate_content(prompt)
        return response.text
            
    except Exception as e:
        return f"AI Summary unavailable. Diagnostics: {str(e)}"
