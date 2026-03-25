import re
import pandas as pd
from src.config import PRIMARY_ASPECT_LABELS, EMOTION_LABELS, CUSTOMER_INTENT_LABELS, PRIORITY_LABELS
from src.rule_engine import *
from src.utils import normalize, any_hit, matched_keywords, best_match_id
from src.bert_model import bert_sentiment

PHONE_PATTERN = re.compile(r"\b\d{10}\b")
STRONG_NEG = re.compile(r"(very|too|bahut|bohot|ghatiya|bekar|खराब|बेकार)\s+(bad|worst|poor|kharaab|घटिया)")

def calculate_priority(text, is_neg):
    score = 0
    if any_hit(text, ["fraud", "scam", "police", "dhokha"]): score += 8
    if any_hit(text, ["refund", "paisa", "money", "stolen"]): score += 5
    if is_neg: score += 3
    if score >= 8: return 3 # Critical
    if score >= 5: return 2 # High
    if score >= 2: return 1 # Medium
    return 0 # Low

def _analyze_core(review_text: str, use_bert: bool = True) -> dict:
    t = normalize(review_text)
    is_strong_neg = bool(STRONG_NEG.search(t))
    
    aspect_id = best_match_id(t, PRIMARY_ASPECT_KEYWORDS, PRIMARY_ASPECT_LABELS, 7)
    emotion_id = best_match_id(t, EMOTION_KEYWORDS, EMOTION_LABELS, 4)
    intent_id = best_match_id(t, CUSTOMER_INTENT_KEYWORDS, CUSTOMER_INTENT_LABELS, 5)

    rule_sent = 0 if any_hit(t, ASPECT_SENT_NEG_KW) else (2 if any_hit(t, ASPECT_SENT_POS_KW) else 1)
    
    if use_bert:
        bert_val, conf = bert_sentiment(review_text)
        final_sent = bert_val if conf > 0.7 else rule_sent
    else:
        final_sent, conf = rule_sent, 0.0

    priority_id = calculate_priority(t, final_sent == 0)

    # Consistency Logic
    if final_sent == 2: # Positive
        priority_id = min(priority_id, 1)
        intent_id = 2 if intent_id == 0 else intent_id

    return {
        "Review": review_text,
        "Sentiment": final_sent,
        "sentiment_label": ["negative", "neutral", "positive"][final_sent],
        "bert_confidence": conf,
        "primary_aspect_label": PRIMARY_ASPECT_LABELS[aspect_id],
        "emotion_label": EMOTION_LABELS[emotion_id],
        "customer_intent_label": CUSTOMER_INTENT_LABELS[intent_id],
        "priority_label": PRIORITY_LABELS[priority_id],
        "matched_keywords": ", ".join(matched_keywords(t, sum(PRIMARY_ASPECT_KEYWORDS.values(), []))[:5])
    }

def analyze_single(text): return _analyze_core(text, True)
def analyze_dataframe(df, text_col):
    results = df[text_col].astype(str).apply(lambda x: _analyze_core(x, False))
    return pd.DataFrame(list(results))
