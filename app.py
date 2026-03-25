import time
import streamlit as st
import pandas as pd
import plotly.express as px
from src.pipeline import analyze_single, analyze_dataframe

# --- CONFIG ---
st.set_page_config(
    page_title="Feedback Intel AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top left, #0d1b36 0%, #081226 45%, #050a16 100%);
        color: #E5E7EB;
    }
    .hero {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 45%, #9333EA 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 15px 35px rgba(76, 29, 149, 0.3);
        text-align: center;
    }
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid #243247;
        border-radius: 15px;
        padding: 15px;
        backdrop-filter: blur(10px);
    }
    .priority-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        color: white;
    }
    .p-critical { background-color: #EF4444; }
    .p-high { background-color: #F97316; }
    .p-medium { background-color: #F59E0B; }
    .p-low { background-color: #10B981; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Controls")
    st.info("This system uses a Hybrid BERT + Rule-Engine approach for maximum accuracy in Hinglish.")
    st.divider()
    st.markdown("### Model Settings")
    use_bert_batch = st.checkbox("Use BERT for Batch (Slower)", value=False)
    st.caption("Tip: Rule-engine is 10x faster for large CSVs.")

# --- HEADER ---
st.markdown('<div class="hero"><h1>🚀 Customer Feedback Intelligence</h1><p>Multilingual Sentiment, Aspect, and Business Analytics Dashboard</p></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🧠 Single Analysis", "📊 Batch Processing"])

# --- TAB 1: SINGLE ANALYSIS ---
with tab1:
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Input Review")
        review_input = st.text_area("Enter Customer Feedback (English/Hindi/Hinglish):", height=150, placeholder="Example: Payment fail ho gaya aur refund bhi nahi mila. Very bad support!")
        if st.button("🚀 Run AI Analysis", use_container_width=True):
            if review_input.strip():
                with st.spinner("Processing..."):
                    st.session_state['single_result'] = analyze_single(review_input)
            else:
                st.warning("Please enter some text first.")

    with col_out:
        st.subheader("Intelligence Output")
        if 'single_result' in st.session_state:
            res = st.session_state['single_result']
            
            # Priority Badge Logic
            p_class = f"p-{res['priority_label']}"
            st.markdown(f"**Priority:** <span class='priority-badge {p_class}'>{res['priority_label'].upper()}</span>", unsafe_allow_html=True)
            
            m1, m2 = st.columns(2)
            m1.metric("Sentiment", res['sentiment_label'].title())
            m2.metric("Aspect", res['primary_aspect_label'].replace("_", " ").title())
            
            m3, m4 = st.columns(2)
            m3.metric("Emotion", res['emotion_label'].title())
            m4.metric("Intent", res['customer_intent_label'].replace("_", " ").title())
            
            st.write(f"**Confidence:** {res['bert_confidence']*100:.1f}% ({res['sentiment_source']})")
            st.write(f"**Keywords Detected:** `{res['matched_keywords']}`")
        else:
            st.info("Enter a review and click Analyze to see results.")

# --- TAB 2: BATCH PROCESSING ---
with tab2:
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.write(f"Loaded {len(df)} rows.")
        
        text_col = st.selectbox("Select Review Column", options=df.columns)
        
        if st.button("📈 Process Batch Data"):
            start = time.time()
            with st.spinner("Analyzing large dataset..."):
                processed_df = analyze_dataframe(df, text_col=text_col, use_bert=use_bert_batch)
                
            elapsed = time.time() - start
            st.success(f"Processed {len(df)} reviews in {elapsed:.2f} seconds.")
            
            # KPI Metrics
            k1, k2, k3 = st.columns(3)
            neg_pct = (processed_df['sentiment_label'] == 'negative').mean() * 100
            crit_count = (processed_df['priority_label'] == 'critical').sum()
            
            k1.metric("Negative Ratio", f"{neg_pct:.1f}%")
            k2.metric("Critical Issues", crit_count)
            k3.metric("Top Aspect", processed_df['primary_aspect_label'].value_counts().index[0])
            
            # Charts
            c1, c2 = st.columns(2)
            fig_sent = px.pie(processed_df, names='sentiment_label', title="Sentiment Breakdown", hole=0.4)
            c1.plotly_chart(fig_sent, use_container_width=True)
            
            fig_aspect = px.bar(processed_df['primary_aspect_label'].value_counts(), title="Issues by Category")
            c2.plotly_chart(fig_aspect, use_container_width=True)
            
            # Download
            csv = processed_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Analyzed Data", data=csv, file_name="analysis_results.csv", mime="text/csv")

st.markdown("---")
st.caption("Built for Manas's Portfolio | Hybrid Multilingual NLP Engine")
