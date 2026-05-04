from dataclasses import dataclass
import re

from app.models.enums import CandidateSignal, DecisionValue

_PROMOTIONAL_TERMS = (
    "deal",
    "sale",
    "discount",
    "offer",
    "promo",
    "coupon",
    "member only",
    "flash sale",
    "limited time",
    "free shipping",
    "gift card",
    "recommended for you",
    "exclusive",
    "stock up",
)

_RECURRING_STRONG_TERMS = (
    "newsletter",
    "digest",
    "roundup",
    "recap",
)

_RECURRING_WEAK_TERMS = (
    "bulletin",
    "weekly",
    "monthly",
    "release notes",
    "community notes",
    "edition",
)

_TRANSACTIONAL_SAFETY_TERMS = (
    "invoice",
    "receipt",
    "statement",
    "payment",
    "billing",
    "security alert",
    "verification",
    "verify",
    "password",
    "login",
    "sign in",
    "account alert",
    "order confirmation",
    "shipment",
    "shipped",
    "delivery",
    "tracking",
    "usage threshold",
)

_NUMERIC_DISCOUNT_PATTERN = re.compile(r"\b\d+%?\s+off\b")
_PRICE_PATTERN = re.compile(r"\$\d")


@dataclass(frozen=True)
class CandidateClassification:
    signal: CandidateSignal
    suggested_decision: DecisionValue
    reason: str
    confidence: float


def classify_demo_candidate(
    sender_name: str, sender_email: str, subject: str, mailbox_category: str
) -> CandidateClassification:
    sender_local_part = sender_email.partition("@")[0]
    identity_text = _normalize_text(sender_name, sender_local_part)
    subject_text = _normalize_text(subject)
    searchable_text = _normalize_text(
        sender_name, sender_local_part, subject, mailbox_category
    )
    category_promotions = _normalize_text(mailbox_category) == "promotions"

    safety_matches = _collect_matches(
        _normalize_text(sender_name, subject), _TRANSACTIONAL_SAFETY_TERMS
    )
    promo_matches = _collect_matches(searchable_text, _PROMOTIONAL_TERMS)
    if _NUMERIC_DISCOUNT_PATTERN.search(searchable_text):
        promo_matches.append("off")
    if _PRICE_PATTERN.search(searchable_text) and "off" not in promo_matches:
        promo_matches.append("price")
    promo_matches = _unique_preserve_order(promo_matches)

    identity_strong = _collect_matches(identity_text, _RECURRING_STRONG_TERMS)
    subject_strong = _collect_matches(subject_text, _RECURRING_STRONG_TERMS)
    identity_weak = _collect_matches(identity_text, _RECURRING_WEAK_TERMS)
    subject_weak = _collect_matches(subject_text, _RECURRING_WEAK_TERMS)

    recurring_matches = _unique_preserve_order(
        [*identity_strong, *subject_strong, *identity_weak, *subject_weak]
    )
    clear_recurring = (
        (bool(identity_strong) and bool(subject_strong or subject_weak))
        or len(identity_strong) >= 2
        or (bool(subject_strong) and bool(identity_weak))
    )
    promo_score = len(promo_matches) + (
        1 if category_promotions and promo_matches else 0
    )

    if safety_matches:
        return CandidateClassification(
            signal=CandidateSignal.ambiguous_source,
            suggested_decision=DecisionValue.keep_for_now,
            reason=(
                "Observed cautionary metadata that can indicate transactional or "
                f"account-related email: {_format_evidence(safety_matches[:3])}. "
                "Keep Source for now and review it locally before taking any stronger action."
            ),
            confidence=0.46,
        )

    if clear_recurring and promo_score <= 2:
        return CandidateClassification(
            signal=CandidateSignal.recurring_updates,
            suggested_decision=DecisionValue.unsubscribe_later,
            reason=(
                "Observed recurring list cues in stored metadata: "
                f"{_format_evidence(recurring_matches[:3])}. "
                "Queue for Unsubscribe may be worth human review."
            ),
            confidence=0.72,
        )

    if promo_score >= 2:
        promo_evidence = promo_matches[:3]
        if category_promotions and len(promo_evidence) < 2:
            promo_evidence.append("Promotions mailbox context")
        return CandidateClassification(
            signal=CandidateSignal.promotional_digest,
            suggested_decision=DecisionValue.mark_low_value,
            reason=(
                "Observed promotional cues in stored metadata: "
                f"{_format_evidence(promo_evidence)}. "
                "Suggest marking this source as low value, while keeping the final decision human-reviewed."
            ),
            confidence=0.84,
        )

    weak_evidence = _unique_preserve_order([*subject_weak, *identity_weak])[:3]
    if category_promotions and len(weak_evidence) < 2:
        weak_evidence.append("Promotions mailbox context")

    return CandidateClassification(
        signal=CandidateSignal.ambiguous_source,
        suggested_decision=DecisionValue.keep_for_now,
        reason=(
            "Observed evidence is limited or mixed in stored metadata: "
            f"{_format_evidence(weak_evidence)}. "
            "Keep Source for now until a human reviews the source."
            if weak_evidence
            else "Stored metadata is too limited or mixed to support a stronger suggestion. "
            "Keep Source for now until a human reviews the source."
        ),
        confidence=0.45,
    )


def _normalize_text(*parts: str) -> str:
    normalized_parts = [
        re.sub(r"[^a-z0-9%$]+", " ", part.lower()).strip()
        for part in parts
        if part and part.strip()
    ]
    return " ".join(part for part in normalized_parts if part)


def _collect_matches(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if _contains_term(text, term)]


def _contains_term(text: str, term: str) -> bool:
    if " " in term:
        return term in text
    return re.search(rf"\b{re.escape(term)}\b", text) is not None


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _format_evidence(values: list[str]) -> str:
    quoted = [f"'{value}'" for value in values if value]
    if not quoted:
        return "stored metadata"
    if len(quoted) == 1:
        return quoted[0]
    if len(quoted) == 2:
        return f"{quoted[0]} and {quoted[1]}"
    return f"{', '.join(quoted[:-1])}, and {quoted[-1]}"
