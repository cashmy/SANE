# Stage 1 ALPHA Review Issue Register

## Purpose

This is the project-facing issue register for the Stage 1 ALPHA candidate.

It tracks practical development issues that need SKY decision, CORE analysis, or BASE repair.

The fuller RBA/process version lives in the SANE-RBA artifact set.

---

## Current Validation

CORE re-ran validation after BASE implementation.

```text
backend: python -m pytest -> 8 passed
frontend: npm run test:run -> 5 passed
frontend: npm run build -> passed
```

---

## Current Strengths

- Stage 1 workflow is functional with local/demo data.
- Backend supports listing candidates, recording decisions, and listing decisions.
- Frontend supports candidate review, decision controls, history, loading state, and error state.
- External email actions are explicitly not executed.
- Tests protect governance behaviors, not only rendering.
- Implementation remains inside Stage 1 boundaries.

---

## Open Issues

| ID | Category | Layer | Issue | Status |
|---|---|---|---|---|
| A1 | SKY Decision | Product/Data Model | Candidates should move toward source/vendor/cluster review units, not individual message units. A source may contain one sender address or multiple related sender addresses/categories depending on reality. | Decided |
| A2 | SKY Decision | Product Language | Use human-facing decision vocabulary: Keep Source, Mark as Low Value, Queue for Unsubscribe. | Decided |
| A3 | Deferred Decision | Frontend/AI Trust | Do not display confidence/scoring in ALPHA. Keep scoring/confidence optional/provisional in data model and revisit in Tier 2/3 with stronger classifier design. | Decided |
| A4 | Deferred Decision | Backend/Test | Current CRUD/API/service tests are acceptable for ALPHA. Improve test DB isolation later before CI/CD, auth, Gmail integration hardening, or larger persistence complexity. | Decided |
| A5 | SKY Decision | Backend/Workflow | Support explicit decision revision with history. Avoid accidental duplicates, but allow user correction/reconsideration. | Decided |
| A6 | Ancillary Procedure | Dev/Test UX | Create documented ALPHA/demo reset procedure; do not add in-app reset control for now. | Decided |
| A7 | Ongoing Review | Frontend/UX | Browser-level UI/workflow review is an ongoing cyclic ALPHA validation step after each meaningful BASE pass. | Ongoing |
| A8 | Umbrella Scale Issue | Product/Data Model/UX | Resolved when A1 source/vendor/cluster rows, A22 email count, and A16 pagination/page-size behavior are implemented. | Dependent |
| A9 | Resolved for ALPHA | Frontend/UX | Previous decisions/history moved to a separate Decisions view. | Resolved |
| A10 | Resolved for ALPHA | Process/UI Design | UI design direction artifact created and copied into project-local docs. | Resolved |
| A11 | Resolved for ALPHA | Frontend/Visual Design | Visual style refactored toward operational console. | Resolved |
| A12 | Resolved for ALPHA | Frontend/Navigation | Sidebar navigation added with Review, Decisions, Connections, and Settings views. | Resolved |
| A13 | Must Fix Now | Process/Handoff | BASE cannot access external CORE/RBA workspace paths; required governance artifacts must live in project-local docs or be embedded in prompts. | Resolved |
| A14 | Fix Before ALPHA | Frontend/Test | React `act(...)` warnings should be examined and fixed if caused by test implementation. Third-party/version-caused warnings may be documented separately. | Decided |
| A15 | Fix Before ALPHA | Frontend/Cleanup | Remove `WorkflowBoard.tsx` and any other dead code from immediate refactors. No preservation value at this early stage. | Decided |
| A16 | Must Fix Before Real Data | Frontend/Backend Contract | Add pagination/page-size behavior before ALPHA with real data and before using real data. Filtering alone is not sufficient. | Decided |
| A17 | Must Fix Now | Process/Governance | BASE reported assumptions after implementation instead of asking clarifying questions before coding; strengthened prompt now produced a pre-coding clarification summary. Still needs validation when ambiguity requires stopping to ask. | Partially Validated |
| A18 | SKY Decision | Frontend/Display Mode | Light/dark mode toggle added with localStorage persistence and document-level `data-theme`. | Resolved |
| A19 | Must Fix Now | Frontend/UI Governance | Theme/color token system added with raw palette scales and semantic SANE tokens. | Resolved |
| A20 | Fix Before ALPHA | Frontend/Auth Readiness | Add user/account placeholder now; real auth/user persistence comes with OAuth/subscription work later. | Decided |
| A21 | Positive Finding | Frontend/Error Handling | When backend server crashed, frontend handled failure gracefully and displayed `Failed to fetch`. | Observed |
| A22 | SKY Decision | Product/Data Model/UX | Add email count per source/vendor/cluster. Count is a high-value signal because it communicates scale and prioritization. | Decided |
| A23 | SKY Decision | Frontend/Workflow | Add multi-select / batch decision support before real high-volume ALPHA, with human confirmation and no external batch execution. | Decided |
| A24 | SKY Decision | Backend/Workflow Lifecycle | Add a way to clear or compact revision history past a selected point so decision history does not become its own clutter source. | Decided |
| A25 | Should Fix Before ALPHA | Frontend/Visual Design | Theme tokens are technically integrated, but components need visual tuning so the selected palette shapes the UI more intentionally. | Open |

---

## SKY UI Review Notes

Initial browser review found that the app is functionally successful, but the current UI will not scale to the real SANE problem.

Known volume context:

- approximately 27,000 Gmail Promotions emails
- approximately 28,500 Gmail Updates emails

Implication:

- the main review surface should likely summarize vendors/sources/clusters rather than display individual email cards
- previous decisions/history likely belongs in a separate view
- future frontend work needs explicit UI design direction before repair generation

---

## UI Refactor Result

Prompt 03 refactored the UI into an operational app shell.

Current result:

- persistent sidebar
- Review / Decisions / Connections / Settings views
- compact KPI cards
- source review table
- search and filters
- separate Decisions history table
- external actions still shown as not executed

Validation after refactor:

```text
frontend: npm run test:run -> 8 passed, with React act(...) warnings
frontend: npm run build -> passed
backend: python -m pytest -> 8 passed
```

Remaining project-facing concerns:

- pagination/page-size support is still missing
- current source rows are still backed by message-shaped demo data
- action controls may need density refinement after pagination/grouping decisions
- test warnings should be cleaned up
- dead `WorkflowBoard.tsx` should be removed or archived
- future prompts need a stronger clarification gate before coding
- SANE-specific UI docs need explicit palette decisions
- app shell may need a future user/account placeholder
- source rows should include an email count field once grouping/ingestion is defined
- theme tokens are in place, but component-level visual integration may need refinement

Positive finding:

- frontend handled backend crash gracefully by displaying `Failed to fetch`

---

## Curation Decisions

### A1 - Candidate Review Unit

Decision:

SANE should review source/vendor/cluster units rather than individual email messages as the primary workflow object.

Rationale:

- the real problem exists at high volume
- users need to prioritize sources that generate accumulated noise
- source-level review better supports rapid decision-making
- individual messages can still appear as supporting examples/details

Caveat:

One vendor/source may map to:

- one sender address
- multiple related sender addresses
- one Gmail category
- multiple Gmail categories

The model should not assume a perfect one-email-address-to-one-source relationship.

### A22 - Email Count

Decision:

Add email count as a source/vendor/cluster field.

Rationale:

Email count is a high-value prioritization signal. It helps the user understand why a source matters and supports the core SANE goal of reducing accumulated low-value email noise.

Future source rows should include something like:

```text
Source | Sender(s) | Email Count | Category | Signal | Suggested Action | State | Actions
```

### A2 - Decision Vocabulary

Decision:

Use the following human-facing decision labels:

```text
Keep Source
Mark as Low Value
Queue for Unsubscribe
```

Rationale:

- `Keep Source` makes clear the user is preserving the source/vendor for now.
- `Mark as Low Value` describes the user's classification decision.
- `Queue for Unsubscribe` records intent without implying that an external unsubscribe action has already executed.

Implementation note:

The backend enum values may remain stable initially:

```text
keep_for_now
mark_low_value
unsubscribe_later
```

but the UI should display the approved human-facing labels.

### A3 - Confidence / Scoring Display

Decision:

Defer confidence/scoring display for ALPHA.

Rationale:

- confidence percentages can make a mock or early classifier appear more authoritative than intended
- quality scoring will require real thought, real data, and better AI/classifier prompting
- the UI refactor already removed the confidence percentage from the main table

Implementation note:

Keeping an optional/provisional data field is acceptable to reduce later refactor friction, but no ALPHA behavior should depend on it.

Revisit in Tier 2/3.

### A4 - Test Database Isolation

Decision:

Defer per-test database isolation improvement.

Rationale:

- current backend tests already exercise CRUD/API/service behavior
- current shared table reset approach is acceptable for ALPHA
- stronger isolation becomes more important before CI/CD, auth, Gmail integration hardening, or larger persistence complexity

This is not a current blocker.

### A5 - Decision Revision

Decision:

SANE must support explicit decision revision/correction.

Rationale:

- users can make accidental decisions
- source/vendor evaluation may change after inspecting representative messages
- a source may contain mostly low-value emails while still having occasional relevant items

Model direction:

```text
current source decision state
decision revision/history events
explicit user action to change/reconsider
```

Avoid:

- accidental duplicate decisions from repeated clicks
- silent overwriting with no trace

Deferred:

- per-message exceptions within a source/cluster

### A24 - Revision History Cleanup

Decision needed:

SANE should include a human-controlled way to clear, compact, or archive revision history past a selected point.

Rationale:

Revision history is useful for correction and audit, but it can become clutter if every correction remains visible indefinitely.

Possible future options:

- clear history older than a selected date
- keep latest decision only and archive older revisions
- compact revisions into a summary count
- clear history for a specific source/vendor
- preserve full history internally but hide older entries by default

Guardrail:

History cleanup should never execute external email actions. It only affects SANE's local decision history/visibility.

### A6 - ALPHA / Demo Reset Procedure

Decision:

Create a documented ancillary reset procedure rather than an integrated UI reset control.

Rationale:

- reset behavior is useful for development, testing, and future live demos
- it does not need to be part of the product UI
- adding it to the UI could create clutter or imply normal-user functionality

Possible artifact:

```text
docs/ALPHA_Reset_Procedure.md
```

### A7 - Ongoing Browser Review

Decision:

Treat browser-level UI/workflow review as an ongoing cyclic validation step.

This is not a closable defect.

Expected loop:

```text
BASE pass -> run app -> SKY UI/workflow review -> append findings -> curate -> repair prompt
```

### A8 - Review Surface Scale

Decision:

A8 is the umbrella scale issue.

It is considered resolved only when the concrete scale requirements are implemented:

- A1 source/vendor/cluster primary review unit
- A22 email count per source/vendor/cluster
- A16 pagination/page-size behavior

### A16 - Pagination / Page Size

Decision:

Pagination or page-size behavior is non-negotiable.

It must be implemented before ALPHA with real data and before using real data.

Rationale:

The known real-world email volume is too high for unpaginated review surfaces.

### A14 - Frontend Test Warnings

Decision:

Fix the React `act(...)` warnings if they are caused by how the tests are written.

Rationale:

- warnings can be ignored only with sufficient knowledge of their source
- if warnings are caused by test structure, the test should be corrected
- if warnings are caused by third-party version incompatibility, document that separately

### A15 - Dead Code Removal

Decision:

Remove `WorkflowBoard.tsx` and any other dead code from the immediate UI refactor.

Rationale:

At this early stage, there is no value in preserving dead UI code after a large AI-assisted refactor.

Git history will preserve prior states once version control is initialized.

### A17 - Clarification Gate

Decision:

Move to partially validated.

Rationale:

The BASE prompt was strengthened to require reading local governance docs and to ask clarifying questions rather than guessing.

In the theme/color pass, BASE produced a clarification gate summary before coding:

- found the generated color CSS files
- identified light/dark selectors
- checked variable naming/collision risk
- confirmed files were not imported
- stated a merge strategy

This validates improvement in the process.

Remaining validation:

We have not yet observed whether BASE will stop and ask when ambiguity is genuinely blocking.

### A18 - Display Mode

Decision:

Resolved.

Rationale:

ALPHA is expected to move quickly toward Tier 1. In a manual coding process, deferring display mode may be a reasonable cost-saving decision. In this AI-assisted / AI-injected context, the implementation cost is lower and deferral provides less value.

Implementation direction:

- include light/dark mode support
- make the control visible in the app shell or Settings
- preserve the operational console style in both modes

Implementation result:

- `ThemeToggle.tsx` added
- toggle is visible in the toolbar
- `data-theme` is applied to `documentElement`
- user choice persists to `localStorage`

### A19 - Color Token System

Decision:

Resolved technically.

Implementation result:

- generated Radix color CSS was merged into `frontend/src/styles/theme.css`
- raw light/dark blue and gray scales are present
- semantic SANE tokens are defined
- `App.css` and `index.css` now use semantic tokens
- source color CSS files were removed
- no Radix package dependency was added

Validation:

```text
frontend: npm run test:run -> 9 passed, with existing act(...) warnings
frontend: npm run build -> passed
```

Follow-up:

The token system exists, but component-level visual design may still need refinement. Track that separately as A25.

### A20 - User / Account Placeholder

Decision:

Add a user/account placeholder now.

Rationale:

OAuth, user-specific settings, display-mode preferences, decisions, connected email accounts, subscription tier, and future multi-account support all require a user/account ownership concept.

Implementation direction for now:

- add a visible app-shell user/account placeholder such as `Local ALPHA User`
- do not implement real login yet
- do not implement OAuth yet
- do not implement subscription/account persistence yet

### A21 - Backend Crash Error Handling

Observation:

When the backend server crashed, the frontend handled failure gracefully by displaying `Failed to fetch`.

This is a positive implementation observation.

It does not require refraction or repair by itself.

### A23 - Multi-Select / Batch Decisions

Decision:

Add multi-select / batch decision support before real high-volume ALPHA.

Rationale:

High-volume source review requires efficient multi-item handling. This is becoming standard operating behavior across many modern apps.

Guardrails:

- batch decisions must require human confirmation
- batch decisions must only update local SANE state at this stage
- no external batch unsubscribe/archive/delete execution
- avoid hidden or accidental bulk action behavior

### A24 - Revision History Cleanup

Decision:

Add a way to clear, compact, archive, or hide revision history past a selected point.

Rationale:

Revision history supports correction and audit, but it can become its own clutter source.

Guardrail:

History cleanup affects SANE local decision history/visibility only. It must not execute external email actions.

---

## Deferred Scope Guardrails

Do not add these while resolving the issues above:

- Gmail OAuth
- Gmail API access
- real unsubscribe/archive/delete actions
- external AI provider calls
- GTD workflow
- billing or subscription enforcement
- multi-account support
- dashboards or analytics

---

## Repair Planning Notes

Repair prompts should be created only after SKY curates the open issues.

Each repair pass should:

- address selected issues only
- preserve Stage 1 boundaries
- include tests when behavior changes
- report changed files and validation results
