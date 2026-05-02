# Prompt 06 - A25 Visible UI Refinement Pass

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this bounded repair prompt.

## Required Context

Before proposing or implementing changes, read only the execution-relevant context below.

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/SANE_UI_UX_Governance_Direction.md`
- `frontend/src/styles/theme.css`
- `frontend/src/App.css`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/views/ReviewView.tsx`
- `frontend/src/components/views/DecisionsView.tsx`
- `frontend/src/App.test.tsx`

Use `docs/sample_image.png` only as a density/layout reference. Do not copy its domain content or exact styling.

Do not read the full issue register unless the prompt or human explicitly asks you to. The full register is CORE/SKY governance memory, not the active BASE execution contract.

## Active Execution Context

The active task is A25 only.

### Active A25 Contract

Theme tokens are technically integrated, but components need visual tuning so the selected palette shapes the UI more intentionally and visible progress is legible to humans.

Make the current Stage 1 ALPHA UI visibly more intentional, polished, and operational without changing backend behavior or adding new product scope.

### Preserve Constraints From Prior Work

Preserve these existing Stage 1 contracts:

- the app is a local Stage 1 ALPHA email-source governance console
- the primary review unit is a source/vendor/cluster, not an individual email card
- source rows include sender emails, email counts, representative subject/reason, signal, suggested decision, and state
- decision labels are `Keep Source`, `Mark as Low Value`, and `Queue for Unsubscribe`
- decisions are human-confirmed and local-only
- no external email actions are executed
- pagination/page-size behavior exists and must remain visible
- batch decisions exist and must remain human-confirmed
- the Decisions view remains separate from Review
- light/dark theme toggle must keep working
- `Local ALPHA User` placeholder must remain visible

### Out Of Scope / Do Not Touch

Do not modify:

- backend files
- database models
- API contracts
- service logic
- test fixtures outside the frontend unless a frontend test requires it
- `docs/Stage1_ALPHA_Review_Issue_Register.md`

Do not implement:

- Gmail OAuth
- Gmail API calls
- real unsubscribe/archive/delete actions
- PostgreSQL migration
- AI provider calls
- GTD workflow
- billing or subscriptions
- multi-account support
- charts/analytics dashboards

## Clarification Gate

Before executing implementation:

1. Summarize what you believe A25 requires.
2. List the frontend files you expect to touch.
3. State any assumptions that affect visual direction, layout behavior, or test expectations.
4. Ask clarifying questions if any ambiguity would affect implementation quality.
5. You must have human approval before executing the implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Issue Being Addressed

Address A25 only:

> Theme tokens are technically integrated, but components need visual tuning so the selected palette shapes the UI more intentionally and visible progress is legible to humans.

A29 is CORE/SKY process guidance, not a BASE implementation contract. Its implication for this pass is simply that visible UI improvement matters because human reviewers need to see progress.

## Goal

Make the current Stage 1 ALPHA UI visibly more intentional, polished, and operational without changing backend behavior or adding new product scope.

The app should still feel like a dense email-source governance console, not a marketing page, tutorial, generic dashboard, or decorative redesign.

## What To Improve

Refine the existing UI so the functional progress from previous passes is more visible:

- source review at scale
- pagination/page-size behavior
- selected row/batch action state
- email count as a prioritization signal
- current review state
- decision history/revision state
- local-only ALPHA safety boundary
- light/dark theme quality

Use the existing token system in `frontend/src/styles/theme.css`.

Make the selected palette visibly shape the interface through layout, emphasis, state, and hierarchy.

## Expected Frontend Direction

Prefer bounded improvements such as:

- stronger toolbar/app-shell hierarchy
- clearer active navigation and local user/status area
- more meaningful summary/KPI strip
- visually stronger email count treatment
- clearer selected-row state and batch action bar
- improved table density and scan rhythm
- better pagination visibility
- refined chips/buttons using existing semantic tokens
- clearer current vs revision state in Decisions
- polished light and dark mode consistency

You may add small presentational subcomponents if they reduce clutter.

You may adjust tests for changed labels/structure if behavior remains the same.

## Hard Scope Boundaries

Do not add:

- Gmail OAuth
- Gmail API calls
- real unsubscribe/archive/delete actions
- backend model changes
- backend API changes
- PostgreSQL migration
- AI provider calls
- GTD workflow
- billing or subscriptions
- multi-account support
- charts/analytics dashboards
- decorative hero sections
- large explanatory panels
- animation-heavy UI

Do not remove existing Stage 1 honesty that no external email actions are executed.

Do not make the page less dense.

Do not turn the table back into cards.

## Testing And Validation

Run:

```powershell
cd frontend
npm run test:run
npm run build
```

If you change behavior covered by tests, update tests meaningfully.

If changes are visual-only and tests do not need updates, say so explicitly.

Report:

- files changed
- what visual improvements were made
- whether A25 is resolved, partially resolved, or still needs SKY browser review
- test/build results
- any remaining visual risks

## Success Criteria

A25 is successful if:

- the UI visibly looks more intentional than the current tokenized-but-flat pass
- pagination and scale handling are easier to notice
- email counts are easier to scan as prioritization signals
- batch selection/action state is clearer
- Decisions view better communicates current vs revision history
- light/dark modes both feel deliberate
- no Stage 1 scope boundaries are violated
- frontend tests and build pass
