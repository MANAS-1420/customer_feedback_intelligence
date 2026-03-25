import streamlit as st
import pandas as pd
import plotly.express as px
import time
from src.pipeline import analyze_single, analyze_dataframe
from src.bert_model import generate_ai_summary

# --- 1. ENTERPRISE CONFIG & THEME ---
st.set_page_config(
    page_title="Feedback Intel AI | Enterprise",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- 2. ADVANCED DESIGN SYSTEM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    /* Global Reset & Hide Sidebar Bug */
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #F3F4F6; }
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    .stApp {
        background: #0B0F1A;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%);
    }

    /* Custom Navigation Bar */
    .custom-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 40px;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
    }

    /* Premium Glassmorphism Cards */
    .premium-card {
        background: rgba(17, 25, 40, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        min-height: 250px;
    }

    /* Typography & Gradients */
    .gradient-text {
        background: linear-gradient(90deg, #A5B4FC, #E879F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Metric Formatting */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.8rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }

    /* Keyword Chips */
    .keyword-chip {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #A5B4FC;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 4px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%) !important;
        border: none !important;
        color: white !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- 3. TOP NAVIGATION ---
st.markdown("""
<div class="custom-nav">
    <div style="font-size: 1.4rem; font-weight: 800; color: #6366F1;">💠 FEEDBACK <span style="color:white;">INTEL AI</span></div>
    <div style="color: #9CA3AF; font-size: 0.85rem; font-weight: 600;">ENTERPRISE SUITE v3.2 ● SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

# --- 4. HERO SECTION ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 0;">Business Intelligence, Reimagined.</h1>
    <p style="color: #9CA3AF; font-size: 1.1rem;">Advanced Hybrid NLP Architecture for Multilingual Customer Voice.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡ REAL-TIME AUDIT", "📦 BATCH INTELLIGENCE"])

# --- 5. TAB 1: REAL-TIME ANALYSIS ---
with tab1:
    col_in, col_out = st.columns([1, 1.4], gap="large")
    
    with col_in:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### ✍️ Input Console")
        review_input = st.text_area("Customer Review", height=200, placeholder="Paste feedback (English/Hindi/Hinglish)...", label_visibility="collapsed")
        if st.button("EXECUTE NEURAL AUDIT", use_container_width=True):
            if review_input.strip():
                with st.spinner("Decoding sentiment..."):
                    st.session_state.single_result = analyze_single(review_input)
            else:
                st.warning("Input required for analysis.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_out:
        if "single_result" in st.session_state:
            res = st.session_state.single_result
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown("### 🛡️ Audit Intelligence Output")
            
            # Metrics Row
            m1, m2, m3 = st.columns(3)
            m1.metric("Priority", res['priority_label'].upper())
            m2.metric("Sentiment", res['sentiment_label'].title())
            m3.metric("Topic", res['primary_aspect_label'].replace("_", " ").title())
            
            st.markdown("---")
            
            # Metadata Grid
            c_a, c_b, c_c = st.columns(3)
            c_a.write(f"**Emotion:** `{res['emotion_label'].title()}`")
            c_b.write(f"**Intent:** `{res['customer_intent_label'].title()}`")
            c_c.write(f"**Confidence:** `{res['bert_confidence']*100:.1f}%`")

            # Keyword Chips
            st.write("**🔍 Intelligence Signals:**")
            if res['matched_keywords']:
                chips = "".join([f'<span class="keyword-chip">{k}</span>' for k in res['matched_keywords'].split(",")])
                st.markdown(chips, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if res['priority_label'] == 'critical':
                st.error("🚨 **CRITICAL:** High-risk issue. Immediate escalation triggered.")
            elif res['priority_label'] == 'high':
                st.warning("⚠️ **ACTION:** Requires priority response within 4 hours.")
            else:
                st.success("✅ **STABLE:** No immediate action required.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Landing Placeholder (No Empty Boxes)
            st.markdown("""
            <div class="premium-card" style="display: flex; align-items: center; justify-content: center; text-align: center;">
                <div>
                    <h2 style="color: #6366F1;">Ready for Audit?</h2>
                    <p style="color: #9CA3AF;">Paste a customer review to begin real-time analysis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- 6. TAB 2: BATCH PROCESSING ---
with tab2:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("### 📂 Bulk Processing Unit")
    up_file = st.file_uploader("Upload CSV/XLSX for Enterprise Audit", type=["csv", "xlsx"])
    
    if up_file:
        df_raw = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
        target_col = st.selectbox("Select Target Column", df_raw.columns)
        
        if st.button("PROCESS ENTERPRISE DATASET"):
            with st.spinner("Executing Batch Pipeline..."):
                st.session_state.batch_df = analyze_dataframe(df_raw, text_col=target_col)

    if "batch_df" in st.session_state:
        b_df = st.session_state.batch_df
        st.divider()
        
        # Gemini Executive Summary
        st.subheader("✨ AI Global Briefing (Gemini 1.5 Flash)")
        with st.spinner("Synthesizing data trends..."):
            summary = generate_ai_summary(b_df.head(15))
            st.markdown(f'<div style="background: rgba(99,102,241,0.1); padding: 25px; border-radius: 15px; border-left: 5px solid #6366F1;">{summary}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Visual Analytics
        v1, v2, v3 = st.columns(3)
        with v1:
            st.plotly_chart(px.pie(b_df, names='sentiment_label', hole=0.6, color_discrete_sequence=['#EF4444', '#6B7280', '#10B981']), use_container_width=True)
        with v2:
            st.plotly_chart(px.bar(b_df['primary_aspect_label'].value_counts(), title="Volume by Aspect"), use_container_width=True)
        with v3:
            st.plotly_chart(px.bar(b_df['emotion_label'].value_counts(), title="Volume by Emotion"), use_container_width=True)
            
        st.dataframe(b_df, use_container_width=True)
        
        # Download
        csv_data = b_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD AUDIT REPORT", data=csv_data, file_name="ai_audit_report.csv", mime="text/csv")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. FOOTER ---
st.markdown("""
<div style="text-align: center; color: #4B5563; font-size: 0.85rem; margin-top: 50px; padding-bottom: 20px;">
    Developed by Manas | Enterprise AI Portfolio v3.2 | Built with Hybrid NLP & Gemini Flash
</div>
""", unsafe_allow_html=True)
