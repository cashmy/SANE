# SANE

Initial scaffold for the SANE Stage 1 execution workspace.

This scaffold keeps the project split into a React frontend and a FastAPI backend while deferring Gmail, OAuth, AI classification, and email actions until later slices.

## Structure

```text
SANE/
  docs/
  frontend/
  backend/
  README.md
```

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
uvicorn app.main:app --reload
```

The default SQLite path is resolved from the backend directory, so copying `.env.example` is safe without setting a database URL immediately.

Run backend tests:

```bash
cd backend
pytest
```

The backend exposes a health endpoint at `http://localhost:8000/api/health`.

## Current Scope

- Stage 1 placeholder workflow: Connect -> Review Candidates -> Decide -> Complete
- Backend health endpoint and environment-based configuration
- SQLite-ready SQLAlchemy session wiring for ALPHA
- Frontend and backend test scaffolds

## Deferred Work

- Gmail OAuth and Gmail API integration
- Candidate ingestion and normalization
- AI classification module
- Human-approved action execution
- Alembic migrations and production deployment concerns