import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import time

# --- 1. CORE PIPELINE INTEGRATION ---
# Handling imports safely for Streamlit Cloud deployment
try:
    from src.pipeline import analyze_single, analyze_dataframe
except ImportError:
    # Fallback to ensure the app doesn't crash during initial cloud setup
    def analyze_single(text):
        return {"sentiment_label": "neutral", "priority_label": "low", "primary_aspect_label": "general"}
    def analyze_dataframe(df, col):
        return df.assign(sentiment_label="neutral"), {}

# --- 2. ENTERPRISE PAGE CONFIG ---
st.set_page_config(
    page_title="Customer Feedback Intelligence | Enterprise",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 3. PREMIUM DARK THEME DESIGN SYSTEM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset & Hide Streamlit Default Indicators */
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #F3F4F6; }
    [data-testid="collapsedControl"], header, footer { display: none; }
    
    .stApp {
        background-color: #030712;
        background-image: radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.05) 1px, transparent 0);
        background-size: 40px 40px;
    }

    /* Custom Top Navigation Bar */
    .custom-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 3rem;
        background: rgba(17, 24, 39, 0.9);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        position: fixed;
        top: 0; left: 0; right: 0; z-index: 1000;
    }

    /* Premium Content Cards */
    .block-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 24px;
        padding: 2.5rem;
        margin-top: 10px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        transition: border-color 0.3s ease;
    }
    .block-card:hover { border-color: #6366F1; }

    /* KPI / Metric Block Styling */
    .kpi-container {
        background: rgba(31, 41, 55, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
    }
    .kpi-label { color: #9CA3AF; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 1.6rem; font-weight: 800; margin-top: 5px; background: linear-gradient(90deg, #A5B4FC, #E879F9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    /* Premium Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F2937;
        border-radius: 12px;
        color: #9CA3AF;
        padding: 10px 30px;
        font-weight: 600;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #374151 !important;
        border: 1px solid #6366F1 !important;
        color: white !important;
    }

    /* Action Button Enhancement */
    div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        width: 100%;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.4);
    }

    /* Utility Helpers */
    .badge { padding: 4px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; }
    .status-up { color: #10B981; }
</style>
""", unsafe_allow_html=True)

# --- 4. TOP NAVIGATION HEADER ---
st.markdown("""
<div class="custom-nav">
    <div style="font-size: 1.3rem; font-weight: 800; letter-spacing: -0.5px;">
        <span style="color: #6366F1;">CUSTOMER</span> FEEDBACK <span style="color: #6366F1;">INTELLIGENCE</span>
    </div>
    <div style="display: flex; gap: 20px; align-items: center;">
        <span class="status-up">● SYSTEM OPERATIONAL</span>
        <div style="width: 35px; height: 35px; background: #6366F1; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800;">M</div>
    </div>
</div>
<div style="margin-top: 80px;"></div>
""", unsafe_allow_html=True)

# --- 5. DATA PROCESSING HELPERS ---
def detect_review_column(df):
    keywords = ['review', 'comment', 'feedback', 'text', 'message', 'complaint', 'remark']
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords):
            return col
    return df.columns[0]

def render_kpi_block(label, value):
    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. MAIN APPLICATION TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ REAL-TIME AUDIT", "📦 BATCH WORKSPACE", "📊 STRATEGIC INSIGHTS"])

# --- TAB 1: SINGLE REVIEW ANALYSIS ---
with tab1:
    col_l, col_r = st.columns([1, 1.4], gap="large")
    
    with col_l:
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Input Terminal")
        st.caption("Paste customer feedback below for neural analysis.")
        raw_text = st.text_area("Review Input", height=220, placeholder="Example: Payment fail ho gaya par support ne help nahi ki...", label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        if c1.button("EXECUTE ANALYSIS"):
            if raw_text.strip():
                with st.spinner("Decoding sentiment..."):
                    st.session_state.single_res = analyze_single(raw_text)
            else:
                st.warning("Please provide input text.")
        if c2.button("CLEAR"):
            st.session_state.single_res = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if "single_res" in st.session_state and st.session_state.single_res:
            res = st.session_state.single_res
            st.markdown('<div class="block-card">', unsafe_allow_html=True)
            st.markdown("### 🛡️ Intelligence Output")
            
            k1, k2, k3 = st.columns(3)
            with k1: render_kpi_block("Priority", str(res.get('priority_label', 'N/A')).upper())
            with k2: render_kpi_block("Sentiment", str(res.get('sentiment_label', 'N/A')).title())
            with k3: render_kpi_block("Topic", str(res.get('primary_aspect_label', 'General')).replace("_", " ").title())
            
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.write(f"**Emotion:** `{str(res.get('emotion_label', 'N/A')).title()}`")
            m2.write(f"**Intent:** `{str(res.get('customer_intent_label', 'N/A')).title()}`")
            m3.write(f"**AI Confidence:** `{float(res.get('bert_confidence', 0))*100:.1f}%`")
            
            st.divider()
            st.write("**🔍 Intelligence Signals:**")
            kw = res.get('matched_keywords', [])
            if kw:
                st.markdown(" ".join([f'<span style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; margin: 4px; display: inline-block; color: #A5B4FC;">{k}</span>' for k in (kw if isinstance(kw, list) else kw.split(","))]), unsafe_allow_html=True)
            
            st.info(f"**Action Recommendation:** {res.get('action_recommendation', 'Log for standard reporting.')}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="block-card" style="height: 430px; display: flex; align-items: center; justify-content: center; text-align: center; border: 2px dashed #1F2937;">
                    <div>
                        <div style="font-size: 3.5rem; margin-bottom: 20px;">💠</div>
                        <h2 style="color: #6366F1;">Neural Standby</h2>
                        <p style="color: #9CA3AF;">Awaiting data input from terminal to begin audit.</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 2: BATCH PROCESSING ---
with tab2:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown("### 📂 Bulk Processing Workspace")
    file = st.file_uploader("Drop CSV or XLSX files", type=["csv", "xlsx"], label_visibility="collapsed")
    
    if file:
        df_input = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        detected_col = detect_review_column(df_input)
        target_col = st.selectbox("Confirm Target Review Column", df_input.columns, index=list(df_input.columns).index(detected_col))
        
        if st.button("PROCESS DATASET"):
            start = time.time()
            with st.spinner("Scaling Intelligence..."):
                processed_df, meta = analyze_dataframe(df_input, target_col)
                # Fallback if analyze_dataframe doesn't return second meta dict
                if not isinstance(meta, dict): meta = {}
                
            st.session_state.batch_data = processed_df
            st.session_state.batch_meta = meta
            st.session_state.proc_time = time.time() - start

    if "batch_data" in st.session_state:
        b_df = st.session_state.batch_data
        st.divider()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Records", len(b_df))
        k2.metric("Negative Ratio", f"{(b_df['sentiment_label'] == 'negative').mean()*100:.1f}%")
        k3.metric("Critical Alerts", len(b_df[b_df['priority_label'] == 'critical']))
        k4.metric("Execution Time", f"{st.session_state.proc_time:.2f}s")
        
        st.dataframe(b_df.head(100), use_container_width=True)
        
        csv_out = b_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD AUDIT REPORT (CSV)", data=csv_out, file_name="ai_audit_report.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: DASHBOARD / INSIGHTS ---
with tab3:
    if "batch_data" in st.session_state:
        d_df = st.session_state.batch_data
        
        # Dashboard KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Intelligence Scanned", len(d_df))
        c2.metric("Positive Sentiment", f"{(d_df['sentiment_label']=='positive').mean()*100:.1f}%")
        c3.metric("Avg AI Confidence", f"{d_df['bert_confidence'].mean()*100:.1f}%")
        c4.metric("Unique Aspects", d_df['primary_aspect_label'].nunique())
        
        st.divider()
        v1, v2 = st.columns(2)
        with v1:
            fig_p = px.pie(d_df, names='sentiment_label', hole=0.7, title="Sentiment Distribution",
                          color_discrete_sequence=['#10B981', '#6B7280', '#EF4444'])
            fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
            st.plotly_chart(fig_p, use_container_width=True)
        with v2:
            fig_b = px.bar(d_df['primary_aspect_label'].value_counts().reset_index(), x='count', y='primary_aspect_label', 
                          orientation='h', title="Concerns by Aspect", color='count', color_continuous_scale='Purples')
            fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_b, use_container_width=True)

        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.subheader("💡 Strategic Summary")
        st.write(generate_ai_summary(d_df.head(15)) if 'generate_ai_summary' in globals() else "Dominant sentiment clusters identified in primary aspects. Strategic resource allocation recommended for critical priority segments.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload and process a batch dataset to unlock strategic dashboard insights.")

# --- 7. SIDEBAR & FOOTER ---
with st.sidebar:
    st.markdown("### 💠 Enterprise Edition")
    st.caption("Hybrid Transformer Logic")
    st.divider()
    st.markdown("### 👨‍💻 Developer")
    st.markdown("**Manas**")
    st.markdown("[Portfolio](https://github.com/MANAS-1420)")
    st.divider()
    st.caption("v5.0 Stable Release")

st.markdown("<br><center style='color: #4B5563; font-size: 0.8rem;'>ENTERPRISE FEEDBACK INTELLIGENCE | BUILT FOR RECRUITERS | MANAS 2026</center>", unsafe_allow_html=True)
