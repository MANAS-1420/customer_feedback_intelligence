import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import time

# Attempting imports from local pipeline
try:
    from src.pipeline import analyze_single, analyze_dataframe
except ImportError:
    # Fallback mock functions if pipeline.py is not in src/ or named differently
    def analyze_single(text):
        return {"sentiment_label": "neutral", "priority_label": "low", "primary_aspect_label": "general"}
    def analyze_dataframe(df, col):
        return df.assign(sentiment_label="neutral"), {}

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Feedback Intel AI | Enterprise Dashboard",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PREMIUM DARK THEME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #6366F1;
        --bg-dark: #0B0F1A;
        --card-bg: rgba(17, 25, 40, 0.75);
        --border: rgba(255, 255, 255, 0.1);
        --text-main: #F3F4F6;
        --text-muted: #9CA3AF;
    }

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }

    .stApp {
        background: var(--bg-dark);
        background-image: radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.05) 1px, transparent 0);
        background-size: 40px 40px;
    }

    /* Modern Card Glassmorphism */
    .premium-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px) saturate(180%);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Metrics / KPI Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border);
        padding: 15px !important;
        border-radius: 16px;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px 12px 0 0;
        padding: 0 24px;
        color: var(--text-muted);
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
    }

    /* Inputs */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid var(--border) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    /* Sidebar Fixes */
    section[data-testid="stSidebar"] {
        background-color: #0D111C !important;
        border-right: 1px solid var(--border);
    }

    /* Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-critical { background: #7F1D1D; color: #FCA5A5; }
    .badge-high { background: #7C2D12; color: #FDBA74; }
    .badge-pos { background: #064E3B; color: #6EE7B7; }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def safe_get(data, key, default="N/A"):
    val = data.get(key, default)
    return val if val is not None else default

def format_bool(val):
    return "✅ Yes" if val is True else "❌ No"

def detect_review_col(columns):
    targets = ['review', 'reviews', 'comment', 'comments', 'feedback', 'text', 'message', 'complaint', 'remark']
    for c in columns:
        if c.lower() in targets:
            return c
    return columns[0] if len(columns) > 0 else None

def render_kpi(label, value, icon=""):
    st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #9CA3AF; font-size: 0.8rem; margin: 0;">{icon} {label}</p>
            <h2 style="margin: 0; font-weight: 800;">{value}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR CONTENT ---
with st.sidebar:
    st.markdown("<h1 style='color: #6366F1;'>💠 Feedback Intel</h1>", unsafe_allow_html=True)
    st.markdown("### Multilingual Decision Support")
    st.divider()
    st.info("System identifies Sentiment, Aspect, Emotion, and Priority in English, Hindi, and Hinglish.")
    st.markdown("---")
    st.caption("v4.0.0 Stable Build")
    st.caption("Engine: Hybrid BERT + Regex")

# --- 5. HEADER SECTION ---
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-weight: 800; letter-spacing: -1px; margin-bottom: 0;">Customer Feedback <span style="color: #6366F1;">Intelligence System</span></h1>
        <p style="color: #9CA3AF; font-size: 1.1rem;">Enterprise-grade sentiment audit and business intelligence dashboard.</p>
    </div>
""", unsafe_allow_html=True)

# --- 6. MAIN APP TABS ---
tab_single, tab_batch, tab_dashboard = st.tabs([
    "🎯 Single Review Analysis", 
    "📦 Batch Processing", 
    "📊 Strategic Insights"
])

# --- TAB 1: SINGLE ANALYSIS ---
with tab_single:
    col_input, col_result = st.columns([1, 1.3], gap="large")
    
    with col_input:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("Input Terminal")
        review_input = st.text_area(
            "Enter customer text (English, Hindi, or Hinglish):", 
            height=200, 
            placeholder="Example: Order late ho gaya, support team is not responding. Please help!",
            key="single_input"
        )
        
        btn_col1, btn_col2 = st.columns([1, 1])
        if btn_col1.button("🚀 Analyze Now"):
            if review_input.strip():
                with st.spinner("Neural audit in progress..."):
                    st.session_state.single_res = analyze_single(review_input)
            else:
                st.warning("Please provide input text first.")
        if btn_col2.button("🧹 Clear"):
            st.session_state.single_res = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        if "single_res" in st.session_state and st.session_state.single_res:
            res = st.session_state.single_res
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            
            # KPI Header
            k1, k2, k3 = st.columns(3)
            with k1: render_kpi("Sentiment", safe_get(res, 'sentiment_label').upper(), "🎭")
            with k2: render_kpi("Priority", safe_get(res, 'priority_label').upper(), "🚨")
            with k3: render_kpi("Aspect", safe_get(res, 'primary_aspect_label').title(), "🏷️")
            
            st.divider()
            
            # Secondary Details
            d1, d2, d3 = st.columns(3)
            d1.write(f"**Emotion:** `{safe_get(res, 'emotion_label').title()}`")
            d2.write(f"**Intent:** `{safe_get(res, 'customer_intent_label').title()}`")
            d3.write(f"**NPS Type:** `{safe_get(res, 'nps_type', 'Neutral')}`")

            st.markdown("---")
            
            # Technical Panel
            t1, t2 = st.columns(2)
            with t1:
                st.write(f"**AI Confidence:** `{float(safe_get(res, 'bert_confidence', 0))*100:.1f}%`")
                st.write(f"**Source:** `{safe_get(res, 'sentiment_source', 'Hybrid')}`")
            with t2:
                st.write(f"**Has Phone:** {format_bool(res.get('has_phone'))}")
                st.write(f"**Urgent Flag:** {format_bool(res.get('urgent'))}")

            st.info(f"**Recommendation:** {safe_get(res, 'action_recommendation', 'Standard Follow-up')}")
            
            with st.expander("🔍 View Explainability / Reasoning"):
                st.write(f"**Detected Keywords:** `{safe_get(res, 'matched_keywords', [])}`")
                st.write(f"**Reasoning:** {safe_get(res, 'reasoning', 'Determined by hybrid pattern matching and BERT context analysis.')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="height: 400px; display: flex; align-items: center; justify-content: center; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;">
                    <p style="color: #6B7280;">Awaiting Input for Real-Time Audit...</p>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 2: BATCH PROCESSING ---
with tab2:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Enterprise Data (CSV, XLSX, XLS)", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            
            st.success(f"File loaded successfully: {len(df_raw)} records detected.")
            
            # Column detection
            auto_col = detect_review_col(df_raw.columns)
            text_col = st.selectbox("Confirm the Review/Comment column:", df_raw.columns, index=list(df_raw.columns).index(auto_col) if auto_col else 0)
            
            if st.button("📈 Start Batch Intelligent Audit"):
                start_time = time.time()
                with st.spinner("Processing Large-Scale Dataset..."):
                    # Process row by row if specific batch function isn't provided
                    results_list = []
                    progress_bar = st.progress(0)
                    for i, row in enumerate(df_raw[text_col]):
                        results_list.append(analyze_single(str(row)))
                        progress_bar.progress((i + 1) / len(df_raw))
                    
                    df_res = pd.concat([df_raw, pd.DataFrame(results_list)], axis=1)
                    st.session_state.batch_df = df_res
                    st.session_state.process_time = time.time() - start_time
                st.success("Analysis Complete!")
        except Exception as e:
            st.error(f"Data loading error: {e}")

    if "batch_df" in st.session_state:
        b_df = st.session_state.batch_df
        
        # KPI Bar
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Rows", len(b_df))
        neg_p = (b_df['sentiment_label'] == 'negative').mean() * 100
        k2.metric("Negative %", f"{neg_p:.1f}%")
        k3.metric("Critical Items", len(b_df[b_df['priority_label'] == 'critical']))
        k4.metric("Avg AI Conf", f"{b_df['bert_confidence'].mean()*100:.1f}%")
        k5.metric("Proc Time", f"{st.session_state.process_time:.2f}s")

        st.dataframe(b_df.head(100), use_container_width=True)
        
        # Downloads
        d_col1, d_col2 = st.columns(2)
        csv = b_df.to_csv(index=False).encode('utf-8')
        d_col1.download_button("📥 Download Result (CSV)", data=csv, file_name="analyzed_feedback.csv", mime="text/csv")
        
        # Buffer for Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            b_df.to_excel(writer, index=False)
        d_col2.download_button("📥 Download Result (Excel)", data=output.getvalue(), file_name="analyzed_feedback.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: DASHBOARD & STRATEGIC INSIGHTS ---
with tab_dashboard:
    if "batch_df" in st.session_state:
        df = st.session_state.batch_df
        
        # Row 1: Key Performance Indicators
        st.markdown("### 💠 Enterprise Performance Pulse")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Net Sentiment Score", f"{((df['sentiment_label']=='positive').mean() - (df['sentiment_label']=='negative').mean())*100:.1f}")
        m2.metric("Critical Resolution Queue", len(df[df['priority_label']=='critical']))
        m3.metric("Mixed Signal Density", f"{(df.get('mixed_feedback_flag', pd.Series([0])).mean())*100:.1f}%")
        m4.metric("Dominant Aspect", df['primary_aspect_label'].mode()[0].title())

        # Row 2: Main Charts
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            fig_sent = px.pie(df, names='sentiment_label', title="Sentiment Distribution", hole=0.5,
                             color_discrete_map={'positive': '#10B981', 'neutral': '#6B7280', 'negative': '#EF4444'})
            fig_sent.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_sent, use_container_width=True)
            
        with c2:
            fig_asp = px.bar(df['primary_aspect_label'].value_counts().reset_index(), x='count', y='primary_aspect_label', 
                            orientation='h', title="Top Concerns by Aspect", color='count', color_continuous_scale='Purples')
            fig_asp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_asp, use_container_width=True)

        # Row 3: Secondary Charts
        c3, c4 = st.columns(2)
        with c3:
            fig_emo = px.treemap(df, path=['emotion_label'], title="Customer Emotional Map")
            fig_emo.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_emo, use_container_width=True)
        with c4:
            fig_pri = px.histogram(df, x='priority_label', title="Priority Matrix Distribution", color='priority_label',
                                  color_discrete_map={'critical': '#7F1D1D', 'high': '#7C2D12', 'medium': '#92400E', 'low': '#064E3B'})
            fig_pri.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pri, use_container_width=True)

        # Row 4: Strategic Panels
        st.divider()
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("💡 Strategic AI Summary")
        st.write(f"The analysis indicates a dominant **{df['sentiment_label'].mode()[0]}** sentiment focused primarily on **{df['primary_aspect_label'].mode()[0]}**. "
                 f"Approximately **{len(df[df['priority_label']=='critical'])}** issues are flagged for immediate legal or management intervention.")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Please process a batch file in the 'Batch Processing' tab to view strategic dashboard insights.")
        st.markdown("""
            <div style="height: 400px; display: flex; align-items: center; justify-content: center; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;">
                <p style="color: #6B7280;">No Batch Data Detected for Dashboard Rendering.</p>
            </div>
        """, unsafe_allow_html=True)

# --- 7. FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #4B5563;'>Enterprise Dashboard | Powered by Hybrid Transformer Architecture | Developed by Manas</div>", 
    unsafe_allow_html=True
)
