import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.pipeline import analyze_single, analyze_dataframe

st.set_page_config(page_title="Customer Feedback Intelligence System", layout="wide")


def pretty_label(x: str) -> str:
    return x.replace("_", " ").title()


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


st.title("Customer Feedback Intelligence System")
st.caption("Hybrid multilingual analysis using Rule Engine + Pre-trained BERT")

tab1, tab2 = st.tabs(["Single Review Analysis", "Batch CSV / Excel Analysis"])

with tab1:
    st.subheader("Single Review Analysis")

    review_text = st.text_area("Enter customer review")

    if st.button("Analyze Review"):
        if review_text.strip():
            start_time = time.time()

            with st.spinner("Analyzing review..."):
                result = analyze_single(review_text)

            elapsed_time = round(time.time() - start_time, 3)

            c1, c2, c3 = st.columns(3)
            c1.metric("Aspect", pretty_label(result["primary_aspect_label"]))
            c2.metric("Emotion", pretty_label(result["emotion_label"]))
            c3.metric("Priority", pretty_label(result["priority_label"]))

            c4, c5, c6 = st.columns(3)
            c4.metric("Intent", pretty_label(result["customer_intent_label"]))
            c5.metric("Aspect Sentiment", pretty_label(result["aspect_sentiment_label"]))
            c6.metric("Sentiment", pretty_label(result["sentiment_label"]))

            st.write("### Hybrid Details")
            st.write(f"**Sentiment Source:** {result['sentiment_source']}")
            st.write(f"**BERT Confidence:** {result['bert_confidence']}")
            st.write(f"**Priority Score:** {result['priority_score']}")
            st.write(f"**Matched Keywords:** {result['matched_keywords'] or 'No major keyword hit'}")
            st.write(f"**Processing Time:** {elapsed_time} seconds")

            st.write("**Regex Flags:**")
            st.write(
                f"Phone: {result['has_phone']} | "
                f"Email: {result['has_email']} | "
                f"Strong Negative: {result['strong_negative']} | "
                f"Urgent: {result['urgent']}"
            )

            if result["priority_label"] == "critical":
                st.error("🚨 Critical issue detected")
            elif result["priority_label"] == "high":
                st.warning("⚠️ High priority issue")
            elif result["priority_label"] == "medium":
                st.info("ℹ️ Medium priority issue")
            else:
                st.success("✅ Low priority issue")
        else:
            st.warning("Please enter review text.")

with tab2:
    st.subheader("Batch CSV / Excel Analysis")
    st.write("Supported file types: `CSV`, `XLSX`, `XLS`")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )

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

            st.write("### Uploaded File Preview")
            st.dataframe(df.head(), use_container_width=True)

            auto_detected_col = detect_review_column(df.columns.tolist())

            if auto_detected_col:
                st.info(f"Auto-detected review column: `{auto_detected_col}`")
            else:
                st.warning("Could not auto-detect review column. Please select manually.")

            selected_col = st.selectbox(
                "Select the review/comment column",
                options=df.columns.tolist(),
                index=df.columns.tolist().index(auto_detected_col) if auto_detected_col in df.columns.tolist() else 0
            )

            if st.button("Process File"):
                start_time = time.time()

                progress_bar = st.progress(10)
                status_text = st.empty()
                status_text.write("Processing file...")

                result_df = analyze_dataframe(df, text_col=selected_col)

                progress_bar.progress(100)
                elapsed_time = round(time.time() - start_time, 2)
                status_text.write(f"✅ Processing complete in {elapsed_time} seconds.")

                st.write("### Output Preview")
                st.dataframe(result_df.head(100), use_container_width=True)

                total_reviews = len(result_df)
                critical_count = (result_df["priority_label"] == "critical").sum()
                high_count = (result_df["priority_label"] == "high").sum()
                top_aspect = result_df["primary_aspect_label"].value_counts().idxmax()

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Reviews", total_reviews)
                m2.metric("Critical Issues", critical_count)
                m3.metric("High Priority", high_count)
                m4.metric("Processing Time", f"{elapsed_time}s")

                st.write(f"**Top Issue:** {pretty_label(top_aspect)}")

                st.write("### Charts")
                col1, col2 = st.columns(2)

                with col1:
                    fig1, ax1 = plt.subplots()
                    result_df["primary_aspect_label"].value_counts().plot(kind="bar", ax=ax1)
                    ax1.set_title("Aspect Distribution")
                    ax1.set_xlabel("Aspect")
                    ax1.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig1)

                with col2:
                    fig2, ax2 = plt.subplots()
                    result_df["priority_label"].value_counts().plot(kind="bar", ax=ax2)
                    ax2.set_title("Priority Distribution")
                    ax2.set_xlabel("Priority")
                    ax2.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig2)

                col3, col4 = st.columns(2)

                with col3:
                    fig3, ax3 = plt.subplots()
                    result_df["emotion_label"].value_counts().plot(kind="bar", ax=ax3)
                    ax3.set_title("Emotion Distribution")
                    ax3.set_xlabel("Emotion")
                    ax3.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig3)

                with col4:
                    fig4, ax4 = plt.subplots()
                    result_df["customer_intent_label"].value_counts().plot(kind="bar", ax=ax4)
                    ax4.set_title("Intent Distribution")
                    ax4.set_xlabel("Intent")
                    ax4.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig4)

                st.write("### Business Insights")
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

        except Exception as e:
            st.error(f"Error while processing file: {e}")
