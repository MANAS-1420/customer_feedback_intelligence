# src/pipeline.py
import re
import pandas as pd

from src.config import EMOTION_LABELS, CUSTOMER_INTENT_LABELS, PRIORITY_LABELS, CATEGORY_SUBCATEGORY_MAP
from src.rule_engine import (
    TAXONOMY_KEYWORDS, EMOTION_KEYWORDS, CUSTOMER_INTENT_KEYWORDS,
    ASPECT_SENT_NEG_KW, ASPECT_SENT_POS_KW, MIXED_FEEDBACK_KW, URGENT_KW, STRONG_NEG_PHRASES, NEGATED_NEGATIVE_PHRASES
)
from src.utils import normalize, any_hit, matched_keywords, split_into_clauses, flexible_match
from src.bert_model import get_bert_sentiment

PHONE_REGEX = re.compile(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
HINGLISH_CUES = ["hai", "nahi", "kya", "kar", "mein", "pe", "se", "ko", "bhi", "toh", "ka", "ki", "tha", "thi", "gaya"]

def get_best_hierarchy_match(text: str) -> tuple:
    max_hits = 0
    best_match = ("neutral_informational", "no_clear_sentiment")
    for (cat, subcat), keywords in TAXONOMY_KEYWORDS.items():
        hits = 0
        for kw in keywords:
            if flexible_match(kw, text):
                hits += (len(kw.split()) ** 2) * 10
        if hits > max_hits:
            max_hits = hits
            best_match = (cat, subcat)
    return best_match

def get_best_match(text: str, keyword_dict: dict, fallback: str) -> str:
    max_hits = 0
    best_label = fallback
    for label, keywords in keyword_dict.items():
        hits = 0
        for kw in keywords:
            if flexible_match(kw, text):
                hits += (len(kw.split()) ** 2) * 10
        if hits > max_hits:
            max_hits = hits
            best_label = label
    return best_label

def compute_priority_score(text: str, sentiment: str, cat: str, subcat: str, is_urgent: bool, is_strong_neg: bool) -> int:
    score = 0
    if any_hit(text, EMOTION_KEYWORDS["Very Angry"]): score += 50
    if cat in ["payment_billing", "fraud_security"]: score += 40
    if subcat in ["double_charge", "payment_deducted_not_processed", "fake_delivery_update", "recovery_agent_issue", "legal_threat", "social_media_threat"]: score += 40
    if subcat in ["product_quality_poor", "delivery_agent_behavior_rude", "product_defect"]: score += 30
    
    if is_urgent: score += 20
    if is_strong_neg: score += 20
    if sentiment == "negative": score += 10
    if sentiment == "positive": score -= 20
    return max(0, min(score, 100))

def analyze_clause(clause_text: str, full_review_mixed: bool, full_urgent: bool, full_strong_neg: bool) -> dict:
    norm_text = normalize(clause_text)
    
    category, subcategory = get_best_hierarchy_match(norm_text)
    emotion = get_best_match(norm_text, EMOTION_KEYWORDS, "Calm")
    intent = get_best_match(norm_text, CUSTOMER_INTENT_KEYWORDS, "Neutral Tone")
    
    is_negated_negative = any_hit(norm_text, NEGATED_NEGATIVE_PHRASES)

    rule_sentiment = "neutral"
    if is_negated_negative:
        rule_sentiment = "positive"
        if emotion in ["Very Angry", "Angry", "Frustrated"]: emotion = "Satisfied"
        if intent in ["Complaint", "Negative Tone"]: intent = "Praise"
        if category == "negative_intent": category, subcategory = "positive_feedback", "great_experience"
    elif any_hit(norm_text, ASPECT_SENT_NEG_KW) or emotion in ["Very Angry", "Angry", "Frustrated"] or intent in ["Complaint", "Negative Tone"]:
        rule_sentiment = "negative"
    elif any_hit(norm_text, ASPECT_SENT_POS_KW) or emotion in ["Happy", "Satisfied"] or intent in ["Praise", "Positive Tone"]:
        rule_sentiment = "positive"
        
    bert_sent, bert_conf = get_bert_sentiment(clause_text)
    
    if rule_sentiment != "neutral":
        final_sentiment = rule_sentiment
    else:
        final_sentiment = bert_sent if bert_conf >= 0.50 else "neutral"
        
    severe_issues = ["double_charge", "payment_failed", "payment_deducted_not_processed", "product_defect", "product_quality_poor", "missing_items", "delayed_delivery", "fake_delivery_update", "recovery_agent_issue"]
    if not is_negated_negative:
        if subcategory in severe_issues or category in ["negative_intent", "fraud_security"]:
            final_sentiment = "negative"
            if intent in ["Neutral Tone", "Positive Tone", "Enquiry"]: intent = "Complaint"
            if emotion in ["Calm", "Happy", "Satisfied"]: emotion = "Frustrated"
            
    if final_sentiment == "positive" and not is_negated_negative and subcategory not in severe_issues and category != "negative_intent":
        if category in ["neutral_informational"]: category, subcategory = "positive_feedback", "great_experience"
        if intent in ["Negative Tone", "Complaint"]: intent = "Praise"
        if emotion in ["Calm", "Frustrated", "Angry", "Very Angry"]: emotion = "Satisfied"
        
    priority_score = compute_priority_score(norm_text, final_sentiment, category, subcategory, full_urgent, full_strong_neg)
    if is_negated_negative: priority_score = min(priority_score, 10)
    
    return {
        "clause_text": clause_text,
        "sentiment": final_sentiment,
        "category": category,
        "subcategory": subcategory,
        "emotion": emotion,
        "intent": intent,
        "priority_score": priority_score
    }

def analyze_single(review_text: str) -> dict:
    try:
        raw_text = str(review_text) if pd.notnull(review_text) else ""
        norm_text = normalize(raw_text)
        
        if not norm_text: raise ValueError("Empty text")

        has_phone = bool(PHONE_REGEX.search(raw_text))
        has_email = bool(EMAIL_REGEX.search(raw_text))
        urgent = any_hit(norm_text, URGENT_KW)
        strong_negative = any_hit(norm_text, STRONG_NEG_PHRASES)
        mixed_feedback = any_hit(norm_text, MIXED_FEEDBACK_KW)
        
        if re.search(r'[\u0900-\u097F]', raw_text): language = "Hindi"
        elif any_hit(norm_text, HINGLISH_CUES): language = "Hinglish"
        else: language = "English"
        
        clauses = split_into_clauses(raw_text)
        clause_results = [analyze_clause(c, mixed_feedback, urgent, strong_negative) for c in clauses]
        clause_results.sort(key=lambda x: x['priority_score'], reverse=True)
        primary = clause_results[0]
        
        priority_score = primary['priority_score']
        if priority_score >= 60: priority_label = "Critical"
        elif priority_score >= 35: priority_label = "High"
        elif priority_score >= 15: priority_label = "Medium"
        else: priority_label = "Low"
        
        final_sentiment = primary['sentiment']
        nps_type = "Promoter" if final_sentiment == "positive" else ("Detractor" if final_sentiment == "negative" else "Passive")
        nps_score = 100 if nps_type == "Promoter" else (-100 if nps_type == "Detractor" else 0)
        
        churn_risk = (primary['category'] == "negative_intent") or (priority_score >= 60 and final_sentiment == "negative")
        
        caps_ratio = sum(1 for c in raw_text if c.isupper()) / (len(raw_text) + 1)
        intensity = min(10.0, 2.0 + (raw_text.count('!') * 1.5) + (caps_ratio * 20.0) + (3.0 if strong_negative else 0.0) + (2.0 if urgent else 0.0))
        sarcasm_flag = final_sentiment == "negative" and any_hit(norm_text, ["great", "awesome", "perfect", "wah", "kamaal", "best", "mast"])
        
        cat_label = primary['category'].replace("_", " ").title()
        subcat_label = primary['subcategory'].replace("_", " ").title()
        _, overall_conf = get_bert_sentiment(raw_text)

        return {
            "Review": raw_text,
            "Sentiment": final_sentiment.capitalize(),
            "sentiment_label": final_sentiment,
            "sentiment_source": "Rule Engine Override" if final_sentiment != "neutral" and overall_conf < 0.50 else "Hybrid ABSA Pipeline",
            "bert_confidence": round(overall_conf, 4),
            "primary_aspect": primary['category'],
            "primary_aspect_label": cat_label,
            "subcategory": primary['subcategory'],
            "subcategory_label": subcat_label,
            "emotion": primary['emotion'].lower().replace(" ", "_"),
            "emotion_label": primary['emotion'],
            "customer_intent": primary['intent'].lower().replace(" ", "_"),
            "customer_intent_label": primary['intent'],
            "priority": priority_label.lower(),
            "priority_label": priority_label,
            "priority_score": priority_score,
            "aspect_sentiment_label": f"{cat_label} is {final_sentiment.capitalize()}",
            "matched_keywords": ", ".join(matched_keywords(norm_text, sum(TAXONOMY_KEYWORDS.values(), []))[:6]) or "None",
            "has_phone": has_phone,
            "has_email": has_email,
            "strong_negative": strong_negative,
            "urgent": urgent,
            "nps_type": nps_type,
            "nps_score": nps_score,
            "mixed_feedback": mixed_feedback or len(clauses) > 1,
            "language_detected": language,
            "churn_risk": churn_risk,
            "tone_intensity_score": round(intensity, 1),
            "sarcasm_suspected": sarcasm_flag,
            "escalation_required": priority_label in ["Critical", "High"],
            "action_recommendation": "Escalate immediately" if priority_label == "Critical" else ("Assign to senior agent" if priority_label == "High" else "Standard logging"),
            "absa_breakdown": clause_results
        }
    except Exception as e:
        return {
            "Review": str(review_text), "Sentiment": "Neutral", "sentiment_label": "neutral", "sentiment_source": "Fallback", "bert_confidence": 0.0,
            "primary_aspect": "neutral_informational", "primary_aspect_label": "Neutral Informational", "subcategory": "no_clear_sentiment", "subcategory_label": "No Clear Sentiment",
            "emotion": "calm", "emotion_label": "Calm", "customer_intent": "neutral_tone", "customer_intent_label": "Neutral Tone",
            "priority": "low", "priority_label": "Low", "priority_score": 0, "aspect_sentiment_label": "Neutral", "matched_keywords": "", 
            "has_phone": False, "has_email": False, "strong_negative": False, "urgent": False, "nps_type": "Passive", "nps_score": 0, "mixed_feedback": False,
            "language_detected": "Unknown", "churn_risk": False, "tone_intensity_score": 0.0, "sarcasm_suspected": False, "escalation_required": False, "action_recommendation": "Skip", "absa_breakdown": []
        }

def analyze_dataframe(df: pd.DataFrame, text_col="Review"):
    results = df[text_col].apply(lambda x: analyze_single(x))
    res_df = pd.DataFrame(list(results))
    
    export_df = res_df.drop(columns=['absa_breakdown'], errors='ignore')
    final_df = pd.concat([df.reset_index(drop=True), export_df.drop(columns=['Review'], errors='ignore')], axis=1)
    
    total = len(final_df)
    promoters = len(final_df[final_df['nps_type'] == 'Promoter'])
    detractors = len(final_df[final_df['nps_type'] == 'Detractor'])
    nps_final = round((promoters/total*100) - (detractors/total*100), 2) if total > 0 else 0
    
    meta = {
        "total_reviews": total, "net_promoter_score": nps_final,
        "critical_count": len(final_df[final_df['priority_label'] == 'Critical']),
        "churn_risk_count": len(final_df[final_df['churn_risk'] == True]) if 'churn_risk' in final_df.columns else 0,
        "negative_percentage": round(len(final_df[final_df['sentiment_label'] == 'negative']) / total * 100, 2) if total > 0 else 0
    }
    return final_df, meta
