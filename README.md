# 💠 Customer Feedback Intelligence


![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?logo=streamlit&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-F9AB00?logo=huggingface&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?logo=google&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-ABSA_%7C_Hinglish-10B981)


**Live App / Demo:** [https://customerfeedbackintelligence-wtoqs5nd8tzmjjjd8efsar.streamlit.app/]


## 🚀 Overview
**Customer Feedback Intelligence** is a production-ready SaaS dashboard designed to analyze complex, multi-lingual customer reviews (English, Hindi, and Hinglish). 


Moving beyond standard document-level sentiment analysis, this system utilizes a **Hybrid NLP Architecture**—combining a HuggingFace multilingual BERT model with a deterministic, exponentially-weighted Rule Engine. It dynamically extracts actionable business intelligence, behavioral profiles, and risk metrics from raw unstructured text.


## ✨ Key Enterprise Features


* **Aspect-Based Sentiment Analysis (ABSA):** Automatically splits complex reviews containing contrastive conjunctions (e.g., *"Delivery boy ka behavior acha tha but product damaged nikla"*) into individual clauses to evaluate conflicting sentiments accurately.
* **Hinglish & Localized NLP Mastery:** Engineered to understand Indian e-commerce nuances, slang (*"ghatiya", "bakwas"*), code-mixing, and negated negatives (e.g., correctly classifying *"koi complaint nahi"* as Positive).
* **Exponential Phrase Weighting:** Prevents "domain bleed" across 100+ subcategories by applying exponential mathematical weights to multi-word phrases (e.g., prioritizing *"loan approval delay"* over the isolated word *"delay"*).
* **Psychological & Behavioral Profiling:** Extracts hidden user signals including:
  * 🚨 **Churn Risk Detection:** Flags high-risk users threatening to switch to competitors or displaying severe trust issues.
  * 🎭 **Sarcasm Suspected:** Identifies contrastive signals where the model detects negative intent but the user utilizes heavily positive phrasing.
  * 📈 **Tone Intensity Scoring:** Algorithmically scores customer aggression based on capitalization ratios, punctuation, and strong negative phrasing.
* **Generative AI Strategic Briefings:** Integrates with the Google Gemini API via a Dynamic Model Finder to automatically generate executive summaries and actionable recommendations for bulk datasets.


## 🧠 System Architecture


1. **Input Layer:** Accepts real-time single text inputs or bulk CSV/XLSX uploads.
2. **Clause Splitter:** Parses text via regex across English and Hinglish contrastive markers.
3. **Hybrid Classification Engine:**
   * **Rule Engine:** Scans against a massive taxonomy matrix mapping Categories to Subcategory threats using a Smart Stemming Matcher.
   * **Transformer Model:** Processes text through `nlptown/bert-base-multilingual-uncased-sentiment` for baseline contextual sentiment.
   * **Arbiter:** Enforces Rule-Engine Supremacy to override AI hallucinations on localized slang and severe category issues.
4. **Scoring Engine:** Calculates Priority (Low to Critical) and NPS Profile based on urgent phrasing and category severity.
5. **Presentation Layer:** Renders interactive Plotly sunburst charts and KPI metrics via Streamlit.


## 🛠️ Tech Stack
* **Frontend/UI:** Streamlit, Plotly Express
* **NLP & Machine Learning:** HuggingFace Transformers (`pipeline`), PyTorch
* **Generative AI:** Google Generative AI SDK (`gemini-1.5-flash`/`gemini-1.5-pro`)
* **Data Processing:** Pandas, Regex (Custom Tokenization & Parsing)


---
*Built by Manas | Data Science & NLP Portfolio 2026*
