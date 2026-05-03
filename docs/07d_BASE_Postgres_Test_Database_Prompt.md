# Prompt 07d - PostgreSQL-Backed Backend Tests

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this follow-up after SQLite runtime deprecation.

## Active Execution Context

Active task:

- A38 - move backend DB-integrated tests from SQLite fallback to PostgreSQL.

PostgreSQL is now the authoritative SANE runtime database.

SQLite should not be used for backend persistence/API validation.

## Required Context

Before proposing or implementing changes, inspect:

- `backend/app/core/config.py`
- `backend/app/db/session.py`
- `backend/tests/conftest.py`
- backend tests
- `backend/.env.example`
- `README.md`
- Alembic config and migrations

## Clarification Gate

Before executing implementation:

1. Summarize how backend tests currently use SQLite.
2. Propose the PostgreSQL test database strategy.
3. State whether you will introduce `SANE_TEST_DATABASE_URL`.
4. State how test data/schema will be reset deterministically.
5. List files you expect to touch.
6. Ask clarifying questions if ambiguity affects local PostgreSQL test setup or destructive test reset behavior.
7. You must have human approval before executing implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Backend persistence/API tests should run against PostgreSQL, not SQLite.

This avoids false positives from dialect differences now that SANE's runtime database is PostgreSQL.

## Required Direction

Implement a separate PostgreSQL test database configuration.

Preferred:

```text
SANE_TEST_DATABASE_URL=postgresql+psycopg://.../sane_test
```

Test behavior should:

- never reset or drop the runtime/development database accidentally
- fail clearly if `SANE_TEST_DATABASE_URL` is missing or points to an unsafe database
- apply Alembic migrations or otherwise ensure schema is current
- reset data deterministically between tests
- keep tests reliable and repeatable

## Safety Requirements

Because test reset can be destructive:

- require a test database URL separate from `SANE_DATABASE_URL`
- prefer requiring the database name to include `test`, such as `sane_test`
- do not drop or truncate an arbitrary database without safety checks
- document setup steps clearly

## Preserve Existing Behavior

Preserve:

- PostgreSQL runtime requirement
- Alembic migration path
- local ALPHA user behavior
- user-scoped source key uniqueness
- source/decision API behavior
- frontend behavior
- no Gmail/OAuth work

## Out Of Scope

Do not implement:

- Gmail OAuth
- Gmail API calls
- ingestion runs
- frontend changes unless documentation references require it
- subscription/account-tier work
- source-key scoping by Gmail connection

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

Report whether backend pytest ran against PostgreSQL and include the test DB safety check behavior.

## Report

Report:

- files changed
- test DB configuration
- reset strategy
- safety checks
- validation results
- whether SQLite remains anywhere
- any remaining test fidelity risks

