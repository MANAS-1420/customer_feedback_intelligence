# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import time

try:
    from src.pipeline import analyze_single, analyze_dataframe
    from src.bert_model import generate_ai_summary
    PIPELINE_CONNECTED = True
except ImportError:
    PIPELINE_CONNECTED = False
    def analyze_single(text): return {"primary_aspect_label": "Error", "subcategory_label": "Offline", "sentiment_label": "neutral", "priority_label": "Low", "emotion_label": "N/A", "customer_intent_label": "N/A"}
    def analyze_dataframe(df, col): return df, {}

# ==========================================
# PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Customer Feedback Intelligence", page_icon="💠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* SAFE FONT OVERRIDE: Applies to the app container but spares the Material Icons */
    .stApp { 
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #030712; 
        background-image: radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.05) 1px, transparent 0); 
        background-size: 40px 40px; 
    }
    
    /* Make the top header transparent instead of hiding it so the sidebar toggle works cleanly */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Clean Custom Nav */
    .custom-nav { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 2rem; background: rgba(31, 41, 55, 0.4); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 2rem;}
    
    .block-card { background: #111827; border: 1px solid #1F2937; border-radius: 24px; padding: 2.5rem; margin-top: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4); }
    .kpi-container { background: rgba(31, 41, 55, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 1.5rem; text-align: center; }
    .kpi-label { color: #9CA3AF; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .kpi-value { font-size: 1.6rem; font-weight: 800; margin-top: 8px; background: linear-gradient(90deg, #A5B4FC, #E879F9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;}
    
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 24px; }
    .stTabs [data-baseweb="tab"] { background-color: #1F2937; border-radius: 14px; color: #9CA3AF; padding: 12px 32px; font-weight: 600; border: 1px solid transparent; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] { background: #374151 !important; border: 1px solid #6366F1 !important; color: white !important; }
    
    /* Target ONLY primary action buttons to avoid breaking the file uploader button */
    div[data-testid="stButton"] > button[kind="primary"] { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; transition: transform 0.2s, box-shadow 0.2s !important; }
    div[data-testid="stButton"] > button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(99, 102, 241, 0.5); }
    
    /* ABSA Mini Cards */
    .absa-card { background: rgba(255,255,255,0.02); border-left: 3px solid #6366F1; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR & HEADER
# ==========================================
with st.sidebar:
    st.markdown("### 💠 Enterprise Edition")
    st.caption("Behavioral AI & Tone Analysis")
    st.divider()
    st.markdown("**Intelligence Layer:**")
    st.markdown("- Aspect-Based Splitting\n- Psychological Churn Risk\n- Language Auto-Detect\n- Sarcasm Flagging")

st.markdown("""
<div class="custom-nav">
    <div style="font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px;"><span style="color: #6366F1;">CUSTOMER</span> FEEDBACK <span style="color: #6366F1;">INTELLIGENCE</span></div>
    <div style="display: flex; gap: 20px; align-items: center;"><span style="color: #10B981; font-weight: 700; font-size: 0.85rem;">● SYSTEM OPERATIONAL</span><div style="width: 38px; height: 38px; background: #6366F1; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white;">M</div></div>
</div>
""", unsafe_allow_html=True)

if not PIPELINE_CONNECTED: st.error("⚠️ `src.pipeline` not found. Running in offline/mock mode.")

def render_kpi(label, value):
    st.markdown(f'<div class="kpi-container"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

def get_review_col(df):
    keywords = ['review', 'comment', 'feedback', 'text', 'message', 'complaint', 'remark']
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords): return col
    return df.columns[0] if len(df.columns) > 0 else None

def bool_badge(val, alert_red=False):
    if val: 
        color = "#EF4444" if alert_red else "#10B981"
        bg = "rgba(239, 68, 68, 0.2)" if alert_red else "rgba(16, 185, 129, 0.2)"
        return f'<span style="background: {bg}; color: {color}; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight:bold;">Yes</span>'
    return '<span style="background: rgba(107, 114, 128, 0.2); color: #9CA3AF; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">No</span>'

# ==========================================
# MAIN TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["⚡ REAL-TIME AUDIT", "📦 BATCH WORKSPACE", "📊 STRATEGIC INSIGHTS"])

with tab1:
    col_l, col_r = st.columns([1, 1.4], gap="large")
    with col_l:
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Input Terminal")
        raw_text = st.text_area("Review Input", height=240, placeholder="Example: Delivery was fast, but the product is completely broken.", label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        if c1.button("EXECUTE ANALYSIS", type="primary", use_container_width=True):
            if raw_text.strip():
                with st.spinner("Analyzing psychological markers..."): st.session_state.single_res = analyze_single(raw_text)
        if c2.button("CLEAR", use_container_width=True):
            st.session_state.single_res = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if "single_res" in st.session_state and st.session_state.single_res:
            res = st.session_state.single_res
            st.markdown('<div class="block-card">', unsafe_allow_html=True)
            st.markdown("### 🛡️ Dominant Intelligence Output")
            
            k1, k2, k3 = st.columns(3)
            with k1: render_kpi("Priority", str(res.get('priority_label', 'N/A')).upper())
            with k2: render_kpi("Sentiment", str(res.get('sentiment_label', 'N/A')).title())
            with k3: render_kpi("NPS Profile", str(res.get('nps_type', 'Passive')))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("#### 🧠 Psychological & Behavioral Profile")
            m1, m2, m3, m4 = st.columns(4)
            m1.write(f"**Emotion:** `{str(res.get('emotion_label', 'N/A'))}`")
            m2.write(f"**Intent:** `{str(res.get('customer_intent_label', 'N/A'))}`")
            m3.write(f"**Language:** `{str(res.get('language_detected', 'N/A'))}`")
            m4.write(f"**Intensity:** `{res.get('tone_intensity_score', 0.0)}/10`")
            
            st.divider()
            
            st.write(f"**Primary Category:** `{str(res.get('primary_aspect_label', 'N/A'))}`  |  **Subcategory Threat:** `{str(res.get('subcategory_label', 'N/A'))}`")
            
            d1, d2 = st.columns(2)
            with d1:
                st.write("**Risk & Signal Flags:**")
                st.markdown(f"- **Churn Risk Detected:** {bool_badge(res.get('churn_risk', False), alert_red=True)}", unsafe_allow_html=True)
                st.markdown(f"- **Sarcasm Suspected:** {bool_badge(res.get('sarcasm_suspected', False), alert_red=True)}", unsafe_allow_html=True)
                st.markdown(f"- **Mixed Feedback:** {bool_badge(res.get('mixed_feedback', False))}", unsafe_allow_html=True)
                st.markdown(f"- **Urgent Language:** {bool_badge(res.get('urgent', False), alert_red=True)}", unsafe_allow_html=True)
            with d2:
                st.write("**Diagnostics:**")
                st.write(f"- **AI Conf:** `{float(res.get('bert_confidence', 0))*100:.1f}%`")
                st.write(f"- **Score:** `{res.get('priority_score', 0)}/100`")
                kw = res.get('matched_keywords', "")
                if kw and kw != "None":
                    st.markdown(" ".join([f'<span style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; margin: 2px; display: inline-block; color: #A5B4FC;">{k}</span>' for k in kw.split(", ")]), unsafe_allow_html=True)
            
            if 'absa_breakdown' in res and res['absa_breakdown'] and len(res['absa_breakdown']) > 1:
                st.divider()
                st.markdown("#### 🔍 Aspect-Based Breakdown (Clauses)")
                for i, clause in enumerate(res['absa_breakdown']):
                    c_sent = clause['sentiment'].upper()
                    color = "#10B981" if c_sent == "POSITIVE" else "#EF4444" if c_sent == "NEGATIVE" else "#6B7280"
                    st.markdown(f"""
                    <div class="absa-card">
                        <div style="color: #9CA3AF; font-size: 0.8rem; margin-bottom: 5px;">Clause {i+1}</div>
                        <div style="font-weight: 600; margin-bottom: 8px;">"{clause['clause_text']}"</div>
                        <span style="color: {color}; font-weight: 700; font-size: 0.8rem;">{c_sent}</span> 
                        <span style="color: #6B7280;">•</span> 
                        <span style="font-size: 0.8rem; color: #A5B4FC;">{clause['subcategory'].replace('_', ' ').title()}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.info(f"**Automated Action:** {res.get('action_recommendation', 'Log for standard reporting.')}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="block-card" style="height: 520px; display: flex; align-items: center; justify-content: center; text-align: center; border: 2px dashed #1F2937;"><div><div style="font-size: 4rem; margin-bottom: 24px;">💠</div><h2 style="color: #6366F1; font-weight: 800;">Neural Standby</h2><p style="color: #9CA3AF; max-width: 320px;">Awaiting data input from terminal to begin the audit process.</p></div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown("### 📂 Bulk Processing Workspace")
    file = st.file_uploader("Drop CSV or XLSX files", type=["csv", "xlsx"], label_visibility="collapsed")
    
    if file:
        df_input = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        detected_col = get_review_col(df_input)
        if detected_col:
            target_col = st.selectbox("Confirm Target Review Column", df_input.columns, index=list(df_input.columns).index(detected_col))
            if st.button("PROCESS DATASET", type="primary"):
                start = time.time()
                with st.spinner("Executing Batch Intelligence..."):
                    processed_res = analyze_dataframe(df_input, target_col)
                    if isinstance(processed_res, tuple) and len(processed_res) == 2:
                        st.session_state.batch_data = processed_res[0]
                        st.session_state.meta = processed_res[1]
                    else:
                        st.session_state.batch_data = processed_res
                        st.session_state.meta = {}
                st.session_state.proc_time = time.time() - start
        else:
            st.error("No valid columns found in the uploaded file.")

    if "batch_data" in st.session_state:
        b_df = st.session_state.batch_data
        st.divider()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Scanned Records", len(b_df))
        k2.metric("Negative Ratio", f"{(b_df['sentiment_label'] == 'negative').mean()*100:.1f}%" if 'sentiment_label' in b_df.columns else "0%")
        k3.metric("Critical Alerts", len(b_df[b_df['priority_label'] == 'Critical']) if 'priority_label' in b_df.columns else 0)
        k4.metric("Process Time", f"{st.session_state.get('proc_time', 0):.2f}s")
        
        st.dataframe(b_df, use_container_width=True)
        
        d_col1, d_col2 = st.columns(2)
        d_col1.download_button("📥 DOWNLOAD AUDIT REPORT (CSV)", data=b_df.to_csv(index=False).encode('utf-8'), file_name="ai_audit_report.csv", mime="text/csv")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer: b_df.to_excel(writer, index=False)
        d_col2.download_button("📥 DOWNLOAD AUDIT REPORT (XLSX)", data=output.getvalue(), file_name="ai_audit_report.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    if "batch_data" in st.session_state:
        d_df = st.session_state.batch_data
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Intelligence", len(d_df))
        c2.metric("Net Promoter Score", int(round(((d_df['nps_type']=='Promoter').mean() - (d_df['nps_type']=='Detractor').mean())*100, 0)) if 'nps_type' in d_df.columns else 0)
        c3.metric("High Churn Risk", st.session_state.meta.get('churn_risk_count', 0))
        c4.metric("Risk Segments", d_df['priority_label'].nunique() if 'priority_label' in d_df.columns else 0)
        
        st.divider()
        v1, v2 = st.columns(2)
        with v1:
            if 'sentiment_label' in d_df.columns:
                fig_p = px.pie(d_df, names='sentiment_label', hole=0.7, title="Dominant Sentiment Share", color_discrete_sequence=['#10B981', '#6B7280', '#EF4444'])
                fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
                st.plotly_chart(fig_p, use_container_width=True)
                
        with v2:
            if 'primary_aspect_label' in d_df.columns and 'subcategory_label' in d_df.columns:
                fig_s = px.sunburst(d_df, path=['primary_aspect_label', 'subcategory_label'], color='sentiment_label', 
                                    color_discrete_map={'positive': '#10B981', 'neutral': '#6B7280', 'negative': '#EF4444'},
                                    title="Hierarchical Threat Root Cause Analysis")
                fig_s.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, l=0, r=0, b=0))
                st.plotly_chart(fig_s, use_container_width=True)
                
        st.markdown('<div class="block-card">', unsafe_allow_html=True)
        st.subheader("💡 Strategic Summary")
        if PIPELINE_CONNECTED and 'sentiment_label' in d_df.columns:
            with st.spinner("Generating AI Briefing..."):
                st.write(generate_ai_summary(d_df.head(30)))
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Process a batch dataset to unlock strategic dashboard insights.")

st.markdown("<br><center style='color: #4B5563; font-size: 0.85rem;'>ENTERPRISE FEEDBACK INTELLIGENCE | MANAS 2026</center><br><br>", unsafe_allow_html=True)
