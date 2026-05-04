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


# ---------------------------------------------------------------------------
# Account / auth / mailbox enums (A40)
# ---------------------------------------------------------------------------


class AuthProvider(str, Enum):
    google = "google"
    microsoft = "microsoft"
    github = "github"
    linkedin = "linkedin"
    facebook = "facebook"
    local_dev = "local_dev"
    email_password = "email_password"
    magic_link = "magic_link"


class EmailAccountProvider(str, Enum):
    gmail = "gmail"
    microsoft = "microsoft"
    imap = "imap"
    local_alpha = "local_alpha"


class ConnectionStatus(str, Enum):
    connected = "connected"
    disconnected = "disconnected"
    expired = "expired"
    revoked = "revoked"
    error = "error"
    local_only = "local_only"


class IngestionTriggerType(str, Enum):
    manual = "manual"
    scheduled = "scheduled"
    alpha_test = "alpha_test"


class IngestionStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class UserEmailRole(str, Enum):
    primary = "primary"
    login = "login"
    contact = "contact"
    recovery = "recovery"
    billing = "billing"
    notification = "notification"
