import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import time

# --- 1. CORE PIPELINE INTEGRATION & SAFE FALLBACK ---
PIPELINE_CONNECTED = True
try:
    from src.pipeline import analyze_single, analyze_dataframe
    from src.bert_model import generate_ai_summary
except ImportError:
    PIPELINE_CONNECTED = False
    def analyze_single(text):
        return {
            "sentiment_label": "neutral", "priority_label": "low", 
            "primary_aspect_label": "General Feedback", "emotion_label": "Neutral",
            "customer_intent_label": "Query", "bert_confidence": 0.85,
            "matched_keywords": "", "action_recommendation": "Check pipeline connection."
        }
    def analyze_dataframe(df, col):
        results = df[col].astype(str).apply(analyze_single)
        res_df = pd.DataFrame(list(results))
        return pd.concat([df.reset_index(drop=True), res_df], axis=1), {}
    def generate_ai_summary(df):
        return "System running in Mock Mode. AI Summary disabled."

# --- 2. ENTERPRISE PAGE CONFIG ---
st.set_page_config(
    page_title="Customer Feedback Intelligence",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 3. PREMIUM DARK THEME DESIGN SYSTEM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #F3F4F6; }
    [data-testid="collapsedControl"], header, footer { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    
    .stApp {
        background-color: #030712;
        background-image: radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.05) 1px, transparent 0);
        background-size: 40px 40px;
    }

    .custom-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 4rem;
        background: rgba(17, 24, 39, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        position: fixed;
        top: 0; left: 0; right: 0; z-index: 1000;
    }

    .block-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 24px;
        padding: 2.5rem;
        margin-top: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }

    .kpi-container {
        background: rgba(31, 41, 55, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
    }
    .kpi-label { color: #9CA3AF; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .kpi-value { font-size: 1.7rem; font-weight: 800; margin-top: 8px; background: linear-gradient(90deg, #A5B4FC, #E879F9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F2937;
        border-radius: 14px;
        color: #9CA3AF;
        padding: 12px 32px;
        font-weight: 600;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] { background: #374151 !important; border: 1px solid #6366F1 !important; color: white !important; }

    div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 24px !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        width: 100%;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(99, 102, 241, 0.5); }
    
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(31, 41, 55, 0.5) !important;
        border: 2px dashed #374151 !important;
        border-radius: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. TOP NAVIGATION HEADER ---
st.markdown("""
<div class="custom-nav">
    <div style="font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px;">
        <span style="color: #6366F1;">CUSTOMER</span> FEEDBACK <span style="color: #6366F1;">INTELLIGENCE</span>
    </div>
    <div style="display: flex; gap: 20px; align-items: center;">
        <span style="color: #10B981; font-weight: 700; font-size: 0.85rem;">● SYSTEM OPERATIONAL</span>
        <div style="width: 38px; height: 38px; background: #6366F1; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white;">M</div>
    </div>
</div>
<div style="margin-top: 100px;"></div>
""", unsafe_allow_html=True)

if not PIPELINE_CONNECTED:
    st.error("⚠️ **SYSTEM WARNING:** The dashboard is running in Mock Safety Mode. `src.pipeline` could not be found.")

# --- 5. DATA PROCESSING HELPERS ---
def detect_review_column(df):
    keywords = ['review', 'comment', 'feedback', 'text', 'message', 'complaint', 'remark']
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords):
            return col
    return df.columns[0] if len(df.columns) > 0 else None

def render_kpi_block(label, value):
    st.markdown(f'<div class="kpi-container"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

# --- 6. MAIN APPLICATION TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ REAL-TIME AUDIT", "📦 BATCH WORKSPACE", "📊 STRATEGIC INSIGHTS"])

with tab1:
    col_l, col_r = st.columns([1, 1.4], gap="large")
    with col_l:
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Input Terminal")
        st.caption("Deep analysis for English, Hindi, and Hinglish feedback.")
        raw_text = st.text_area("Review Input", height=240, placeholder="Example: Payment was smooth and fast, excellent experience!", label_visibility="collapsed")
        
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
            with k3: render_kpi_block("Contextual Topic", str(res.get('primary_aspect_label', 'General')).replace("_", " ").title())
            
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.write(f"**Emotion:** `{str(res.get('emotion_label', 'N/A')).title()}`")
            m2.write(f"**Intent:** `{str(res.get('customer_intent_label', 'N/A')).title()}`")
            m3.write(f"**AI Confidence:** `{float(res.get('bert_confidence', 0))*100:.1f}%`")
            
            st.divider()
            st.write("**🔍 Intelligence Signals:**")
            kw = res.get('matched_keywords', "")
            if kw:
                st.markdown(" ".join([f'<span style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; margin: 4px; display: inline-block; color: #A5B4FC;">{k}</span>' for k in (kw if isinstance(kw, list) else kw.split(",")) if k]), unsafe_allow_html=True)
            else:
                st.caption("No specific rule-based keywords triggered.")
                
            st.info(f"**Action Recommendation:** {res.get('action_recommendation', 'Log for standard reporting.')}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="block-card" style="height: 460px; display: flex; align-items: center; justify-content: center; text-align: center; border: 2px dashed #1F2937;"><div><div style="font-size: 4rem; margin-bottom: 24px;">💠</div><h2 style="color: #6366F1; font-weight: 800;">Neural Standby</h2><p style="color: #9CA3AF; max-width: 320px;">Awaiting data input from terminal to begin the audit process.</p></div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown("### 📂 Bulk Processing Workspace")
    file = st.file_uploader("Drop CSV or XLSX files", type=["csv", "xlsx"], label_visibility="collapsed")
    
    if file:
        df_input = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        detected_col = detect_review_column(df_input)
        if detected_col:
            target_col = st.selectbox("Confirm Target Review Column", df_input.columns, index=list(df_input.columns).index(detected_col))
            
            if st.button("PROCESS DATASET"):
                start = time.time()
                with st.spinner("Executing Batch Intelligence..."):
                    processed_res = analyze_dataframe(df_input, target_col)
                    st.session_state.batch_data = processed_res[0] if isinstance(processed_res, tuple) else processed_res
                st.session_state.proc_time = time.time() - start
        else:
            st.error("No valid columns found in the uploaded file.")

    if "batch_data" in st.session_state:
        b_df = st.session_state.batch_data
        st.divider()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Scanned Records", len(b_df))
        neg_ratio = (b_df['sentiment_label'] == 'negative').mean() * 100 if 'sentiment_label' in b_df.columns else 0.0
        k2.metric("Negative Ratio", f"{neg_ratio:.1f}%")
        crit_count = len(b_df[b_df['priority_label'] == 'critical']) if 'priority_label' in b_df.columns else 0
        k3.metric("Critical Alerts", crit_count)
        k4.metric("Process Time", f"{st.session_state.get('proc_time', 0):.2f}s")
        
        st.dataframe(b_df, use_container_width=True)
        
        d_col1, d_col2 = st.columns(2)
        csv_out = b_df.to_csv(index=False).encode('utf-8')
        d_col1.download_button("📥 DOWNLOAD AUDIT REPORT (CSV)", data=csv_out, file_name="ai_audit_report.csv", mime="text/csv")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            b_df.to_excel(writer, index=False)
        d_col2.download_button("📥 DOWNLOAD AUDIT REPORT (XLSX)", data=output.getvalue(), file_name="ai_audit_report.xlsx")
        
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    if "batch_data" in st.session_state:
        d_df = st.session_state.batch_data
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Intelligence", len(d_df))
        pos_ratio = (d_df['sentiment_label'] == 'positive').mean() * 100 if 'sentiment_label' in d_df.columns else 0.0
        c2.metric("Positive Sentiment", f"{pos_ratio:.1f}%")
        avg_conf = d_df['bert_confidence'].mean() * 100 if 'bert_confidence' in d_df.columns else 0.0
        c3.metric("Avg AI Confidence", f"{avg_conf:.1f}%")
        risk_segs = d_df['priority_label'].nunique() if 'priority_label' in d_df.columns else 0
        c4.metric("Risk Segments", risk_segs)
        
        st.divider()
        v1, v2 = st.columns(2)
        with v1:
            if 'sentiment_label' in d_df.columns:
                fig_p = px.pie(d_df, names='sentiment_label', hole=0.7, title="Sentiment Share", color_discrete_sequence=['#10B981', '#6B7280', '#EF4444'])
                fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
                st.plotly_chart(fig_p, use_container_width=True)
            else:
                st.info("Sentiment data not available for charting.")
        with v2:
            if 'primary_aspect_label' in d_df.columns:
                fig_b = px.bar(d_df['primary_aspect_label'].value_counts().reset_index(), x='count', y='primary_aspect_label', orientation='h', title="Contextual Category Volume", color='count', color_continuous_scale='Purples')
                fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_b, use_container_width=True)
            else:
                st.info("Aspect data not available for charting.")
                
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.subheader("💡 Strategic Summary")
        if PIPELINE_CONNECTED and 'sentiment_label' in d_df.columns and 'primary_aspect_label' in d_df.columns:
            with st.spinner("Generating AI Briefing..."):
                st.write(generate_ai_summary(d_df.head(20)))
        else:
            st.write("Insufficient data or pipeline disconnected. Automated strategic summary unavailable.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload and process a batch dataset to unlock strategic dashboard insights.")

st.markdown("<br><center style='color: #4B5563; font-size: 0.85rem;'>ENTERPRISE FEEDBACK INTELLIGENCE | MANAS 2026</center><br><br>", unsafe_allow_html=True)
