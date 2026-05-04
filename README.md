# SANE

SANE is a human-governed inbound email decision system.

It is being developed as a real-world RBA-guided application that helps users identify low-value email sources, make explicit decisions, and reduce ongoing inbox noise without replacing their email client.

SANE stands for **Signal Analysis & Notification Elimination**.

## Problem

Modern email systems generate large volumes of low-value, subscription-based messages. Email clients often categorize these messages into folders such as Promotions or Updates, but categorization can hide accumulation instead of resolving it.

The core problem is not only unwanted email. The deeper problem is the absence of a practical decision loop for identifying low-value inbound messages, acting on them, and marking the decision complete.

## Goal

SANE helps users process inbound email as a decision stream:

```text
Identify -> Decide -> Act -> Complete
```

Stage 1 focuses on proving this core loop with a bounded, human-in-the-loop workflow.

AI may classify, suggest, and explain candidates. The human remains responsible for approving meaningful actions.

## Current Status

This repository currently contains a bounded Stage 1 ALPHA candidate:

- React + Vite + TypeScript review UI
- Python + FastAPI workflow API
- PostgreSQL-backed runtime persistence with Alembic-managed schema
- PostgreSQL-backed backend tests through a dedicated test database
- app authentication with Google sign-in and an HttpOnly JWT session cookie
- development-only Local ALPHA auth bypass for local UI/workflow review
- separate Gmail connection/disconnection and manual bounded scan controls
- Fernet-encrypted Gmail credential storage using a local environment key
- local user ownership foundation for sources and decisions via the seeded `Local ALPHA User`
- deterministic backend classifier for demo candidates
- Pydantic-based backend settings
- frontend and backend workflow tests, including mocked auth/Gmail integration coverage

Live Google sign-in and live Gmail API validation are still manual environment-driven checks. Automated tests remain mocked and deterministic.

## Architecture

Current and planned architecture:

```mermaid
flowchart LR
    User["User / Human Decision"] --> UI["React + Vite UI"]
    UI --> API["FastAPI Backend"]
    API --> DB["PostgreSQL Runtime"]
  API -. "test only" .-> TestDB["PostgreSQL Test DB"]

    API --> Gmail["Google OAuth + Gmail API"]
    API -. "future" .-> AI["Bounded AI Classifier"]
    AI -. "suggestions only" .-> API
    API --> UI
```

The frontend is the user decision surface for reviewing candidates and recording explicit decisions.

The backend is the classification, workflow, and persistence layer for the ALPHA slice.

The current classifier is deterministic and local. A future AI-backed classifier can replace it without becoming the final authority.

Google sign-in and Gmail connection are implemented in the runtime backend, but real OAuth/Gmail reality contact still depends on local Google Cloud setup and placeholder-free local environment values.

## Structure

```text
SANE/
  docs/
  frontend/
  backend/
  count-lines.ps1
  README.md
```

## Tech Stack

- Frontend: React, Vite, TypeScript
- Backend: Python, FastAPI
- Data: SQLAlchemy 2.x, Pydantic, PostgreSQL runtime and dedicated PostgreSQL test database
- Migrations: Alembic
- Testing: Vitest and pytest
- External integrations: Google OAuth and Gmail API
- Future integration: bounded AI classifier

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Run tests:

```bash
cd frontend
npm run test:run
```

Install the Chromium browser that the Playwright smoke tests use:

```bash
cd frontend
npm run test:e2e:install
```

Run the browser smoke tests:

```bash
cd frontend
npm run test:e2e
```

The frontend starts on `http://localhost:5173` by default.

## Browser E2E Smoke Tests

Prompt 11b adds a small Playwright smoke layer on top of the existing Vitest and pytest coverage.

Current E2E design:

- real Chromium browser
- real Vite frontend server
- deterministic Playwright API routing/mocking
- no real backend-backed auth mode switching
- no real Google OAuth, Gmail OAuth, Gmail scan, Gmail reset, or Gmail mutation

The Playwright config starts its own frontend server and sets `VITE_API_BASE_URL` only for that spawned process, so normal local `.env` files do not need to be edited for E2E.

Current smoke coverage:

- local-dev auth shell entry and app navigation
- Connections safety copy plus reset dialog open/cancel path
- Review evidence toggle and decision flow with Decisions pagination/history checks

These tests intentionally do not cover:

- real Google sign-in
- real Gmail authorization
- real Gmail scan execution
- live mailbox reset
- any real mailbox mutation path

Those flows remain manual local validation steps because they are credential-dependent and not appropriate for deterministic CI or student repeatability.

## Backend

Copy the example environment file, install dependencies, and start the API:

```bash
cd backend
python -m venv .venv
# activate the virtual environment for your shell
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

PostgreSQL is the required runtime database path for the backend. The backend now expects `SANE_DATABASE_URL` to be configured and will fail clearly if it is missing or points to SQLite during normal runtime.

Set `SANE_DATABASE_URL` and `SANE_TEST_DATABASE_URL` in `backend/.env`, for example:

```bash
SANE_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/sane
SANE_TEST_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/sane_test
```

For local auth and Gmail validation, `backend/.env` also needs placeholder-free values for:

```bash
SANE_AUTH_MODE=google_oauth
SANE_FRONTEND_URL=http://localhost:5173
SANE_JWT_SECRET=REPLACE_WITH_A_LONG_RANDOM_LOCAL_SECRET
SANE_CREDENTIAL_ENCRYPTION_KEY=PASTE_A_LOCAL_FERNET_KEY_HERE
SANE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
SANE_GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
SANE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
SANE_GMAIL_REDIRECT_URI=http://localhost:8000/api/gmail/callback
```

Generate a local Fernet key with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Keep all real values in the ignored local `backend/.env` only. Never commit real client secrets, JWT secrets, encryption keys, refresh tokens, or access tokens.

For local UI/workflow review before Google OAuth is configured, you can use:

```bash
SANE_AUTH_MODE=local_dev
SANE_DEBUG=true
```

This development-only bypass creates or reuses the Local ALPHA app session, is blocked when `SANE_DEBUG=false`, and does not connect Gmail or trigger ingestion.

Runtime schema changes should flow through Alembic. SQLite is no longer a supported database for SANE runtime or DB-integrated backend tests. The old `backend/sane_alpha.db` file, if present, should be treated as a disposable legacy artifact rather than an authoritative database.

Backend pytest now requires a separate PostgreSQL test database via `SANE_TEST_DATABASE_URL`. That database must already exist, must differ from `SANE_DATABASE_URL`, and its database name must include `test`.

Before backend tests run, the pytest fixture applies `alembic upgrade head` to the test database and then truncates SANE app tables with `RESTART IDENTITY CASCADE` between tests so IDs and row state reset deterministically without dropping the database.

Run backend tests:

```bash
cd backend
pytest
```

## Local Source Reclassification

Use the one-off local reclassification command after classifier heuristic changes when you want already-ingested Review rows to reflect the new deterministic rules without running a new Gmail scan.

Run it against a single mailbox account id:

```bash
cd backend
python -m app.commands.reclassify_sources --account-id 2
```

The command only uses stored local source rows for that mailbox and reports:

- rows inspected
- rows changed
- resulting signal counts

It recomputes only these source fields:

- `classifier_signal`
- `suggested_decision`
- `candidate_reason`
- `confidence`

It does not:

- run a Gmail scan
- call the Gmail API
- modify Gmail
- change decision history
- change `processing_state`
- change ingestion runs
- change credentials
- change mailbox connection state

This is a mailbox-scoped local refresh step for classifier output only, not a mailbox sync or action execution path.

The backend exposes a health endpoint at `http://localhost:8000/api/health`.

## Google OAuth and Gmail Local Setup

Prompt 09 is a reality-contact pass. The code already implements the live runtime path, but the Google Cloud project and local environment must be configured manually before live sign-in or Gmail scans can succeed.

If you only need local UI/workflow review first, set `SANE_AUTH_MODE=local_dev` in `backend/.env`. That bypass is limited to app authentication and keeps Gmail authorization separate.

1. Create or choose a Google Cloud project for local ALPHA testing.
2. Enable the Gmail API for that project.
3. Configure the OAuth consent screen for a local test app.
4. Add your local test Google account as a test user.
5. Create a Web application OAuth client.
6. Add these exact redirect URIs to that client:

```text
http://localhost:8000/api/auth/google/callback
http://localhost:8000/api/gmail/callback
```

The current implementation uses the backend callback routes above for both app sign-in and Gmail connection. It does not use a frontend Google SDK callback.

Consent/scope expectations for local ALPHA:

- Google sign-in requests `openid email profile`.
- Gmail mailbox connection requests `https://www.googleapis.com/auth/gmail.readonly`.
- The app must remain inside the manual Stage 1 guardrails: no modify/delete/send scopes, no automatic scans, and no full email body storage.

## Running a Local Live Check

Start the backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then perform the minimum live validation path:

1. Open `http://localhost:5173`.
2. Click `Sign in with Google`.
3. Complete Google sign-in and confirm the authenticated app shell and account menu appear.
4. Open `Connections`.
5. Click `Connect Gmail`.
6. Complete the separate Gmail consent flow.
7. Confirm the Gmail account row shows `Connected` and `Gmail read-only`.
8. Leave the limit at `50`.
9. Click `Scan Now`.
10. Confirm an ingestion run completes or fails with a visible status.
11. Open `Review` and confirm source rows were created or updated from the connected Gmail account.

Guardrail checks during live validation:

- No scan should run when the app opens.
- No scan should run when Google sign-in completes.
- No scan should run when Gmail connects.
- No scan should run when the `Connections` view loads.
- A scan should run only after the explicit `Scan Now` click.

If live validation fails, check backend logs first for redirect mismatch, missing test-user access, placeholder env values, or Gmail API configuration errors.

## Project Line Count

To count project lines, including Markdown docs but excluding generated/vendor folders and lock files:

```powershell
.\count-lines.ps1
```

Optional detail view:

```powershell
.\count-lines.ps1 -Details
```

Current workflow endpoints:

- `GET /api/auth/google/login`
- `GET /api/auth/google/callback`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/sources`
- `POST /api/decisions`
- `POST /api/decisions/batch`
- `GET /api/decisions`
- `GET /api/gmail/accounts`
- `GET /api/gmail/connect`
- `GET /api/gmail/callback`
- `POST /api/gmail/disconnect`
- `POST /api/gmail/scan`
- `GET /api/gmail/runs/{account_id}`

## Current Scope

- Stage 1 review workflow for demo and Gmail-ingested sources: review, decide, and preserve processed state
- Backend candidate listing and decision recording endpoints
- PostgreSQL-backed runtime persistence through `SANE_DATABASE_URL`
- PostgreSQL-backed backend persistence/API tests through `SANE_TEST_DATABASE_URL`
- Google sign-in with an ALPHA JWT cookie session
- Separate Gmail connect/disconnect flow with encrypted stored credentials
- Manual Gmail scan only, bounded to 50 / 100 / 200 and `CATEGORY_PROMOTIONS`
- Local ALPHA user ownership for sources and decisions when real login is not in use
- Deterministic classifier suggestions that remain subordinate to explicit human approval
- Frontend loading, error, and processed-history states
- No scan on app open, sign-in, Gmail connect, or `Connections` render
- No external email actions are executed

## Deferred Work

- Live Google/Gmail reality contact with a configured local Google Cloud project
- Production-grade session revocation and secret management
- Scheduled scans and full mailbox import
- AI classification module
- Human-approved action execution
- Subscription tiers, billing, GTD workflow, and multi-account support
