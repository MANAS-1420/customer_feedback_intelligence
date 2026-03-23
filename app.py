import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.pipeline import analyze_single, analyze_dataframe

st.set_page_config(
    page_title="Customer Feedback Intelligence System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    .hero-card {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #9333ea 100%);
        color: white;
        padding: 28px 30px;
        border-radius: 22px;
        box-shadow: 0 18px 40px rgba(79, 70, 229, 0.22);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #111827;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .soft-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(226,232,240,0.9);
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }

    .mini-note {
        color: #64748b;
        font-size: 0.93rem;
        margin-top: -0.15rem;
        margin-bottom: 0.85rem;
    }

    .info-chip-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .info-chip {
        background: #eef2ff;
        color: #3730a3;
        border: 1px solid #c7d2fe;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .priority-badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        color: white;
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        margin-top: 2px;
        margin-bottom: 8px;
    }

    .priority-low {
        background: #10b981;
    }

    .priority-medium {
        background: #f59e0b;
    }

    .priority-high {
        background: #f97316;
    }

    .priority-critical {
        background: #ef4444;
    }

    .reason-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #6366f1;
        border-radius: 14px;
        padding: 14px 16px;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .metric-caption {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: -3px;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #4f46e5, #9333ea);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1.2rem;
        font-weight: 700;
        height: 46px;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.18);
    }

    div.stButton > button:hover {
        filter: brightness(1.03);
    }

    div[data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 14px;
        padding: 4px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 10px 12px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }

    .footer-note {
        color: #64748b;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 18px;
    }
</style>
""", unsafe_allow_html=True)


def pretty_label(x: str) -> str:
    return str(x).replace("_", " ").title()


def detect_review_column(columns):
    possible_text_cols = [
        "Review", "review", "Reviews", "reviews",
        "Comment", "comment", "Comments", "comments",
        "Feedback", "feedback",
        "Text", "text",
        "Message", "message",
        "Complaint", "complaint",
        "Customer Review", "customer review",
        "Customer_Review", "customer_review"
    ]

    for col in possible_text_cols:
        if col in columns:
            return col

    lowered = {c.lower(): c for c in columns}
    keywords = ["review", "reviews", "comment", "comments", "feedback", "text", "message", "complaint"]

    for low_col, original_col in lowered.items():
        for kw in keywords:
            if kw in low_col:
                return original_col

    return None


def priority_badge(priority_label: str) -> str:
    priority_label = str(priority_label).lower()
    cls = f"priority-{priority_label}"
    text = pretty_label(priority_label)
    return f'<span class="priority-badge {cls}">{text}</span>'


def build_reason_text(result: dict) -> str:
    reason_parts = []

    if result.get("matched_keywords"):
        reason_parts.append(f"Matched keywords: {result['matched_keywords']}")

    if result.get("urgent"):
        reason_parts.append("Urgency signal detected")

    if result.get("strong_negative"):
        reason_parts.append("Strong negative phrase detected")

    if result.get("has_phone") or result.get("has_email"):
        signals = []
        if result.get("has_phone"):
            signals.append("phone number")
        if result.get("has_email"):
            signals.append("email")
        reason_parts.append("Contact signal detected: " + ", ".join(signals))

    reason_parts.append(
        f"Sentiment source: {result.get('sentiment_source', 'N/A')} "
        f"(confidence: {result.get('bert_confidence', 0)})"
    )

    return " | ".join(reason_parts)


st.markdown("""
<div class="hero-card">
    <div class="hero-title">Customer Feedback Intelligence System</div>
    <div class="hero-subtitle">
        Hybrid multilingual analysis using Rule Engine + Pre-trained BERT
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Single Review Analysis", "Batch CSV / Excel Analysis"])

with tab1:
    st.markdown('<div class="section-title">Analyze a single customer review</div>', unsafe_allow_html=True)
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)

    review_text = st.text_area(
        "Enter customer review",
        height=160,
        placeholder="Example: You guys are cheaters, support never replied and I still have not received my refund..."
    )

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Analyze Review", use_container_width=False):
        if review_text.strip():
            start_time = time.time()

            with st.spinner("Analyzing review..."):
                result = analyze_single(review_text)

            elapsed_time = round(time.time() - start_time, 3)

            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Prediction Summary</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Aspect", pretty_label(result["primary_aspect_label"]))
            c2.metric("Emotion", pretty_label(result["emotion_label"]))
            c3.metric("Priority", pretty_label(result["priority_label"]))

            c4, c5, c6 = st.columns(3)
            c4.metric("Intent", pretty_label(result["customer_intent_label"]))
            c5.metric("Aspect Sentiment", pretty_label(result["aspect_sentiment_label"]))
            c6.metric("Sentiment", pretty_label(result["sentiment_label"]))

            st.markdown(priority_badge(result["priority_label"]), unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="reason-box">
                    <strong>Why this result?</strong><br>
                    {build_reason_text(result)}
                </div>
                """,
                unsafe_allow_html=True
            )

            chip_html = f"""
            <div class="info-chip-wrap">
                <span class="info-chip">Sentiment Source: {result['sentiment_source']}</span>
                <span class="info-chip">BERT Confidence: {result['bert_confidence']}</span>
                <span class="info-chip">Priority Score: {result['priority_score']}</span>
                <span class="info-chip">Processing Time: {elapsed_time}s</span>
            </div>
            """
            st.markdown(chip_html, unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="mini-note">
                    Regex Flags → Phone: {result['has_phone']} | Email: {result['has_email']} |
                    Strong Negative: {result['strong_negative']} | Urgent: {result['urgent']}
                </div>
                """,
                unsafe_allow_html=True
            )

            if result["priority_label"] == "critical":
                st.error("🚨 Critical issue detected. Immediate action is recommended.")
            elif result["priority_label"] == "high":
                st.warning("⚠️ High priority issue detected. Fast follow-up is recommended.")
            elif result["priority_label"] == "medium":
                st.info("ℹ️ Medium priority issue detected. Follow-up may be required.")
            else:
                st.success("✅ Low priority issue detected.")

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter review text.")

with tab2:
    st.markdown('<div class="section-title">Batch analysis for CSV / Excel files</div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-note">Supported file types: CSV, XLSX, XLS</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            file_name = uploaded_file.name

            if file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format.")
                st.stop()

            st.success(f"Loaded file: {file_name}")

            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Uploaded File Preview</div>', unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)

            auto_detected_col = detect_review_column(df.columns.tolist())

            if auto_detected_col:
                st.info(f"Auto-detected review column: `{auto_detected_col}`")
            else:
                st.warning("Could not auto-detect the review column. Please select manually.")

            selected_col = st.selectbox(
                "Select the review/comment column",
                options=df.columns.tolist(),
                index=df.columns.tolist().index(auto_detected_col) if auto_detected_col in df.columns.tolist() else 0
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Process File"):
                start_time = time.time()

                progress_bar = st.progress(10)
                status_text = st.empty()
                status_text.write("Preparing analysis...")

                progress_bar.progress(30)
                status_text.write("Running NLP pipeline...")
                result_df = analyze_dataframe(df, text_col=selected_col)

                progress_bar.progress(75)
                status_text.write("Computing dashboard insights...")

                total_reviews = len(result_df)
                critical_count = (result_df["priority_label"] == "critical").sum()
                high_count = (result_df["priority_label"] == "high").sum()
                top_aspect = result_df["primary_aspect_label"].value_counts().idxmax()
                elapsed_time = round(time.time() - start_time, 2)

                progress_bar.progress(100)
                status_text.write(f"✅ Processing complete in {elapsed_time} seconds.")

                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Business Snapshot</div>', unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Reviews", total_reviews)
                m2.metric("Critical Issues", critical_count)
                m3.metric("High Priority", high_count)
                m4.metric("Processing Time", f"{elapsed_time}s")

                st.markdown(
                    f"""
                    <div class="reason-box">
                        <strong>Top Issue</strong><br>
                        {pretty_label(top_aspect)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Output Preview</div>', unsafe_allow_html=True)
                st.dataframe(result_df.head(100), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Analytics Dashboard</div>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    fig1, ax1 = plt.subplots(figsize=(6, 4))
                    result_df["primary_aspect_label"].value_counts().plot(kind="bar", ax=ax1)
                    ax1.set_title("Aspect Distribution")
                    ax1.set_xlabel("Aspect")
                    ax1.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig1, use_container_width=True)

                with col2:
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    result_df["priority_label"].value_counts().plot(kind="bar", ax=ax2)
                    ax2.set_title("Priority Distribution")
                    ax2.set_xlabel("Priority")
                    ax2.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig2, use_container_width=True)

                col3, col4 = st.columns(2)

                with col3:
                    fig3, ax3 = plt.subplots(figsize=(6, 4))
                    result_df["emotion_label"].value_counts().plot(kind="bar", ax=ax3)
                    ax3.set_title("Emotion Distribution")
                    ax3.set_xlabel("Emotion")
                    ax3.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig3, use_container_width=True)

                with col4:
                    fig4, ax4 = plt.subplots(figsize=(6, 4))
                    result_df["customer_intent_label"].value_counts().plot(kind="bar", ax=ax4)
                    ax4.set_title("Intent Distribution")
                    ax4.set_xlabel("Intent")
                    ax4.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig4, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Business Insights</div>', unsafe_allow_html=True)
                st.write(f"- Total reviews analyzed: **{total_reviews}**")
                st.write(f"- Critical issues: **{critical_count}**")
                st.write(f"- High priority issues: **{high_count}**")
                st.write(f"- Top aspect: **{pretty_label(top_aspect)}**")
                st.write(f"- Processing completed in: **{elapsed_time} seconds**")

                if critical_count > 0:
                    st.error(f"🚨 {critical_count} critical issues detected in uploaded data.")

                csv_bytes = result_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Results CSV",
                    data=csv_bytes,
                    file_name="customer_feedback_output.csv",
                    mime="text/csv"
                )
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error while processing file: {e}")

st.markdown('<div class="footer-note">Built with Streamlit • Hybrid NLP • Multilingual Review Intelligence</div>', unsafe_allow_html=True)
