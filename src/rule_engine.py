# src/rule_engine.py
TAXONOMY_KEYWORDS = {
    ("product_service_quality", "product_defect"): ["defect", "broken", "not working", "faulty", "kharab", "toota", "damage", "kaam nahi kar", "chalta nahi", "fata hua", "defective"],
    ("product_service_quality", "product_quality_poor"): ["poor quality", "bad quality", "cheap", "bekar", "bekaar", "ghatiya", "gatiya", "bakwas", "kachra", "raddi", "third class", "waste", "sasta material", "fake product", "duplicate"],
    ("product_service_quality", "product_quality_good"): ["good quality", "nice", "awesome", "acha", "mast", "superb", "ek number", "badiya", "original product", "genuine"],
    ("product_service_quality", "missing_items"): ["missing", "not inside", "empty box", "gayab", "kuch nahi mila", "khali dabba", "aaha saman", "item missing"],
    ("product_service_quality", "wrong_item_delivered"): ["wrong item", "different", "galat item", "kuch aur bhej diya", "wrong product", "galat color", "wrong size", "dusra de diya"],
    ("product_service_quality", "packaging_issue"): ["torn package", "open box", "bad packaging", "fata hua", "khula box", "packing kharab", "seal tooti", "crushed", "leak ho raha"],
    ("product_service_quality", "service_quality_poor"): ["bad service", "poor service", "bekar service", "ghatiya service", "kharab service", "wahiyaat service", "third class service"],

    ("delivery_logistics", "delayed_delivery"): ["delay", "late", "not delivered", "deri", "abhi tak nahi aaya", "late delivery", "bahut time lagaya", "kab aayega", "still waiting"],
    ("delivery_logistics", "early_delivery"): ["early", "fast delivery", "jaldi", "time se pehle", "fatafat"],
    ("delivery_logistics", "no_delivery"): ["not delivered", "never arrived", "delivery nahi hui", "parcel nahi mila", "nahi aaya"],
    ("delivery_logistics", "fake_delivery_update"): ["fake update", "fake delivery", "jhutha status", "bina call kiye cancel", "delivered dikha raha par mila nahi", "jhooth bol raha"],
    ("delivery_logistics", "delivery_agent_behavior_rude"): ["rude delivery boy", "arrogant rider", "badtameez", "gali diya", "rider rude", "delivery wala bekar", "attitude dikha raha", "upar aane se mana"],
    ("delivery_logistics", "delivery_agent_behavior_good"): ["polite", "good delivery guy", "acha ladka", "behavior good", "cooperative rider"],
    ("delivery_logistics", "tracking_issue"): ["track", "location", "where is my order", "kaha hai order", "status update nahi", "stuck at hub"],
    ("delivery_logistics", "wrong_address_delivery"): ["wrong address", "somewhere else", "kisi aur ko", "galat address", "padosi ko de diya", "security guard ko de diya"],

    ("payment_billing", "payment_failed"): ["fail", "error", "payment nahi ho raha", "transaction failed", "upi fail", "server down payment", "stuck", "atak gaya"],
    ("payment_billing", "double_charge"): ["double charge", "do baar", "twice", "double deduct", "double payment", "do bar kat gaye", "2 times"],
    ("payment_billing", "payment_deducted_not_processed"): ["deduct", "kat gaye", "debited", "cut", "account se kat", "paise cut gaye par order nahi", "bank se cut gaya"],
    ("payment_billing", "hidden_charges"): ["hidden", "extra tax", "loot", "faltu charge", "convenience fee", "zyada paise liye"],
    ("payment_billing", "refund_not_received"): ["refund nahi aaya", "wapas nahi aaye", "refund pending", "paise wapas", "refund delay", "kab aayega refund"],
    ("payment_billing", "fraud_suspicion"): ["fraud", "scam", "chori", "dhokha", "bina otp", "hacked", "mere account se paise nikal", "dhokhebaaz"],

    ("loan_finance", "loan_approval_delay"): ["loan approval", "loan pending", "approval delay", "approve nahi hua", "loan pass", "file atki", "process slow"],
    ("loan_finance", "loan_rejected"): ["rejected", "declined", "cancel", "mana kar diya", "cibil issue", "reject kar diya"],
    ("loan_finance", "interest_rate_issue"): ["interest", "roi", "byaj", "rate zyada", "high interest"],
    ("loan_finance", "loan_disbursal_delay"): ["disbursal", "disbursement", "credited", "loan ka paisa nahi aaya", "account me nahi aaya"],
    ("loan_finance", "emi_calculation_issue"): ["emi", "installment", "kist", "bounce charge", "emi zyada", "wrong emi"],
    ("loan_finance", "recovery_agent_issue"): ["recovery agent", "pareshan kar rahe", "harassment", "gali galoch", "dhamki de rahe", "call karke pareshan"],
    ("loan_finance", "kyc_issue"): ["kyc", "video kyc", "pan card", "aadhaar", "document reject", "kyc pending"],

    ("customer_service", "support_unresponsive"): ["no response", "not answering", "koi jawab nahi", "phone nahi uthate", "ignoring", "reply nahi karte", "hold pe rakha"],
    ("customer_service", "slow_response"): ["slow reply", "late response", "time lagate", "bahut wait karaya"],
    ("customer_service", "helpful_support"): ["helpful", "good support", "solved", "madad ki", "problem solve"],
    ("customer_service", "rude_behavior"): ["rude staff", "abusive", "badtameezi", "customer care rude", "tameez nahi"],
    ("customer_service", "issue_not_resolved"): ["unresolved", "not helping", "problem still", "kuch solve nahi", "koi fayda nahi", "ticket close kar diya"],
    ("customer_service", "call_drop_issue"): ["disconnected", "cut", "phone kaat diya", "beech me kaat diya"],
    ("customer_service", "chatbot_issue"): ["bot", "machine", "chat bot bekar", "human se baat", "loop me fasa diya", "useless bot"],

    ("technical_app_website", "app_crash"): ["crash", "closes", "band ho jata", "app crash", "force close", "apne aap band"],
    ("technical_app_website", "login_issue"): ["login", "sign in", "login nahi ho raha", "password galat", "id block"],
    ("technical_app_website", "otp_issue"): ["otp", "otp nahi aa raha", "otp delay", "verification code", "sms nahi aaya"],
    ("technical_app_website", "slow_app"): ["app is slow", "lag", "hang", "loading", "chakka ghum raha", "atak atak ke"],
    ("technical_app_website", "website_down"): ["website down", "site down", "server error", "404", "chal nahi rahi"],

    ("returns_refund_cancellation", "return_rejected"): ["return denied", "wapas nahi le rahe", "return reject", "policy ka bahana"],
    ("returns_refund_cancellation", "return_pickup_delay"): ["pickup delay", "koi lene nahi aaya", "pickup boy call nahi kiya", "pickup pending"],
    ("returns_refund_cancellation", "cancellation_issue"): ["cannot cancel", "cancel nahi ho raha", "cancel option gayab", "order cancel karna hai"],

    ("negative_intent", "angry_customer"): ["angry", "terrible", "worst", "hate", "gussa", "bekar", "ghatiya", "dimag kharab"],
    ("negative_intent", "very_angry_customer"): ["fucking", "bullshit", "bhenchod", "madarchod", "gali", "chutiya", "harami", "kutta", "saale", "bhadwe"],
    ("negative_intent", "legal_threat"): ["sue", "court", "consumer forum", "consumer court", "police complaint", "fir karunga", "case kar dunga", "lawyer"],
    ("negative_intent", "social_media_threat"): ["twitter pe dalunga", "viral kar dunga", "social media", "expose karunga", "youtube pe dalunga"],
    ("negative_intent", "threatening_to_leave"): ["uninstall", "delete app", "never use", "app delete", "amazon use karunga", "flipkart better hai", "bye bye"]
}

for key in ["pricing_value", "order_management", "customer_experience", "suggestions_feedback"]:
    TAXONOMY_KEYWORDS[(key, "general_issue")] = [key.replace("_", " ")]

EMOTION_KEYWORDS = {
    "Very Angry": ["scam", "fraud", "court", "chor", "fucking", "hell", "sue", "lutera", "police", "fir", "chutiya", "bhenchod"],
    "Angry": ["terrible", "worst", "pathetic", "ghatiya", "bekar", "kachra", "bakwas", "angry", "rubbish", "raddi"],
    "Frustrated": ["waiting", "tired", "annoyed", "pareshan", "dimag", "again", "frustrated", "irritating", "kat", "deduct", "thak gaya", "roz roz"],
    "Happy": ["nice", "good", "acha", "badiya", "khush", "happy", "smile", "mast"],
    "Satisfied": ["resolved", "solved", "fine", "okay", "theek", "kaam ho gaya", "satisfied", "done"],
    "Calm": []
}

CUSTOMER_INTENT_KEYWORDS = {
    "Complaint": ["issue", "problem", "not working", "dikkat", "shikayat", "kharab", "fail", "complaint", "fix", "ghatiya", "bekar", "deduct", "charge", "toota"],
    "Delay": ["late", "delay", "waiting", "deri", "pending", "abhi tak", "time lag raha"],
    "Praise": ["great", "best", "superb", "thank you", "shukriya", "praise", "kudos", "dhanyawad", "awesome"],
    "Enquiry": ["how", "status", "kab", "kaha", "guide", "query", "help", "kaise", "batao", "update"],
    "Negative Tone": ["bad", "poor", "sad", "disappointed", "nirash"],
    "Positive Tone": ["love", "mast", "perfect", "pyara", "zabardast"],
    "Neutral Tone": []
}

ASPECT_SENT_NEG_KW = [
    "not", "bad", "fail", "worst", "kharab", "bekar", "bekaar", "nahi", "nhi", "mat", "poor", "hate", "terrible", "issue", "problem", "dont", "cant",
    "ghatiya", "gatiya", "kachra", "bakwas", "pathetic", "fraud", "scam", "useless", "garbage", "rubbish", "slow", "late", "delay", "rude",
    "deduct", "charge", "kat", "chutiya", "chor", "lutera", "fake", "jhutha"
]
ASPECT_SENT_POS_KW = [
    "good", "great", "excellent", "fast", "best", "mast", "acha", "smooth", "awesome", "perfect", "love", "badiya", "zabardast",
    "superb", "amazing", "fantastic", "polite", "helpful", "ek number", "fatafat"
]
MIXED_FEEDBACK_KW = ["but", "however", "although", "lekin", "par", "magar", "phir bhi", "though", "yet", "warna", "jabki"]
URGENT_KW = ["urgent", "asap", "immediately", "jaldi", "turant", "abhi", "fast", "priority", "fatafat"]
STRONG_NEG_PHRASES = ["worst", "pathetic", "fraud", "scam", "waste", "barbad", "never", "useless", "ghatiya", "bakwas", "consumer court", "police"]

NEGATED_NEGATIVE_PHRASES = [
    "no complaint", "koi complaint nahi", "no issue", "koi issue nahi",
    "no problem", "koi problem nahi", "koi dikkat nahi", "dikkat nahi",
    "no delay", "bina delay", "without delay", "not bad", "kabhi fail nahi",
    "nahi phata", "not broken", "not damaged", "shikayat nahi", "koi shikayat nahi",
    "zero complaint", "sab theek hai", "sab sahi hai", "all good"
]
