import re
import pandas as pd
from collections import Counter
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
from src.utils import normalize, any_hit, matched_keywords
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
    "product_quality": True,
    "delivery_issue": True,
    "payment_issue": True,
    "customer_service": True,
    "pricing_issue": True,
    "technical_issue": True,
    "refund_return": True,
    "general_feedback": False
}

POSITIVE_ASPECT_ALLOW = {
    "customer_service": True,
    "general_feedback": True,
    "product_quality": True
}


def score_labels(text: str, keywords_by_label: dict, labels: list[str]) -> tuple[int, int]:
    scores = Counter()
    for label in labels:
        for kw in keywords_by_label.get(label, []):
            if kw and kw in text:
                scores[label] += 1

    if not scores:
        return -1, 0

    best_label, best_score = scores.most_common(1)[0]
    return labels.index(best_label), best_score


def detect_rule_sentiment(text: str, aspect_label: str) -> int:
    if any_hit(text, ASPECT_SENT_NEG_KW):
        return 0
    if any_hit(text, ASPECT_SENT_POS_KW):
        if POSITIVE_ASPECT_ALLOW.get(aspect_label, False):
            return 2
        return 1
    if any_hit(text, ASPECT_SENT_NEU_KW):
        return 1
    if NEGATIVE_ASPECT_BIAS.get(aspect_label, False):
        return 0
    return 1


def hybrid_sentiment(text: str, rule_sentiment: int):
    bert_pred, confidence = bert_sentiment(text)
    if confidence > 0.75:
        return bert_pred, "BERT", confidence
    return rule_sentiment, "RULE", confidence


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
        "फ्रॉड", "धोखा", "धमकी"
    ]

    # -----------------------------
    # Aspect
    # -----------------------------
    aspect_idx, aspect_score = score_labels(t, PRIMARY_ASPECT_KEYWORDS, PRIMARY_ASPECT_LABELS)
    if aspect_idx == -1 or aspect_score < 2:
        primary_aspect = PRIMARY_ASPECT_LABELS.index("general_feedback")
    else:
        primary_aspect = aspect_idx

    primary_aspect_label = PRIMARY_ASPECT_LABELS[primary_aspect]

    # -----------------------------
    # Emotion
    # -----------------------------
    emotion_idx, emotion_score = score_labels(t, EMOTION_KEYWORDS, EMOTION_LABELS)
    if emotion_idx == -1 or emotion_score < 1:
        emotion = EMOTION_LABELS.index("calm")
    else:
        emotion = emotion_idx

    # -----------------------------
    # Intent
    # -----------------------------
    intent_idx, intent_score = score_labels(t, CUSTOMER_INTENT_KEYWORDS, CUSTOMER_INTENT_LABELS)
    if intent_idx == -1 or intent_score < 1:
        customer_intent = CUSTOMER_INTENT_LABELS.index("neutral_tone")
    else:
        customer_intent = intent_idx

    # -----------------------------
    # Priority
    # -----------------------------
    priority_idx, priority_kw_score = score_labels(t, PRIORITY_KEYWORDS, PRIORITY_LABELS)
    if priority_idx == -1:
        rule_priority = PRIORITY_LABELS.index("medium")
    else:
        rule_priority = priority_idx

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

    # -----------------------------
    # Sentiment
    # -----------------------------
    rule_sentiment = detect_rule_sentiment(t, primary_aspect_label)

    if use_bert:
        final_sentiment, sentiment_source, bert_confidence = hybrid_sentiment(review_text, rule_sentiment)
    else:
        final_sentiment, sentiment_source, bert_confidence = rule_sentiment, "RULE", 0.0

    if strong_negative:
        final_sentiment = 0

    if forced_sentiment is not None:
        final_sentiment = forced_sentiment

    # -----------------------------
    # Strong correction layer
    # -----------------------------
    if final_sentiment == 0:
        if customer_intent in [
            CUSTOMER_INTENT_LABELS.index("neutral_tone"),
            CUSTOMER_INTENT_LABELS.index("positive_tone"),
            CUSTOMER_INTENT_LABELS.index("praise")
        ]:
            customer_intent = CUSTOMER_INTENT_LABELS.index("complaint")

        if emotion == EMOTION_LABELS.index("calm"):
            emotion = EMOTION_LABELS.index("angry")

        if primary_aspect == PRIMARY_ASPECT_LABELS.index("general_feedback"):
            if any_hit(t, ["refund", "return", "money back", "रिफंड", "पैसे वापस"]):
                primary_aspect = PRIMARY_ASPECT_LABELS.index("refund_return")
            elif any_hit(t, ["delivery", "shipment", "courier", "tracking", "डिलीवरी", "कूरियर"]):
                primary_aspect = PRIMARY_ASPECT_LABELS.index("delivery_issue")
            elif any_hit(t, ["payment", "upi", "charged", "debit", "पेमेंट", "पैसा कट"]):
                primary_aspect = PRIMARY_ASPECT_LABELS.index("payment_issue")
            elif any_hit(t, ["support", "service", "staff", "customer care", "सपोर्ट", "स्टाफ"]):
                primary_aspect = PRIMARY_ASPECT_LABELS.index("customer_service")
            elif any_hit(t, ["app", "login", "server", "otp", "ऐप", "लॉगिन", "ओटीपी"]):
                primary_aspect = PRIMARY_ASPECT_LABELS.index("technical_issue")
            elif any_hit(t, ["quality", "damaged", "broken", "fake", "खराब", "डैमेज", "नकली"]):
                primary_aspect = PRIMARY_ASPECT_LABELS.index("product_quality")
            else:
                primary_aspect = PRIMARY_ASPECT_LABELS.index("customer_service")

    if final_sentiment == 2:
        if customer_intent == CUSTOMER_INTENT_LABELS.index("negative_tone"):
            customer_intent = CUSTOMER_INTENT_LABELS.index("praise")

        if emotion in [
            EMOTION_LABELS.index("angry"),
            EMOTION_LABELS.index("very_angry"),
            EMOTION_LABELS.index("frustrated")
        ]:
            emotion = EMOTION_LABELS.index("happy")

    # Negative sentiment should not remain neutral tone
    if final_sentiment == 0 and customer_intent == CUSTOMER_INTENT_LABELS.index("neutral_tone"):
        customer_intent = CUSTOMER_INTENT_LABELS.index("complaint")

    # Positive sentiment should not remain complaint unless keywords are strong
    if final_sentiment == 2 and customer_intent == CUSTOMER_INTENT_LABELS.index("complaint"):
        customer_intent = CUSTOMER_INTENT_LABELS.index("praise")

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
