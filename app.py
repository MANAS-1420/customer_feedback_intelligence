import streamlit as st
import pandas as pd
import plotly.express as px
from src.pipeline import analyze_single, analyze_dataframe
from src.bert_model import generate_ai_summary

# --- CONFIG ---
st.set_page_config(page_title="Feedback Intel AI", page_icon="💠", layout="wide")

# --- CSS (Same as before, but added transition for smooth loading) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #F3F4F6; }
    .stApp { background: #0B0F1A; }
    .premium-card {
        background: rgba(17, 25, 40, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        transition: all 0.5s ease-in-out;
    }
    .gradient-text {
        background: linear-gradient(90deg, #A5B4FC, #E879F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
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

with tab1:
    # We change the column structure slightly to prevent the "empty box" look
    col_input, col_output = st.columns([1, 1.4], gap="large")
    
    with col_input:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### ✍️ Input Console")
        review_text = st.text_area("Customer Review", height=200, placeholder="Paste feedback here...", label_visibility="collapsed")
        analyze_btn = st.button("EXECUTE AI AUDIT", use_container_width=True)
        
        if analyze_btn:
            if review_text.strip():
                with st.spinner("Decoding..."):
                    st.session_state.result = analyze_single(review_text)
            else:
                st.warning("Please enter text to analyze.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_output:
        # --- KEY CHANGE: ONLY RENDER IF RESULT EXISTS ---
        if "result" in st.session_state:
            res = st.session_state.result
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown("### 🛡️ Analysis Engine Output")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Priority", res['priority_label'].upper())
            m2.metric("Sentiment", res['sentiment_label'].title())
            m3.metric("Category", res['primary_aspect_label'].replace("_", " ").title())
            
            st.markdown("---")
            ca, cb, cc = st.columns(3)
            ca.write(f"**Emotion:** `{res['emotion_label'].title()}`")
            cb.write(f"**Intent:** `{res['customer_intent_label'].title()}`")
            cc.write(f"**Confidence:** `{res['bert_confidence']*100:.1f}%`")

            st.write("**🔍 Keywords Detected:**")
            if res['matched_keywords']:
                kw_html = "".join([f'<span class="keyword-chip">{k}</span>' for k in res['matched_keywords'].split(",")])
                st.markdown(kw_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if res['priority_label'] == 'critical': st.error("🚨 **CRITICAL ALERT:** Escalating to Customer Relations Head.")
            elif res['priority_label'] == 'high': st.warning("⚠️ **ACTION:** Requires 4-hour turnaround response.")
            else: st.success("✅ **STABLE:** Categorized for weekly report.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # --- LANDING STATE: NICE TIP INSTEAD OF EMPTY BOX ---
            st.markdown("""
            <div class="premium-card" style="display: flex; align-items: center; justify-content: center; text-align: center;">
                <div>
                    <h2 style="color: #6366F1; margin-bottom: 10px;">Ready for Intelligence?</h2>
                    <p style="color: #9CA3AF;">Enter a customer review on the left to begin the Neural Audit.</p>
                    <p style="font-size: 0.8rem; color: #4B5563;">Tip: Use Hinglish (Hindi + English) for localized accuracy.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    # Similar logic for Batch processing
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    up_file = st.file_uploader("Upload Bulk Dataset", type=["csv", "xlsx"])
    if up_file:
        df = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
        text_col = st.selectbox("Select Target Column", df.columns)
        if st.button("PROCESS BULK DATA"):
            res_df = analyze_dataframe(df, text_col=text_col)
            st.session_state.batch_res = res_df

    if "batch_res" in st.session_state:
        res_df = st.session_state.batch_res
        st.divider()
        st.subheader("✨ AI Global Summary (Gemini 1.5)")
        summary = generate_ai_summary(res_df.head(15))
        st.markdown(f'<div style="background: rgba(99,102,241,0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #6366F1;">{summary}</div>', unsafe_allow_html=True)
        
        v1, v2 = st.columns(2)
        v1.plotly_chart(px.pie(res_df, names='sentiment_label', hole=0.6, color_discrete_sequence=['#EF4444', '#6B7280', '#10B981']), use_container_width=True)
        v2.plotly_chart(px.bar(res_df['primary_aspect_label'].value_counts(), title="Top Issues"), use_container_width=True)
        st.dataframe(res_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 👨‍💻 Developed by Manas")
    st.markdown("[🔗 GitHub Portfolio](https://github.com/MANAS-1420)")
    st.divider()
    st.caption("Hybrid Multilingual NLP v3.1")
