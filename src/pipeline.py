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
from src.utils import normalize, best_match_id, any_hit, matched_keywords
from src.bert_model import bert_sentiment

PHONE_PATTERN = re.compile(r"\b\d{10}\b")
EMAIL_PATTERN = re.compile(r"\S+@\S+")
STRONG_NEG_PATTERN = re.compile(
    r"(very|too|extremely|bahut|bohot|बहुत)\s+"
    r"(bad|worst|poor|ghatiya|bekar|खराब|बेकार|घटिया)"
)
URGENT_PATTERN = re.compile(
    r"(urgent|asap|immediately|jaldi|abhi|turant|ज़रूरी|तुरंत|अभी)"
)

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


def detect_rule_sentiment(text: str, aspect: int) -> int:
    if any_hit(text, ASPECT_SENT_NEG_KW):
        return 0
    if any_hit(text, ASPECT_SENT_POS_KW):
        if POSITIVE_ASPECT_ALLOW.get(int(aspect), False):
            return 2
        return 1
    if any_hit(text, ASPECT_SENT_NEU_KW):
        return 1
    if NEGATIVE_ASPECT_BIAS.get(int(aspect), False):
        return 0
    return 1


def hybrid_sentiment(text: str, rule_sentiment: int):
    bert_pred, confidence = bert_sentiment(text)
    if confidence > 0.75:
        return bert_pred, "BERT", confidence
    return rule_sentiment, "RULE", confidence


def tone_override(row_text: str, sentiment: int) -> int:
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

    if sentiment == 0:
        return neg_tone_id
    if sentiment == 2:
        return pos_tone_id
    return neu_tone_id


def calculate_priority_score(text: str, has_urgent: bool, strong_negative: bool) -> int:
    score = 0

    if any_hit(text, [
        "fraud", "frauds", "scam", "scammers", "cheater", "cheaters",
        "threat", "harassment", "illegal", "dhokha", "dhokebaaz",
        "फ्रॉड", "धोखा", "धमकी", "चोरी"
    ]):
        score += 5

    if any_hit(text, [
        "money deducted", "double payment", "refund not received",
        "damaged", "not delivered", "wrong product",
        "paisa kat gaya", "refund nahi mila", "delivery nahi hui",
        "पैसा कट गया", "रिफंड नहीं मिला", "डिलीवरी नहीं हुई"
    ]):
        score += 4

    if strong_negative:
        score += 3

    if has_urgent:
        score += 3

    if any_hit(text, [
        "delay", "pending", "no response", "slow", "waiting",
        "late", "follow up", "der", "pending hai",
        "देरी", "पेंडिंग", "इंतज़ार"
    ]):
        score += 2

    if any_hit(text, [
        "good", "nice", "ok", "fine", "happy", "satisfied",
        "acha", "theek", "khush", "अच्छा", "ठीक", "खुश"
    ]):
        score -= 2

    return score


def score_to_priority(score: int) -> int:
    if score >= 7:
        return PRIORITY_LABELS.index("critical")
    if score >= 5:
        return PRIORITY_LABELS.index("high")
    if score >= 2:
        return PRIORITY_LABELS.index("medium")
    return PRIORITY_LABELS.index("low")


def enforce_consistency(sentiment: int, intent: int, priority: int, emotion: int) -> int:
    low = PRIORITY_LABELS.index("low")
    medium = PRIORITY_LABELS.index("medium")

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
    return ", ".join(deduped[:15])


def _analyze_core(review_text: str, use_bert: bool = True) -> dict:
    t = normalize(review_text)

    has_phone = bool(PHONE_PATTERN.search(review_text))
    has_email = bool(EMAIL_PATTERN.search(review_text))
    strong_negative = bool(STRONG_NEG_PATTERN.search(t))
    is_urgent = bool(URGENT_PATTERN.search(t))

    severe_risk_terms = [
        "fraud", "frauds", "scam", "scammers", "cheater", "cheaters",
        "fraud company", "scam company", "you are cheater", "you are cheaters",
        "chor", "dhokebaaz", "dhokha", "dhamki",
        "फ्रॉड", "धोखा", "धमकी", "चोरी"
    ]

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

    if has_phone or has_email:
        priority = max(priority, PRIORITY_LABELS.index("medium"))

    if any_hit(t, severe_risk_terms):
        priority = PRIORITY_LABELS.index("critical")
        emotion = EMOTION_LABELS.index("very_angry")
        forced_sentiment = 0
    else:
        forced_sentiment = None

    rule_sentiment = detect_rule_sentiment(t, primary_aspect)

    if use_bert:
        final_sentiment, sentiment_source, bert_confidence = hybrid_sentiment(review_text, rule_sentiment)
    else:
        final_sentiment, sentiment_source, bert_confidence = rule_sentiment, "RULE", 0.0

    if strong_negative:
        final_sentiment = 0

    if forced_sentiment is not None:
        final_sentiment = forced_sentiment

    customer_intent = tone_override(t, final_sentiment)

    if any_hit(t, severe_risk_terms):
        customer_intent = CUSTOMER_INTENT_LABELS.index("complaint")

    # Strong fallback correction for negative reviews
    if final_sentiment == 0:
        if customer_intent == CUSTOMER_INTENT_LABELS.index("neutral_tone"):
            customer_intent = CUSTOMER_INTENT_LABELS.index("complaint")

        if emotion == EMOTION_LABELS.index("calm"):
            emotion = EMOTION_LABELS.index("angry")

        if primary_aspect == PRIMARY_ASPECT_LABELS.index("general_feedback"):
            primary_aspect = PRIMARY_ASPECT_LABELS.index("customer_service")

    # Positive correction
    if final_sentiment == 2:
        if customer_intent == CUSTOMER_INTENT_LABELS.index("negative_tone"):
            customer_intent = CUSTOMER_INTENT_LABELS.index("praise")

        if emotion in [
            EMOTION_LABELS.index("angry"),
            EMOTION_LABELS.index("very_angry"),
            EMOTION_LABELS.index("frustrated")
        ]:
            emotion = EMOTION_LABELS.index("happy")

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


def analyze_single(review_text: str) -> dict:
    return _analyze_core(review_text, use_bert=True)


def analyze_row(review_text: str, use_bert: bool = False) -> dict:
    return _analyze_core(review_text, use_bert=use_bert)


def analyze_dataframe(df: pd.DataFrame, text_col: str = "Review", use_bert: bool = False) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        rows.append(analyze_row(str(row[text_col]), use_bert=use_bert))
    return pd.DataFrame(rows)
