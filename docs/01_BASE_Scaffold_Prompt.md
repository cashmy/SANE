# BASE Prompt 01 - Scaffold SANE

## Role

You are the BASE coding LLM for SANE.

Your task is to create the initial project scaffold only.

Do not implement Gmail OAuth, Gmail API calls, AI classification, or real email actions yet unless explicitly requested in a later prompt.

---

## Product Context

SANE is a real-world RBA-developed application for inbound email governance.

The problem:

Modern email systems generate large volumes of low-value, subscription-based messages. Email clients categorize these messages, but categorization often hides accumulation rather than resolving it. Users avoid manual cleanup because it is too high-friction.

SANE exists to help users rapidly process inbound email as a decision stream.

The Stage 1 loop is:

```text
Identify -> Decide -> Act -> Complete
```

Stage 1 means:

- identify likely low-value email candidates
- present candidates to the user
- require human decision
- record the decision
- eventually support user-approved action

SANE is:

- a decision system for inbound email
- focused on restoring user control
- focused on reducing low-value email noise
- human-in-the-loop
- intended to become a subscription-based service after ALPHA validation

SANE is not:

- an email client
- a Gmail replacement
- a general productivity system
- a GTD system in Stage 1
- an autonomous unsubscribe bot
- an AI-embedded decision authority

---

## Product Tier Context

SANE is expected to evolve toward a three-tier subscription model.

Do not implement billing or tier enforcement during this scaffold.

The current working tier direction is:

- Tier 1: core email governance loop
- Tier 2: expanded GTD-aligned processing workflow
- Tier 3: multiple email accounts / advanced source governance

This matters for scaffolding because the project should avoid local-only assumptions.

It does not mean the first scaffold should include payment systems, subscription models, or multi-account features.

---

## Locked Tech Stack

Frontend:

- React
- Vite
- TypeScript

Backend:

- Python
- FastAPI

Data:

- SQLAlchemy 2.x
- Pydantic
- SQLite for ALPHA
- PostgreSQL migration path for publication / SaaS deployment
- Alembic later when schema evolution becomes meaningful

Testing:

- pytest for backend
- Vitest for frontend
- Playwright later, not now

Integration later:

- Gmail API
- Google OAuth
- bounded server-side AI classifier module

---

## Scaffold Requirements

Create a clear multi-tech project scaffold with separate frontend and backend areas.

Recommended structure:

```text
SANE/
  docs/
  frontend/
  backend/
  README.md
```

Frontend scaffold:

- Vite React TypeScript app
- simple initial app shell
- no real Gmail or AI calls yet
- include a placeholder screen that reflects the Stage 1 loop
- include basic test setup if Vite template supports it cleanly

Backend scaffold:

- FastAPI app
- health check endpoint
- minimal app structure with routers/services/models/schemas placeholders
- SQLAlchemy dependency setup prepared but not over-modeled
- SQLite local configuration
- pytest setup with a health check test
- `.env.example` for expected future configuration

Root:

- README describing how to run frontend and backend
- `.gitignore`
- keep generated dependencies and lock files appropriate to the package managers selected
- avoid hardcoded local-only assumptions where environment configuration is straightforward

---

## Backend Structure Guidance

Prefer a simple backend shape like:

```text
backend/
  app/
    main.py
    core/
      config.py
    db/
      session.py
      base.py
    models/
      __init__.py
    schemas/
      __init__.py
    routers/
      health.py
    services/
      __init__.py
  tests/
    test_health.py
  requirements.txt
  .env.example
```

Do not create a large domain model yet.

If you add a placeholder model, keep it explicitly provisional.

Keep the backend ready for future production configuration by using environment-based settings for database URL and CORS origins.

---

## Frontend Structure Guidance

Prefer a simple frontend shape like:

```text
frontend/
  src/
    App.tsx
    main.tsx
    components/
    services/
    types/
```

The initial UI should be a functional placeholder, not a marketing landing page.

It should show the future workflow:

```text
Connect -> Review Candidates -> Decide -> Complete
```

Do not over-design the interface.

---

## Guardrails

- Do not build Gmail integration yet.
- Do not add OAuth yet.
- Do not add AI provider code yet.
- Do not create unsubscribe automation yet.
- Do not add GTD concepts.
- Do not add dashboards, scoring, analytics, or advanced personalization.
- Do not add billing, payment, Stripe, subscription enforcement, or tier-limit logic.
- Do not add multi-account support yet.
- Do not collapse the app into a generic unsubscribe tool.
- Keep the scaffold simple, inspectable, and easy for a human to review.

---

## Expected Output Back to CORE/SKY

After scaffolding, report:

- files and directories created
- package/runtime choices made
- commands to run frontend tests/backend tests
- commands to start frontend/backend dev servers
- any assumptions made
- any blockers or questions
