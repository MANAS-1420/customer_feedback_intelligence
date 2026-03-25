import re
import pandas as pd
from collections import Counter
from src.config import (
    PRIMARY_ASPECT_LABELS,
    EMOTION_LABELS,
    CUSTOMER_INTENT_LABELS,
    PRIORITY_LABELS,
    LABEL_MAPS
)
from src.rule_engine import (
    PRIMARY_ASPECT_KEYWORDS,
    EMOTION_KEYWORDS,
    CUSTOMER_INTENT_KEYWORDS,
    PRIORITY_KEYWORDS,
    ASPECT_SENT_NEG_KW,
    ASPECT_SENT_POS_KW,
    ASPECT_SENT_NEU_KW,
    NEGATION_WORDS
)
from src.utils import normalize, any_hit, matched_keywords, best_match_id
from src.bert_model import bert_sentiment

# Pre-compiled Patterns for Speed
PHONE_PATTERN = re.compile(r"\b\d{10}\b")
EMAIL_PATTERN = re.compile(r"\S+@\S+")
STRONG_NEG_PATTERN = re.compile(
    r"(very|too|extremely|bahut|bohot|बहुत)\s+"
    r"(bad|worst|poor|ghatiya|bekar|kharaab|खराब|बेकार|घटिया)"
)
URGENT_PATTERN = re.compile(
    r"(urgent|asap|immediately|jaldi|abhi|turant|zaroori|तुरंत|अभी|जल्दी)"
)

def detect_rule_sentiment(text: str, aspect_label: str) -> int:
    """Rule-based sentiment with negation awareness."""
    neg_score = any_hit(text, ASPECT_SENT_NEG_KW)
    pos_score = any_hit(text, ASPECT_SENT_POS_KW)
    
    # Basic Negation Flip (e.g., "not good")
    has_negation = any_hit(text, NEGATION_WORDS)
    
    if neg_score and not has_negation: return 0
    if pos_score and has_negation: return 0 # "not good" -> negative
    if pos_score: return 2
    
    return 1 # Default Neutral

def calculate_priority_score(text: str, is_urgent: bool, strong_neg: bool) -> int:
    """Weighted scoring for business priority."""
    score = 0
    # Level 5: Legal/Security Risk
    if any_hit(text, ["fraud", "scam", "police", "court", "threat", "dhokha"]): score += 7
    # Level 4: Monetary/Core Service Fail
    if any_hit(text, ["paisa", "money", "deducted", "refund", "broken", "wrong product"]): score += 5
    # Level 3: Intensity
    if strong_neg: score += 3
    if is_urgent: score += 2
    # Level 2: Delays
    if any_hit(text, ["delay", "pending", "late", "waiting"]): score += 2
    # Level 1: Positive Buffer
    if any_hit(text, ["good", "nice", "thanks", "happy"]): score -= 2
    
    return score

def _analyze_core(review_text: str, use_bert: bool = True) -> dict:
    clean_text = normalize(review_text)
    
    # 1. Regex Signals
    has_phone = bool(PHONE_PATTERN.search(review_text))
    has_email = bool(EMAIL_PATTERN.search(review_text))
    is_strong_neg = bool(STRONG_NEG_PATTERN.search(clean_text))
    is_urgent = bool(URGENT_PATTERN.search(clean_text))

    # 2. Aspect & Emotion & Intent Detection
    aspect_id = best_match_id(clean_text, PRIMARY_ASPECT_KEYWORDS, PRIMARY_ASPECT_LABELS, 7)
    emotion_id = best_match_id(clean_text, EMOTION_KEYWORDS, EMOTION_LABELS, 4)
    intent_id = best_match_id(clean_text, CUSTOMER_INTENT_KEYWORDS, CUSTOMER_INTENT_LABELS, 5)

    # 3. Hybrid Sentiment
    rule_sent = detect_rule_sentiment(clean_text, PRIMARY_ASPECT_LABELS[aspect_id])
    if use_bert:
        bert_sent_val, confidence = bert_sentiment(review_text)
        # Trust BERT if confidence is high, else fallback to Rule Engine
        if confidence > 0.70:
            final_sent = bert_sent_val
            source = "BERT"
        else:
            final_sent = rule_sent
            source = "RULE"
    else:
        final_sent = rule_sent
        source = "RULE"
        confidence = 0.0

    # 4. Priority Logic
    p_score = calculate_priority_score(clean_text, is_urgent, is_strong_neg)
    if p_score >= 7: priority_id = 3 # Critical
    elif p_score >= 5: priority_id = 2 # High
    elif p_score >= 2: priority_id = 1 # Medium
    else: priority_id = 0 # Low

    # 5. Consistency Layer (Force Logic)
    if final_sent == 2: # Positive
        priority_id = min(priority_id, 1) # Max Medium
        if intent_id == 0: intent_id = 2 # Complaint -> Praise
        if emotion_id < 3: emotion_id = 5 # Angry -> Happy
    
    if final_sent == 0: # Negative
        if emotion_id >= 3: emotion_id = 1 # Happy -> Angry

    return {
        "Review": review_text,
        "Sentiment": final_sent,
        "sentiment_label": ["negative", "neutral", "positive"][final_sent],
        "sentiment_source": source,
        "bert_confidence": round(confidence, 4),
        "primary_aspect_label": PRIMARY_ASPECT_LABELS[aspect_id],
        "emotion_label": EMOTION_LABELS[emotion_id],
        "customer_intent_label": CUSTOMER_INTENT_LABELS[intent_id],
        "priority_label": PRIORITY_LABELS[priority_id],
        "priority_score": p_score,
        "matched_keywords": ", ".join(matched_keywords(clean_text, sum(PRIMARY_ASPECT_KEYWORDS.values(), []))[:10]),
        "has_phone": has_phone, "has_email": has_email, "urgent": is_urgent
    }

def analyze_single(text: str) -> dict:
    return _analyze_core(text, use_bert=True)

def analyze_dataframe(df: pd.DataFrame, text_col: str = "Review", use_bert: bool = False) -> pd.DataFrame:
    # Set use_bert=False for batch to save time/resources, but allow override
    results = df[text_col].astype(str).apply(lambda x: _analyze_core(x, use_bert=use_bert))
    return pd.DataFrame(list(results))
