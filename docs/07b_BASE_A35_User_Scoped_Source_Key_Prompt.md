# Prompt 07b - A35 User-Scoped Source Identity

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this small corrective architecture prompt before Gmail ingestion.

## Active Execution Context

Active task:

- A35 - fix source identity uniqueness before Gmail/OAuth ingestion

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, but only section A35 and `Contract A35`
- backend models for user/source/decision
- Alembic revisions
- backend workflow service
- backend tests

## Clarification Gate

Before executing implementation:

1. Summarize the A35 issue in your own words.
2. State whether you will solve it with `unique(user_id, source_key)`.
3. List files you expect to touch.
4. State whether a new Alembic migration is needed.
5. State how you will test same-user duplicate rejection and cross-user duplicate allowance.
6. Ask clarifying questions if ambiguity affects the uniqueness rule or migration strategy.
7. You must have human approval before executing implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Problem

`source_key` is currently globally unique.

That is wrong for future multi-user/OAuth use because two different users may have the same email source/vendor/sender cluster.

User ownership exists, but it is not yet acting as the higher-order partition for source identity.

## Required Fix

Replace global `source_key` uniqueness with user-scoped source identity:

```text
unique(user_id, source_key)
```

Preserve current ALPHA behavior for the local ALPHA user.

Preserve the existing frontend/API contract.

## Expected Backend Work

Likely work:

- update `Candidate` model constraints/indexes
- add an Alembic migration after `0001_postgres_user_foundation`
- update tests to prove the corrected uniqueness behavior
- run backend tests
- run frontend regression tests/build if API behavior remains unchanged

Test expectations:

- same user cannot have duplicate `source_key`
- different users can each have the same `source_key`
- existing local ALPHA source listing still works
- existing decisions still work
- API payloads do not expose ownership fields

## Out Of Scope

Do not implement:

- Gmail OAuth
- Gmail API calls
- `GmailConnection` model unless it is absolutely necessary for the uniqueness fix
- ingestion runs
- scheduled scans
- frontend changes
- subscription/account-tier work
- real authentication/login UI

## Future Note

When SANE supports multiple Gmail accounts per user, source identity may need to become Gmail-connection-scoped:

```text
unique(gmail_connection_id, source_key)
```

That future review belongs to the Gmail/OAuth pass. For now, use `unique(user_id, source_key)`.

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If live PostgreSQL validation is available, run the new Alembic migration against the local PostgreSQL database and report the exact result.

Do not claim live PostgreSQL validation unless it actually runs.

## Report

Report:

- files changed
- migration created
- uniqueness rule implemented
- tests added/updated
- backend validation results
- frontend regression results
- whether live PostgreSQL migration was exercised
- any remaining ownership/model risks

