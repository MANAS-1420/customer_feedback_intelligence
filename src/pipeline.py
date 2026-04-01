# src/pipeline.py
import re
import pandas as pd

from src.config import EMOTION_LABELS, CUSTOMER_INTENT_LABELS, PRIORITY_LABELS, CATEGORY_SUBCATEGORY_MAP
from src.rule_engine import (
    TAXONOMY_KEYWORDS, EMOTION_KEYWORDS, CUSTOMER_INTENT_KEYWORDS,
    ASPECT_SENT_NEG_KW, ASPECT_SENT_POS_KW, MIXED_FEEDBACK_KW, URGENT_KW, STRONG_NEG_PHRASES
)
from src.utils import normalize, any_hit, matched_keywords
from src.bert_model import get_bert_sentiment

PHONE_REGEX = re.compile(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def get_best_hierarchy_match(text: str) -> tuple:
    max_hits = 0
    best_match = ("neutral_informational", "no_clear_sentiment")
    for (cat, subcat), keywords in TAXONOMY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text))
        if hits > max_hits:
            max_hits = hits
            best_match = (cat, subcat)
    return best_match

def get_best_match(text: str, keyword_dict: dict, fallback: str) -> str:
    max_hits = 0
    best_label = fallback
    for label, keywords in keyword_dict.items():
        hits = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text))
        if hits > max_hits:
            max_hits = hits
            best_label = label
    return best_label

def compute_priority_score(text: str, sentiment: str, cat: str, is_urgent: bool, is_strong_neg: bool) -> int:
    score = 0
    if any_hit(text, EMOTION_KEYWORDS["Very Angry"]): score += 50
    if cat in ["payment_billing", "fraud_security", "loan_finance"]: score += 30
    if is_urgent: score += 20
    if is_strong_neg: score += 15
    if sentiment == "negative": score += 10
    if sentiment == "positive": score -= 20
    if any_hit(text, ["wait", "delay", "pending"]): score += 10
    return max(0, min(score, 100))

def analyze_single(review_text: str) -> dict:
    try:
        raw_text = str(review_text) if pd.notnull(review_text) else ""
        norm_text = normalize(raw_text)
        
        if not norm_text:
            raise ValueError("Empty")

        has_phone = bool(PHONE_REGEX.search(raw_text))
        has_email = bool(EMAIL_REGEX.search(raw_text))
        urgent = any_hit(norm_text, URGENT_KW)
        strong_negative = any_hit(norm_text, STRONG_NEG_PHRASES)
        mixed_feedback = any_hit(norm_text, MIXED_FEEDBACK_KW)
        
        category, subcategory = get_best_hierarchy_match(norm_text)
        emotion = get_best_match(norm_text, EMOTION_KEYWORDS, "Calm")
        intent = get_best_match(norm_text, CUSTOMER_INTENT_KEYWORDS, "Neutral Tone")
        
        rule_sentiment = "neutral"
        if any_hit(norm_text, ASPECT_SENT_NEG_KW): rule_sentiment = "negative"
        elif any_hit(norm_text, ASPECT_SENT_POS_KW): rule_sentiment = "positive"
        
        bert_sent, bert_conf = get_bert_sentiment(raw_text)
        final_sentiment = bert_sent if bert_conf >= 0.60 else rule_sentiment
        sentiment_source = "BERT Pipeline" if bert_conf >= 0.60 else "Rule Engine"
            
        # Fallback Correction Logic to reduce "neutral/general" dominance
        if final_sentiment == "negative":
            if category == "neutral_informational":
                if "delay" in norm_text: category, subcategory = "delivery_logistics", "delayed_delivery"
                else: category, subcategory = "customer_experience", "overall_dissatisfaction"
            if intent in ["Neutral Tone", "Positive Tone", "Praise"]: intent = "Complaint"
            if emotion in ["Calm", "Happy", "Satisfied"]: emotion = "Frustrated"
                
        if final_sentiment == "positive":
            if category == "neutral_informational" or category == "negative_intent":
                category, subcategory = "positive_feedback", "great_experience"
            if intent in ["Negative Tone", "Complaint"]: intent = "Praise"
            if emotion in ["Calm", "Frustrated", "Angry", "Very Angry"]: emotion = "Satisfied"
            
        priority_score = compute_priority_score(norm_text, final_sentiment, category, urgent, strong_negative)
        if priority_score >= 60: priority_label = "Critical"
        elif priority_score >= 35: priority_label = "High"
        elif priority_score >= 15: priority_label = "Medium"
        else: priority_label = "Low"
        
        nps_type = "Promoter" if final_sentiment == "positive" else ("Detractor" if final_sentiment == "negative" else "Passive")
        nps_score = 100 if nps_type == "Promoter" else (-100 if nps_type == "Detractor" else 0)
        
        # Format labels clearly
        cat_label = category.replace("_", " ").title()
        subcat_label = subcategory.replace("_", " ").title()
        
        # 26+ specific keys matching output request
        return {
            "Review": raw_text,
            "Sentiment": final_sentiment.capitalize(),
            "sentiment_label": final_sentiment,
            "sentiment_source": sentiment_source,
            "bert_confidence": round(bert_conf, 4),
            "primary_aspect": category,
            "primary_aspect_label": cat_label,
            "subcategory": subcategory,
            "subcategory_label": subcat_label,
            "emotion": emotion.lower().replace(" ", "_"),
            "emotion_label": emotion,
            "customer_intent": intent.lower().replace(" ", "_"),
            "customer_intent_label": intent,
            "priority": priority_label.lower(),
            "priority_label": priority_label,
            "priority_score": priority_score,
            "aspect_sentiment": final_sentiment,
            "aspect_sentiment_label": f"{cat_label} is {final_sentiment.capitalize()}",
            "matched_keywords": ", ".join(matched_keywords(norm_text, sum(TAXONOMY_KEYWORDS.values(), []))[:6]) or "None",
            "has_phone": has_phone,
            "has_email": has_email,
            "strong_negative": strong_negative,
            "urgent": urgent,
            "nps_type": nps_type,
            "nps_score": nps_score,
            "mixed_feedback": mixed_feedback,
            "action_recommendation": "Escalate immediately" if priority_label == "Critical" else ("Assign to senior agent" if priority_label == "High" else "Standard logging"),
            "batch_summary_insights": f"{emotion} emotion detected regarding {subcat_label}."
        }
    except Exception as e:
        return {
            "Review": str(review_text), "Sentiment": "Neutral", "sentiment_label": "neutral", "sentiment_source": "Fallback", "bert_confidence": 0.0,
            "primary_aspect": "neutral_informational", "primary_aspect_label": "Neutral Informational", "subcategory": "no_clear_sentiment", "subcategory_label": "No Clear Sentiment",
            "emotion": "calm", "emotion_label": "Calm", "customer_intent": "neutral_tone", "customer_intent_label": "Neutral Tone",
            "priority": "low", "priority_label": "Low", "priority_score": 0, "aspect_sentiment": "neutral", "aspect_sentiment_label": "Neutral",
            "matched_keywords": "", "has_phone": False, "has_email": False, "strong_negative": False, "urgent": False, "nps_type": "Passive", "nps_score": 0, "mixed_feedback": False,
            "action_recommendation": "Skip", "batch_summary_insights": "Skipped due to parsing error."
        }

def analyze_dataframe(df: pd.DataFrame, text_col="Review"):
    results = df[text_col].apply(lambda x: analyze_single(x))
    res_df = pd.DataFrame(list(results))
    final_df = pd.concat([df.reset_index(drop=True), res_df.drop(columns=['Review'], errors='ignore')], axis=1)
    
    total = len(final_df)
    promoters = len(final_df[final_df['nps_type'] == 'Promoter'])
    detractors = len(final_df[final_df['nps_type'] == 'Detractor'])
    nps_final = round((promoters/total*100) - (detractors/total*100), 2) if total > 0 else 0
    
    meta = {
        "total_reviews": total, "net_promoter_score": nps_final,
        "critical_count": len(final_df[final_df['priority_label'] == 'Critical']),
        "negative_percentage": round(len(final_df[final_df['sentiment_label'] == 'negative']) / total * 100, 2) if total > 0 else 0
    }
    return final_df, meta
