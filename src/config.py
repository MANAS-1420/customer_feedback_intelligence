# =========================================================
# CLASSIFICATION LABELS
# =========================================================

# Index 0-7
PRIMARY_ASPECT_LABELS = [
    "product_quality",   # 0
    "delivery_issue",    # 1
    "payment_issue",     # 2
    "customer_service",  # 3
    "pricing_issue",     # 4
    "technical_issue",   # 5
    "refund_return",     # 6
    "general_feedback"   # 7
]

# Index 0-5
EMOTION_LABELS = [
    "very_angry",  # 0
    "angry",       # 1
    "frustrated",  # 2
    "satisfied",   # 3
    "calm",        # 4
    "happy"        # 5
]

# Index 0-6
CUSTOMER_INTENT_LABELS = [
    "complaint",      # 0
    "delay",          # 1
    "praise",          # 2
    "enquiry",        # 3
    "negative_tone",  # 4
    "neutral_tone",   # 5
    "positive_tone"   # 6
]

# Index 0-3
PRIORITY_LABELS = [
    "low",      # 0
    "medium",   # 1
    "high",     # 2
    "critical"  # 3
]

# Index 0-2
ASPECT_SENTIMENT_LABELS = [
    "negative",  # 0
    "neutral",   # 1
    "positive"   # 2
]

# Helper for dynamic ID lookups
LABEL_MAPS = {
    "aspect": {label: i for i, label in enumerate(PRIMARY_ASPECT_LABELS)},
    "emotion": {label: i for i, label in enumerate(EMOTION_LABELS)},
    "intent": {label: i for i, label in enumerate(CUSTOMER_INTENT_LABELS)},
    "priority": {label: i for i, label in enumerate(PRIORITY_LABELS)},
    "sentiment": {label: i for i, label in enumerate(ASPECT_SENTIMENT_LABELS)}
}
