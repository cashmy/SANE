# SANE Data Model ERD

## Purpose

This artifact records the SANE account/auth/mailbox/source data model after the A40/A41/A42 planning pass, Prompt 07e foundation implementation, and Prompt 08 auth/Gmail implementation.

It exists as a CORE/SKY review aid and as a future BASE reference.

Implementation status:

- Prompt 07e added the account/auth/mailbox/ingestion foundation.
- Prompt 08 added Google app authentication, separate Gmail authorization, encrypted Gmail credential storage, and manual bounded Gmail ingestion.
- Alembic head after Prompt 08 is `0006_gmail_credential_storage`.
- Backend validation reported `46/46` tests passing.
- Frontend regression validation reported `13/13` tests passing and build passing.

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
      text credential_json
      datetime token_expiry
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

Prompt 08 made any remaining `User.email` value legacy/nullable. `UserEmail` is authoritative for email ownership and account linking.

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

Prompt 08 stores Gmail OAuth credentials as an encrypted credential blob on the email account for ALPHA. Tokens must never be exposed through frontend APIs.

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

Current ALPHA behavior:

- manual user-requested scan only
- default scan scope `CATEGORY_PROMOTIONS`
- bounded scan limits 50 / 100 / 200
- no scan on app open
- no scan on sign-in
- no scan on Connections view render

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

Implemented email authority rule:

```text
UserEmail is authoritative for email addresses and verified-email linking.
User.email is legacy/nullable only if still present for compatibility.
```

## Disconnect vs Delete

Disconnect means:

- mailbox is not connected
- scans/imports/actions are blocked
- local SANE data is preserved
- stored Gmail credentials are cleared for Prompt 08 ALPHA behavior

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

Prompt 08 implemented this as minimal clustering/source-review storage from Gmail metadata/snippets only.

## Future Notes

Potential future additions:

- MessageEvidence / SourceEvidence
- token/credential reference model
- account merge policy
- subscription/account tier model
- scheduled ingestion jobs
