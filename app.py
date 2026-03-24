import time
import streamlit as st
import pandas as pd
import plotly.express as px
from src.pipeline import analyze_single, analyze_dataframe

st.set_page_config(
    page_title="Customer Feedback Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# HELPERS
# =========================================================
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
    cls = f"priority-{p}"
    return f'<span class="priority-badge {cls}">{pretty_label(priority_label)}</span>'


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


def compute_nps(result_df: pd.DataFrame):
    nps_types = result_df["sentiment_label"].apply(lambda x: sentiment_to_nps(x)[0])
    promoters = (nps_types == "Promoter").mean() * 100
    detractors = (nps_types == "Detractor").mean() * 100
    nps_value = round(promoters - detractors, 1)
    return nps_value, nps_types


def batch_summary(result_df: pd.DataFrame) -> str:
    if result_df.empty:
        return "No reviews were processed."

    top_aspect = pretty_label(result_df["primary_aspect_label"].value_counts().idxmax())
    top_intent = pretty_label(result_df["customer_intent_label"].value_counts().idxmax())
    top_emotion = pretty_label(result_df["emotion_label"].value_counts().idxmax())
    negative_pct = round((result_df["sentiment_label"] == "negative").mean() * 100, 1)
    critical_pct = round((result_df["priority_label"] == "critical").mean() * 100, 1)

    return (
        f"Most reviews are centered around {top_aspect}, with {top_intent} as the most common intent. "
        f"The dominant emotion is {top_emotion}. Negative sentiment accounts for {negative_pct}% "
        f"of reviews, while {critical_pct}% are critical issues."
    )


# =========================================================
# THEME COLORS
# =========================================================
bg = "#081226"
text = "#E5E7EB"
subtext = "#94A3B8"
border = "#243247"
card_bg = "rgba(12,22,40,0.90)"
card_bg_2 = "rgba(17,24,39,0.95)"
muted_bg = "#0b1220"
sidebar_bg = "#0A1328"
sidebar_text = "#E5E7EB"
select_bg = "#111C33"
option_hover_bg = "#1E293B"
textarea_bg = "#050D1C"
metric_bg = "#0E172A"
uploader_bg = "#0E172A"

# =========================================================
# CSS
# =========================================================
st.markdown(f"""
<style>
    .stApp {{
        background: radial-gradient(circle at top left, #0d1b36 0%, #081226 45%, #050a16 100%);
        color: {text};
    }}

    .block-container {{
        max-width: 1320px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    section[data-testid="stSidebar"] {{
        min-width: 295px !important;
        max-width: 295px !important;
        background: {sidebar_bg} !important;
        border-right: 1px solid {border};
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

    .hero {{
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 45%, #9333EA 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 28px 30px;
        margin-bottom: 18px;
        box-shadow: 0 20px 45px rgba(76, 29, 149, 0.35);
    }}

    .hero h1 {{
        color: white !important;
        font-size: 2.3rem;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }}

    .hero p {{
        color: rgba(255,255,255,0.92) !important;
        margin-top: 8px;
        font-size: 1rem;
    }}

    .section-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }}

    .sub-card {{
        background: {card_bg_2};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 14px;
    }}

    .section-title {{
        font-size: 1.25rem;
        font-weight: 800;
        color: {text};
        margin-bottom: 4px;
    }}

    .section-subtitle {{
        color: {subtext};
        font-size: 0.95rem;
        margin-bottom: 14px;
    }}

    .reason-box {{
        background: {muted_bg};
        border: 1px solid {border};
        border-left: 5px solid #8B5CF6;
        border-radius: 16px;
        padding: 15px 16px;
        margin-top: 10px;
        margin-bottom: 12px;
        color: {text};
    }}

    .chip-wrap {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin: 10px 0 6px 0;
    }}

    .chip {{
        background: rgba(99,102,241,0.14);
        color: #C7D2FE !important;
        border: 1px solid rgba(129,140,248,0.25);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.82rem;
        font-weight: 700;
    }}

    .priority-badge {{
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        color: white !important;
        font-size: 0.88rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        margin-top: 6px;
        margin-bottom: 8px;
    }}

    .priority-low {{ background: #10B981; }}
    .priority-medium {{ background: #F59E0B; }}
    .priority-high {{ background: #F97316; }}
    .priority-critical {{ background: #EF4444; }}

    div.stButton > button {{
        background: linear-gradient(90deg, #4F46E5, #9333EA);
        color: white !important;
        border: none;
        border-radius: 14px;
        padding: 0.72rem 1.25rem;
        font-weight: 800;
        height: 48px;
        box-shadow: 0 12px 25px rgba(124,58,237,0.28);
        transition: all 0.18s ease;
    }}

    div.stButton > button:hover {{
        transform: translateY(-1px);
        filter: brightness(1.03);
    }}

    div[data-testid="stMetric"] {{
        background: {metric_bg};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 10px 12px;
    }}

    div[data-testid="stFileUploader"] {{
        background: {uploader_bg};
        border-radius: 16px;
        padding: 6px;
        border: 1px solid {border};
    }}

    textarea {{
        border-radius: 16px !important;
        border: 1px solid {border} !important;
        padding: 14px !important;
        background-color: {textarea_bg} !important;
        color: {text} !important;
        caret-color: {text} !important;
        font-size: 15px !important;
    }}

    textarea::placeholder {{
        color: {subtext} !important;
        opacity: 1 !important;
    }}

    textarea:focus {{
        border: 1px solid #8B5CF6 !important;
        box-shadow: 0 0 0 1px #8B5CF6 !important;
    }}

    input {{
        color: {text} !important;
        caret-color: {text} !important;
    }}

    input::placeholder {{
        color: {subtext} !important;
        opacity: 1 !important;
    }}

    button[data-baseweb="tab"] {{
        color: {text} !important;
        font-weight: 800;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #C4B5FD !important;
        border-bottom: 3px solid #8B5CF6 !important;
    }}

    div[data-baseweb="select"] {{
        background: {select_bg} !important;
        border-radius: 12px !important;
        color: {sidebar_text} !important;
    }}

    div[data-baseweb="select"] > div {{
        background: {select_bg} !important;
        color: {sidebar_text} !important;
    }}

    div[data-baseweb="select"] input {{
        color: {sidebar_text} !important;
        caret-color: {sidebar_text} !important;
    }}

    div[data-baseweb="select"] span {{
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
    }}

    .footer-note {{
        color: {subtext};
        font-size: 0.85rem;
        text-align: center;
        margin-top: 18px;
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## ⚙️ Dashboard")
st.sidebar.markdown("Use the tabs to switch between single review and batch analysis.")
st.sidebar.markdown("---")
st.sidebar.markdown("## 📌 Usage")
st.sidebar.markdown("- **Single Review** → analyze one review")
st.sidebar.markdown("- **Batch Analysis** → upload CSV / Excel")
st.sidebar.markdown("- Supported formats: **CSV, XLSX, XLS**")
st.sidebar.markdown("---")
st.sidebar.markdown("## 💡 Features")
st.sidebar.markdown("- Sentiment analysis")
st.sidebar.markdown("- Aspect detection")
st.sidebar.markdown("- Emotion + intent classification")
st.sidebar.markdown("- Priority scoring")
st.sidebar.markdown("- NPS + business dashboard")

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>Customer Feedback Intelligence System</h1>
    <p>AI-powered multilingual sentiment, aspect, priority, intent, and business analytics dashboard.</p>
</div>
""", unsafe_allow_html=True)

st.info("👉 Use **Single Review Analysis** for one review or switch to **Batch CSV / Excel Analysis** to upload files.")

tab1, tab2 = st.tabs(["🧠 Single Review Analysis", "📊 Batch CSV / Excel Analysis"])

# =========================================================
# SINGLE REVIEW TAB
# =========================================================
with tab1:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">Analyze Customer Review</div>
        <div class="section-subtitle">Supports English • Hindi • Hinglish</div>
    """, unsafe_allow_html=True)

    review_text = st.text_area(
        "✍️ Enter review",
        height=150,
        placeholder="Example: You guys are cheaters, support never replied and I still have not received my refund..."
    )

    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        analyze_clicked = st.button("🚀 Analyze Review", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked:
        if review_text.strip():
            start_time = time.time()
            with st.spinner("Analyzing review..."):
                result = analyze_single(review_text)

            elapsed_time = round(time.time() - start_time, 3)
            mixed_feedback = detect_mixed_feedback(review_text)
            nps_type, nps_score = sentiment_to_nps(result["sentiment_label"])
            action_text = action_recommendation(result["priority_label"])

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Prediction Summary</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Structured output from the hybrid NLP engine</div>', unsafe_allow_html=True)

            a, b, c = st.columns(3)
            a.metric("Aspect", pretty_label(result["primary_aspect_label"]))
            b.metric("Emotion", pretty_label(result["emotion_label"]))
            c.metric("Priority", pretty_label(result["priority_label"]))

            d, e, f = st.columns(3)
            d.metric("Intent", pretty_label(result["customer_intent_label"]))
            e.metric("Aspect Sentiment", pretty_label(result["aspect_sentiment_label"]))
            f.metric("Sentiment", pretty_label(result["sentiment_label"]))

            st.markdown(priority_badge(result["priority_label"]), unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="chip-wrap">
                    <span class="chip">Sentiment Source: {result['sentiment_source']}</span>
                    <span class="chip">BERT Confidence: {result['bert_confidence']}</span>
                    <span class="chip">Priority Score: {result['priority_score']}</span>
                    <span class="chip">Processing Time: {elapsed_time}s</span>
                    <span class="chip">NPS Type: {nps_type}</span>
                    <span class="chip">NPS Score: {nps_score}</span>
                    <span class="chip">Mixed Feedback: {mixed_feedback}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

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

            st.caption(
                f"Regex Flags → Phone: {result['has_phone']} | "
                f"Email: {result['has_email']} | "
                f"Strong Negative: {result['strong_negative']} | "
                f"Urgent: {result['urgent']}"
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

# =========================================================
# BATCH TAB
# =========================================================
with tab2:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">Batch File Analysis</div>
        <div class="section-subtitle">Upload CSV or Excel and generate business-ready review intelligence</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )

    st.markdown("</div>", unsafe_allow_html=True)

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

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Uploaded File Preview</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-subtitle">Loaded file: {file_name}</div>', unsafe_allow_html=True)

            st.dataframe(df.head(), use_container_width=True)

            auto_detected_col = detect_review_column(df.columns.tolist())

            if auto_detected_col:
                st.success(f"Auto-detected review column: {auto_detected_col}")
            else:
                st.warning("Could not auto-detect the review column. Please select manually.")

            selected_col = st.selectbox(
                "Select the review/comment column",
                options=df.columns.tolist(),
                index=df.columns.tolist().index(auto_detected_col) if auto_detected_col in df.columns.tolist() else 0
            )

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("📈 Process File"):
                start_time = time.time()

                progress_bar = st.progress(10)
                status_text = st.empty()
                status_text.write("Preparing analysis...")

                progress_bar.progress(35)
                status_text.write("Running NLP pipeline...")
                result_df = analyze_dataframe(df, text_col=selected_col)

                progress_bar.progress(78)
                status_text.write("Computing dashboard insights...")

                total_reviews = len(result_df)
                critical_count = (result_df["priority_label"] == "critical").sum()
                high_count = (result_df["priority_label"] == "high").sum()
                negative_pct = round((result_df["sentiment_label"] == "negative").mean() * 100, 1)
                top_aspect = result_df["primary_aspect_label"].value_counts().idxmax()
                mixed_count = df[selected_col].astype(str).apply(detect_mixed_feedback).sum()
                elapsed_time = round(time.time() - start_time, 2)

                nps_value, nps_types = compute_nps(result_df)
                result_df["nps_type"] = nps_types
                result_df["action_recommendation"] = result_df["priority_label"].apply(action_recommendation)
                result_df["mixed_feedback"] = df[selected_col].astype(str).apply(detect_mixed_feedback)

                progress_bar.progress(100)
                status_text.write(f"✅ Processing complete in {elapsed_time} seconds.")

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Business Snapshot</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-subtitle">High-level KPIs from the uploaded dataset</div>', unsafe_allow_html=True)

                k1, k2, k3, k4, k5 = st.columns(5)
                k1.metric("Total Reviews", total_reviews)
                k2.metric("Critical Issues", critical_count)
                k3.metric("High Priority", high_count)
                k4.metric("Negative %", f"{negative_pct}%")
                k5.metric("NPS Score", nps_value)

                st.markdown(
                    f"""
                    <div class="reason-box">
                        <strong>Top Issue:</strong> {pretty_label(top_aspect)}<br><br>
                        <strong>Batch Summary:</strong><br>
                        {batch_summary(result_df)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Output Preview</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-subtitle">First 100 processed rows</div>', unsafe_allow_html=True)
                st.dataframe(result_df.head(100), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Plotly charts
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Analytics Dashboard</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-subtitle">Interactive business charts powered by Plotly</div>', unsafe_allow_html=True)

                plot_bg = "#0E172A"
                plot_paper = "rgba(0,0,0,0)"
                plot_font = "#E5E7EB"
                plot_grid = "#334155"

                c1, c2 = st.columns(2)

                with c1:
                    aspect_counts = result_df["primary_aspect_label"].value_counts().reset_index()
                    aspect_counts.columns = ["Aspect", "Count"]

                    fig1 = px.bar(
                        aspect_counts,
                        x="Aspect",
                        y="Count",
                        title="Aspect Distribution",
                        text="Count"
                    )
                    fig1.update_layout(
                        paper_bgcolor=plot_paper,
                        plot_bgcolor=plot_bg,
                        font_color=plot_font,
                        xaxis_title="Aspect",
                        yaxis_title="Count",
                        xaxis_tickangle=-35,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    fig1.update_xaxes(showgrid=False)
                    fig1.update_yaxes(gridcolor=plot_grid)
                    st.plotly_chart(fig1, use_container_width=True)

                with c2:
                    priority_counts = result_df["priority_label"].value_counts().reset_index()
                    priority_counts.columns = ["Priority", "Count"]

                    fig2 = px.pie(
                        priority_counts,
                        names="Priority",
                        values="Count",
                        title="Priority Distribution",
                        hole=0.45
                    )
                    fig2.update_layout(
                        paper_bgcolor=plot_paper,
                        plot_bgcolor=plot_bg,
                        font_color=plot_font,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                c3, c4 = st.columns(2)

                with c3:
                    emotion_counts = result_df["emotion_label"].value_counts().reset_index()
                    emotion_counts.columns = ["Emotion", "Count"]

                    fig3 = px.bar(
                        emotion_counts,
                        x="Emotion",
                        y="Count",
                        title="Emotion Distribution",
                        text="Count"
                    )
                    fig3.update_layout(
                        paper_bgcolor=plot_paper,
                        plot_bgcolor=plot_bg,
                        font_color=plot_font,
                        xaxis_title="Emotion",
                        yaxis_title="Count",
                        xaxis_tickangle=-35,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    fig3.update_xaxes(showgrid=False)
                    fig3.update_yaxes(gridcolor=plot_grid)
                    st.plotly_chart(fig3, use_container_width=True)

                with c4:
                    intent_counts = result_df["customer_intent_label"].value_counts().reset_index()
                    intent_counts.columns = ["Intent", "Count"]

                    fig4 = px.bar(
                        intent_counts,
                        x="Intent",
                        y="Count",
                        title="Intent Distribution",
                        text="Count"
                    )
                    fig4.update_layout(
                        paper_bgcolor=plot_paper,
                        plot_bgcolor=plot_bg,
                        font_color=plot_font,
                        xaxis_title="Intent",
                        yaxis_title="Count",
                        xaxis_tickangle=-35,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    fig4.update_xaxes(showgrid=False)
                    fig4.update_yaxes(gridcolor=plot_grid)
                    st.plotly_chart(fig4, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
