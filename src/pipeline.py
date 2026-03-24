import re
import time
import pandas as pd
from typing import Dict, List, Tuple


# =========================================================
# NORMALIZATION
# =========================================================
def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text).lower().strip()

    # Keep english, digits, hindi chars, and spaces
    text = re.sub(r"[^a-z0-9\u0900-\u097F\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================================================
# KEYWORDS
# =========================================================
ASPECT_KEYWORDS = {
    "Customer Service": [
        "customer care", "customer service", "support", "helpdesk", "helpline",
        "staff", "executive", "agent", "representative", "service team",
        "team", "branch staff", "manager", "sales person", "salesperson",
        "care team", "support team", "customer support",
        "सपोर्ट", "कस्टमर केयर", "स्टाफ", "मैनेजर", "एजेंट", "टीम",
        "madad", "help", "response", "behaviour", "behavior", "service"
    ],
    "Charges": [
        "charge", "charges", "hidden charge", "hidden charges", "extra charge",
        "extra charges", "processing fee", "fee", "fees", "penalty", "fine",
        "late fee", "foreclosure charges", "gst", "cost", "expensive",
        "zyada paisa", "extra paisa", "कटौती", "चार्ज", "फीस", "पेनल्टी"
    ],
    "Interest Rate": [
        "interest", "interest rate", "roi", "rate", "high interest",
        "low interest", "apr", "expensive interest", "rate of interest",
        "ब्याज", "ब्याज दर", "interest jyada", "rate high"
    ],
    "EMI / Payment": [
        "emi", "installment", "payment", "repayment", "pay", "due date",
        "autodebit", "ecs", "debit", "monthly payment", "emi date",
        "emi amount", "payment issue", "paid", "payment failed",
        "किस्त", "ईएमआई", "पेमेंट", "भुगतान", "कट गया", "कटौती"
    ],
    "App / Portal": [
        "app", "application", "portal", "website", "login", "otp", "server",
        "crash", "bug", "slow", "lag", "not working", "ui", "interface",
        "dashboard", "online", "technical issue",
        "ऐप", "लॉगिन", "वेबसाइट", "स्लो", "हैंग", "काम नहीं कर रहा"
    ],
    "Loan Process / Approval": [
        "loan", "approval", "approved", "rejected", "application process",
        "processing", "verification", "sanction", "eligibility", "apply",
        "applied", "instant approval", "quick approval",
        "loan process", "approval process",
        "लोन", "अप्रूव", "रिजेक्ट", "प्रोसेस", "वेरिफिकेशन"
    ],
    "Disbursal": [
        "disbursal", "disbursement", "credited", "amount received", "money received",
        "transfer", "credited to account", "loan amount received",
        "amount transfer", "payout",
        "डिस्बर्सल", "पैसे मिले", "अमाउंट मिला", "क्रेडिट हुआ"
    ],
    "Documentation": [
        "document", "documents", "documentation", "paperwork", "kyc",
        "id proof", "address proof", "minimal documentation",
        "form filling", "upload document",
        "दस्तावेज", "डॉक्यूमेंट", "केवाईसी", "पेपरवर्क"
    ],
    "Collection / Recovery": [
        "collection", "recovery", "recovery agent", "collection agent",
        "harassment", "threat", "pressure", "aggressive", "repeated calls",
        "calls again and again", "spam calls", "follow up calls",
        "legal notice", "warning call",
        "रिकवरी", "कलेक्शन", "बार बार कॉल", "धमकी", "परेशान", "हरासमेंट"
    ],
    "General Feedback": [
        "experience", "overall", "service", "good", "bad", "average",
        "decent", "nice", "fine", "okay", "ok", "satisfied", "unsatisfied",
        "recommend", "recommended",
        "अच्छा", "बुरा", "ठीक", "ओके", "संतुष्ट", "अनुभव"
    ]
}


POSITIVE_WORDS = [
    "good", "great", "excellent", "amazing", "awesome", "smooth", "fast",
    "quick", "helpful", "polite", "happy", "satisfied", "impressed",
    "cooperative", "best", "nice", "transparent", "easy", "hassle free",
    "resolved", "solved", "fixed", "prompt", "supportive", "professional",
    "thank you", "thanks", "very good", "well done", "recommended",
    "achha", "accha", "bahut accha", "sahi", "mast", "badhiya", "jaldi",
    "theek", "shukriya", "dhanyawad", "khush", "samadhan", "samasya solve"
]

NEGATIVE_WORDS = [
    "bad", "worst", "poor", "slow", "delay", "delayed", "rude", "issue",
    "problem", "error", "failed", "high", "expensive", "confusing", "hidden",
    "unfair", "not satisfied", "unsatisfied", "difficult", "hard", "harassment",
    "threat", "aggressive", "spam", "crash", "bug", "worried", "frustrated",
    "angry", "disappointed", "rejected", "fake", "fraud", "complaint",
    "bakwas", "bekar", "bura", "ghatiya", "problem", "dikat", "dikkat",
    "pareshan", "kharab", "slow hai", "kaam nahi kar raha", "nahi hua"
]

NEUTRAL_WORDS = [
    "okay", "ok", "fine", "average", "decent", "normal", "nothing great",
    "nothing bad", "manageable", "theek thaak", "thik thak", "theek tha"
]

RESOLUTION_WORDS = [
    "solved", "resolved", "fixed", "helped", "supportive", "helpful",
    "issue resolved", "problem solved", "quick resolution", "handled well",
    "sorted", "happy with the support", "satisfied with the support",
    "got solution", "better solution", "samasya solve", "problem solve",
    "madad ki", "solve kar diya", "resolve kar diya"
]

PRAISE_WORDS = [
    "thank you", "thanks", "helpful", "great support", "excellent service",
    "good service", "happy", "satisfied", "impressed", "very helpful",
    "quick support", "resolved quickly", "solved quickly", "polite",
    "cooperative", "recommended", "shukriya", "dhanyawad", "khush"
]

COMPLAINT_WORDS = [
    "complaint", "bad experience", "worst", "rude", "hidden charges",
    "too high", "issue", "problem", "harassment", "aggressive", "delay",
    "not satisfied", "poor service", "frustrated", "angry", "rejected",
    "bekar", "bakwas", "pareshan", "dikkat", "problem", "dhokha"
]

QUERY_WORDS = [
    "can you", "please tell", "want to know", "need help", "how to",
    "what is", "when will", "why", "query", "question", "poochna"
]

HIGH_PRIORITY_WORDS = [
    "harassment", "threat", "fraud", "legal", "worst", "aggressive",
    "recovery agent", "spam calls", "repeated calls", "serious issue",
    "urgent", "not received", "money not received", "payment failed",
    "critical", "danger", "धमकी", "फ्रॉड", "बहुत खराब"
]

MEDIUM_PRIORITY_WORDS = [
    "issue", "problem", "delay", "slow", "not working", "confusing",
    "login issue", "emi issue", "charges", "interest high", "rejected",
    "dikkat", "pareshan", "late", "bug", "crash"
]

HAPPY_WORDS = [
    "happy", "satisfied", "impressed", "thank you", "thanks", "great",
    "excellent", "good", "helpful", "resolved", "solved", "awesome",
    "badhiya", "khush", "shukriya", "dhanyawad", "accha"
]

ANGRY_WORDS = [
    "angry", "worst", "harassment", "threat", "rude", "frustrated",
    "aggressive", "fraud", "fake", "spam", "very bad", "terrible",
    "ghussa", "bakwas", "bekar", "bura", "pareshan"
]

CALM_WORDS = [
    "okay", "fine", "average", "decent", "normal", "manageable",
    "theek", "ok", "acceptable"
]


# =========================================================
# HELPERS
# =========================================================
def count_matches(text: str, keywords: List[str]) -> int:
    count = 0
    for kw in keywords:
        if kw in text:
            count += 1
    return count


def has_any(text: str, keywords: List[str]) -> bool:
    return any(kw in text for kw in keywords)


def get_matches(text: str, keywords: List[str]) -> List[str]:
    return [kw for kw in keywords if kw in text]


def detect_aspect(text: str) -> Tuple[str, List[str]]:
    scores = {}
    matched_keywords = {}

    for aspect, keywords in ASPECT_KEYWORDS.items():
        matches = get_matches(text, keywords)
        if matches:
            scores[aspect] = len(matches)
            matched_keywords[aspect] = matches

    if not scores:
        return "General Feedback", []

    best_aspect = max(scores, key=scores.get)
    return best_aspect, matched_keywords.get(best_aspect, [])


def is_positive_resolution(text: str) -> bool:
    has_negative_context = has_any(
        text,
        [
            "issue", "problem", "complaint", "not working", "dikkat", "pareshan",
            "error", "failed", "customer care", "support", "helpdesk"
        ]
    )
    has_resolution = has_any(text, RESOLUTION_WORDS)
    has_positive = has_any(text, POSITIVE_WORDS)

    return (has_negative_context and has_resolution) or (has_resolution and has_positive)


def detect_sentiment(text: str) -> Tuple[int, str]:
    if is_positive_resolution(text):
        return 2, "Positive"

    pos_score = count_matches(text, POSITIVE_WORDS)
    neg_score = count_matches(text, NEGATIVE_WORDS)
    neu_score = count_matches(text, NEUTRAL_WORDS)

    if "not helpful" in text or "not good" in text or "not satisfied" in text:
        neg_score += 2

    if "no hidden charges" in text or "without hidden charges" in text:
        pos_score += 2

    if "too high" in text or "very high" in text:
        neg_score += 2

    if "quick approval" in text or "fast disbursal" in text:
        pos_score += 2

    if pos_score > neg_score and pos_score >= neu_score:
        return 2, "Positive"
    elif neg_score > pos_score and neg_score >= neu_score:
        return 0, "Negative"
    else:
        return 1, "Neutral"


def detect_aspect_sentiment(text: str, aspect: str) -> str:
    if is_positive_resolution(text):
        return "Positive"

    pos_score = count_matches(text, POSITIVE_WORDS)
    neg_score = count_matches(text, NEGATIVE_WORDS)
    neu_score = count_matches(text, NEUTRAL_WORDS)

    if aspect == "Charges":
        if has_any(text, ["hidden charges", "extra charges", "processing fee too high", "too high charges"]):
            neg_score += 3
        if has_any(text, ["no hidden charges", "transparent charges", "charges clear"]):
            pos_score += 2

    if aspect == "Interest Rate":
        if has_any(text, ["high interest", "interest too high", "rate too high"]):
            neg_score += 3

    if aspect == "Customer Service":
        if has_any(text, ["helpful", "polite", "solved", "resolved", "supportive"]):
            pos_score += 2
        if has_any(text, ["rude", "ignored", "no response", "bad behaviour", "bad behavior"]):
            neg_score += 2

    if aspect == "App / Portal":
        if has_any(text, ["slow", "crash", "bug", "login issue", "not working"]):
            neg_score += 2

    if pos_score > neg_score and pos_score >= neu_score:
        return "Positive"
    elif neg_score > pos_score and neg_score >= neu_score:
        return "Negative"
    else:
        return "Neutral"


def detect_emotion(text: str, sentiment_label: str) -> str:
    if is_positive_resolution(text):
        return "Happy"

    happy_score = count_matches(text, HAPPY_WORDS)
    angry_score = count_matches(text, ANGRY_WORDS)
    calm_score = count_matches(text, CALM_WORDS)

    if sentiment_label == "Positive":
        happy_score += 1
    elif sentiment_label == "Negative":
        angry_score += 1
    else:
        calm_score += 1

    if happy_score >= angry_score and happy_score >= calm_score:
        return "Happy"
    elif angry_score > happy_score and angry_score >= calm_score:
        return "Angry"
    else:
        return "Calm"


def detect_intent(text: str, sentiment_label: str) -> str:
    if is_positive_resolution(text):
        return "Praise"

    praise_score = count_matches(text, PRAISE_WORDS)
    complaint_score = count_matches(text, COMPLAINT_WORDS)
    query_score = count_matches(text, QUERY_WORDS)

    if sentiment_label == "Positive":
        praise_score += 1
    elif sentiment_label == "Negative":
        complaint_score += 1

    if praise_score >= complaint_score and praise_score >= query_score:
        return "Praise"
    elif complaint_score > praise_score and complaint_score >= query_score:
        return "Complaint"
    else:
        return "Neutral Tone"


def detect_priority(text: str, sentiment_label: str) -> Tuple[str, int]:
    high_score = count_matches(text, HIGH_PRIORITY_WORDS)
    medium_score = count_matches(text, MEDIUM_PRIORITY_WORDS)

    if is_positive_resolution(text):
        if has_any(text, ["issue", "problem", "support", "customer care"]):
            return "Medium", 0
        return "Low", -1

    if high_score >= 1:
        return "High", 2

    if medium_score >= 1:
        return "Medium", 1

    if sentiment_label == "Negative":
        return "Medium", 1

    return "Low", -1


def detect_nps(sentiment_label: str, text: str) -> Tuple[str, int]:
    if is_positive_resolution(text):
        return "Promoter", 9

    if sentiment_label == "Positive":
        return "Promoter", 9
    elif sentiment_label == "Neutral":
        return "Passive", 6
    else:
        return "Detractor", 3


def keyword_source(text: str) -> str:
    if is_positive_resolution(text):
        return "RULE+CONTEXT"
    return "RULE"


# =========================================================
# MAIN ANALYSIS
# =========================================================
def analyze_review(text: str) -> Dict:
    start_time = time.time()

    original_text = text
    text = normalize_text(text)

    aspect, aspect_keywords = detect_aspect(text)
    sentiment_num, sentiment_label = detect_sentiment(text)
    aspect_sentiment = detect_aspect_sentiment(text, aspect)
    emotion = detect_emotion(text, sentiment_label)
    intent = detect_intent(text, sentiment_label)
    priority, priority_score = detect_priority(text, sentiment_label)
    nps_type, nps_score = detect_nps(sentiment_label, text)

    processing_time = round(time.time() - start_time, 3)

    matched_total = (
        count_matches(text, POSITIVE_WORDS)
        + count_matches(text, NEGATIVE_WORDS)
        + count_matches(text, NEUTRAL_WORDS)
    )

    if is_positive_resolution(text):
        confidence = 0.92
    elif matched_total >= 5:
        confidence = 0.89
    elif matched_total >= 3:
        confidence = 0.81
    elif matched_total >= 1:
        confidence = 0.72
    else:
        confidence = 0.60

    return {
        "review": original_text,
        "normalized_text": text,
        "aspect": aspect,
        "matched_aspect_keywords": ", ".join(aspect_keywords) if aspect_keywords else "",
        "emotion": emotion,
        "priority": priority,
        "priority_score": priority_score,
        "intent": intent,
        "aspect_sentiment": aspect_sentiment,
        "sentiment": sentiment_label,
        "sentiment_score": sentiment_num,
        "sentiment_source": keyword_source(text),
        "bert_confidence": round(confidence, 4),
        "processing_time": f"{processing_time}s",
        "nps_type": nps_type,
        "nps_score": nps_score
    }


# =========================================================
# WRAPPER FUNCTIONS FOR APP COMPATIBILITY
# =========================================================
def analyze_single(text: str) -> Dict:
    return analyze_review(text)


def analyze_dataframe(df: pd.DataFrame, text_col: str = "Review") -> pd.DataFrame:
    if text_col not in df.columns:
        raise ValueError(f"Column '{text_col}' not found in dataframe.")

    working_df = df.copy()
    working_df[text_col] = working_df[text_col].fillna("").astype(str)

    results = working_df[text_col].apply(analyze_review)
    results_df = pd.DataFrame(results.tolist())

    return pd.concat(
        [working_df.reset_index(drop=True), results_df.reset_index(drop=True)],
        axis=1
    )


# =========================================================
# TESTING
# =========================================================
if __name__ == "__main__":
    test_reviews = [
        "I contacted customer care regarding my issue and they solved it quickly. Very helpful team. Happy with the support.",
        "hidden charges were not explained clearly very bad experience",
        "app works fine but sometimes it crashes during payment",
        "support team ne meri problem solve kar di thank you",
        "recovery agents ka behavior bahut aggressive hai",
        "emi payment process is simple and hassle free",
        "loan reject kar diya bina proper reason ke"
    ]

    for i, review in enumerate(test_reviews, 1):
        result = analyze_single(review)
        print(f"\n{'=' * 70}")
        print(f"Review {i}: {review}")
        print(f"{'=' * 70}")
        for k, v in result.items():
            print(f"{k}: {v}")
