# SANE Data Model ERD

## Purpose

This artifact records the SANE account/auth/mailbox/source data model after the A40/A41/A42 planning and Prompt 07e implementation pass.

It exists as a CORE/SKY review aid and as a future BASE reference.

Implementation status:

- Prompt 07e added the account/auth/mailbox/ingestion foundation.
- Alembic head after this pass is `0003_email_account_foundation`.
- Backend validation reported `21/21` tests passing.
- Frontend regression validation reported `10/10` tests passing and build passing.

The key modeling lesson is:

```text
Do not implement deferred integrations prematurely,
but do model known future ownership boundaries.
```

## Intended Ownership Hierarchy

```text
User
-> UserEmail
-> AuthIdentity
-> EmailAccount
    -> Source/Candidate
    -> IngestionRun
        -> optional future message evidence
    -> Decision
```

## Mermaid ERD

```mermaid
erDiagram
    USER ||--o{ USER_EMAIL : has
    USER ||--o{ AUTH_IDENTITY : signs_in_with
    USER ||--o{ EMAIL_ACCOUNT : owns
    EMAIL_ACCOUNT ||--o{ CANDIDATE : contains_sources
    EMAIL_ACCOUNT ||--o{ INGESTION_RUN : has_runs
    CANDIDATE ||--o{ DECISION : receives
    USER ||--o{ DECISION : makes
    DECISION ||--o{ DECISION : revises

    USER {
      int id PK
      string display_name
      datetime created_at
      datetime updated_at
    }

    USER_EMAIL {
      int id PK
      int user_id FK
      string email
      string role
      boolean is_primary
      datetime verified_at
      datetime created_at
    }

    AUTH_IDENTITY {
      int id PK
      int user_id FK
      string provider
      string provider_subject
      string provider_email
      datetime created_at
    }

    EMAIL_ACCOUNT {
      int id PK
      int user_id FK
      string provider
      string account_email
      string display_name
      string connection_status
      datetime created_at
      datetime updated_at
    }

    CANDIDATE {
      int id PK
      int email_account_id FK
      string source_key
      string source_name
      json sender_emails
      int email_count
      string representative_subject
      string mailbox_category
      string classifier_signal
      string suggested_decision
      string processing_state
      datetime created_at
      datetime updated_at
    }

    DECISION {
      int id PK
      int user_id FK
      int candidate_id FK
      int revised_from_decision_id FK
      string decision
      boolean human_confirmed
      string external_action_status
      datetime created_at
    }

    INGESTION_RUN {
      int id PK
      int user_id FK
      int email_account_id FK
      string trigger_type
      string status
      string scope
      int limit_count
      string lookback_window
      datetime started_at
      datetime completed_at
      int message_count_scanned
      int source_count_created
      string error_summary
    }
```

## Table Meaning

### User

The stable SANE account owner.

Do not treat an email address as the user identity.

### UserEmail

Email addresses associated with the user.

Used for primary/contact/login/notification identity and verification state.

### AuthIdentity

Ways the user can sign into SANE.

Examples:

- Google
- Microsoft
- GitHub
- LinkedIn
- Facebook
- local dev
- email/password
- magic link

Auth identity does not imply mailbox access.

### EmailAccount

Mailbox/account SANE is authorized to scan or represent.

Examples:

- Gmail
- Microsoft/Outlook
- IMAP
- Local ALPHA mailbox

Mailbox access does not imply app sign-in method.

### Candidate / Source

The current model name is `Candidate`, but the product concept is source/vendor/sender cluster.

Sources belong to an `EmailAccount`, not directly to the `User`.

This supports one user with multiple mailboxes that contain the same source.

### Decision

Human decision about a source.

`Decision.user_id` is intentionally retained for direct user decision queries and authorization checks.

This is controlled denormalization.

Invariant:

```text
Decision.user_id must match Decision -> Candidate -> EmailAccount.user_id
```

### IngestionRun

An explicit scan/import/analyze operation for one email account.

Gmail ingestion must never run simply because the app opens.

Allowed future triggers:

- manual user-requested scan
- scheduled/chrono-controlled scan
- bounded ALPHA/test scan

## Key Constraints

Expected constraints:

```text
UserEmail.email should be unique or carefully governed for account-linking policy.
AuthIdentity should be unique by provider + provider_subject.
EmailAccount should likely be unique by user_id + provider + account_email.
Candidate/Source should be unique by email_account_id + source_key.
```

Implemented source identity rule:

```text
unique(email_account_id, source_key)
```

This supersedes both the original global `source_key` uniqueness and the interim user-scoped rule.

## Disconnect vs Delete

Disconnect means:

- mailbox is not connected
- scans/imports/actions are blocked
- local SANE data is preserved

Delete means:

- mailbox is disassociated from SANE
- related local mailbox data is removed
- cascade behavior must be intentional and tested

## Data Minimization

Early Gmail ingestion should not store full email bodies.

Prefer minimal metadata/snippets needed for:

- source classification
- representative examples
- dedupe/reference
- human decision support

## Future Notes

Potential future additions:

- MessageEvidence / SourceEvidence
- token/credential reference model
- account merge policy
- subscription/account tier model
- scheduled ingestion jobs
