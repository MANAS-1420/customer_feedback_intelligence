# =========================================================
# NEGATION & INTENSITY (Used to flip or boost sentiment)
# =========================================================
NEGATION_WORDS = ["not", "no", "never", "nahi", "nahin", "ni", "nahi hai", "नहीं", "mat"]
INTENSITY_WORDS = ["very", "too", "extremely", "highly", "bahut", "bohot", "kaafi", "बहुत", "काफी"]

# =========================================================
# PRIMARY ASPECT KEYWORDS (300+ Total)
# =========================================================
PRIMARY_ASPECT_KEYWORDS = {
    "customer_service": [
        # English
        "customer service", "customer support", "support", "helpdesk", "helpline", "call center", 
        "agent", "executive", "representative", "staff", "behavior", "attitude", "rude", "polite",
        "no response", "no reply", "ignored", "ghosted", "unprofessional", "misbehave", "arrogant",
        "callback", "unresponsive", "not picking", "not answering", "waiting on hold", "transferring",
        # Hinglish/Slang
        "reply nahi", "koi response nahi", "baat nahi sun rahe", "phone nahi uthaya", "staff bekar",
        "badtamiz", "badtameez", "batameezi", "sunwai nahi", "ignore kiya", "help nahi mila",
        # Hindi
        "कोई जवाब नहीं", "सपोर्ट खराब", "स्टाफ बदतमीज़", "कस्टमर केयर", "सुनवाई", "बदतमीजी", "मदद नहीं मिली"
    ],

    "delivery_issue": [
        # English
        "delivery", "late delivery", "delayed", "shipment", "parcel", "courier", "not received", 
        "order not received", "tracking stuck", "delivery boy", "wrong address", "package missing", 
        "lost package", "failed delivery", "rescheduled", "shipping", "transit", "out for delivery",
        # Hinglish
        "delivery nahi hui", "parcel nahi aaya", "tracking nahi chal raha", "late hai", "deri se",
        "order kab aayega", "rasta bhatak gaya", "delivery wala", "boy nahi aaya",
        # Hindi
        "डिलीवरी", "ऑर्डर नहीं मिला", "कूरियर", "समय पर नहीं", "देरी से मिला", "पार्सल गुम"
    ],

    "payment_issue": [
        # English
        "payment", "transaction", "money deducted", "amount debited", "payment failed", "charged twice", 
        "double payment", "upi issue", "upi failed", "card declined", "billing error", "overcharged", 
        "processing fee", "convenience fee", "checkout", "emi", "cibil", "loan", "interest", "wallet",
        # Hinglish
        "paisa kat gaya", "amount kat gaya", "2 baar payment", "paisa wapas", "upi fail", 
        "money deduct", "double paise", "balance cut", "interest rate", "loan approval",
        # Hindi
        "पैसा कट गया", "पेमेंट फेल", "भुगतान", "गलत चार्ज", "ईएमआई", "ब्याज", "पैसे कट गए"
    ],

    "refund_return": [
        # English
        "refund", "return", "refund pending", "refund stuck", "not processed", "replacement", 
        "money back", "pickup not done", "return rejected", "cancellation", "cancelled", "reversal",
        # Hinglish
        "refund nahi mila", "paise wapas", "pickup nahi hua", "return le jao", "return reject",
        "refund kab milega", "paisa return karo", "cancel kar diya",
        # Hindi
        "रिफंड नहीं मिला", "पैसे वापस", "रिटर्न", "रिप्लेसमेंट", "पिकअप", "कैंसिल"
    ],

    "product_quality": [
        # English
        "quality", "bad quality", "defective", "broken", "damaged", "not working", "fake", "duplicate", 
        "wrong product", "used product", "dirty", "scratched", "missing parts", "manufacturing defect",
        "poor material", "low grade", "authentic", "original", "expired",
        # Hinglish
        "product kharab", "bekar quality", "nakli", "toota hua", "tuta hua", "ghatiya product",
        "duplicate maal", "fake product", "damaged nikla", "kharab maal",
        # Hindi
        "प्रोडक्ट खराब", "खराब क्वालिटी", "नकली", "डैमेज", "टूटा हुआ", "घटिया क्वालिटी"
    ],

    "technical_issue": [
        # English
        "technical", "app issue", "app crash", "bug", "error", "server down", "login issue", 
        "otp", "otp not received", "website not working", "slow app", "loading problem", 
        "verification", "kyc", "authentication", "frozen", "hanging", "lagging", "interface",
        # Hinglish
        "app nahi chal raha", "otp nahi aa raha", "error aa raha hai", "site slow", "server down",
        "login nahi ho raha", "otp send karo", "app hang", "update nahi ho raha",
        # Hindi
        "ऐप नहीं चल रहा", "सर्वर डाउन", "लॉगिन", "ओटीपी", "तकनीकी समस्या", "लोड नहीं हो रहा"
    ],

    "pricing_issue": [
        # English
        "price", "expensive", "overpriced", "costly", "hidden charges", "platform fee", "processing fee", 
        "discount not applied", "coupon", "tax", "gst", "subscription", "membership", "high rate",
        # Hinglish
        "mehenga", "bahut mehenga", "zyada mehenga", "price jyada hai", "loot macha rakhi hai",
        "discount nahi mila", "extra charges", "hidden fee", "paise loot rahe",
        # Hindi
        "महंगा", "ज्यादा चार्ज", "कीमत ज्यादा", "लूट", "डिस्काउंट नहीं", "कूपन"
    ],

    "general_feedback": [
        # English
        "experience", "service", "overall", "satisfaction", "recommend", "suggestion", "feedback",
        # Hinglish
        "theek hai", "sahi hai", "sab theek", "acha experience", "thik thak", "ok hai",
        # Hindi
        "ठीक है", "अच्छा है", "नॉर्मल", "औसत", "अनुभव", "सुझाव"
    ]
}

# =========================================================
# EMOTION & SENTIMENT KEYWORDS
# =========================================================
EMOTION_KEYWORDS = {
    "very_angry": [
        "fraud", "scam", "cheater", "hate", "worst", "pathetic", "useless", "looted", "lawsuit", "police",
        "dhokha", "chor", "bakwas", "ghatiya", "faltu", "third class", "waste of money", "fraudsters",
        "घटिया", "लूट लिया", "धोखेबाज़", "बेकार", "बर्बाद"
    ],
    "angry": [
        "bad", "poor", "problem", "upset", "rude", "bekar", "gussa", "naraaz", "disappointed", "annoying",
        "खराब", "नाराज़", "परेशान", "बुरा"
    ],
    "frustrated": [
        "waiting", "pending", "delay", "no update", "slow", "tired", "sick of", "stuck", "fed up",
        "abhi tak", "der ho rahi hai", "kab se wait", "pareshan ho gaya", "इंतज़ार", "देरी"
    ],
    "satisfied": [
        "resolved", "solved", "helpful", "smooth", "decent", "reasonable", "cooperative",
        "santusht", "solve ho gaya", "help mila", "sahi kaam", "संतुष्ट", "मदद"
    ],
    "happy": [
        "great", "excellent", "awesome", "amazing", "happy", "best", "wonderful", "impressed", "love",
        "mast", "badiya", "shandar", "zindabad", "bahut acha", "शानदार", "बहुत बढ़िया", "मजा आ गया"
    ],
    "calm": [
        "ok", "fine", "average", "normal", "okay", "acceptable", "theek", "thik", "ठीक", "नॉर्मल"
    ]
}

# =========================================================
# INTENT & PRIORITY
# =========================================================
CUSTOMER_INTENT_KEYWORDS = {
    "complaint": ["complaint", "issue", "not working", "bad service", "fraud", "scam", "problem hai", "शिकायत", "धोखा", "शिकायत है"],
    "delay": ["late", "delay", "waiting", "slow", "der hai", "late hai", "kab aayega", "देरी", "इंतज़ार"],
    "praise": ["good", "great", "awesome", "helpful", "nice", "badiya", "mast", "acha kaam", "अच्छा", "शानदार"],
    "enquiry": ["how", "what", "why", "status", "query", "details", "kaise", "kya", "kab", "janna hai", "कैसे", "बताएं"]
}

PRIORITY_KEYWORDS = {
    "critical": ["fraud", "scam", "police", "court", "threat", "stolen", "hacked", "illegal", "money stolen", "account breach", "dhokha", "धोखा", "पुलिस", "गंभीर"],
    "high": ["refund not received", "money deducted", "wrong product", "urgent", "asap", "paisa kat gaya", "broken product", "डैमेज", "जरूरी", "तुरंत"],
    "medium": ["delay", "pending", "slow", "late", "update", "missing", "deri", "देरी", "इंतज़ार"],
    "low": ["good", "nice", "ok", "fine", "satisfied", "thanks", "thank you", "अच्छा", "ठीक", "शुक्रिया"]
}

# =========================================================
# GLOBAL SENTIMENT MAPPING
# =========================================================
ASPECT_SENT_NEG_KW = [
    "bad", "poor", "worst", "broken", "failed", "error", "scam", "late", "bekar", "kharab", "ghatiya", 
    "faltu", "bakwas", "useless", "pathetic", "third class", "not good", "खराब", "बेकार", "घटिया"
]
ASPECT_SENT_POS_KW = [
    "good", "great", "excellent", "fast", "smooth", "helpful", "acha", "mast", "badiya", "superb", 
    "shandar", "shandar", "zindabad", "अच्छा", "शानदार", "बढ़िया"
]
ASPECT_SENT_NEU_KW = [
    "ok", "fine", "average", "normal", "theek", "thik", "okay", "ठीक", "औसत", "नॉर्मल"
]
