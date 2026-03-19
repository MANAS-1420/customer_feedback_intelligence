import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.pipeline import analyze_single, analyze_dataframe

st.set_page_config(page_title="Customer Feedback Intelligence System", layout="wide")

st.title("Customer Feedback Intelligence System")
st.caption("Hybrid multilingual analysis using Rule Engine + Pre-trained BERT")

tab1, tab2 = st.tabs(["Single Review Analysis", "Batch CSV Analysis"])

with tab1:
    st.subheader("Single Review Analysis")

    review_text = st.text_area("Enter customer review")
    sentiment_input = st.selectbox(
        "Select sentiment",
        options=[0, 1, 2],
        format_func=lambda x: {0: "Negative", 1: "Neutral", 2: "Positive"}[x]
    )

    if st.button("Analyze"):
        if review_text.strip():
            result = analyze_single(review_text, sentiment_input)

            c1, c2, c3 = st.columns(3)
            c1.metric("Aspect", result["primary_aspect_label"])
            c2.metric("Emotion", result["emotion_label"])
            c3.metric("Priority", result["priority_label"])

            c4, c5, c6 = st.columns(3)
            c4.metric("Intent", result["customer_intent_label"])
            c5.metric("Aspect Sentiment", result["aspect_sentiment_label"])
            c6.metric("Sentiment", result["sentiment_label"])

            st.write("### Hybrid Details")
            st.write(f"**Sentiment Source:** {result['sentiment_source']}")
            st.write(f"**BERT Confidence:** {result['bert_confidence']}")
            st.write(f"**Priority Score:** {result['priority_score']}")
            st.write(f"**Matched Keywords:** {result['matched_keywords'] or 'No major keyword hit'}")

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
    st.subheader("Batch CSV Analysis")
    st.write("Required columns: `Review`, `Sentiment`")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        required_cols = ["Review", "Sentiment"]
        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            result_df = analyze_dataframe(df)

            st.write("### Output Preview")
            st.dataframe(result_df, use_container_width=True)

            st.write("### Charts")
            col1, col2 = st.columns(2)

            with col1:
                fig1, ax1 = plt.subplots()
                result_df["primary_aspect_label"].value_counts().plot(kind="bar", ax=ax1)
                ax1.set_title("Aspect Distribution")
                ax1.set_xlabel("Aspect")
                ax1.set_ylabel("Count")
                st.pyplot(fig1)

            with col2:
                fig2, ax2 = plt.subplots()
                result_df["priority_label"].value_counts().plot(kind="bar", ax=ax2)
                ax2.set_title("Priority Distribution")
                ax2.set_xlabel("Priority")
                ax2.set_ylabel("Count")
                st.pyplot(fig2)

            col3, col4 = st.columns(2)

            with col3:
                fig3, ax3 = plt.subplots()
                result_df["emotion_label"].value_counts().plot(kind="bar", ax=ax3)
                ax3.set_title("Emotion Distribution")
                ax3.set_xlabel("Emotion")
                ax3.set_ylabel("Count")
                st.pyplot(fig3)

            with col4:
                fig4, ax4 = plt.subplots()
                result_df["customer_intent_label"].value_counts().plot(kind="bar", ax=ax4)
                ax4.set_title("Intent Distribution")
                ax4.set_xlabel("Intent")
                ax4.set_ylabel("Count")
                st.pyplot(fig4)

            critical_count = (result_df["priority_label"] == "critical").sum()
            high_count = (result_df["priority_label"] == "high").sum()
            top_aspect = result_df["primary_aspect_label"].value_counts().idxmax()

            st.write("### Business Insights")
            st.write(f"- Total reviews analyzed: **{len(result_df)}**")
            st.write(f"- Critical issues: **{critical_count}**")
            st.write(f"- High priority issues: **{high_count}**")
            st.write(f"- Top aspect: **{top_aspect}**")

            if critical_count > 0:
                st.error(f"🚨 {critical_count} critical issues detected in uploaded data.")

            csv_bytes = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Results CSV",
                data=csv_bytes,
                file_name="customer_feedback_output.csv",
                mime="text/csv"
            )
