# src/rule_engine.py

# ==========================================
# A. MASTER TAXONOMY KEYWORDS
# ==========================================
TAXONOMY_KEYWORDS = {
    # PRODUCT SERVICE QUALITY
    ("product_service_quality", "product_defect"): ["product defect", "item broken", "not working", "faulty", "kharab product", "toota hua", "खराब सामान", "kaam nahi kar raha"],
    ("product_service_quality", "product_quality_poor"): ["poor quality", "bad quality", "cheap material", "bekar quality", "ghatiya product", "घटिया", "bakwas quality"],
    ("product_service_quality", "product_quality_good"): ["good quality", "nice product", "awesome material", "acha product", "mast quality", "अच्छा", "बढ़िया"],
    ("product_service_quality", "missing_items"): ["missing item", "not inside box", "empty box", "gayab", "kuch nahi mila", "गायब", "खाली डिब्बा"],
    ("product_service_quality", "wrong_item_delivered"): ["wrong item", "different product", "galat item", "kuch aur bhej diya", "wrong product", "गलत सामान"],
    ("product_service_quality", "packaging_issue"): ["torn package", "open box", "bad packaging", "fata hua", "khula box", "packing kharab", "पैकिंग खराब"],
    ("product_service_quality", "service_quality_poor"): ["bad service", "poor service", "bekar service", "ghatiya service", "kharab service", "खराब सर्विस"],
    ("product_service_quality", "service_quality_good"): ["good service", "best service", "great service", "acha service", "mast service", "अच्छी सर्विस"],

    # DELIVERY LOGISTICS (Anchored Logistics)
    ("delivery_logistics", "delayed_delivery"): ["delivery delay", "order late", "shipping delay", "late delivery", "not delivered yet", "delivery me deri", "late order", "देर से डिलीवरी"],
    ("delivery_logistics", "early_delivery"): ["early delivery", "fast delivery", "jaldi aa gaya", "time se pehle delivery", "जल्दी डिलीवरी"],
    ("delivery_logistics", "no_delivery"): ["not delivered", "never arrived", "delivery nahi hui", "parcel nahi mila", "पार्सल नहीं मिला"],
    ("delivery_logistics", "delivery_agent_behavior_rude"): ["rude delivery boy", "arrogant rider", "badtameez delivery", "gali diya delivery", "बदतमीज़ डिलीवरी बॉय"],
    ("delivery_logistics", "delivery_agent_behavior_good"): ["polite boy", "good delivery guy", "acha ladka tha", "polite behavior", "विनम्र डिलीवरी"],
    ("delivery_logistics", "tracking_issue"): ["track order", "order location", "where is my order", "track nahi ho raha", "ऑर्डर ट्रैक"],
    ("delivery_logistics", "wrong_address_delivery"): ["wrong address", "delivered somewhere else", "kisi aur ko de diya", "galat address", "गलत पते पर"],
    ("delivery_logistics", "logistics_damage"): ["damaged in transit", "crushed box", "courier damage", "raste me toot gaya", "पार्सल टूट गया"],

    # PAYMENT BILLING (Anchored Payment)
    ("payment_billing", "payment_failed"): ["payment fail", "transaction failed", "payment error", "payment nahi ho raha", "पेमेंट फेल", "भुगतान विफल"],
    ("payment_billing", "payment_deducted_not_processed"): ["money deducted", "paise kat gaye", "account debited", "payment cut but no order", "पैसे कट गए"],
    ("payment_billing", "double_charge"): ["charged twice", "double payment", "do bar paise kate", "double charge lag gaya", "दो बार चार्ज"],
    ("payment_billing", "hidden_charges"): ["hidden charge", "extra tax", "loot liya", "faltu charge", "अतिरिक्त चार्ज"],
    ("payment_billing", "refund_not_received"): ["refund not received", "refund pending", "refund nahi mila", "paise wapas nahi aaye", "रिफंड नहीं मिला"],
    ("payment_billing", "billing_error"): ["wrong bill", "invoice error", "galat bill", "zyada bill", "गलत बिल"],
    ("payment_billing", "fraud_suspicion"): ["fraud transaction", "scam payment", "paise chori", "dhokha fraud", "धोखाधड़ी"],

    # LOAN FINANCE (Anchored Finance)
    ("loan_finance", "loan_approval_delay"): ["loan approval delay", "loan pending", "approval delay", "loan approve nahi hua", "loan pass nahi hua", "loan approval", "लोन में देरी"],
    ("loan_finance", "loan_rejected"): ["loan rejected", "loan declined", "loan cancel", "loan mana kar diya", "लोन रिजेक्ट"],
    ("loan_finance", "interest_rate_issue"): ["high interest rate", "roi issue", "zyada byaj", "interest rate", "ब्याज दर"],
    ("loan_finance", "loan_disbursal_delay"): ["loan disbursal delay", "disbursement pending", "loan amount not credited", "loan ka paisa nahi aaya", "लोन का पैसा"],
    ("loan_finance", "emi_calculation_issue"): ["emi calculation wrong", "wrong emi", "emi issue", "galat emi", "गलत ईएमआई"],
    ("loan_finance", "foreclosure_issue"): ["foreclosure", "prepayment", "close loan", "loan band karna", "लोन बंद"],
    ("loan_finance", "penalty_charges"): ["penalty", "late fee", "bounce charge", "loan penalty", "जुर्माना"],
    ("loan_finance", "documentation_issue"): ["document", "file", "paperwork", "pan card", "aadhaar", "दस्तावेज़"],
    ("loan_finance", "kyc_issue"): ["kyc pending", "video kyc", "kyc fail", "kyc nahi ho raha", "केवाईसी"],

    # CUSTOMER SERVICE (Anchored Support)
    ("customer_service", "support_unresponsive"): ["customer care no response", "support not answering", "koi jawab nahi de raha", "phone nahi uthate", "कोई जवाब नहीं"],
    ("customer_service", "slow_response"): ["slow reply", "late response from support", "bahut time lagate reply", "देर से जवाब"],
    ("customer_service", "helpful_support"): ["helpful support", "good support", "solved my issue", "madad ki", "मददगार सपोर्ट"],
    ("customer_service", "rude_behavior"): ["rude staff", "abusive support", "customer care arrogant", "badtameezi se baat ki", "कस्टमर केयर बदतमीज़"],
    ("customer_service", "issue_not_resolved"): ["issue unresolved", "not helping", "problem still there", "kuch solve nahi hua support se", "समस्या हल नहीं हुई"],
    ("customer_service", "call_drop_issue"): ["call disconnected", "cut the call", "phone kaat diya", "beech me phone kaata", "फ़ोन काट दिया"],
    ("customer_service", "chatbot_issue"): ["useless bot", "bot not helping", "stupid chatbot", "bot samajh nahi raha", "बॉट"],

    # TECHNICAL APP WEBSITE (Anchored Tech)
    ("technical_app_website", "app_crash"): ["app crash", "app closes", "app band ho jata hai", "ऐप क्रैश"],
    ("technical_app_website", "login_issue"): ["cannot login", "login failed", "login nahi ho raha", "sign in problem", "लॉग इन नहीं हो रहा"],
    ("technical_app_website", "otp_issue"): ["otp not received", "otp problem", "otp nahi aa raha", "ओटीपी नहीं आ रहा"],
    ("technical_app_website", "payment_gateway_error"): ["payment gateway error", "gateway crash", "payment page stuck", "पेमेंट गेटवे"],
    ("technical_app_website", "slow_app"): ["app is slow", "app lag", "hang", "bahut slow chal raha", "app hang ho raha", "ऐप धीमा"],
    ("technical_app_website", "website_down"): ["website down", "site down", "server error", "404", "website nahi chal rahi", "वेबसाइट नहीं चल रही"],

    # RETURNS REFUND CANCELLATION (Anchored Return)
    ("returns_refund_cancellation", "return_rejected"): ["return denied", "rejected my return", "return cancel kar diya", "wapas nahi le rahe", "रिटर्न रिजेक्ट"],
    ("returns_refund_cancellation", "return_pickup_delay"): ["pickup delayed", "return pickup pending", "pickup nahi hua", "koi pickup lene nahi aaya", "पिकअप नहीं हुआ"],
    ("returns_refund_cancellation", "cancellation_issue"): ["cannot cancel order", "cancel nahi ho raha", "cancellation option gayab", "ऑर्डर रद्द नहीं हो रहा"],

    # FRAUD SECURITY
    ("fraud_security", "scam_alert"): ["scam", "fraud", "fake company", "chor", "lutera", "scammer", "घोटाला", "फ्रॉड"],
    ("fraud_security", "unauthorized_transaction"): ["hacked", "did not authorize", "apne aap paise kat gaye", "hacker", "अवैध लेन-देन"],
    ("fraud_security", "data_privacy_issue"): ["selling data", "privacy", "spam calls", "mera data leak", "डेटा लीक"],

    # NEGATIVE INTENT
    ("negative_intent", "angry_customer"): ["angry", "terrible", "worst", "hate", "gussa", "bekar", "ghatiya", "गुस्सा"],
    ("negative_intent", "very_angry_customer"): ["fucking", "bullshit", "bastard", "bhenchod", "madarchod", "gali", "sue", "consumer court", "गाली"],
    ("negative_intent", "threatening_to_leave"): ["will uninstall", "delete app", "never use again", "uninstalling", "app delete kar raha hu", "ऐप डिलीट"],

    # POSITIVE FEEDBACK
    ("positive_feedback", "fast_service"): ["quick", "very fast", "lightning fast", "bahut tez", "jaldi kaam", "तेज़ सर्विस"],
    ("positive_feedback", "excellent_product"): ["superb", "excellent", "amazing", "best", "ek number", "zabardast", "लाजवाब प्रोडक्ट"],
    
    # NEUTRAL INFORMATIONAL
    ("neutral_informational", "status_check"): ["what is status", "track", "kab aayega", "update kya hai", "स्टेटस"],
    ("neutral_informational", "information_request"): ["how to use", "need help", "guide me", "kaise karna hai", "jankari", "जानकारी"]
}

# General Fallbacks
for key in ["pricing_value", "order_management", "customer_experience", "suggestions_feedback"]:
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
