from enum import Enum


class CandidateSignal(str, Enum):
    promotional_digest = "promotional_digest"
    recurring_updates = "recurring_updates"
    ambiguous_source = "ambiguous_source"


class CandidateState(str, Enum):
    pending_review = "pending_review"
    kept = "kept"
    marked_low_value = "marked_low_value"
    action_recommended = "action_recommended"


class DecisionValue(str, Enum):
    keep_for_now = "keep_for_now"
    mark_low_value = "mark_low_value"
    unsubscribe_later = "unsubscribe_later"


class ExternalActionStatus(str, Enum):
    not_executed = "not_executed"
