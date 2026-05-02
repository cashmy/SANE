# BASE Prompt 02 - Stage 1 ALPHA Candidate Generation

## Role

You are the BASE coding LLM for SANE.

Your task is to generate a Stage 1 ALPHA candidate from the existing scaffold.

This is a larger implementation pass, but it is still bounded.

Do not treat this as a finished product.

Treat the result as an ALPHA candidate that will be reviewed by CORE and validated by SKY through manual ALPHA testing.

Before implementing, read:

```text
docs/RBA_HOMSP_BASE_Primer.md
docs/00_BASE_Context_and_Guardrails.md
```

You are operating at the BASE layer:

- implement scoped work
- write and run tests
- report assumptions and friction
- do not redefine purpose or expand scope

---

## Product Frame

SANE is a human-governed inbound email decision system.

The core Stage 1 loop is:

```text
Identify -> Decide -> Act -> Complete
```

Stage 1 must help a user:

- review likely low-value email candidates
- make explicit decisions
- record those decisions
- preserve processed state

SANE is not an email client, not a Gmail replacement, not a GTD system in Stage 1, and not an autonomous unsubscribe bot.

---

## Implementation Boundary

Build a functional Stage 1 ALPHA candidate using local/demo data and local persistence.

Do not implement real Gmail OAuth or Gmail API access in this pass unless explicitly instructed later.

Do not implement real unsubscribe, archive, delete, or external email actions.

Use realistic mock/demo candidates to model the future Gmail ingestion output.

The goal is to prove the decision workflow before integrating external email systems.

---

## Required Functional Scope

### Backend

Implement:

- SQLAlchemy model(s) for Stage 1 candidate/decision persistence
- Pydantic schemas for API input/output
- demo candidate source or seed data
- API endpoint to list candidates
- API endpoint to record a human decision
- API endpoint to list recorded decisions or processed items
- clear service-layer functions for classification/decision workflow

Candidate data should include enough fields to support the UI:

- id
- sender/source name
- sender email or source identifier
- subject or representative message summary
- category or mailbox context
- reason/signal for why it is a candidate
- confidence or status only if implemented clearly and not over-weighted
- current processing state

Decisions should support at least:

- ignore / keep for now
- mark as low value
- unsubscribe later / action recommended

Do not execute actions externally.

### Frontend

Implement:

- candidate review screen
- candidate list/cards/table
- decision controls
- processed/decision history view
- loading/error states for API calls
- clear indication that no external email actions are executed yet

Keep the UI practical and workflow-focused.

Do not create a marketing landing page.

### AI / Classification Layer

Create a bounded classifier module using deterministic or mock logic for ALPHA.

This module may classify demo candidates or explain candidate reasons.

Do not call an external AI provider in this pass.

Design the module so it can later be replaced by an LLM-backed classifier.

---

## Testing Requirement

Generate the Stage 1 ALPHA candidate with tests created alongside implementation.

Tests are not optional.

Use tests to document expected behavior, protect the decision loop, and expose assumptions.

Do not write tests only for happy-path rendering.

Include tests that protect the SANE governance rules:

- human approval is required before a decision is recorded
- no autonomous external action is executed
- processed decisions are persisted
- ambiguous candidates remain reviewable
- candidate classification/suggestion does not become final authority
- Stage 1 does not introduce GTD workflow, billing, or multi-account behavior

### Expected Test Types

Backend:

- service/unit tests for candidate classification and decision recording
- API tests for candidate listing and decision creation/listing
- tests proving decisions are persisted locally
- tests proving external actions are not executed

Frontend:

- component tests for candidate display and decision controls
- tests for loading and error states where practical
- tests for API client behavior using mocked responses
- tests that user decision controls are required before processed state changes

End-to-end:

- do not add Playwright yet unless it is very small and does not destabilize the scaffold

---

## Data and Persistence

Use SQLite through the existing SQLAlchemy setup.

Do not add Alembic yet unless schema changes become difficult to manage without it.

Do not hardcode production-only assumptions.

Do not implement PostgreSQL in this pass.

Keep schema simple, but do not make it throwaway.

---

## Guardrails

Do not implement:

- Gmail OAuth
- Gmail API access
- real unsubscribe
- real archive/delete
- external AI provider calls
- GTD workflow
- billing or subscription enforcement
- multi-account support
- dashboards or analytics
- advanced personalization

Do not collapse SANE into a generic unsubscribe tool.

Do not let the UI imply actions are being executed externally.

---

## Reporting Back To CORE/SKY

After implementation, report:

- files changed
- features implemented
- tests added
- commands run and results
- assumptions made
- known weaknesses
- areas where typicality bias may have influenced design
- what still requires SKY validation

If you encounter ambiguity, implement the smallest coherent version and explicitly report the assumption.
