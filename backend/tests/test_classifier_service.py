from app.models.enums import CandidateSignal, DecisionValue
from app.services.classifier import classify_demo_candidate


def test_classifier_flags_promotional_rows_with_concrete_metadata_evidence() -> None:
    classification = classify_demo_candidate(
        sender_name="Verizon Wireless",
        sender_email="no-reply@customer.verizon.com",
        subject="Exclusive: Get $200 off Samsung Galaxy Tab.",
        mailbox_category="Promotions",
    )

    assert classification.signal == CandidateSignal.promotional_digest
    assert classification.suggested_decision == DecisionValue.mark_low_value
    assert classification.reason == (
        "Observed promotional cues in stored metadata: 'exclusive' and 'off'. "
        "Suggest marking this source as low value, while keeping the final decision human-reviewed."
    )


def test_classifier_reserves_unsubscribe_for_clear_recurring_list_patterns() -> None:
    classification = classify_demo_candidate(
        sender_name="Workspace Vendor Update",
        sender_email="newsletter@workspacevendor.example",
        subject="April feature digest and customer webinar recap",
        mailbox_category="Updates",
    )

    assert classification.signal == CandidateSignal.recurring_updates
    assert classification.suggested_decision == DecisionValue.unsubscribe_later
    assert classification.reason == (
        "Observed recurring list cues in stored metadata: 'newsletter', 'digest', and 'recap'. "
        "Queue for Unsubscribe may be worth human review."
    )


def test_classifier_keeps_weak_or_mixed_metadata_ambiguous() -> None:
    classification = classify_demo_candidate(
        sender_name="Tooling Community Notes",
        sender_email="notes@tooling-community.example",
        subject="Community office hours and release notes",
        mailbox_category="Updates",
    )

    assert classification.signal == CandidateSignal.ambiguous_source
    assert classification.suggested_decision == DecisionValue.keep_for_now
    assert classification.reason == (
        "Observed evidence is limited or mixed in stored metadata: 'release notes' and 'community notes'. "
        "Keep Source for now until a human reviews the source."
    )


def test_classifier_keeps_transactional_or_security_rows_reviewable() -> None:
    security = classify_demo_candidate(
        sender_name="Bank Security",
        sender_email="alerts@bank.example",
        subject="Security alert: verify your login attempt",
        mailbox_category="Promotions",
    )
    billing = classify_demo_candidate(
        sender_name="Cloud Billing Notices",
        sender_email="alerts@cloudbilling.example",
        subject="Usage threshold reminder and invoice preview",
        mailbox_category="Updates",
    )

    assert security.signal == CandidateSignal.ambiguous_source
    assert security.suggested_decision == DecisionValue.keep_for_now
    assert security.reason == (
        "Observed cautionary metadata that can indicate transactional or account-related email: "
        "'security alert', 'verify', and 'login'. Keep Source for now and review it locally before taking any stronger action."
    )

    assert billing.signal == CandidateSignal.ambiguous_source
    assert billing.suggested_decision == DecisionValue.keep_for_now
    assert billing.reason == (
        "Observed cautionary metadata that can indicate transactional or account-related email: "
        "'invoice', 'billing', and 'usage threshold'. Keep Source for now and review it locally before taking any stronger action."
    )
