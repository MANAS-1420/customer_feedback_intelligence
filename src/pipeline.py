import re
import pandas as pd
from src.config import (
    PRIMARY_ASPECT_LABELS,
    EMOTION_LABELS,
    CUSTOMER_INTENT_LABELS,
    PRIORITY_LABELS
)
from src.rule_engine import (
    PRIMARY_ASPECT_KEYWORDS,
    EMOTION_KEYWORDS,
    CUSTOMER_INTENT_KEYWORDS,
    PRIORITY_KEYWORDS,
    ASPECT_SENT_NEG_KW,
    ASPECT_SENT_POS_KW,
    ASPECT_SENT_NEU_KW
)
from src.utils import normalize, best_match_id, any_hit, parse_global_sentiment, matched_keywords
from src.bert_model import bert_sentiment

PHONE_PATTERN = re.compile(r"\b\d{10}\b")
EMAIL_PATTERN = re.compile(r"\S+@\S+")
STRONG_NEG_PATTERN = re.compile(r"(very|too|extremely|bahut|bohot)\s+(bad|worst|poor|ghatiya|bekar)")
URGENT_PATTERN = re.compile(r"(urgent|asap|immediately|jaldi|abhi|turant)")

NEGATIVE_ASPECT_BIAS = {
    PRIMARY_ASPECT_LABELS.index("product_quality"): True,
    PRIMARY_ASPECT_LABELS.index("delivery_issue"): True,
    PRIMARY_ASPECT_LABELS.index("payment_issue"): True,
    PRIMARY_ASPECT_LABELS.index("customer_service"): True,
    PRIMARY_ASPECT_LABELS.index("pricing_issue"): True,
    PRIMARY_ASPECT_LABELS.index("technical_issue"): True,
    PRIMARY_ASPECT_LABELS.index("refund_return"): True,
    PRIMARY_ASPECT_LABELS.index("general_feedback"): False
}

POSITIVE_ASPECT_ALLOW = {
    PRIMARY_ASPECT_LABELS.index("customer_service"): True,
    PRIMARY_ASPECT_LABELS.index("general_feedback"): True,
    PRIMARY_ASPECT_LABELS.index("product_quality"): True
}

def assign_aspect_sentiment(text: str, global_sentiment: int, aspect: int) -> int:
    t = text

    if any_hit(t, ASPECT_SENT_NEG_KW):
        return 0

    if any_hit(t, ASPECT_SENT_POS_KW):
        if POSITIVE_ASPECT_ALLOW.get(int(aspect), False):
            return 2
        return 1

    if any_hit(t, ASPECT_SENT_NEU_KW):
        return 1

    if int(global_sentiment) == 0 and NEGATIVE_ASPECT_BIAS.get(int(aspect), False):
        return 0

    if int(global_sentiment) == 2 and POSITIVE_ASPECT_ALLOW.get(int(aspect), False):
        return 2

    return 1

def hybrid_sentiment(text: str, rule_sentiment: int):
    bert_pred, confidence = bert_sentiment(text)
    if confidence > 0.75:
        return bert_pred, "BERT", confidence
    return rule_sentiment, "RULE", confidence

def tone_override(row_text: str, asp_sent: int) -> int:
    complaint_id = CUSTOMER_INTENT_LABELS.index("complaint")
    delay_id = CUSTOMER_INTENT_LABELS.index("delay")
    praise_id = CUSTOMER_INTENT_LABELS.index("praise")
    enquiry_id = CUSTOMER_INTENT_LABELS.index("enquiry")
    neg_tone_id = CUSTOMER_INTENT_LABELS.index("negative_tone")
    neu_tone_id = CUSTOMER_INTENT_LABELS.index("neutral_tone")
    pos_tone_id = CUSTOMER_INTENT_LABELS.index("positive_tone")

    if any_hit(row_text, CUSTOMER_INTENT_KEYWORDS["enquiry"]):
        return enquiry_id
    if any_hit(row_text, CUSTOMER_INTENT_KEYWORDS["delay"]):
        return delay_id
    if any_hit(row_text, CUSTOMER_INTENT_KEYWORDS["complaint"]):
        return complaint_id
    if any_hit(row_text, CUSTOMER_INTENT_KEYWORDS["praise"]):
        return praise_id

    if asp_sent == 0:
        return neg_tone_id
    if asp_sent == 2:
        return pos_tone_id
    return neu_tone_id

def calculate_priority_score(text, has_urgent, strong_negative):
    score = 0

    if any_hit(text, ["fraud", "scam", "threat", "harassment", "illegal", "dhokha"]):
        score += 5

    if any_hit(text, ["money deducted", "double payment", "refund not received", "damaged", "not delivered"]):
        score += 4

    if strong_negative:
        score += 3

    if has_urgent:
        score += 3

    if any_hit(text, ["delay", "pending", "no response", "slow", "waiting"]):
        score += 2

    if any_hit(text, ["good", "nice", "ok", "fine", "happy", "satisfied"]):
        score -= 2

    return score

def score_to_priority(score):
    if score >= 7:
        return PRIORITY_LABELS.index("critical")
    elif score >= 5:
        return PRIORITY_LABELS.index("high")
    elif score >= 2:
        return PRIORITY_LABELS.index("medium")
    else:
        return PRIORITY_LABELS.index("low")

def enforce_consistency(sentiment, intent, priority, emotion):
    low = PRIORITY_LABELS.index("low")
    medium = PRIORITY_LABELS.index("medium")
    high = PRIORITY_LABELS.index("high")
    critical = PRIORITY_LABELS.index("critical")

    if sentiment == 2:
        return low

    if sentiment == 1 and priority > medium:
        return medium

    if emotion == EMOTION_LABELS.index("happy"):
        return low

    if emotion == EMOTION_LABELS.index("calm") and priority > medium:
        return medium

    if intent == CUSTOMER_INTENT_LABELS.index("praise"):
        return low

    if intent == CUSTOMER_INTENT_LABELS.index("enquiry") and priority > medium:
        return medium

    return priority

def collect_matches(text: str) -> str:
    all_kw = []
    for kw_list in [
        *PRIMARY_ASPECT_KEYWORDS.values(),
        *EMOTION_KEYWORDS.values(),
        *CUSTOMER_INTENT_KEYWORDS.values(),
        *PRIORITY_KEYWORDS.values()
    ]:
        all_kw.extend(matched_keywords(text, kw_list))
    deduped = list(dict.fromkeys(all_kw))
    return ", ".join(deduped[:12])

def analyze_single(review_text: str, sentiment_value) -> dict:
    t = normalize(review_text)
    global_sentiment = parse_global_sentiment(sentiment_value)

    has_phone = bool(PHONE_PATTERN.search(review_text))
    has_email = bool(EMAIL_PATTERN.search(review_text))
    strong_negative = bool(STRONG_NEG_PATTERN.search(t))
    is_urgent = bool(URGENT_PATTERN.search(t))

    primary_aspect = best_match_id(
        t, PRIMARY_ASPECT_KEYWORDS, PRIMARY_ASPECT_LABELS, default_id=7
    )

    emotion = best_match_id(
        t, EMOTION_KEYWORDS, EMOTION_LABELS, default_id=4
    )

    customer_intent = best_match_id(
        t, CUSTOMER_INTENT_KEYWORDS, CUSTOMER_INTENT_LABELS, default_id=5
    )

    rule_priority = best_match_id(
        t, PRIORITY_KEYWORDS, PRIORITY_LABELS, default_id=1
    )

    priority_score = calculate_priority_score(t, is_urgent, strong_negative)
    scored_priority = score_to_priority(priority_score)
    priority = max(rule_priority, scored_priority)

    risk_keywords = ["fraud", "scam", "threat", "harassment", "illegal", "dhokha", "dhamki"]
    if any_hit(t, risk_keywords):
        priority = PRIORITY_LABELS.index("critical")

    if has_phone or has_email:
        priority = max(priority, PRIORITY_LABELS.index("medium"))

    rule_sentiment = assign_aspect_sentiment(t, global_sentiment, primary_aspect)
    final_sentiment, sentiment_source, bert_confidence = hybrid_sentiment(review_text, rule_sentiment)

    if strong_negative:
        final_sentiment = 0

    customer_intent = tone_override(t, final_sentiment)
    priority = enforce_consistency(final_sentiment, customer_intent, priority, emotion)

    return {
        "Review": review_text,
        "Sentiment": final_sentiment,
        "sentiment_label": ["negative", "neutral", "positive"][final_sentiment],
        "sentiment_source": sentiment_source,
        "bert_confidence": round(float(bert_confidence), 4),
        "primary_aspect": primary_aspect,
        "primary_aspect_label": PRIMARY_ASPECT_LABELS[primary_aspect],
        "emotion": emotion,
        "emotion_label": EMOTION_LABELS[emotion],
        "customer_intent": customer_intent,
        "customer_intent_label": CUSTOMER_INTENT_LABELS[customer_intent],
        "priority": priority,
        "priority_label": PRIORITY_LABELS[priority],
        "priority_score": priority_score,
        "aspect_sentiment": final_sentiment,
        "aspect_sentiment_label": ["negative", "neutral", "positive"][final_sentiment],
        "matched_keywords": collect_matches(t),
        "has_phone": has_phone,
        "has_email": has_email,
        "strong_negative": strong_negative,
        "urgent": is_urgent
    }

def analyze_dataframe(df: pd.DataFrame, text_col="Review", sentiment_col="Sentiment") -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        rows.append(analyze_single(row[text_col], row[sentiment_col]))
    return pd.DataFrame(rows)
