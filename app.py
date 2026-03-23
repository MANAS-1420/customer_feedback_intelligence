import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.pipeline import analyze_single, analyze_dataframe

st.set_page_config(
    page_title="Customer Feedback Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# HELPERS
# -----------------------------
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
    p = str(priority_label).lower()
    return f'<span class="priority-badge priority-{p}">{pretty_label(priority_label)}</span>'


def build_reason_text(result: dict) -> str:
    parts = []

    if result.get("matched_keywords"):
        parts.append(f"Matched keywords: {result['matched_keywords']}")

    if result.get("urgent"):
        parts.append("Urgency signal detected")

    if result.get("strong_negative"):
        parts.append("Strong negative phrase detected")

    if result.get("has_phone") or result.get("has_email"):
        signals = []
        if result.get("has_phone"):
            signals.append("phone")
        if result.get("has_email"):
            signals.append("email")
        parts.append("Contact signal detected: " + ", ".join(signals))

    parts.append(
        f"Sentiment source: {result.get('sentiment_source', 'N/A')} "
        f"(confidence: {result.get('bert_confidence', 0)})"
    )

    return " | ".join(parts)


def action_recommendation(priority_label: str) -> str:
    p = str(priority_label).lower()
    if p == "critical":
        return "Immediate escalation required"
    if p == "high":
        return "Assign to senior agent and follow up quickly"
    if p == "medium":
        return "Standard follow-up recommended"
    return "No urgent action needed"


def detect_mixed_feedback(text: str) -> bool:
    t = str(text).lower()
    markers = [" but ", " however ", " although ", " though ", "lekin", " par ", "but still"]
    return any(m in t for m in markers)


def sentiment_to_nps(sentiment_label: str):
    s = str(sentiment_label).lower()
    if s == "positive":
        return "Promoter", 9
    if s == "neutral":
        return "Passive", 7
    return "Detractor", 3


def batch_summary(result_df: pd.DataFrame) -> str:
    if result_df.empty:
        return "No reviews were processed."

    top_aspect = pretty_label(result_df["primary_aspect_label"].value_counts().idxmax())
    top_intent = pretty_label(result_df["customer_intent_label"].value_counts().idxmax())
    top_emotion = pretty_label(result_df["emotion_label"].value_counts().idxmax())
    negative_pct = round((result_df["sentiment_label"] == "negative").mean() * 100, 1)
    critical_pct = round((result_df["priority_label"] == "critical").mean() * 100, 1)

    return (
        f"Most reviews are centered around **{top_aspect}**, with **{top_intent}** as the most common intent. "
        f"The dominant customer emotion is **{top_emotion}**. "
        f"Negative sentiment accounts for **{negative_pct}%** of reviews, while **{critical_pct}%** are critical issues."
    )


def compute_nps(result_df: pd.DataFrame):
    nps_types = result_df["sentiment_label"].apply(lambda x: sentiment_to_nps(x)[0])
    promoters = (nps_types == "Promoter").mean() * 100
    detractors = (nps_types == "Detractor").mean() * 100
    nps_value = round(promoters - detractors, 1)
    return nps_value, nps_types


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("## ⚙️ Settings")
theme = st.sidebar.selectbox("🎨 Select Theme", ["Light", "Dark"])
st.sidebar.markdown("Use Light or Dark mode for better viewing.")
st.sidebar.markdown("---")
st.sidebar.markdown("## 📌 Usage")
st.sidebar.markdown("- **Single Review** → analyze one review")
st.sidebar.markdown("- **Batch Analysis** → upload CSV / Excel")
st.sidebar.markdown("- Supported formats: **CSV, XLSX, XLS**")
st.sidebar.markdown("---")
st.sidebar.markdown("## 💡 What this app does")
st.sidebar.markdown("- Sentiment analysis")
st.sidebar.markdown("- Aspect detection")
st.sidebar.markdown("- Emotion + intent classification")
st.sidebar.markdown("- Priority scoring")
st.sidebar.markdown("- Business dashboard + NPS")

# -----------------------------
# THEME VALUES
# -----------------------------
if theme == "Light":
    bg = "#f5f7fb"
    text = "#111827"
    subtext = "#6b7280"
    card_bg = "rgba(255,255,255,0.97)"
    border = "#e5e7eb"
    textarea_bg = "#ffffff"
    metric_bg = "#ffffff"
    sidebar_bg = "#ffffff"
    sidebar_text = "#111827"
    uploader_bg = "#ffffff"
    muted_bg = "#f8fafc"
    select_bg = "#ffffff"
    option_hover_bg = "#f3f4f6"
else:
    bg = "#0f172a"
    text = "#e5e7eb"
    subtext = "#94a3b8"
    card_bg = "rgba(17,24,39,0.96)"
    border = "#334155"
    textarea_bg = "#020617"
    metric_bg = "#111827"
    sidebar_bg = "#111827"
    sidebar_text = "#e5e7eb"
    uploader_bg = "#111827"
    muted_bg = "#0b1220"
    select_bg = "#1f2937"
    option_hover_bg = "#374151"

# -----------------------------
# CSS
# -----------------------------
st.markdown(f"""
<style>
    .stApp {{
        background: {bg};
        color: {text};
    }}

    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        min-width: 290px !important;
        max-width: 290px !important;
        background: {sidebar_bg} !important;
        overflow-y: auto !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background: {sidebar_bg} !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1rem !important;
    }}

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {{
        color: {sidebar_text} !important;
    }}

    /* Selectbox fix */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {{
        background: {select_bg} !important;
        border-radius: 10px !important;
        color: {sidebar_text} !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: {select_bg} !important;
        color: {sidebar_text} !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        color: {sidebar_text} !important;
        caret-color: {sidebar_text} !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
        color: {sidebar_text} !important;
    }}

    div[role="listbox"] {{
        background: {select_bg} !important;
        border: 1px solid {border} !important;
    }}

    div[role="option"] {{
        background: {select_bg} !important;
        color: {sidebar_text} !important;
    }}

    div[role="option"]:hover {{
        background: {option_hover_bg} !important;
        color: {sidebar_text} !important;
    }}

    button[title="Collapse sidebar"] {{
        color: {sidebar_text} !important;
    }}

    [data-testid="collapsedControl"] {{
        color: {sidebar_text} !important;
    }}

    /* Header */
    .hero-card {{
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #9333ea 100%);
        color: white;
        padding: 28px 30px;
        border-radius: 22px;
        box-shadow: 0 18px 40px rgba(79, 70, 229, 0.22);
        margin-bottom: 1rem;
    }}

    .hero-title {{
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.35rem;
        color: white !important;
    }}

    .hero-subtitle {{
        font-size: 1rem;
        opacity: 0.96;
        color: white !important;
    }}

    .section-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {text};
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }}

    .soft-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }}

    .mini-note {{
        color: {subtext};
        font-size: 0.93rem;
        margin-top: -0.15rem;
        margin-bottom: 0.85rem;
    }}

    .info-chip-wrap {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
        margin-bottom: 8px;
    }}

    .info-chip {{
        background: #eef2ff;
        color: #3730a3 !important;
        border: 1px solid #c7d2fe;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
    }}

    .priority-badge {{
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        color: white !important;
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        margin-top: 2px;
        margin-bottom: 8px;
    }}

    .priority-low {{ background: #10b981; }}
    .priority-medium {{ background: #f59e0b; }}
    .priority-high {{ background: #f97316; }}
    .priority-critical {{ background: #ef4444; }}

    .reason-box {{
        background: {muted_bg};
        border: 1px solid {border};
        border-left: 5px solid #6366f1;
        border-radius: 14px;
        padding: 14px 16px;
        color: {text};
        margin-top: 10px;
        margin-bottom: 10px;
    }}

    div.stButton > button {{
        background: linear-gradient(90deg, #4f46e5, #9333ea);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1.2rem;
        font-weight: 700;
        height: 46px;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.18);
    }}

    div.stButton > button:hover {{
        filter: brightness(1.03);
    }}

    div[data-testid="stMetric"] {{
        background: {metric_bg};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 10px 12px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }}

    div[data-testid="stFileUploader"] {{
        background: {uploader_bg};
        border-radius: 14px;
        padding: 4px;
    }}

    button[data-baseweb="tab"] {{
        color: {text} !important;
        font-weight: 700;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #4f46e5 !important;
        border-bottom: 3px solid #4f46e5 !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label, span, div {{
        color: {text};
    }}

    textarea {{
        border-radius: 14px !important;
        border: 1px solid {border} !important;
        padding: 12px !important;
        background-color: {textarea_bg} !important;
        color: {text} !important;
        caret-color: {text} !important;
    }}

    textarea::placeholder {{
        color: {subtext} !important;
        opacity: 1 !important;
    }}

    textarea:focus {{
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
        color: {text} !important;
        caret-color: {text} !important;
    }}

    input {{
        color: {text} !important;
        caret-color: {text} !important;
    }}

    input::placeholder {{
        color: {subtext} !important;
        opacity: 1 !important;
    }}

    .footer-note {{
        color: {subtext};
        font-size: 0.85rem;
        text-align: center;
        margin-top: 18px;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="hero-card">
    <div class="hero-title">Customer Feedback Intelligence System</div>
    <div class="hero-subtitle">
        Hybrid multilingual analysis using Rule Engine + Pre-trained BERT
    </div>
</div>
""", unsafe_allow_html=True)

st.info("👉 Use **Single Review Analysis** for one review or switch to **Batch CSV / Excel Analysis** to upload files.")

tab1, tab2 = st.tabs(["🧠 Single Review Analysis", "📊 Batch CSV / Excel Analysis"])

# -----------------------------
# SINGLE REVIEW
# -----------------------------
with tab1:
    st.markdown('<div class="section-title">Analyze a single customer review</div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-note">Tip: You can enter English, Hindi, or Hinglish reviews.</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    review_text = st.text_area(
        "Enter customer review",
        height=160,
        placeholder="Example: You guys are cheaters, support never replied and I still have not received my refund..."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    b1, b2, b3 = st.columns([1, 1.4, 1])
    with b2:
        analyze_clicked = st.button("Analyze Review", use_container_width=True)

    if analyze_clicked:
        if review_text.strip():
            start_time = time.time()

            with st.spinner("Analyzing review..."):
                result = analyze_single(review_text)

            elapsed_time = round(time.time() - start_time, 3)
            mixed_feedback = detect_mixed_feedback(review_text)
            nps_type, nps_score = sentiment_to_nps(result["sentiment_label"])
            action_text = action_recommendation(result["priority_label"])

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

            chips = f"""
            <div class="info-chip-wrap">
                <span class="info-chip">Sentiment Source: {result['sentiment_source']}</span>
                <span class="info-chip">BERT Confidence: {result['bert_confidence']}</span>
                <span class="info-chip">Priority Score: {result['priority_score']}</span>
                <span class="info-chip">Processing Time: {elapsed_time}s</span>
                <span class="info-chip">NPS Type: {nps_type}</span>
                <span class="info-chip">NPS Score: {nps_score}</span>
                <span class="info-chip">Mixed Feedback: {mixed_feedback}</span>
            </div>
            """
            st.markdown(chips, unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="reason-box">
                    <strong>Why this result?</strong><br>
                    {build_reason_text(result)}<br><br>
                    <strong>Recommended Action:</strong> {action_text}
                </div>
                """,
                unsafe_allow_html=True
            )

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

# -----------------------------
# BATCH ANALYSIS
# -----------------------------
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
                negative_pct = round((result_df["sentiment_label"] == "negative").mean() * 100, 1)
                mixed_count = df[selected_col].astype(str).apply(detect_mixed_feedback).sum()
                elapsed_time = round(time.time() - start_time, 2)

                nps_value, nps_types = compute_nps(result_df)
                result_df["nps_type"] = nps_types
                result_df["action_recommendation"] = result_df["priority_label"].apply(action_recommendation)
                result_df["mixed_feedback"] = df[selected_col].astype(str).apply(detect_mixed_feedback)

                progress_bar.progress(100)
                status_text.write(f"✅ Processing complete in {elapsed_time} seconds.")

                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Business Snapshot</div>', unsafe_allow_html=True)

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Total Reviews", total_reviews)
                m2.metric("Critical Issues", critical_count)
                m3.metric("High Priority", high_count)
                m4.metric("Negative %", f"{negative_pct}%")
                m5.metric("NPS Score", nps_value)

                st.markdown(
                    f"""
                    <div class="reason-box">
                        <strong>Top Issue</strong><br>
                        {pretty_label(top_aspect)}<br><br>
                        <strong>Batch Summary</strong><br>
                        {batch_summary(result_df)}
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
                st.write(f"- Mixed feedback reviews: **{mixed_count}**")
                st.write(f"- NPS Score: **{nps_value}**")
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

st.markdown(
    '<div class="footer-note">Built with Streamlit • Hybrid NLP • Multilingual Review Intelligence</div>',
    unsafe_allow_html=True
)
