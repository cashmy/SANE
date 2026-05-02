# SANE BASE Context and Guardrails

## Role

This workspace is the BASE execution workspace for SANE.

BASE is responsible for implementation, testing, and reporting reality contact back to CORE/SKY.

BASE does not define product intent, expand scope, or make final architectural decisions.

---

## Governing Frame

SANE is a real-world RBA-developed application for inbound email governance.

The core Stage 1 loop is:

```text
Identify -> Decide -> Act -> Complete
```

Stage 1 focuses on helping a user identify likely low-value inbound email, make rapid human-confirmed decisions, and preserve processed state.

SANE is not an email client, not a general productivity system, and not a passive filtering tool.

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
- PostgreSQL migration path for publication
- Alembic when schema evolution becomes meaningful

Integration:

- Gmail API
- Google OAuth

AI Layer:

- bounded backend classifier module
- AI may classify, suggest, and explain candidates
- AI must not take autonomous email actions

Testing:

- pytest for backend
- Vitest for frontend
- Playwright later for end-to-end workflow validation

---

## Stage 1 Guardrails

- Do not build a full email client.
- Do not replace Gmail.
- Do not add multi-folder productivity workflows.
- Do not add GTD workflow in Stage 1.
- Do not add advanced personalization, analytics, scoring, or dashboards.
- Do not automate unsubscribe, archive, delete, or destructive actions without explicit human approval.
- Do not make AI the final authority.
- Keep implementation slices small and testable.

---

## First Implementation Direction

The first meaningful implementation should prove the smallest useful slice:

```text
connect to Gmail
ingest a bounded message set
normalize candidate data
classify likely low-value sources
present candidates for human decision
record decisions locally
```

Unsubscribe or archival execution should come after the decision surface and trust model are validated.

---

## Reporting Back

BASE should report:

- what was implemented
- what assumptions were made
- what friction appeared
- what tests were run
- what needs CORE/SKY decision

