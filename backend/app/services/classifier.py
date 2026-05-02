from dataclasses import dataclass

from app.models.enums import CandidateSignal, DecisionValue


@dataclass(frozen=True)
class CandidateClassification:
    signal: CandidateSignal
    suggested_decision: DecisionValue
    reason: str
    confidence: float


def classify_demo_candidate(
    sender_name: str, sender_email: str, subject: str, mailbox_category: str
) -> CandidateClassification:
    searchable_text = " ".join(
        [sender_name, sender_email, subject, mailbox_category]
    ).lower()

    if any(
        keyword in searchable_text for keyword in ("deal", "sale", "promo", "discount")
    ):
        return CandidateClassification(
            signal=CandidateSignal.promotional_digest,
            suggested_decision=DecisionValue.mark_low_value,
            reason="Repeated promotional language suggests this source is mostly marketing noise.",
            confidence=0.93,
        )

    if any(
        keyword in searchable_text
        for keyword in ("newsletter", "digest", "roundup", "weekly", "recap")
    ):
        return CandidateClassification(
            signal=CandidateSignal.recurring_updates,
            suggested_decision=DecisionValue.unsubscribe_later,
            reason="This looks like a recurring update stream that may merit a later unsubscribe decision.",
            confidence=0.81,
        )

    return CandidateClassification(
        signal=CandidateSignal.ambiguous_source,
        suggested_decision=DecisionValue.keep_for_now,
        reason="The source shows some low-value traits, but it remains ambiguous and should stay reviewable.",
        confidence=0.58,
    )
