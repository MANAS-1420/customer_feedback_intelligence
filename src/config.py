# src/config.py

CATEGORY_SUBCATEGORY_MAP = {
    "product_service_quality": ["product_defect", "product_quality_good", "product_quality_poor", "missing_items", "wrong_item_delivered", "packaging_issue", "service_quality_good", "service_quality_poor"],
    "delivery_logistics": ["delayed_delivery", "early_delivery", "no_delivery", "delivery_agent_behavior_good", "delivery_agent_behavior_rude", "delivery_attempt_failed", "tracking_issue", "wrong_address_delivery", "partial_delivery", "logistics_damage"],
    "payment_billing": ["payment_failed", "payment_deducted_not_processed", "double_charge", "hidden_charges", "emi_issue", "billing_error", "refund_not_received", "refund_delay", "incorrect_amount", "fraud_suspicion"],
    "loan_finance": ["loan_approval_delay", "loan_rejected", "interest_rate_issue", "loan_disbursal_delay", "loan_disbursal_issue", "emi_calculation_issue", "foreclosure_issue", "penalty_charges", "documentation_issue", "kyc_issue"],
    "customer_service": ["support_unresponsive", "slow_response", "helpful_support", "rude_behavior", "issue_not_resolved", "multiple_followups_needed", "lack_of_knowledge", "escalation_needed", "call_drop_issue", "chatbot_issue"],
    "technical_app_website": ["app_crash", "login_issue", "otp_issue", "payment_gateway_error", "ui_bug", "slow_app", "website_down", "feature_not_working", "update_issue", "compatibility_issue"],
    "pricing_value": ["too_expensive", "value_for_money_good", "value_for_money_poor", "hidden_costs", "discount_issue", "offer_not_applied", "misleading_pricing"],
    "returns_refund_cancellation": ["return_rejected", "return_pickup_delay", "refund_not_processed", "refund_partial", "cancellation_issue", "no_refund_policy_issue", "exchange_issue"],
    "order_management": ["order_not_placed", "order_cancelled_by_company", "order_duplicate", "order_modification_issue", "order_status_wrong", "invoice_issue"],
    "customer_experience": ["overall_satisfaction", "overall_dissatisfaction", "mixed_experience", "first_time_experience", "repeated_issue", "trust_issue", "brand_loyalty", "switching_intent"],
    "fraud_security": ["scam_alert", "unauthorized_transaction", "data_privacy_issue", "account_hacked", "fake_commitment", "phishing_issue"],
    "suggestions_feedback": ["feature_request", "improvement_suggestion", "complaint_general", "appreciation", "recommendation", "policy_feedback"],
    "positive_feedback": ["fast_service", "polite_staff", "excellent_product", "smooth_process", "satisfied_customer", "great_experience"],
    "negative_intent": ["angry_customer", "very_angry_customer", "frustrated_customer", "threatening_to_leave", "legal_threat", "social_media_threat"],
    "neutral_informational": ["enquiry", "status_check", "information_request", "clarification_needed", "no_clear_sentiment"]
}

EMOTION_LABELS = ["Very Angry", "Angry", "Frustrated", "Calm", "Happy", "Satisfied"]
CUSTOMER_INTENT_LABELS = ["Complaint", "Delay", "Enquiry", "Negative Tone", "Neutral Tone", "Positive Tone", "Praise"]
PRIORITY_LABELS = ["Low", "Medium", "High", "Critical"]
