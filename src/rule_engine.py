Skip to content
MANAS-1420
customer_feedback_intelligence
Repository navigation
Code
Issues
Pull requests
Actions
Projects
Wiki
Security and quality
1
 (1)
Insights
Settings
Files
Go to file
t
src
__init__.py
bert_model.py
config.py
pipeline.py
rule_engine.py
utils.py
.gitignore
README.md
app.py
requirements.txt
customer_feedback_intelligence/src
/
rule_engine.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

4
Line wrap mode

No wrap
Editing rule_engine.py file contents
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
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
Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
 
