# src/rule_engine.py

# ==========================================
# A. MASTER TAXONOMY KEYWORDS (English, Hindi, Hinglish)
# ==========================================
TAXONOMY_KEYWORDS = {
    ("product_service_quality", "product_defect"): ["defect", "broken", "not working", "faulty", "kharab", "toota", "खराब", "टूटा", "kaam nahi kar raha"],
    ("product_service_quality", "product_quality_poor"): ["poor quality", "bad quality", "cheap material", "bekar quality", "ghatiya", "घटिया", "kachra", "bakwas"],
    ("product_service_quality", "product_quality_good"): ["good quality", "nice product", "awesome material", "acha product", "mast quality", "अच्छा", "बढ़िया"],
    ("product_service_quality", "missing_items"): ["missing", "not inside", "empty box", "gayab", "kuch nahi mila", "missing item", "गायब", "खाली"],
    ("product_service_quality", "wrong_item_delivered"): ["wrong item", "different product", "galat item", "kuch aur bhej diya", "गलत", "wrong product"],
    ("product_service_quality", "packaging_issue"): ["torn package", "open box", "bad packaging", "fata hua", "khula box", "packing kharab", "खुला", "फटा"],
    ("product_service_quality", "service_quality_poor"): ["bad service", "poor service", "bekar service", "ghatiya service", "kharab service", "खराब सर्विस"],
    ("product_service_quality", "service_quality_good"): ["good service", "best service", "great service", "acha service", "mast service", "अच्छी सर्विस"],

    ("delivery_logistics", "delayed_delivery"): ["late", "delay", "not delivered yet", "deri", "abhi tak nahi aaya", "late delivery", "देर", "विलंब"],
    ("delivery_logistics", "early_delivery"): ["early", "before time", "fast delivery", "jaldi aa gaya", "time se pehle", "जल्दी", "समय से पहले"],
    ("delivery_logistics", "no_delivery"): ["not delivered", "never arrived", "did not get", "nahi mila", "delivery nahi hui", "नहीं मिला"],
    ("delivery_logistics", "delivery_agent_behavior_rude"): ["rude delivery boy", "arrogant rider", "badtameez", "gali diya delivery", "बदतमीज़"],
    ("delivery_logistics", "delivery_agent_behavior_good"): ["polite boy", "good delivery guy", "acha ladka tha", "polite behavior", "विनम्र"],
    ("delivery_logistics", "tracking_issue"): ["track", "location", "where is my order", "kaha hai order", "track nahi ho raha", "ट्रैक"],
    ("delivery_logistics", "wrong_address_delivery"): ["wrong address", "delivered somewhere else", "kisi aur ko de diya", "galat address", "गलत पता"],
    ("delivery_logistics", "logistics_damage"): ["damaged in transit", "crushed box", "toot gaya raste me", "courier damage", "क्षतिग्रस्त"],

    ("payment_billing", "payment_failed"): ["payment fail", "transaction failed", "error in payment", "payment nahi ho raha", "भुगतान विफल"],
    ("payment_billing", "payment_deducted_not_processed"): ["money deducted", "paise kat gaye", "account debited", "amount deducted but", "पैसे कट गए"],
    ("payment_billing", "double_charge"): ["charged twice", "double payment", "do bar paise kate", "extra charge lag gaya", "दो बार पैसे"],
    ("payment_billing", "hidden_charges"): ["hidden charge", "extra tax", "loot liya", "faltu charge", "अतिरिक्त शुल्क"],
    ("payment_billing", "refund_not_received"): ["no refund", "refund pending", "refund nahi mila", "paise wapas nahi aaye", "रिफंड नहीं मिला"],
    ("payment_billing", "billing_error"): ["wrong bill", "invoice error", "galat bill", "zyada bill", "गलत बिल"],
    ("payment_billing", "fraud_suspicion"): ["fraud transaction", "scam payment", "dhokha kiya", "paise chori", "धोखाधड़ी"],

    ("customer_service", "support_unresponsive"): ["no response", "not answering", "ignoring", "koi jawab nahi", "phone nahi uthate", "कोई जवाब नहीं"],
    ("customer_service", "slow_response"): ["slow reply", "late response", "bahut time lagate", "late reply karte hai", "देर से जवाब"],
    ("customer_service", "helpful_support"): ["helpful", "good support", "solved my issue", "madad ki", "problem solve kar di", "मददगार"],
    ("customer_service", "rude_behavior"): ["rude staff", "abusive", "arrogant", "badtameezi se baat ki", "gali", "असभ्य"],
    ("customer_service", "issue_not_resolved"): ["unresolved", "not helping", "problem still there", "kuch solve nahi hua", "koi fayda nahi", "हल नहीं हुआ"],
    ("customer_service", "call_drop_issue"): ["call disconnected", "cut the call", "phone kaat diya", "beech me phone kaata", "फ़ोन काट दिया"],
    ("customer_service", "chatbot_issue"): ["useless bot", "bot not helping", "stupid chatbot", "bot samajh nahi raha", "बॉट"],

    ("technical_app_website", "app_crash"): ["app crashing", "app closes", "band ho jata hai", "crash", "क्रैश"],
    ("technical_app_website", "login_issue"): ["cannot login", "login failed", "login nahi ho raha", "sign in problem", "लॉग इन"],
    ("technical_app_website", "otp_issue"): ["otp not received", "otp problem", "otp nahi aa raha", "ओटीपी"],
    ("technical_app_website", "slow_app"): ["app is slow", "lag", "hang", "bahut slow chal raha", "hang ho raha", "धीमा"],
    ("technical_app_website", "website_down"): ["site down", "server error", "404", "website nahi chal rahi", "सर्वर डाउन"],

    ("returns_refund_cancellation", "return_rejected"): ["return denied", "rejected my return", "return cancel kar diya", "wapas nahi le rahe", "वापस नहीं"],
    ("returns_refund_cancellation", "return_pickup_delay"): ["pickup delayed", "no one came for pickup", "pickup nahi hua", "koi lene nahi aaya", "पिकअप"],
    ("returns_refund_cancellation", "cancellation_issue"): ["cannot cancel", "cancel nahi ho raha", "cancellation option gayab", "रद्द"],

    ("fraud_security", "scam_alert"): ["scam", "fraud", "thief", "fake company", "chor", "lutera", "scammer", "घोटाला", "चोर"],
    ("fraud_security", "unauthorized_transaction"): ["hacked", "did not authorize", "apne aap paise kat gaye", "hacker", "हैक"],
    ("fraud_security", "data_privacy_issue"): ["selling data", "privacy", "spam calls", "mera data leak", "डेटा लीक"],

    ("negative_intent", "angry_customer"): ["angry", "terrible", "worst", "hate", "gussa", "bekar", "ghatiya", "गुस्सा"],
    ("negative_intent", "very_angry_customer"): ["fucking", "bullshit", "bastard", "bhenchod", "madarchod", "gali", "sue", "consumer court"],
    ("negative_intent", "threatening_to_leave"): ["will uninstall", "delete app", "never use again", "uninstalling", "app delete kar raha hu", "छोड़ दूंगा"],

    ("positive_feedback", "fast_service"): ["quick", "very fast", "lightning fast", "bahut tez", "jaldi kaam", "तेज़"],
    ("positive_feedback", "excellent_product"): ["superb", "excellent", "amazing", "best", "ek number", "zabardast", "लाजवाब"],
    
    ("neutral_informational", "status_check"): ["what is status", "track", "kab aayega", "update kya hai", "स्थिति"],
    ("neutral_informational", "information_request"): ["how to use", "need help", "guide me", "kaise karna hai", "jankari", "जानकारी"]
}

for key in ["pricing_value", "order_management", "customer_experience", "suggestions_feedback", "loan_finance"]:
    TAXONOMY_KEYWORDS[(key, "general_issue")] = [key.replace("_", " ")]

# ==========================================
# B. CORE EMOTION & INTENT
# ==========================================
EMOTION_KEYWORDS = {
    "Very Angry": ["scam", "fraud", "consumer court", "chor", "fucking", "hell", "sue", "lutera"],
    "Angry": ["terrible", "worst", "pathetic", "ghatiya", "bekar", "kachra", "bakwas", "angry", "rubbish"],
    "Frustrated": ["waiting", "tired", "annoyed", "pareshan", "dimag kharab", "again", "frustrated", "irritating"],
    "Happy": ["nice", "good", "acha", "badiya", "khush", "happy", "smile"],
    "Satisfied": ["resolved", "solved", "fine", "okay", "theek", "kaam ho gaya", "satisfied"],
    "Calm": []
}

CUSTOMER_INTENT_KEYWORDS = {
    "Complaint": ["issue", "problem", "not working", "dikkat", "shikayat", "kharab", "fail", "complaint", "fix"],
    "Delay": ["late", "delay", "waiting", "deri", "pending"],
    "Praise": ["great", "best", "superb", "thank you", "shukriya", "praise", "kudos"],
    "Enquiry": ["how", "status", "kab", "kaha", "guide", "query", "help"],
    "Negative Tone": ["bad", "poor", "sad", "disappointed"],
    "Positive Tone": ["awesome", "love", "mast", "perfect"],
    "Neutral Tone": []
}

# ==========================================
# C. SENTIMENT OVERRIDES & FLAGS
# ==========================================
# Expanded to catch all severe words so it forces a negative sentiment calculation
ASPECT_SENT_NEG_KW = [
    "not", "bad", "fail", "worst", "kharab", "bekar", "nahi", "mat", "poor", "hate", "terrible", "issue", "problem", "dont", "cant",
    "ghatiya", "kachra", "bakwas", "pathetic", "fraud", "scam", "useless", "garbage", "rubbish", "slow", "late", "delay", "rude",
    "नहीं", "मत", "खराब", "बुरा", "बेकार", "घटिया", "कचरा", "बकवास"
]
ASPECT_SENT_POS_KW = [
    "good", "great", "excellent", "fast", "best", "mast", "acha", "smooth", "awesome", "perfect", "love", "badiya", "zabardast",
    "superb", "amazing", "fantastic", "polite", "helpful",
    "अच्छा", "बढ़िया", "शानदार", "मस्त", "बेहतरीन"
]
MIXED_FEEDBACK_KW = ["but", "however", "although", "lekin", "par", "magar", "phir bhi", "though", "yet"]
URGENT_KW = ["urgent", "asap", "immediately", "jaldi", "turant", "abhi", "fast", "priority"]
STRONG_NEG_PHRASES = ["worst", "pathetic", "fraud", "scam", "waste of money", "paisa barbad", "never buy", "useless", "ghatiya"]
