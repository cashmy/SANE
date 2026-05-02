# Prompt 07 - PostgreSQL and User Ownership Foundation

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this bounded architecture foundation prompt.

## Active Execution Context

Active task:

- A30 - PostgreSQL persistence foundation
- A31 - basic user/account ownership foundation

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect the execution-relevant project files:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, but only sections A30, A31, and `Contract A30 / A31`
- backend dependency/config files
- backend database/session/base setup
- backend models, schemas, services, routers, and tests
- frontend API/types only if backend contract changes require frontend compatibility checks
- `.env.example`, README, and any existing setup docs

## Clarification Gate

Before executing implementation:

1. Summarize the A30/A31 contract in your own words.
2. Report whether the workspace already has Alembic, PostgreSQL dependencies, Docker/compose files, or a local PostgreSQL assumption.
3. List the files you expect to touch.
4. State whether validation will use a live PostgreSQL database, SQLite test fallback, or both.
5. Ask clarifying questions if any ambiguity affects database setup, migration strategy, or user ownership semantics.
6. You must have human approval before executing the implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Move SANE from SQLite-first ALPHA persistence toward PostgreSQL-ready Tier 1 architecture while adding a basic user/account ownership foundation.

This is one architecture foundation pass because future Gmail OAuth, settings, decisions, subscription/account state, and connected email accounts all require user ownership.

## Required Behavior

Implement PostgreSQL-ready persistence:

- support PostgreSQL through `.env` / `DATABASE_URL`
- keep local development understandable and documented
- add or formalize migration support with Alembic if not already present
- preserve working tests
- avoid SQLite-specific assumptions where practical

Implement basic user/account ownership:

- add a basic user or account model
- create a local ALPHA user path so current demo/local behavior still works without real login
- associate source review rows with a user/account
- associate decisions with a user/account, either directly or through owned sources, as appropriate
- preserve current Stage 1 behavior under the local ALPHA user
- preserve visible `Local ALPHA User` frontend behavior unless you explicitly explain why a small frontend adjustment is needed

## Preserve Existing Contracts

Preserve:

- source/vendor/cluster review units
- `/api/sources` behavior unless a backward-compatible ownership field is necessary
- `source_id` and `source_ids` decision payload behavior
- human-confirmed decisions
- append-only decision history with revision semantics
- repeated identical decision no-op behavior
- batch decision confirmation
- no external email actions
- pagination/page-size behavior
- light/dark frontend behavior
- no Gmail access

## Out Of Scope

Do not implement:

- Gmail OAuth
- Gmail API calls
- Gmail token storage
- ingestion runs
- scheduled jobs
- real login/auth UI
- password handling
- billing/subscription enforcement
- multi-account Gmail support
- real unsubscribe/archive/delete actions
- external AI provider calls
- GTD workflow

## PostgreSQL Setup Guidance

Prefer pragmatic local development support.

If PostgreSQL is not currently available in the workspace, you may add a documented local dev option such as `docker-compose.yml` for PostgreSQL, but do not assume Docker is running unless you validate it.

If tests cannot depend on a live PostgreSQL instance in this environment, keep tests deterministic through a test database strategy and document the difference between:

- runtime PostgreSQL configuration
- test database configuration

Do not silently pretend live PostgreSQL validation occurred if it did not.

## Testing And Validation

Run the relevant validation you can run locally:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If frontend files were not changed and backend API responses remain compatible, frontend validation is still preferred as a regression check.

If live PostgreSQL validation is possible, also run a minimal migration/schema validation against PostgreSQL and report exactly what command was used.

## Report

Report:

- files changed
- dependency changes
- migration files created
- database configuration changes
- user/account ownership design
- how the local ALPHA user is resolved/seeded
- validation results
- whether live PostgreSQL was actually exercised
- any remaining risks or follow-up issues

