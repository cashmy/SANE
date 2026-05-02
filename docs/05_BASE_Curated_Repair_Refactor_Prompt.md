# BASE Prompt 05 - Curated Repair Refactor

## Role

You are the BASE coding LLM for SANE.

This pass should be performed with a strong coding/reasoning model.

Your task is to execute the curated Stage 1 ALPHA repair refactor.

Do not treat this as open-ended product generation.

You are repairing and extending the current ALPHA candidate according to the curated issue register.

---

## Required Reading

Before coding, read:

```text
docs/RBA_HOMSP_BASE_Primer.md
docs/00_BASE_Context_and_Guardrails.md
docs/SANE_UI_UX_Governance_Direction.md
docs/Stage1_ALPHA_Review_Issue_Register.md
```

Also inspect the current frontend and backend implementation before deciding your approach.

---

## Clarification Gate

Before coding, provide a brief implementation plan.

Your plan must include:

- which issues you intend to address
- what files/modules you expect to change
- whether backend schema/API changes are needed
- whether frontend behavior changes are needed
- what tests you will add/update
- any assumptions that affect product meaning, data model, workflow, or user-facing language

Stop and ask clarifying questions before implementation if any assumption affects:

- source/vendor/cluster modeling
- decision revision semantics
- pagination/page-size behavior
- batch decision behavior
- user/account ownership
- display mode behavior
- external email action boundaries
- deferred Gmail/OAuth/AI/billing/GTD/multi-account scope

Do not treat reporting assumptions after implementation as a substitute for pre-coding clarification.

If all assumptions are local implementation details and do not affect product meaning, proceed after the plan.

You must have human approval before executing the implementation.

---

## Target Issues

Address these curated items from the issue register.

### A1 - Source/Vendor/Cluster Review Unit

Move the Stage 1 model and UI toward source/vendor/cluster review units rather than individual message units.

The current backend data is message-shaped, but the review unit should be source-like.

Requirements:

- introduce or adapt a source/cluster-like model shape for ALPHA
- preserve representative message information where useful
- do not assume one sender email always equals one source
- keep this simple enough for ALPHA

### A22 - Email Count

Add email count per source/vendor/cluster.

The Review table should display this count.

For demo data, use realistic seeded counts.

### A16 - Pagination / Page Size

Add pagination/page-size behavior before any real data use.

This is non-negotiable.

Requirements:

- backend API should support page/page size or equivalent limit/offset behavior
- response should include enough metadata for frontend pagination
- frontend Review table should expose page-size and page navigation
- do not rely only on client-side filtering

### A2 - Decision Vocabulary

Use approved human-facing labels:

```text
Keep Source
Mark as Low Value
Queue for Unsubscribe
```

Backend enum values may remain stable unless there is a strong reason to change them.

### A5 - Decision Revision

Support explicit decision revision/correction.

Requirements:

- avoid accidental duplicate decisions from repeated clicks
- allow the user to change/reconsider a previous decision explicitly
- preserve enough history to understand that a revision happened
- keep the implementation bounded for ALPHA

### A23 - Multi-Select / Batch Decisions

Add multi-select / batch decision support before real high-volume ALPHA.

Requirements:

- user can select multiple sources/rows
- user can apply one decision to selected rows
- human confirmation required
- no external batch unsubscribe/archive/delete execution
- batch action only updates SANE local state

### A20 - User / Account Placeholder

Add a visible user/account placeholder now.

Requirements:

- app shell should show something like `Local ALPHA User`
- do not implement real auth
- do not implement OAuth
- do not implement user persistence yet unless needed for local placeholder only

### A15 - Dead Code Cleanup

Remove `WorkflowBoard.tsx` and any other dead code created by immediate refactors.

Do not preserve unused UI code at this early stage.

### A14 - Frontend Test Warnings

Fix React `act(...)` warnings if they are caused by how tests are written.

If the warning is caused by a third-party/version issue, document that clearly.

### A6 - ALPHA / Demo Reset Procedure

Create a documented ancillary reset procedure.

Preferred file:

```text
docs/ALPHA_Reset_Procedure.md
```

Do not add an in-app reset button.

### A25 - Component-Level Theme Tuning

Theme tokens exist, but component-level visual integration may need refinement.

Make small, focused tuning improvements only if they are clearly needed while touching the relevant components.

Do not redesign the whole UI again.

---

## Do Not Address In This Pass

Do not implement:

- Gmail OAuth
- Gmail API access
- real unsubscribe/archive/delete actions
- external AI provider calls
- GTD workflow
- billing or subscription enforcement
- multi-account support
- analytics dashboards
- real user login
- production deployment

Do not add bulk external actions.

Do not add advanced scoring/confidence display.

Do not implement full per-message exception handling yet.

Do not implement revision-history cleanup/compaction yet unless it is trivial and clearly isolated. A24 is decided but can remain later.

---

## Expected Architecture Direction

Keep the architecture clear:

```text
models -> schemas -> services -> routers -> frontend API client -> UI views
```

If schema changes are needed, keep them SQLite-compatible and simple.

Alembic migrations are still deferred unless absolutely necessary.

If changing existing tables in a way that conflicts with local ALPHA data, document reset steps rather than overbuilding migration handling.

---

## Testing Requirements

Update tests with the implementation.

Expected coverage:

Backend:

- source/cluster listing includes email count
- pagination metadata is returned
- page size limits are respected
- single decision recording still works
- decision revision works explicitly
- batch decisions require confirmation and do not execute external actions

Frontend:

- Review table shows email count
- pagination/page-size controls render and change API calls or displayed data appropriately
- approved decision labels render
- multi-select batch decision flow requires user action/confirmation
- user/account placeholder renders
- dark/light toggle still works
- no React `act(...)` warnings from test-authored async behavior

Run:

```bash
cd backend
python -m pytest

cd frontend
npm run test:run
npm run build
```

---

## Reporting Back

Report:

- clarification gate summary
- issues addressed
- files changed
- backend schema/API changes
- frontend behavior changes
- tests added/updated
- validation commands and results
- assumptions made
- items intentionally deferred
- any remaining risks or questions for CORE/SKY

