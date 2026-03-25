import streamlit as st
import pandas as pd
import plotly.express as px
from src.pipeline import analyze_single, analyze_dataframe
from src.bert_model import generate_ai_summary

st.set_page_config(page_title="Feedback Intel | Enterprise", layout="wide")

# --- CUSTOM THEME ---
st.markdown("""
<style>
    .stApp { background: #050a18; color: #E5E7EB; font-family: 'Inter', sans-serif; }
    .css-card { background: rgba(17, 25, 40, 0.8); border: 1px solid #243247; border-radius: 20px; padding: 25px; margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(90deg, #4F46E5, #9333EA); border: none; border-radius: 12px; font-weight: 700; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("💠 Enterprise Feedback Intelligence")
st.caption("Hybrid Multilingual NLP Architecture • Powered by Gemini AI")

tab1, tab2 = st.tabs(["🚀 Command Center", "📊 Batch Processing"])

with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        txt = st.text_area("Live Review", height=150, placeholder="Type customer feedback...")
        if st.button("Run Intelligence"):
            st.session_state.result = analyze_single(txt)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if "result" in st.session_state:
            res = st.session_state.result
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            k1, k2, k3 = st.columns(3)
            k1.metric("Priority", res['priority_label'].upper())
            k2.metric("Sentiment", res['sentiment_label'].title())
            k3.metric("Aspect", res['primary_aspect_label'].title())
            st.info(f"**Intent:** {res['customer_intent_label']} | **Emotion:** {res['emotion_label']}")
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    up = st.file_uploader("Bulk Upload", type=["csv", "xlsx"])
    if up:
        df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
        col = st.selectbox("Text Column", df.columns)
        if st.button("Process Bulk Data"):
            res_df = analyze_dataframe(df, col)
            st.success("Analysis Complete!")
            
            # AI SUMMARY SECTION
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.subheader("✨ AI Executive Summary")
            with st.spinner("Gemini is reading reviews..."):
                summary = generate_ai_summary(res_df.head(20))
                st.write(summary)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Charts
            st.plotly_chart(px.pie(res_df, names='sentiment_label', title="Sentiment Share", hole=0.5))
            st.dataframe(res_df)

with st.sidebar:
    st.markdown("### 👨‍💻 Developed by Manas")
    st.markdown("[🔗 GitHub Portfolio](https://github.com/MANAS-1420)")
