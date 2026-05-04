# Prompt 13c - UserEmail Role Enum and Candidate Rename Audit

## Status

Ready for BASE clarification gate after Prompt 13b.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this data-model stabilization prompt.

## Context

SANE now has a future-ready account/auth/mailbox model:

```text
User
-> UserEmail
-> AuthIdentity
-> EmailAccount
    -> Candidate/Source
    -> IngestionRun
    -> Decision
```

During SKY/CORE ERD review, SKY considered whether `UserEmail` could be merged into `EmailAccount`, and whether `AuthIdentity` could be simplified similarly.

CORE pushed back and SKY accepted the distinction:

- `UserEmail` answers: what email addresses are associated with this SANE user for identity/contact/login/recovery/notification purposes?
- `AuthIdentity` answers: how can this user sign into SANE?
- `EmailAccount` answers: what mailbox has SANE been authorized to access, scan, or represent?

That governance decision is preserved in:

```text
SANE-RBA/Ancillary/Identity_Mailbox_Model_Governance.md
```

Project-facing issue:

```text
A61 - UserEmail.role should become enum-backed rather than an unconstrained string.
```

Related existing technical debt:

```text
A26 - internal SQLAlchemy Candidate model/table name remains while API/UI/docs use source language.
```

## Active Execution Context

Active task:

- stabilize `UserEmail.role` as a governed enum-backed field
- preserve the conceptual separation of `UserEmail`, `AuthIdentity`, and `EmailAccount`
- audit A26 `Candidate` rename blast radius
- do not implement A26 rename unless the clarification gate proves it is small and SKY explicitly approves it

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- `backend/app/models/enums.py`
- `backend/app/models/user_email.py`
- `backend/app/models/user.py`
- `backend/app/models/auth_identity.py`
- `backend/app/models/email_account.py`
- auth/linking services that create or query `UserEmail`
- Alembic migrations touching `user_emails`
- tests touching auth/user email/linking behavior
- references to `Candidate` model/table/class in backend code, migrations, tests, schemas, frontend types, and docs

## Clarification Gate

Before implementation:

1. State the current `UserEmail.role` implementation.
2. State where `UserEmail.role` is created, updated, queried, or assumed.
3. State whether any current code relies on arbitrary free-form role strings.
4. Propose the enum values needed now, using this approved starting set unless inspection proves a conflict:
   - `primary`
   - `login`
   - `contact`
   - `recovery`
   - `billing`
   - `notification`
5. State whether the enum should be a SQLAlchemy native enum, non-native enum, or constrained string, and why. Prefer consistency with current project enum patterns.
6. State whether a migration is required and how existing rows should be backfilled or validated.
7. State which backend tests need updating or adding.
8. State whether any frontend/API contract changes are required. The expected answer should usually be no unless inspection proves otherwise.
9. Audit A26 `Candidate` rename blast radius:
   - list major backend files affected
   - list migration/table implications
   - list frontend/API/docs implications
   - classify rename as small, medium, or large
10. Recommend whether A26 should remain deferred after this audit.
11. Ask clarifying questions if role semantics, enum migration behavior, account-linking behavior, or Candidate rename scope are ambiguous.
12. Ask any other clarifying questions from code inspection, tests, UI implications, or conflicts between prompt and implementation.
13. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Approved Direction

The intended model is:

```text
UserEmail.role: governed role enum
```

Role meanings:

- `primary`: main user email for account identity/contact
- `login`: email usable for email-based login or linking
- `contact`: general contact email
- `recovery`: account recovery email
- `billing`: billing/subscription email
- `notification`: notification delivery email

Keep these tables separate:

- `UserEmail`
- `AuthIdentity`
- `EmailAccount`

Do not merge them in this pass.

## Guardrails

Do not change:

- app authentication behavior
- Google OAuth behavior
- Gmail OAuth behavior
- Gmail scan/ingestion behavior
- credential storage
- source identity
- decision behavior
- reset behavior
- frontend UX unless inspection proves it is necessary for tests/contracts

Do not rename `Candidate` yet unless SKY approves after the audit.

Do not introduce subscription/billing workflow behavior. `billing` is only an email role value in this pass.

## Likely Preferred Outcome

Expected implementation if the clarification gate confirms no conflict:

- add `UserEmailRole` enum to `backend/app/models/enums.py`
- update `UserEmail.role` to use SQLAlchemy enum consistent with project enum style
- add Alembic migration for existing `user_emails.role` values
- preserve existing rows such as `primary` or `contact`
- add tests proving allowed roles and account-linking behavior still work
- update ERD and issue register
- report A26 Candidate rename as audited/deferred unless unexpectedly small

## Testing

For role enum changes:

```powershell
cd backend
python -m pytest
python -m alembic current
```

If migrations are added:

```powershell
python -m alembic upgrade head
```

If any frontend contract or fixture changes are required:

```powershell
cd frontend
npm run test:run
npm run test:e2e
npm run build
```

## Report

Report:

- clarification gate findings
- approved enum values implemented
- files changed
- migration added and Alembic head/current
- tests updated
- validation results
- A26 Candidate rename blast-radius classification
- remaining data-model risks

