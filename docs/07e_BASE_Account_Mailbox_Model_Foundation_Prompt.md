# Prompt 07e - Account/Auth/Mailbox Model Foundation

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this pre-Gmail data-model foundation prompt.

## Active Execution Context

Active task:

- A40 - account/auth/mailbox hierarchy
- A41 - Gmail data minimization
- A42 - disconnect vs delete lifecycle semantics

This is a database/model foundation pass before Gmail OAuth/API implementation.

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, but only A40/A41/A42 and `Contract A40 / A41 / A42`
- backend models
- backend services
- backend schemas/routers if needed
- Alembic migrations
- backend PostgreSQL test fixture
- relevant backend tests
- README and `.env.example` only if docs need updates

## Clarification Gate

Before executing implementation:

1. Summarize the account/auth/mailbox hierarchy in your own words.
2. List the new models/tables you expect to add.
3. State how existing local ALPHA data will map to a local ALPHA email account/mailbox.
4. State how source uniqueness will change.
5. State whether current API/frontend behavior will remain unchanged.
6. List files you expect to touch.
7. Ask clarifying questions if ambiguity affects model ownership, cascade behavior, or migration strategy.
8. You must have human approval before executing implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Prepare the database model for known future SANE requirements before live Gmail integration:

- one SANE user can have multiple login identities
- one SANE user can have multiple associated email addresses
- one SANE user can connect multiple email accounts/mailboxes
- Gmail comes first
- Microsoft/Outlook, IMAP, or other providers may come later
- Tier 3 may support multiple mailboxes for one user

## Required Model Direction

Use this conceptual hierarchy:

```text
User
-> UserEmail
-> AuthIdentity
-> EmailAccount
    -> Source/Candidate
    -> IngestionRun
```

Definitions:

- `User` is the stable SANE account owner with generated ID.
- `UserEmail` stores emails associated with the user, including primary/secondary/contact/login emails and verification state.
- `AuthIdentity` stores sign-in identities/providers. Auth provider does not imply mailbox access.
- `EmailAccount` stores connected mailboxes SANE may scan. Mailbox provider does not imply app login method.
- `IngestionRun` stores explicit scan/import/analyze operations for one email account.

## Required Source Identity Change

Move source identity to the email-account boundary.

Expected rule:

```text
unique(email_account_id, source_key)
```

This replaces user-scoped source identity because one user may later connect multiple mailboxes that contain the same source.

## Local ALPHA Mailbox

Create or resolve a local ALPHA email account/mailbox for existing demo/local data.

Expected shape:

```text
provider = local_alpha
account_email = local-alpha@sane.local
display_name = Local ALPHA Mailbox
connection_status = local_only
```

Current demo sources should belong to that local ALPHA email account.

Current API/frontend behavior should remain unchanged unless you identify a necessary compatibility issue.

## Provider Concepts

Auth providers may include values such as:

- google
- microsoft
- github
- linkedin
- facebook
- local_dev
- email_password
- magic_link

Email account providers may include values such as:

- gmail
- microsoft
- imap
- local_alpha

Do not implement any real provider behavior yet.

## IngestionRun Foundation

Add an `IngestionRun` model or equivalent table now, but do not execute Gmail scans.

Initial fields should support:

- user ownership
- email account ownership
- trigger type
- status
- scope
- limit count
- lookback window
- started/completed timestamps
- message count scanned
- source count created
- error summary

No scan-on-app-open behavior should exist.

## Data Minimization

Prepare for minimal email-derived storage.

Do not add full email body storage.

Future Gmail ingestion should initially store only metadata/snippets needed for source classification and representative examples.

## Disconnect vs Delete Semantics

Model connection status so future flows can distinguish:

- connected
- disconnected
- expired
- revoked
- error
- local_only

Disconnect/revoke/expire/error means scans and mailbox actions are blocked, but local SANE data remains.

Delete means disassociate the mailbox and remove related local data. If cascade delete behavior is introduced, document it and test it carefully.

## Preserve Existing Behavior

Preserve:

- current `/api/sources`, `/api/decisions`, and `/api/decisions/batch` behavior
- local ALPHA user behavior
- source-oriented review units
- append-only decision history
- repeated identical decision no-op
- batch decision confirmation
- PostgreSQL runtime/test setup
- Alembic migration path
- no external email actions

## Out Of Scope

Do not implement:

- live OAuth
- Gmail API calls
- Gmail token exchange
- actual scan execution
- scheduled jobs
- real login UI
- Microsoft/IMAP integrations
- billing/subscription
- full email body storage
- frontend changes unless absolutely necessary

## Testing

Use the PostgreSQL-backed test setup.

Add/update backend tests to prove:

- local ALPHA user gets a local ALPHA email account
- demo sources belong to the local ALPHA email account
- duplicate source keys are rejected within the same email account
- duplicate source keys are allowed across different email accounts
- current source listing and decision behavior still works
- ingestion runs can be represented without executing Gmail
- delete/cascade behavior is correct if implemented now

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

Run Alembic against PostgreSQL and report the current head.

## Report

Report:

- files changed
- models/tables added
- migrations created
- source uniqueness rule after the change
- local ALPHA mailbox behavior
- tests added/updated
- validation results
- whether frontend/API behavior changed
- remaining model risks before Prompt 08

