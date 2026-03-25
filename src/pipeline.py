import re
import pandas as pd
from src.config import PRIMARY_ASPECT_LABELS, EMOTION_LABELS, CUSTOMER_INTENT_LABELS, PRIORITY_LABELS
from src.rule_engine import PRIMARY_ASPECT_KEYWORDS, EMOTION_KEYWORDS, CUSTOMER_INTENT_KEYWORDS, ASPECT_SENT_NEG_KW, ASPECT_SENT_POS_KW
from src.utils import normalize, any_hit, matched_keywords, best_match_id
from src.bert_model import bert_sentiment

STRONG_NEG = re.compile(r"(very|too|bahut|bohot|ghatiya|bekar)\s+(bad|worst|poor|kharaab|घटिया)")

def calculate_priority(text, is_neg):
    score = 0
    if any_hit(text, ["fraud", "scam", "police", "dhokha", "consumer court"]): score += 8
    if any_hit(text, ["refund", "paisa", "money", "stolen", "deducted"]): score += 5
    if is_neg: score += 3
    
    if score >= 8: return 3 # Critical
    if score >= 5: return 2 # High
    if score >= 2: return 1 # Medium
    return 0 # Low

def _analyze_core(review_text: str, use_bert: bool = True) -> dict:
    t = normalize(str(review_text))
    
    # 1. Base Identification
    base_aspect_id = best_match_id(t, PRIMARY_ASPECT_KEYWORDS, PRIMARY_ASPECT_LABELS, 5) # 5 is General
    base_aspect_name = PRIMARY_ASPECT_LABELS[base_aspect_id]
    
    emotion_id = best_match_id(t, EMOTION_KEYWORDS, EMOTION_LABELS, 2)
    intent_id = best_match_id(t, CUSTOMER_INTENT_KEYWORDS, CUSTOMER_INTENT_LABELS, 1)

    # 2. Hybrid Sentiment Engine
    rule_sent = 0 if any_hit(t, ASPECT_SENT_NEG_KW) else (2 if any_hit(t, ASPECT_SENT_POS_KW) else 1)
    if use_bert:
        bert_val, conf = bert_sentiment(str(review_text))
        final_sent = bert_val if conf > 0.65 else rule_sent
    else:
        final_sent, conf = rule_sent, 0.0

    # 3. CONTEXT-AWARE ASPECT FORMATTING
    if final_sent == 0: # Negative
        context_aspect = f"{base_aspect_name} Issue"
    elif final_sent == 2: # Positive
        context_aspect = f"{base_aspect_name} Experience"
    else: # Neutral
        context_aspect = f"{base_aspect_name} Feedback"

    # 4. Priority & Consistency Logic
    priority_id = calculate_priority(t, final_sent == 0)
    
    if final_sent == 2: # Override for positive reviews
        priority_id = min(priority_id, 1) # Cap priority at Medium
        if emotion_id in [0, 1]: emotion_id = 3 # Force Happy if rule engine missed it
        if intent_id == 0: intent_id = 3 # Convert Complaint to Praise

    # Ensure keywords flat list for tracking
    all_kws = []
    for klist in PRIMARY_ASPECT_KEYWORDS.values(): all_kws.extend(klist)

    action_rec = "Log for standard reporting."
    if priority_id == 3: action_rec = "Immediate management intervention required."
    elif priority_id == 2: action_rec = "Requires 4-hour SLA response."

    return {
        "Review": review_text,
        "sentiment_label": ["negative", "neutral", "positive"][final_sent],
        "bert_confidence": conf,
        "primary_aspect_label": context_aspect,
        "emotion_label": EMOTION_LABELS[emotion_id],
        "customer_intent_label": CUSTOMER_INTENT_LABELS[intent_id],
        "priority_label": PRIORITY_LABELS[priority_id],
        "matched_keywords": ", ".join(matched_keywords(t, all_kws)[:4]),
        "action_recommendation": action_rec
    }

def analyze_single(text): 
    return _analyze_core(text, True)

def analyze_dataframe(df, text_col):
    results = df[text_col].astype(str).apply(lambda x: _analyze_core(x, False))
    res_df = pd.DataFrame(list(results))
    final_df = pd.concat([df.reset_index(drop=True), res_df.drop(columns=['Review'], errors='ignore')], axis=1)
    return final_df, {}
