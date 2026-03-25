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
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        min-height: 350px;
    }

    /* Fix for text cutting off in metrics */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.6rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
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
        padding: 10px;
        border-left: 4px solid #6366F1;
    }

    /* Chip Styling */
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
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 0;">Business Intelligence, Reimagined.</h1>
    <p style="color: #9CA3AF; font-size: 1.1rem;">Enterprise-grade Hybrid NLP Architecture.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡ REAL-TIME ANALYSIS", "📦 BATCH PROCESSING"])

# --- TAB 1: SINGLE ANALYSIS ---
with tab1:
    c1, c2 = st.columns([1, 1.4], gap="large")
    
    with c1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### ✍️ Input Console")
        review_text = st.text_area("Customer Review", height=200, placeholder="Paste feedback here...", label_visibility="collapsed")
        analyze_btn = st.button("EXECUTE AI AUDIT", use_container_width=True)
        
        if analyze_btn and review_text:
            with st.spinner("Decoding..."):
                st.session_state.result = analyze_single(review_text)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        if "result" in st.session_state:
            res = st.session_state.result
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown(f"### 🛡️ Analysis Engine Output")
            
            # Row 1: Key Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Priority Score", res['priority_label'].upper())
            m2.metric("Sentiment", res['sentiment_label'].title())
            m3.metric("Topic/Aspect", res['primary_aspect_label'].replace("_", " ").title())
            
            # Row 2: Secondary Metadata
            st.markdown("---")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.write("**🎭 Emotion:**")
                st.write(f"`{res['emotion_label'].title()}`")
            with col_b:
                st.write("**🎯 Intent:**")
                st.write(f"`{res['customer_intent_label'].title()}`")
            with col_c:
                st.write("**🤖 Confidence:**")
                st.write(f"`{res['bert_confidence']*100:.1f}%`")

            # Row 3: Keyword Cloud
            st.write("**🔍 Keywords Detected:**")
            if res['matched_keywords']:
                kw_html = "".join([f'<span class="keyword-chip">{k}</span>' for k in res['matched_keywords'].split(",")])
                st.markdown(kw_html, unsafe_allow_html=True)
            else:
                st.caption("No specific keywords detected.")

            # Recommendations
            st.markdown("<br>", unsafe_allow_html=True)
            if res['priority_label'] == 'critical':
                st.error("🚨 **CRITICAL ALERT:** Escalating to Customer Relations Head.")
            elif res['priority_label'] == 'high':
                st.warning("⚠️ **ACTION:** Requires 4-hour turnaround response.")
            else:
                st.success("✅ **STABLE:** Categorized for weekly report.")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: BATCH PROCESSING ---
with tab2:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    up_file = st.file_uploader("Upload Bulk Dataset", type=["csv", "xlsx"])
    
    if up_file:
        df = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
        text_col = st.selectbox("Select Target Column", df.columns)
        
        if st.button("PROCESS BULK DATA"):
            res_df = analyze_dataframe(df, text_col=text_col)
            
            st.divider()
            st.subheader("✨ AI Global Summary (Gemini 1.5)")
            with st.spinner("Synthesizing..."):
                summary = generate_ai_summary(res_df.head(15))
                st.markdown(f'<div style="background: rgba(99,102,241,0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #6366F1;">{summary}</div>', unsafe_allow_html=True)
            
            st.divider()
            # Visual Analytics
            v1, v2, v3 = st.columns(3)
            with v1:
                st.plotly_chart(px.pie(res_df, names='sentiment_label', hole=0.6, color_discrete_sequence=['#EF4444', '#6B7280', '#10B981']), use_container_width=True)
            with v2:
                st.plotly_chart(px.bar(res_df['primary_aspect_label'].value_counts(), title="Top Issues"), use_container_width=True)
            with v3:
                st.plotly_chart(px.bar(res_df['emotion_label'].value_counts(), title="Customer Mood"), use_container_width=True)
                
            st.dataframe(res_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 👨‍💻 Developed by Manas")
    st.markdown("[🔗 GitHub Portfolio](https://github.com/MANAS-1420)")
    st.divider()
    st.caption("Hybrid Multilingual NLP v3.0")
