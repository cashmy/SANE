# Prompt 07c - Deprecate SQLite Runtime Path

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this cleanup prompt after PostgreSQL validation and the A35 source-key fix.

## Active Execution Context

Active task:

- Deprecate SQLite as a normal SANE runtime database.
- PostgreSQL is now the authoritative development/publication runtime path.

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `backend/app/core/config.py`
- `backend/app/db/session.py`
- `backend/.env.example`
- `backend/README` or root `README.md`
- backend tests and test config
- Alembic config and migrations

## Clarification Gate

Before executing implementation:

1. Summarize how SQLite is currently used in config, runtime, docs, and tests.
2. State exactly what you will change so PostgreSQL is the authoritative runtime database.
3. State whether SQLite will remain only for tests, or whether you can remove it from tests as well.
4. List files you expect to touch.
5. Ask clarifying questions if ambiguity affects runtime config or test determinism.
6. You must have human approval before executing implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Remove SQLite as a normal runtime option for SANE.

PostgreSQL should be the expected database for running the backend.

SQLite may remain only if needed for deterministic tests, and if so it must be clearly labeled as a test-only fallback.

## Required Changes

Update runtime configuration so:

- `SANE_DATABASE_URL` is required for normal backend runtime, or defaults to a PostgreSQL URL only if that is clearly safe for local dev
- SQLite is not presented as the ALPHA/runtime default
- missing database configuration should fail clearly rather than silently creating/using a stale SQLite database
- PostgreSQL remains the expected runtime database

Update docs so:

- `.env.example` presents PostgreSQL as the runtime database
- README/setup docs no longer describe SQLite as the normal ALPHA database
- any SQLite mention is explicitly test-only or legacy/deprecated
- old SQLite files are described as disposable legacy artifacts if mentioned

Update tests so:

- tests still pass deterministically
- if tests use SQLite, that usage is isolated and clearly test-only
- tests do not depend on the runtime PostgreSQL database unless explicitly documented

## Preserve Existing Behavior

Preserve:

- source-oriented API behavior
- local ALPHA user behavior
- user-scoped source key uniqueness
- Alembic migration path
- no Gmail/OAuth behavior
- no external email actions
- frontend API contract

## Out Of Scope

Do not implement:

- Gmail OAuth
- Gmail API calls
- ingestion runs
- source-key scoping by Gmail connection
- subscription/account-tier work
- frontend redesign
- real authentication/login UI

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If PostgreSQL is available, also validate:

```powershell
cd backend
python -m alembic current
python -m alembic upgrade head
```

Report whether those commands ran against PostgreSQL.

## Report

Report:

- files changed
- whether SQLite remains anywhere
- if SQLite remains, why and where
- how missing/runtime database configuration behaves
- validation results
- whether PostgreSQL was exercised
- any remaining SQLite drift risk

