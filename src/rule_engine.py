# Map keywords to the neutral entities defined in config.py
PRIMARY_ASPECT_KEYWORDS = {
    "Payment": ["payment", "money", "refund", "paisa", "transaction", "upi", "charge", "paid", "wallet", "deducted", "bill"],
    "Customer Support": ["support", "customer care", "helpline", "service", "call", "agent", "response", "reply", "executive"],
    "Delivery & Logistics": ["delivery", "late", "time", "boy", "order", "track", "received", "wait", "address", "shipping"],
    "Product Quality": ["product", "quality", "broken", "taste", "item", "package", "damaged", "stale", "fake", "original"],
    "Platform UI": ["app", "crash", "lag", "bug", "update", "glitch", "screen", "slow", "loading", "website"],
    "General": []
}

EMOTION_KEYWORDS = {
    "Angry": ["fucking", "hell", "wtf", "scam", "fraud", "chor", "lutera", "disgusting", "terrible"],
    "Frustrated": ["annoying", "why", "again", "stuck", "waiting", "pareshan", "bakwas", "irritating", "waste"],
    "Satisfied": ["good", "nice", "okay", "fine", "theek", "acha", "decent"],
    "Delighted": ["love", "amazing", "best", "excellent", "superb", "perfect", "wow", "fantastic"]
}

CUSTOMER_INTENT_KEYWORDS = {
    "Complaint": ["fix", "resolve", "terrible", "worst", "ghatiya", "issue", "problem", "broken"],
    "Query": ["how", "when", "where", "status", "kaha", "kab", "help", "guide"],
    "Praise": ["great job", "thank you", "thanks", "appreciate", "shukriya", "kudos"],
    "Churn_Risk": ["uninstall", "delete", "never again", "switch", "leaving", "fraud", "bye", "cancel"]
}

ASPECT_SENT_NEG_KW = ["not", "never", "fail", "bad", "poor", "bekar", "kharab", "worst", "hate"]
ASPECT_SENT_POS_KW = ["good", "fast", "smooth", "great", "awesome", "mast", "best", "love"]
