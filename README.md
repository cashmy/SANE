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
- local user ownership foundation for sources and decisions via the seeded `Local ALPHA User`
- deterministic backend classifier for demo candidates
- Pydantic-based backend settings
- frontend and backend workflow tests

Gmail OAuth, Gmail API integration, AI classification, and email actions are intentionally deferred.

## Architecture

Current and planned architecture:

```mermaid
flowchart LR
    User["User / Human Decision"] --> UI["React + Vite UI"]
    UI --> API["FastAPI Backend"]
    API --> DB["PostgreSQL Runtime"]
  API -. "test only" .-> TestDB["PostgreSQL Test DB"]

    API -. "future" .-> Gmail["Gmail API + OAuth"]
    API -. "future" .-> AI["Bounded AI Classifier"]
    AI -. "suggestions only" .-> API
    API --> UI
```

The frontend is the user decision surface for reviewing candidates and recording explicit decisions.

The backend is the classification, workflow, and persistence layer for the ALPHA slice.

The current classifier is deterministic and local. A future AI-backed classifier can replace it without becoming the final authority.

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
- Future integrations: Gmail API, Google OAuth, bounded AI classifier

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

The frontend starts on `http://localhost:5173` by default.

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

Runtime schema changes should flow through Alembic. SQLite is no longer a supported database for SANE runtime or DB-integrated backend tests. The old `backend/sane_alpha.db` file, if present, should be treated as a disposable legacy artifact rather than an authoritative database.

Backend pytest now requires a separate PostgreSQL test database via `SANE_TEST_DATABASE_URL`. That database must already exist, must differ from `SANE_DATABASE_URL`, and its database name must include `test`.

Before backend tests run, the pytest fixture applies `alembic upgrade head` to the test database and then truncates SANE app tables with `RESTART IDENTITY CASCADE` between tests so IDs and row state reset deterministically without dropping the database.

Run backend tests:

```bash
cd backend
pytest
```

The backend exposes a health endpoint at `http://localhost:8000/api/health`.

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

- `GET /api/sources`
- `POST /api/decisions`
- `POST /api/decisions/batch`
- `GET /api/decisions`

## Current Scope

- Stage 1 review workflow for demo candidates: review, decide, and preserve processed state
- Backend candidate listing and decision recording endpoints
- PostgreSQL-backed runtime persistence through `SANE_DATABASE_URL`
- PostgreSQL-backed backend persistence/API tests through `SANE_TEST_DATABASE_URL`
- Local ALPHA user ownership for sources and decisions without requiring real login yet
- Deterministic classifier suggestions that remain subordinate to explicit human approval
- Frontend loading, error, and processed-history states
- No live email data or external email actions are executed yet

## Deferred Work

- Gmail OAuth and Gmail API integration
- Candidate ingestion and normalization
- AI classification module
- Human-approved action execution
- Subscription tiers, billing, GTD workflow, and multi-account support
