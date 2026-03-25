import streamlit as st
import pandas as pd
import plotly.express as px
from src.pipeline import analyze_single, analyze_dataframe
from src.bert_model import generate_ai_summary

# --- 1. CONFIG & APP STATE ---
st.set_page_config(
    page_title="Customer Feedback Intelligence | Titan v4",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. THE ULTIMATE PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}

    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #030712;
        color: #F9FAFB;
    }

    /* Main Background with subtle grid */
    .stApp {
        background-color: #030712;
        background-image: 
            linear-gradient(rgba(99, 102, 241, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
    }

    /* Top Navigation */
    .nav-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 3rem;
        background: rgba(17, 24, 39, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        position: fixed;
        top: 0; left: 0; right: 0; z-index: 1000;
    }

    /* Premium Block Cards */
    .block-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 24px;
        padding: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .block-card:hover {
        border-color: #6366F1;
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
    }

    /* Glowing Metrics */
    .metric-box {
        text-align: center;
        padding: 1.5rem;
        background: rgba(31, 41, 55, 0.5);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
    .metric-label { color: #9CA3AF; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 1.8rem; font-weight: 800; margin-top: 0.5rem; background: linear-gradient(to right, #818CF8, #C084FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    /* Action Button Custom Styling */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
        transform: scale(1.02);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F2937;
        border-radius: 12px;
        color: #9CA3AF;
        padding: 10px 25px;
        font-weight: 600;
        border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #6366F1; }
    .stTabs [aria-selected="true"] {
        background: #374151 !important;
        border: 1px solid #6366F1 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CUSTOM NAVBAR ---
st.markdown("""
<div class="nav-header">
    <div style="font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px;">
        <span style="color: #6366F1;">CUSTOMER</span> FEEDBACK <span style="color: #6366F1;">INTELLIGENCE</span>
    </div>
    <div style="display: flex; gap: 20px; align-items: center;">
        <span style="font-size: 0.8rem; color: #10B981; font-weight: 600;">● SYSTEM LIVE</span>
        <div style="width: 35px; height: 35px; background: #6366F1; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800;">M</div>
    </div>
</div>
<div style="margin-top: 100px;"></div>
""", unsafe_allow_html=True)

# --- 4. HERO SECTION ---
st.markdown("""
<div style="text-align: center; max-width: 800px; margin: 0 auto 50px auto;">
    <h1 style="font-size: 4rem; font-weight: 800; line-height: 1; margin-bottom: 20px;">
        AI Intelligence for the <span style="color: #6366F1;">Modern Enterprise.</span>
    </h1>
    <p style="color: #9CA3AF; font-size: 1.2rem; font-weight: 400;">
        Deep sentiment audit, multilingual aspect detection, and executive summaries powered by Hybrid NLP.
    </p>
</div>
""", unsafe_allow_html=True)

# --- 5. MAIN INTERFACE ---
tab1, tab2 = st.tabs(["⚡ REAL-TIME AUDIT", "📦 BATCH WORKSPACE"])

with tab1:
    col_input, col_output = st.columns([1, 1.4], gap="large")
    
    with col_input:
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Input Terminal")
        st.caption("Paste customer feedback below for instant analysis.")
        review_input = st.text_area("Review Input", height=250, placeholder="Example: Payment fail ho gaya par support ne help nahi ki. Very bad...", label_visibility="collapsed")
        
        if st.button("EXECUTE ANALYSIS"):
            if review_input.strip():
                with st.spinner("Decoding..."):
                    st.session_state.v4_result = analyze_single(review_input)
            else:
                st.warning("Input terminal is empty.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_output:
        if "v4_result" in st.session_state:
            res = st.session_state.v4_result
            st.markdown('<div class="block-card">', unsafe_allow_html=True)
            st.markdown("### 🛠️ Intelligence Metrics")
            
            # Metric Blocks
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-box"><div class="metric-label">Priority</div><div class="metric-value">{res["priority_label"].upper()}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-box"><div class="metric-label">Sentiment</div><div class="metric-value">{res["sentiment_label"].title()}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-box"><div class="metric-label">Topic</div><div class="metric-value">{res["primary_aspect_label"].replace("_", " ").title()}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Secondary Data Row
            ca, cb, cc = st.columns(3)
            ca.write(f"**Emotion:** `{res['emotion_label'].title()}`")
            cb.write(f"**Intent:** `{res['customer_intent_label'].title()}`")
            cc.write(f"**BERT Conf:** `{res['bert_confidence']*100:.1f}%`")
            
            st.divider()
            st.write("**🔍 Intelligence Signals:**")
            if res['matched_keywords']:
                kw_html = "".join([f'<span style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; margin: 4px; display: inline-block; color: #A5B4FC;">{k}</span>' for k in res['matched_keywords'].split(",")])
                st.markdown(kw_html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if res['priority_label'] == 'critical': st.error("🚨 **CRITICAL RISK:** Immediate escalation to management required.")
            else: st.success("✅ **STABLE:** Logged for standard reporting.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Landing Placeholder
            st.markdown("""
            <div class="block-card" style="height: 480px; display: flex; align-items: center; justify-content: center; text-align: center; border: 2px dashed #1F2937;">
                <div>
                    <div style="font-size: 3rem; margin-bottom: 20px;">🛡️</div>
                    <h2 style="color: #6366F1;">Neural Standby</h2>
                    <p style="color: #9CA3AF;">Awaiting data input from the terminal to begin analysis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown("### 📂 Bulk Processing Workspace")
    file = st.file_uploader("Drop CSV or XLSX files here", type=["csv", "xlsx"], label_visibility="collapsed")
    
    if file:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        col = st.selectbox("Select Text Column", df.columns)
        if st.button("PROCESS DATASET"):
            with st.spinner("Scaling Intelligence..."):
                st.session_state.v4_batch = analyze_dataframe(df, col)

    if "v4_batch" in st.session_state:
        b_df = st.session_state.v4_batch
        st.divider()
        st.subheader("✨ Executive Summary")
        summary = generate_ai_summary(b_df.head(20))
        st.markdown(f'<div style="background: rgba(99, 102, 241, 0.05); border: 1px solid #6366F1; padding: 30px; border-radius: 20px; color: #E5E7EB; line-height: 1.6;">{summary}</div>', unsafe_allow_html=True)
        
        st.divider()
        v1, v2 = st.columns([1, 1.2])
        v1.plotly_chart(px.pie(b_df, names='sentiment_label', hole=0.7, color_discrete_sequence=['#EF4444', '#6B7280', '#10B981']), use_container_width=True)
        v2.plotly_chart(px.bar(b_df['primary_aspect_label'].value_counts(), orientation='h', title="Top Issue Categories"), use_container_width=True)
        
        st.dataframe(b_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding-bottom: 30px; color: #4B5563; font-size: 0.8rem;">
    TITAN ENTERPRISE v4.0 | BUILT BY MANAS | HYBRID NLP & GEMINI 1.5 FLASH
</div>
""", unsafe_allow_html=True)
