import streamlit as st
import pandas as pd
import plotly.express as px
import time
from src.pipeline import analyze_single, analyze_dataframe
from src.bert_model import generate_ai_summary

# --- ENTERPRISE CONFIG ---
st.set_page_config(
    page_title="Feedback Intel AI | Enterprise",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN DESIGN SYSTEM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    /* Global Reset */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #F3F4F6;
    }

    .stApp {
        background: #0B0F1A;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%);
    }

    /* Glassmorphism Containers */
    .premium-card {
        background: rgba(17, 25, 40, 0.6);
        backdrop-filter: blur(12px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Top Navigation Bar */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        border-radius: 12px;
    }

    /* Gradient Typography */
    .gradient-text {
        background: linear-gradient(90deg, #A5B4FC, #E879F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Modern Metric Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        border-left: 4px solid #6366F1;
    }

    /* Clean Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%) !important;
        border: none !important;
        color: white !important;
        padding: 12px 28px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100%;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- TOP NAV ---
st.markdown("""
<div class="nav-bar">
    <div style="font-size: 1.5rem; font-weight: 800; color: #6366F1;">💠 FEEDBACK <span style="color:white;">INTEL</span></div>
    <div style="color: #9CA3AF; font-size: 0.85rem;">Status: <span style="color: #10B981;">● Neural Engine Online</span></div>
</div>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 0;">Business Intelligence, Reimagined.</h1>
    <p style="color: #9CA3AF; font-size: 1.2rem;">Analyze multilingual customer sentiment with Enterprise-grade AI.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡ REAL-TIME ANALYSIS", "📦 BATCH PROCESSING"])

# --- TAB 1: SINGLE ANALYSIS ---
with tab1:
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### ✍️ Input Console")
        review_text = st.text_area("Customer Review", height=180, placeholder="Type or paste feedback here...", label_visibility="collapsed")
        analyze_btn = st.button("EXECUTE ANALYSIS")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        if analyze_btn and review_text:
            with st.spinner("Decoding sentiment..."):
                res = analyze_single(review_text)
            
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown(f"### 🛡️ AI Audit Results")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Priority", res['priority_label'].upper())
            m2.metric("Sentiment", res['sentiment_label'].title())
            m3.metric("Category", res['primary_aspect_label'].title())
            
            st.markdown("---")
            st.markdown(f"**Emotion:** `{res['emotion_label'].title()}` | **Intent:** `{res['customer_intent_label'].title()}`")
            
            # Smart Recommendation
            if res['priority_label'] == 'critical':
                st.error("🚨 **ACTION REQUIRED:** High-risk issue detected. Escalating to supervisor.")
            else:
                st.success("✅ **STABLE:** No immediate manual intervention required.")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: BATCH PROCESSING ---
with tab2:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    up_file = st.file_uploader("Drop Enterprise Data (CSV/XLSX)", type=["csv", "xlsx"])
    
    if up_file:
        df = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
        text_col = st.selectbox("Select Target Column", df.columns)
        
        if st.button("BEGIN BATCH PROCESSING"):
            with st.spinner("Scaling Intelligence Pipeline..."):
                processed_df = analyze_dataframe(df, text_col=text_col)
            
            st.divider()
            
            # AI EXECUTIVE SUMMARY (PREMIUM FEATURE)
            st.subheader("✨ AI Executive Briefing")
            with st.spinner("Gemini is synthesizing trends..."):
                summary = generate_ai_summary(processed_df.head(15))
                st.markdown(f'<div style="background: rgba(99, 102, 241, 0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #6366F1;">{summary}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # DATA VISUALIZATION
            v1, v2 = st.columns(2)
            with v1:
                fig = px.pie(processed_df, names='sentiment_label', hole=0.6, 
                             color_discrete_sequence=['#EF4444', '#6B7280', '#10B981'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with v2:
                fig2 = px.bar(processed_df['primary_aspect_label'].value_counts(), orientation='h')
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
                
            st.dataframe(processed_df.style.background_gradient(cmap='Blues'), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; color: #4B5563; font-size: 0.8rem; margin-top: 50px;">
    Developed by Manas | Enterprise AI Suite v2.5 | © 2026
</div>
""", unsafe_allow_html=True)
