# src/rule_engine.py

# ==========================================
# A. MASTER TAXONOMY KEYWORDS (English, Hindi, Hinglish)
# Maps (Category, Subcategory) -> Extensive Keyword List
# ==========================================
TAXONOMY_KEYWORDS = {
    # ================= 1. PRODUCT & SERVICE QUALITY =================
    ("product_service_quality", "product_defect"): [
        "defect", "broken", "not working", "faulty", "damaged", "torn", "scratched", "ruined", "busted", "malfunctioning",
        "kharab", "toota", "tuta", "kaam nahi kar raha", "chalta nahi", "fata hua", "bekar nikla", "defect hai", "damage piece",
        "खराब", "टूटा", "काम नहीं कर रहा", "क्षतिग्रस्त", "दोषपूर्ण", "फटा हुआ"
    ],
    ("product_service_quality", "product_quality_poor"): [
        "poor quality", "bad quality", "cheap material", "worst quality", "low quality", "terrible product", "fake material", "garbage",
        "bekar quality", "ghatiya", "kachra", "bakwas product", "cheap quality", "sasta material", "thakela", "raddi",
        "घटिया", "बेकार गुणवत्ता", "कचरा", "बकवास", "सस्ता सामान"
    ],
    ("product_service_quality", "product_quality_good"): [
        "good quality", "nice product", "awesome material", "excellent quality", "premium", "top notch", "durable", "sturdy",
        "acha product", "mast quality", "ek number", "zabardast quality", "badiya saman", "superb material",
        "अच्छा", "बढ़िया गुणवत्ता", "मस्त", "शानदार", "एक नंबर"
    ],
    ("product_service_quality", "missing_items"): [
        "missing", "not inside", "empty box", "did not receive", "forgot to send", "incomplete", "parts missing", "where is the rest",
        "gayab", "kuch nahi mila", "missing item", "adhoora", "khali dabba", "box khali tha", "saman kam hai",
        "गायब", "खाली डिब्बा", "सामान नहीं मिला", "अधूरा", "कुछ नहीं था"
    ],
    ("product_service_quality", "wrong_item_delivered"): [
        "wrong item", "different product", "not what I ordered", "incorrect item", "wrong size", "wrong color", "sent something else",
        "galat item", "kuch aur bhej diya", "wrong product", "order alag tha", "size galat", "color galat",
        "गलत", "गलत सामान", "कुछ और भेज दिया", "आर्डर कुछ और था"
    ],
    ("product_service_quality", "packaging_issue"): [
        "torn package", "open box", "bad packaging", "poorly packed", "seal broken", "crushed box", "leaking", "spilled",
        "fata hua", "khula box", "packing kharab", "seal tuti thi", "dab gaya", "leak ho raha",
        "खुला", "फटा", "पैकिंग खराब", "सील टूटी", "रिस रहा है"
    ],
    ("product_service_quality", "service_quality_poor"): [
        "bad service", "poor service", "terrible service", "worst service", "horrible service", "unprofessional service",
        "bekar service", "ghatiya service", "kharab service", "third class service", "koi dhyan nahi deta",
        "खराब सर्विस", "बेकार सेवा", "घटिया सर्विस", "असुविधा"
    ],
    ("product_service_quality", "service_quality_good"): [
        "good service", "best service", "great service", "excellent service", "professional service", "top service",
        "acha service", "mast service", "badiya service", "dil khush kar diya",
        "अच्छी सर्विस", "बढ़िया सेवा", "बेहतरीन सेवा"
    ],

    # ================= 2. DELIVERY & LOGISTICS =================
    ("delivery_logistics", "delayed_delivery"): [
        "late", "delay", "not delivered yet", "taking too long", "still waiting", "postponed", "delayed", "slow shipping",
        "deri", "abhi tak nahi aaya", "late delivery", "bahut time lagaya", "kab aayega", "itna wait",
        "देर", "विलंब", "अभी तक नहीं आया", "बहुत समय लग गया"
    ],
    ("delivery_logistics", "early_delivery"): [
        "early", "before time", "fast delivery", "quick shipping", "arrived early", "super fast", "overnight",
        "jaldi aa gaya", "time se pehle", "fast delivery", "fatafat bhej diya",
        "जल्दी", "समय से पहले", "तेज़ डिलीवरी"
    ],
    ("delivery_logistics", "no_delivery"): [
        "not delivered", "never arrived", "did not get", "lost package", "shows delivered but not received", "fake delivery",
        "nahi mila", "delivery nahi hui", "jhuth bol rahe", "kisko de diya", "parcel nahi aaya",
        "नहीं मिला", "डिलीवरी नहीं हुई", "झूठा स्टेटस", "पार्सल गायब"
    ],
    ("delivery_logistics", "delivery_agent_behavior_rude"): [
        "rude delivery boy", "arrogant rider", "misbehaved delivery", "yelled", "unprofessional courier", "refused to come to door",
        "badtameez", "gali diya delivery", "rider rude tha", "upar aane se mana kar diya", "attitude dikha raha tha",
        "बदतमीज़", "डिलीवरी बॉय", "अभद्र व्यवहार", "गुस्सा किया"
    ],
    ("delivery_logistics", "delivery_agent_behavior_good"): [
        "polite boy", "good delivery guy", "helpful rider", "friendly courier", "nice delivery person",
        "acha ladka tha", "polite behavior", "delivery boy acha tha", "cooperative",
        "विनम्र", "अच्छा लड़का", "मददगार डिलीवरी वाला"
    ],
    ("delivery_logistics", "delivery_attempt_failed"): [
        "delivery attempt failed", "customer not available", "door locked", "could not find address",
        "attempt fail", "phone nahi laga", "ghar par nahi the", "address nahi mila",
        "डिलीवरी विफल", "पता नहीं मिला", "दरवाजा बंद था"
    ],
    ("delivery_logistics", "tracking_issue"): [
        "track", "location", "where is my order", "tracking not updating", "tracking link broken", "status wrong",
        "kaha hai order", "track nahi ho raha", "status update nahi ho raha", "kaha pahuncha",
        "ट्रैक", "कहाँ है", "स्थिति अपडेट नहीं", "लोकेशन"
    ],
    ("delivery_logistics", "wrong_address_delivery"): [
        "wrong address", "delivered somewhere else", "wrong person", "neighbor got it",
        "kisi aur ko de diya", "galat address", "dusre ghar de diya", "padosi ko de diya",
        "गलत पता", "किसी और को", "पड़ोसी"
    ],
    ("delivery_logistics", "partial_delivery"): [
        "partial delivery", "half order", "missing parts of order", "only one item came",
        "aadha saman", "ek hi piece aaya", "baki kaha hai", "partial aya",
        "आधा सामान", "एक ही मिला", "अधूरा आर्डर"
    ],
    ("delivery_logistics", "logistics_damage"): [
        "damaged in transit", "crushed box", "broken during shipping", "mishandled", "courier damage",
        "toot gaya raste me", "courier walo ne tod diya", "rasta me kharab",
        "क्षतिग्रस्त", "रास्ते में टूट गया", "कूरियर ने तोड़ा"
    ],

    # ================= 3. PAYMENT & BILLING =================
    ("payment_billing", "payment_failed"): [
        "payment fail", "transaction failed", "error in payment", "could not pay", "card declined", "upi failed", "timeout",
        "payment nahi ho raha", "fail ho gaya", "stuck ho gaya payment", "error aa raha hai",
        "भुगतान विफल", "ट्रांज़ैक्शन फेल", "पेमेंट नहीं हो रहा"
    ],
    ("payment_billing", "payment_deducted_not_processed"): [
        "money deducted", "account debited", "amount deducted but", "paid but order not placed", "balance deducted",
        "paise kat gaye", "kat gaya", "bank se kat gaya par order nahi hua", "paisa cut gaya",
        "पैसे कट गए", "खाते से कट गया", "आर्डर नहीं हुआ"
    ],
    ("payment_billing", "double_charge"): [
        "charged twice", "double payment", "paid two times", "extra charge", "billed twice",
        "do bar paise kate", "double charge lag gaya", "do dafa kat gaya",
        "दो बार पैसे", "डबल चार्ज", "दो बार कटा"
    ],
    ("payment_billing", "hidden_charges"): [
        "hidden charge", "extra tax", "unexpected fee", "handling fee", "convenience fee", "overcharged",
        "loot liya", "faltu charge", "extra paise liye", "hidden tax", "ye kaisa charge hai",
        "अतिरिक्त शुल्क", "छिपा हुआ चार्ज", "ज्यादा पैसे", "लूटा"
    ],
    ("payment_billing", "emi_issue"): [
        "emi", "installment", "monthly payment issue", "emi bounced", "auto debit failed",
        "emi nahi katti", "emi issue", "kist", "bounce charge",
        "ईएमआई", "किस्त", "ऑटो डेबिट"
    ],
    ("payment_billing", "billing_error"): [
        "wrong bill", "invoice error", "wrong amount on invoice", "billed incorrectly",
        "galat bill", "zyada bill", "invoice galat", "name wrong on bill",
        "गलत बिल", "इनवॉइस गलत", "ज्यादा बिल"
    ],
    ("payment_billing", "refund_not_received"): [
        "no refund", "refund pending", "where is my refund", "did not get my money back", "still waiting for refund",
        "refund nahi mila", "paise wapas nahi aaye", "refund process nahi hua", "kab aayega paisa",
        "रिफंड नहीं मिला", "पैसे वापस नहीं आए", "रिफंड पेंडिंग"
    ],
    ("payment_billing", "refund_delay"): [
        "refund delay", "refund taking too long", "days passed no refund", "slow refund",
        "refund me time lag raha", "late refund", "bahut din ho gaye refund nahi aaya",
        "रिफंड में देरी", "रिफंड लेट", "बहुत दिन हो गए"
    ],
    ("payment_billing", "incorrect_amount"): [
        "incorrect amount", "wrong amount charged", "short payment", "charged more",
        "galat amount", "zyada paise kat liye", "kam paise",
        "गलत राशि", "ज्यादा पैसे कट गए"
    ],
    ("payment_billing", "fraud_suspicion"): [
        "fraud transaction", "scam payment", "unauthorized charge", "someone used my card", "hacked",
        "dhokha kiya", "paise chori", "mere account se fraud", "bina otp ke paise kate",
        "धोखाधड़ी", "स्कैम", "चोरी", "अवैध लेन-देन"
    ],

    # ================= 4. LOAN & FINANCE =================
    ("loan_finance", "loan_approval_delay"): [
        "approval delay", "loan pending", "still in review", "not approved yet", "taking time to approve",
        "loan pass nahi hua", "pending dikha raha hai", "approve kab hoga", "file atki hai",
        "लोन अप्रूवल", "मंजूरी में देरी", "लंबित है"
    ],
    ("loan_finance", "loan_rejected"): [
        "loan rejected", "application declined", "loan denied", "not eligible",
        "loan cancel kar diya", "reject ho gaya", "mana kar diya", "cibil issue bata ke reject",
        "लोन रिजेक्ट", "अस्वीकार", "खारिज"
    ],
    ("loan_finance", "interest_rate_issue"): [
        "high interest", "interest rate changed", "roi issue", "charging more interest",
        "zyada byaj", "interest bada diya", "hidden interest", "roi galat",
        "ब्याज दर", "ज्यादा ब्याज", "रेट"
    ],
    ("loan_finance", "loan_disbursal_delay"): [
        "disbursal delay", "money not in bank yet", "approved but not credited",
        "paise account me nahi aaye", "disburse nahi hua", "late aayega paisa",
        "पैसे खाते में नहीं आए", "डिसबर्सल में देरी"
    ],
    ("loan_finance", "emi_calculation_issue"): [
        "emi calculation wrong", "high emi", "wrong emi amount",
        "emi zyada aa rahi", "galat emi", "calculation mistake",
        "ईएमआई गलत", "किस्त ज्यादा है", "कैलकुलेशन"
    ],
    ("loan_finance", "foreclosure_issue"): [
        "foreclosure", "prepayment penalty", "close loan", "settlement issue",
        "loan band karna hai", "foreclose charge", "preclose nahi karne de rahe",
        "लोन बंद", "फोरक्लोज़र", "प्रीपेमेंट"
    ],
    ("loan_finance", "penalty_charges"): [
        "penalty", "late fee", "bounce charge", "overdue charge",
        "penalty laga di", "faltu fine", "late fee charge", "bounce charges",
        "जुर्माना", "लेट फीस", "पेनल्टी", "फाइन"
    ],
    ("loan_finance", "kyc_issue"): [
        "kyc", "pan card", "aadhaar", "document rejected", "kyc pending",
        "kyc nahi ho raha", "document fail", "kyc update nahi hua",
        "केवाईसी", "दस्तावेज़", "पैन कार्ड", "आधार"
    ],

    # ================= 5. CUSTOMER SERVICE =================
    ("customer_service", "support_unresponsive"): [
        "no response", "not answering", "ignoring", "no reply", "they don't answer", "useless support", "deaf ears",
        "koi jawab nahi", "phone nahi uthate", "reply nahi dete", "message seen and ignored", "sunta koi nahi",
        "कोई जवाब नहीं", "फ़ोन नहीं उठाते", "रिप्लाई नहीं", "कोई सुनता नहीं"
    ],
    ("customer_service", "slow_response"): [
        "slow reply", "late response", "taking hours to reply", "delayed support", "on hold for 20 mins",
        "bahut time lagate", "late reply karte hai", "ghanto wait karaya", "slow service",
        "देर से जवाब", "बहुत समय लगाते हैं", "धीमा रिप्लाई"
    ],
    ("customer_service", "helpful_support"): [
        "helpful", "good support", "solved my issue", "thank you support", "great assistance", "fast resolution",
        "madad ki", "problem solve kar di", "achi service", "help kiya bahut",
        "मददगार", "मदद की", "समस्या हल कर दी"
    ],
    ("customer_service", "rude_behavior"): [
        "rude staff", "abusive", "arrogant", "disrespectful", "yelled at me", "bad attitude", "unprofessional agent",
        "badtameezi se baat ki", "gali", "attitude dikhaya", "tameez nahi hai", "rude agent",
        "असभ्य", "बदतमीज़", "गाली", "खराब बर्ताव", "अहंकारी"
    ],
    ("customer_service", "issue_not_resolved"): [
        "unresolved", "not helping", "problem still there", "closed ticket without fixing", "useless call",
        "kuch solve nahi hua", "koi fayda nahi", "problem wahi ki wahi", "ticket close kar diya", "time waste kiya",
        "हल नहीं हुआ", "समस्या वहीं है", "कोई फायदा नहीं", "समय बर्बाद"
    ],
    ("customer_service", "multiple_followups_needed"): [
        "calling again and again", "following up", "emailed 10 times", "repeated calls", "tired of calling",
        "bar bar call", "roz phone karna padta hai", "thak gaya bol bol ke", "koi follow up nahi",
        "बार-बार कॉल", "थक गया", "रोज़ फ़ोन"
    ],
    ("customer_service", "lack_of_knowledge"): [
        "clueless agent", "lack of knowledge", "doesn't know anything", "giving wrong info", "incompetent",
        "kuch pata nahi agent ko", "galat jankari", "bewakoof staff", "training nahi di kya",
        "जानकारी नहीं", "गलत जानकारी", "बेवकूफ एजेंट"
    ],
    ("customer_service", "escalation_needed"): [
        "escalate", "talk to manager", "senior", "give me supervisor", "complaint against agent",
        "manager se baat karni hai", "senior ko transfer karo", "escalation", "complain karni hai inki",
        "मैनेजर", "सीनियर", "शिकायत", "एस्केलेट"
    ],
    ("customer_service", "call_drop_issue"): [
        "call disconnected", "cut the call", "call dropped", "hung up on me",
        "phone kaat diya", "beech me phone kaata", "disconnect kar diya", "line kat gayi",
        "फ़ोन काट दिया", "डिस्कनेक्ट", "कॉल कट गई"
    ],
    ("customer_service", "chatbot_issue"): [
        "useless bot", "bot not helping", "stupid chatbot", "can't talk to human", "stuck in loop", "automated voice",
        "bot samajh nahi raha", "human se baat karni hai", "bot bekar hai", "machine bol rahi hai",
        "बॉट", "चैटबॉट", "इंसान से बात", "मशीन"
    ],

    # ================= 6. TECHNICAL APP & WEBSITE =================
    ("technical_app_website", "app_crash"): [
        "app crashing", "app closes automatically", "force close", "crash", "keeps stopping",
        "band ho jata hai", "crash ho raha", "app apne aap close", "chalte chalte band",
        "क्रैश", "बंद हो जाता है", "ऐप बंद"
    ],
    ("technical_app_website", "login_issue"): [
        "cannot login", "login failed", "sign in problem", "credential error", "invalid password",
        "login nahi ho raha", "id open nahi ho rahi", "password galat bata raha", "account login issue",
        "लॉग इन", "साइन इन", "पासवर्ड गलत", "आईडी नहीं खुल रही"
    ],
    ("technical_app_website", "otp_issue"): [
        "otp not received", "otp problem", "invalid otp", "otp delay", "verification failed",
        "otp nahi aa raha", "otp late aaya", "verify nahi ho raha", "message nahi aaya",
        "ओटीपी", "मैसेज नहीं आया", "वेरिफिकेशन"
    ],
    ("technical_app_website", "payment_gateway_error"): [
        "gateway error", "payment page blank", "redirect failed", "white screen on payment",
        "payment page crash", "gateway stuck", "loading par atak gaya",
        "पेमेंट गेटवे", "सफेद स्क्रीन", "अटक गया"
    ],
    ("technical_app_website", "ui_bug"): [
        "button not working", "ui bug", "layout broken", "can't click", "screen overlapping",
        "click nahi ho raha", "button dab nahi raha", "screen kharab dikh rahi",
        "बटन काम नहीं कर रहा", "क्लिक नहीं हो रहा", "यूआई"
    ],
    ("technical_app_website", "slow_app"): [
        "app is slow", "lagging", "hangs", "takes forever to load", "loading screen", "buffering",
        "bahut slow chal raha", "hang ho raha", "atkat atak ke chal raha", "load hone me time",
        "धीमा", "हैंग", "अटक रहा है", "लोडिंग"
    ],
    ("technical_app_website", "website_down"): [
        "site down", "server error", "404", "500 internal server error", "maintenance", "not reachable",
        "website nahi chal rahi", "server down hai", "site nahi khul rahi", "link not working",
        "सर्वर डाउन", "वेबसाइट नहीं चल रही", "लिंक खराब"
    ],
    ("technical_app_website", "feature_not_working"): [
        "search not working", "filter broken", "feature broken", "cart issue", "can't add to cart",
        "add nahi ho raha", "search kaam nahi kar raha", "feature bekar hai",
        "फीचर", "कार्ट", "सर्च काम नहीं कर रहा"
    ],
    ("technical_app_website", "update_issue"): [
        "after update", "new update is bad", "worst update", "please revert update", "force update",
        "update ke baad kharab", "naya update bekar", "update issue", "purana version acha tha",
        "अपडेट", "नया वर्ज़न", "अपडेट के बाद"
    ],

    # ================= 7. PRICING & VALUE =================
    ("pricing_value", "too_expensive"): [
        "too expensive", "overpriced", "costly", "not worth it", "charging too much", "loot", "robbery",
        "bahut mehenga", "loot macha rakhi hai", "paisa barbad itna mehenga", "itna rate",
        "महँगा", "लूट", "कीमत ज्यादा है", "ओवरप्राइज्ड"
    ],
    ("pricing_value", "value_for_money_good"): [
        "value for money", "worth it", "cheap and best", "good price", "affordable", "reasonable",
        "paisa vasool", "sasta aur acha", "sahi rate", "budget me hai",
        "पैसा वसूल", "सस्ता और अच्छा", "सही दाम", "वाजिब"
    ],
    ("pricing_value", "value_for_money_poor"): [
        "not worth the price", "waste of money", "poor value", "rip off",
        "paisa barbad", "kisi kaam ka nahi itne me", "bekar price",
        "पैसा बर्बाद", "कीमत के लायक नहीं", "फालतू"
    ],
    ("pricing_value", "hidden_costs"): [
        "hidden costs", "extra charges", "sudden fee", "unexpected price increase", "tax too high",
        "hidden charge", "extra tax lagaya", "pehle kam bataya baad me zyada", "faltu charge",
        "छिपा हुआ चार्ज", "अतिरिक्त शुल्क", "ज्यादा टैक्स"
    ],
    ("pricing_value", "discount_issue"): [
        "discount not applied", "fake discount", "promo code not working", "coupon invalid",
        "discount nahi mila", "coupon code fail", "fake sale", "offer apply nahi hua",
        "छूट", "डिस्काउंट नहीं मिला", "कूपन", "सेल धोखा"
    ],

    # ================= 8. RETURNS & CANCELLATION =================
    ("returns_refund_cancellation", "return_rejected"): [
        "return denied", "rejected my return", "refused to take back", "return policy fake",
        "return cancel kar diya", "wapas nahi le rahe", "reject kar diya", "policy ka bahana",
        "वापस नहीं ले रहे", "रिटर्न रिजेक्ट", "रद्द कर दिया"
    ],
    ("returns_refund_cancellation", "return_pickup_delay"): [
        "pickup delayed", "no one came for pickup", "pickup pending", "return guy didn't come",
        "pickup nahi hua", "koi lene nahi aaya", "pickup boy call nahi kiya", "kab aayega pickup",
        "पिकअप नहीं हुआ", "लेने कोई नहीं आया", "पिकअप लेट"
    ],
    ("returns_refund_cancellation", "cancellation_issue"): [
        "cannot cancel", "no cancellation option", "cancel button missing", "charged for cancellation",
        "cancel nahi ho raha", "cancellation option gayab", "cancel karne par paise kate", "order cancel karna hai",
        "रद्द नहीं हो रहा", "कैंसिल", "रद्दीकरण"
    ],
    ("returns_refund_cancellation", "exchange_issue"): [
        "exchange denied", "exchange product defective", "want to exchange", "replace it",
        "replace nahi kar rahe", "exchange karna hai", "badal ke do", "replacement bekar",
        "एक्सचेंज", "बदलना है", "रिप्लेसमेंट"
    ],

    # ================= 9. ORDER MANAGEMENT =================
    ("order_management", "order_not_placed"): [
        "order not placed", "failed to order", "cart empty after payment",
        "order nahi hua", "place order fail", "order dikh nahi raha",
        "ऑर्डर नहीं हुआ", "ऑर्डर फेल"
    ],
    ("order_management", "order_cancelled_by_company"): [
        "auto cancelled", "you cancelled my order", "cancelled without permission", "seller cancelled",
        "apne aap cancel", "mera order kyu cancel kiya", "bina bataye cancel",
        "अपने आप रद्द", "सेलर ने कैंसिल किया"
    ],
    ("order_management", "order_duplicate"): [
        "duplicate order", "ordered twice by mistake", "two orders placed",
        "do bar order ho gaya", "galti se double ho gaya",
        "दो बार ऑर्डर", "डुप्लीकेट"
    ],

    # ================= 10. CUSTOMER EXPERIENCE =================
    ("customer_experience", "trust_issue"): [
        "lost trust", "cannot trust", "cheaters", "unreliable", "never again", "fraud company",
        "bharosa uth gaya", "dhokhebaaz", "scam chal raha hai", "in par trust mat karna",
        "भरोसा नहीं", "धोखेबाज़", "भरोसा टूट गया"
    ],
    ("customer_experience", "switching_intent"): [
        "moving to competitor", "uninstalling", "will use another app", "deleting your app", "goodbye",
        "app delete kar raha hu", "amazon use karunga", "flipkart better hai", "uninstalling", "bye bye",
        "डिलीट कर रहा हूँ", "दूसरी ऐप इस्तेमाल करूंगा", "अनइंस्टॉल"
    ],

    # ================= 11. FRAUD & SECURITY =================
    ("fraud_security", "scam_alert"): [
        "scam", "fraud", "thief", "fake company", "cheating", "robbing", "scammer", "loot",
        "chor", "lutera", "maha chor", "fraudsters", "dhokha kiya",
        "घोटाला", "चोर", "धोखा", "फ़र्ज़ी"
    ],
    ("fraud_security", "unauthorized_transaction"): [
        "hacked", "did not authorize", "money stolen from account", "without otp", "fraud transaction",
        "apne aap paise kat gaye", "hacker", "bina otp ke", "chori ho gaye paise",
        "हैक", "अवैध लेन-देन", "बिना ओटीपी", "चोरी"
    ],
    ("fraud_security", "data_privacy_issue"): [
        "selling data", "privacy", "spam calls", "number leaked", "security issue",
        "mera data leak", "spam sms aa rahe", "number bech diya",
        "डेटा लीक", "प्राइवेसी", "स्पैम कॉल"
    ],

    # ================= 12. NEGATIVE INTENT (Severe) =================
    ("negative_intent", "very_angry_customer"): [
        "fucking", "bullshit", "bastard", "idiots", "assholes", "son of a bitch", "wtf",
        "bhenchod", "madarchod", "chutiya", "harami", "kutta", "maa ki", "bhadwe", "saale",
        "कुत्ते", "हरामी", "चूतिया", "साले", "गाली"
    ],
    ("negative_intent", "legal_threat"): [
        "sue you", "legal action", "lawyer", "consumer court", "police complaint", "fir",
        "case karunga", "police bulata hu", "consumer forum", "court me dekhunga",
        "पुलिस", "कोर्ट", "मुकदमा", "एफआईआर"
    ],
    ("negative_intent", "social_media_threat"): [
        "post on twitter", "viral", "expose you", "youtube", "social media", "instagram",
        "twitter pe dalunga", "viral kar dunga video", "sabko bataunga", "expose karunga",
        "वायरल", "ट्विटर", "एक्सपोज़"
    ]
}

# Add default fallbacks for broad categories
for key in ["pricing_value", "order_management", "customer_experience", "suggestions_feedback", "loan_finance", "neutral_informational"]:
    TAXONOMY_KEYWORDS[(key, "general_issue")] = [key.replace("_", " ")]

# ==========================================
# B. CORE EMOTION & INTENT
# ==========================================
EMOTION_KEYWORDS = {
    "Very Angry": ["scam", "fraud", "consumer court", "chor", "fucking", "hell", "sue", "lutera", "police", "legal", "bhenchod", "chutiya", "madarchod"],
    "Angry": ["terrible", "worst", "pathetic", "ghatiya", "bekar", "kachra", "bakwas", "angry", "hate", "useless", "garbage", "rubbish"],
    "Frustrated": ["waiting", "tired", "annoyed", "pareshan", "dimag kharab", "again", "frustrated", "headache", "stuck", "fed up", "pakk gaya"],
    "Happy": ["nice", "good", "acha", "badiya", "khush", "happy", "smile", "glad"],
    "Satisfied": ["resolved", "solved", "fine", "okay", "theek", "kaam ho gaya", "satisfied", "decent", "acceptable"],
    "Calm": []
}

CUSTOMER_INTENT_KEYWORDS = {
    "Complaint": ["issue", "problem", "not working", "dikkat", "shikayat", "kharab", "fail", "broken", "complaint", "complain", "fix"],
    "Delay": ["late", "delay", "waiting", "deri", "abhi tak", "pending", "time taking"],
    "Praise": ["great", "best", "superb", "thank you", "shukriya", "praise", "excellent", "kudos", "appreciate", "amazing"],
    "Enquiry": ["how", "status", "kab", "kaha", "guide", "query", "question", "help me", "information", "kaise"],
    "Negative Tone": ["bad", "poor", "sad", "disappointing", "worse"],
    "Positive Tone": ["awesome", "love", "mast", "beautiful", "perfect", "pyara"],
    "Neutral Tone": []
}

# ==========================================
# C. HYBRID SENTIMENT OVERRIDES & FLAGS
# ==========================================
ASPECT_SENT_NEG_KW = [
    "not", "bad", "fail", "worst", "kharab", "bekar", "nahi", "mat", "nhi", "poor", "hate", "terrible", "issue", "problem", "dont", "cant",
    "नहीं", "मत", "खराब", "बुरा", "बेकार"
]
ASPECT_SENT_POS_KW = [
    "good", "great", "excellent", "fast", "best", "mast", "acha", "smooth", "awesome", "perfect", "love", "badiya", "zabardast",
    "अच्छा", "बढ़िया", "शानदार", "मस्त"
]
MIXED_FEEDBACK_KW = [
    "but", "however", "although", "lekin", "par", "magar", "phir bhi", "though", "still", "yet", "on the other hand",
    "लेकिन", "पर", "मगर", "फिर भी"
]
URGENT_KW = [
    "urgent", "asap", "immediately", "jaldi", "turant", "abhi", "emergency", "fast", "priority", "right now", "hurry",
    "तत्काल", "जल्दी", "तुरंत", "अभी"
]
STRONG_NEG_PHRASES = [
    "worst", "pathetic", "fraud", "scam", "waste of money", "paisa barbad", "never buy", "useless", "garbage", "rip off",
    "sabse kharab", "ghatiya", "kabhi mat lena", "loot liya",
    "सबसे खराब", "पैसा बर्बाद", "घटिया", "लूट", "धोखा"
]
