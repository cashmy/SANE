# Prompt 08d - Authenticated Empty-State UX

## Status

Execute after Prompt 08c if local-dev UI review is available and the app needs first-run/authenticated empty-state polish before live OAuth reality contact.

This is a narrow frontend-focused polish prompt.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this Prompt 08d UX polish pass.

## Active Execution Context

Active task:

- A46 - authenticated empty-state UX

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, only A46 plus A32/A33/A47/A48 guardrails
- `frontend/src/components/views/ReviewView.tsx`
- `frontend/src/components/views/DecisionsView.tsx`
- `frontend/src/components/views/ConnectionsView.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/services/api.ts`
- frontend types and tests
- backend source/decision/Gmail response shapes only if needed to understand empty states

## Clarification Gate

Before executing implementation:

1. Confirm Prompt 08b local-dev auth and Prompt 08c auth/status UI polish are present.
2. Summarize current empty-state behavior in Review and Decisions.
3. State which authenticated empty states you will add.
4. State whether any backend/API changes are required. Prefer no backend changes.
5. State how the empty states will guide users toward Connections without triggering scans.
6. State frontend files and tests you expect to change.
7. Ask clarifying questions if empty-state meaning, navigation, or Gmail connection status is ambiguous.
8. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Make authenticated first-run states clear and calm.

After Prompt 08, real signed-in users do not see Local ALPHA demo data. That is correct, but it can produce empty Review/Decisions surfaces until Gmail is connected and scanned.

The UI should explain the empty state without becoming a marketing page or expository tutorial.

## Required Empty States

Add clear empty states for:

```text
signed in but no Gmail connected
Gmail connected but no scan run
scan completed with no sources found
decisions empty because no source decisions exist yet
```

Use concise operational language.

Prefer action-oriented guidance:

- go to Connections
- connect Gmail
- run a bounded manual scan
- review sources after scan

Do not add large hero panels.

Do not add marketing copy.

## Navigation / Action Direction

If the app already has internal view switching available, empty-state actions may navigate to Connections.

If navigation wiring is not cleanly available, use a clear non-invasive message rather than overbuilding.

Do not trigger:

- Google sign-in
- Gmail connect
- Gmail scan

from rendering an empty state.

All actions must remain explicit user actions.

## Guardrails

Preserve:

- local-dev auth behavior
- Google OAuth behavior
- Gmail connect/disconnect behavior
- manual-only scan behavior
- no scan-on-render
- no external email actions
- no full email body storage
- source/decision API contracts

Do not change backend behavior unless there is no frontend-safe way to distinguish the required empty states.

If backend data is insufficient, stop and ask before adding API fields.

## Testing

Frontend tests should prove:

- authenticated user with no Gmail account sees a Review empty state that points to Connections
- Gmail-connected/no-scan state is clear if the existing API shape supports it
- scan-complete/no-sources state is clear if the existing API shape supports it
- Decisions empty state is clear
- rendering empty states does not trigger Gmail scan
- local-dev review flow still works

Backend tests are not expected unless backend files change.

## Validation

Run:

```powershell
cd frontend
npm run test:run
npm run build
```

Run backend tests only if backend files change:

```powershell
cd backend
python -m pytest
```

## Report

Report:

- files changed
- empty states added
- whether backend/API changes were needed
- tests added/updated
- validation results
- remaining first-run/live-OAuth UX risks before Prompt 09

