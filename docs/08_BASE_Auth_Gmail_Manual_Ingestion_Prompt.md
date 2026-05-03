# Prompt 08 - Auth, Gmail Connection, and Manual Bounded Ingestion

## Status

Do not execute until Prompt 07e / A40-A42 is complete and validated.

This prompt assumes the database already has:

- `User`
- `UserEmail`
- `AuthIdentity`
- `EmailAccount`
- `IngestionRun`
- sources/candidates scoped to `EmailAccount`
- PostgreSQL-backed runtime and tests

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this post-07e integration prompt.

## Active Execution Context

Active tasks:

- app authentication/session surface
- Google sign-in account creation/linking
- Gmail mailbox connection
- manual-only bounded Gmail ingestion
- Connections view as authorization/scan control center

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, but only A32/A33/A40/A41/A42 and related contracts
- `docs/SANE_Data_Model_ERD.md`
- backend config and environment handling
- account/auth/mailbox models from Prompt 07e
- source/decision services
- Connections view
- AppShell/top toolbar/account area
- frontend API/types/tests
- backend tests

## Clarification Gate

Before executing implementation:

1. Confirm A40/A41/A42 are complete and validated.
2. Summarize the distinction between app authentication, Gmail authorization, and Gmail ingestion.
3. List the Google sign-in and Gmail scopes you believe are needed and why.
4. State how OAuth client secrets and mailbox tokens will be represented without exposing secrets.
5. State how account creation/linking will work on first Google sign-in.
6. State how Gmail connection differs from app sign-in.
7. State how manual scan will be triggered and bounded.
8. List files you expect to touch.
9. State how behavior will be tested without calling real Google/Gmail APIs in automated tests.
10. Ask clarifying questions if ambiguity affects auth, OAuth scopes, token handling, account linking, ingestion limits, or privacy expectations.
11. You must have human approval before executing implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Core Conceptual Separation

Keep these separate:

```text
App authentication = who is using SANE
Gmail authorization = what mailbox access SANE is allowed to use
Ingestion = when SANE scans/imports/analyzes email
```

Google can participate in both app sign-in and Gmail authorization, but the model must not collapse those concepts.

Examples:

- a user may later sign in with GitHub and connect Gmail
- a user may later sign in with Google and connect Microsoft/Outlook
- a user may later connect multiple Gmail accounts

## Hard Governance Rules

SANE must never scan, import, or analyze Gmail merely because:

- the app opens
- the user signs in
- Gmail is connected
- the Connections view renders

Gmail ingestion must be triggered only by an explicit controlled action.

For this pass:

```text
manual user-requested scan only
```

No scheduled scans unless SKY explicitly approves later.

## Auth / Session Direction

Implement a minimal app session path suitable for ALPHA/Tier 1 progression.

Preferred UX:

- sign in with Google
- first successful sign-in creates or links the SANE `User`
- app shell shows signed-in identity
- user can sign out
- no email/password auth in this pass
- no password storage
- no password reset

Account linking policy:

- auto-link identities when provider email is verified and matches an existing verified `UserEmail`
- otherwise create a new `User`
- record provider identity in `AuthIdentity`
- record/maintain user email in `UserEmail`

## Gmail Connection Direction

Connections view should become the external-service authorization and scan-control center.

It should support:

- Gmail connection status
- connected Gmail account email
- granted scope summary
- connect/reconnect/disconnect Gmail
- last ingestion run status if available
- manual bounded scan action

Sign out and disconnect are different:

- sign out ends the SANE app session
- disconnect Gmail blocks scans/actions for that mailbox but preserves local SANE data
- delete mailbox/data is not required in this pass unless already implemented by 07e and safe

## OAuth / Token Handling

Do not expose secrets or tokens to the frontend.

Use `.env` configuration for:

- Google OAuth client ID
- Google OAuth client secret
- OAuth redirect URI
- allowed frontend origin if needed

Token storage should be safe for ALPHA and clearly documented.

If full encryption-at-rest is not implemented in this pass, use a `credential_ref` / token metadata approach or clearly mark stored token handling as ALPHA-only and not production-safe.

Do not pretend token storage is production secure if it is not.

## Gmail Scope Direction

Use the minimum necessary scopes.

Likely initial scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```

Do not request modify/delete/send scopes.

No unsubscribe/archive/delete actions are allowed.

## Manual Bounded Ingestion Direction

Implement an explicit manual scan endpoint/action.

Default bounds:

- latest 50 messages unless SKY chooses another limit
- optional category/label scope if feasible without overbuilding
- no full mailbox import
- no full email body storage

Create an `IngestionRun` for each scan.

Record:

- trigger type = manual
- status
- scope
- limit count
- message count scanned
- source count created/updated
- error summary if failed

Normalize Gmail messages into source/vendor/cluster review units under the connected `EmailAccount`.

Source uniqueness should use:

```text
unique(email_account_id, source_key)
```

## Data Minimization

Do not store full email bodies.

Prefer minimal data needed for source governance:

- provider message id where needed
- sender/from metadata
- sender/domain/source identity
- labels/categories if available
- date/internal timestamp if needed
- subject/snippet only if useful for representative examples

## Frontend Direction

Add only the UI needed for this workflow.

Expected UI:

- auth/sign-in modal or screen when unauthenticated
- app shell account area with signed-in user and sign out option
- Connections view for Gmail connect/reconnect/disconnect
- Connections view manual scan button
- Connections view bounded scan settings/status
- Review view may show last scan summary compactly if helpful

Do not turn Review into the OAuth setup surface.

Do not add marketing/expository panels.

## Testing

Automated tests must not call real Google/Gmail APIs.

Use mocks/fakes for:

- Google OAuth exchange
- ID/profile response
- Gmail message listing
- Gmail message metadata normalization
- token refresh/error cases
- ingestion errors

Backend test expectations:

- app load/startup does not scan Gmail
- sign-in creates/links User, UserEmail, and AuthIdentity correctly
- Gmail connect creates/updates EmailAccount
- disconnect blocks scan but preserves local data
- manual scan requires authenticated user and connected Gmail EmailAccount
- manual scan respects limit count
- manual scan records IngestionRun
- manual scan creates/updates source review units under EmailAccount
- no external unsubscribe/archive/delete action executes

Frontend test expectations:

- unauthenticated state shows sign-in path
- signed-in app shell shows account/sign-out surface
- Connections view shows Gmail connection status
- manual scan only triggers from explicit user action
- app open/render does not trigger scan

## Out Of Scope

Do not implement:

- full mailbox import
- scan-on-app-open
- scan-on-sign-in
- scheduled scans
- unsubscribe/archive/delete actions
- send mail
- AI provider calls
- GTD workflow
- billing/subscription enforcement
- multi-account UI beyond what the model already supports
- Microsoft/IMAP integration
- full email body storage

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If live Google OAuth validation is not possible in this environment, report that clearly and provide exact manual validation steps.

If live validation is performed, report exactly what was live-tested and what was mocked.

## Report

Report:

- files changed
- auth/session design
- Google/Gmail scopes selected
- account linking behavior
- Gmail connection behavior
- disconnect behavior
- token/credential handling approach
- manual scan trigger behavior
- ingestion bounds
- data minimization choices
- test strategy
- validation results
- mocked vs live-tested behavior
- remaining security/privacy risks

