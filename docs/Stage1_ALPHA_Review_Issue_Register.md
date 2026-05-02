# Stage 1 ALPHA Review Issue Register

## Purpose

This is the project-facing issue register for the Stage 1 ALPHA candidate.

It tracks practical development issues that need SKY decision, CORE analysis, or BASE repair.

The fuller RBA/process version lives in the SANE-RBA artifact set.

---

## Current Validation

CORE re-ran validation after BASE implementation.

```text
backend: python -m pytest -> 15 passed
frontend: npm run test:run -> 10 passed
frontend: npm run build -> passed
```

Validation note:

- Frontend React `act(...)` warnings were removed.
- Backend validation currently emits a `pytest-asyncio` deprecation warning about unset `asyncio_default_fixture_loop_scope`; this is not the prior frontend test warning and should be tracked separately if backend test config is hardened.

---

## Current Strengths

- Stage 1 workflow is functional with local/demo source data.
- Backend supports paginated source listing, single decisions, batch decisions, and decision history.
- Frontend supports source review, source counts, decision controls, batch selection, history, loading state, and error state.
- External email actions are explicitly not executed.
- Tests protect governance behaviors, not only rendering.
- Implementation remains inside Stage 1 boundaries.

---

## Open Issues

| ID | Category | Layer | Issue | Status |
|---|---|---|---|---|
| A1 | SKY Decision | Product/Data Model | Candidates should move toward source/vendor/cluster review units, not individual message units. A source may contain one sender address or multiple related sender addresses/categories depending on reality. | Resolved for ALPHA |
| A2 | SKY Decision | Product Language | Use human-facing decision vocabulary: Keep Source, Mark as Low Value, Queue for Unsubscribe. | Resolved |
| A3 | Deferred Decision | Frontend/AI Trust | Do not display confidence/scoring in ALPHA. Keep scoring/confidence optional/provisional in data model and revisit in Tier 2/3 with stronger classifier design. | Resolved for ALPHA |
| A4 | Deferred Decision | Backend/Test | Current CRUD/API/service tests are acceptable for ALPHA. Improve test DB isolation later before CI/CD, auth, Gmail integration hardening, or larger persistence complexity. | Deferred |
| A5 | SKY Decision | Backend/Workflow | Support explicit decision revision with history. Avoid accidental duplicates, but allow user correction/reconsideration. | Resolved for ALPHA |
| A6 | Ancillary Procedure | Dev/Test UX | Create documented ALPHA/demo reset procedure; do not add in-app reset control for now. | Resolved |
| A7 | Ongoing Review | Frontend/UX | Browser-level UI/workflow review is an ongoing cyclic ALPHA validation step after each meaningful BASE pass. | Ongoing |
| A8 | Umbrella Scale Issue | Product/Data Model/UX | Resolved when A1 source/vendor/cluster rows, A22 email count, and A16 pagination/page-size behavior are implemented. | Resolved for ALPHA |
| A9 | Resolved for ALPHA | Frontend/UX | Previous decisions/history moved to a separate Decisions view. | Resolved |
| A10 | Resolved for ALPHA | Process/UI Design | UI design direction artifact created and copied into project-local docs. | Resolved |
| A11 | Resolved for ALPHA | Frontend/Visual Design | Visual style refactored toward operational console. | Resolved |
| A12 | Resolved for ALPHA | Frontend/Navigation | Sidebar navigation added with Review, Decisions, Connections, and Settings views. | Resolved |
| A13 | Must Fix Now | Process/Handoff | BASE cannot access external CORE/RBA workspace paths; required governance artifacts must live in project-local docs or be embedded in prompts. | Resolved |
| A14 | Fix Before ALPHA | Frontend/Test | React `act(...)` warnings should be examined and fixed if caused by test implementation. Third-party/version-caused warnings may be documented separately. | Resolved |
| A15 | Fix Before ALPHA | Frontend/Cleanup | Remove `WorkflowBoard.tsx` and any other dead code from immediate refactors. No preservation value at this early stage. | Resolved |
| A16 | Must Fix Before Real Data | Frontend/Backend Contract | Add pagination/page-size behavior before ALPHA with real data and before using real data. Filtering alone is not sufficient. | Resolved for ALPHA |
| A17 | Must Fix Now | Process/Governance | BASE reported assumptions after implementation instead of asking clarifying questions before coding; strengthened prompt now produced a pre-coding clarification summary and later surfaced blocking contract questions before implementation. | Validated |
| A18 | SKY Decision | Frontend/Display Mode | Light/dark mode toggle added with localStorage persistence and document-level `data-theme`. | Resolved |
| A19 | Must Fix Now | Frontend/UI Governance | Theme/color token system added with raw palette scales and semantic SANE tokens. | Resolved |
| A20 | Fix Before ALPHA | Frontend/Auth Readiness | Add user/account placeholder now; real auth/user persistence comes with OAuth/subscription work later. | Resolved for ALPHA |
| A21 | Positive Finding | Frontend/Error Handling | When backend server crashed, frontend handled failure gracefully and displayed `Failed to fetch`. | Observed |
| A22 | SKY Decision | Product/Data Model/UX | Add email count per source/vendor/cluster. Count is a high-value signal because it communicates scale and prioritization. | Resolved for ALPHA |
| A23 | SKY Decision | Frontend/Workflow | Add multi-select / batch decision support before real high-volume ALPHA, with human confirmation and no external batch execution. | Resolved for ALPHA |
| A24 | SKY Decision | Backend/Workflow Lifecycle | Add a way to clear or compact revision history past a selected point so decision history does not become its own clutter source. | Deferred |
| A25 | Must Fix Before ALPHA Review | Frontend/Visual Design | Theme tokens are technically integrated, but components need visual tuning so the selected palette shapes the UI more intentionally and visible progress is legible to humans. | Partially Resolved |
| A26 | Technical Debt | Backend/Data Model | Internal SQLAlchemy `Candidate` model/table name was retained to reduce ALPHA churn while API/UI/docs use source language. Rename to `Source`/`EmailSource` before the model hardens. | Open |
| A27 | Deferred Scale Risk | Backend/Search | Source search uses simple ALPHA-scale filtering, including casted SQLite JSON email search. Replace with a deliberate large-scale search/index strategy before real mailbox volume. | Open |
| A28 | Architecture Reconsideration | Backend/Database | SQLite-first may be a Native workforce default that creates unnecessary churn under AI-Injected compressed development. Reconsider starting or moving quickly to PostgreSQL. | Decided |
| A29 | RBA Recommendation | Process/UI Validation | Do not defer visible UI refinement solely because functionality works. Human reviewers often need visible change to perceive progress, trust the loop, and understand what changed. | Process Captured |
| A30 | Architecture Foundation | Backend/Database | Migrate from SQLite-first ALPHA persistence to PostgreSQL-ready persistence with migration support before Gmail/auth/subscription work hardens around SQLite. | Partially Resolved |
| A31 | Architecture Foundation | Backend/Auth Readiness | Add basic user/account ownership foundation so sources, decisions, settings, and future Gmail connections have a real owner. | Resolved for ALPHA |
| A32 | Gmail Governance | Integration/Workflow | Gmail scanning/importing/analyzing must never run merely because the app opens; ingestion must be user-requested or chrono-controlled. | Decided |
| A33 | Gmail Integration | Integration/API | Implement Gmail OAuth/API and bounded ingestion only after the database/user foundation is in place; first real-data contact should be limited by count and/or recency. | Deferred |
| A34 | Visual Identity | Frontend/Design System | Current palette may be too close to the original UI to produce the expected perceived visual change; consider a stronger SANE visual identity pass after architecture foundation. | Open |
| A35 | Architecture Risk | Backend/Data Model | `source_key` remains globally unique; future OAuth/multi-user work likely requires uniqueness scoped by user/account. | Open |
| A36 | Validation Gap | Backend/Database | PostgreSQL is configured and migration-ready, but live PostgreSQL migration/runtime validation has not yet been exercised. | Open |

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

Validated for this repair loop.

Rationale:

The BASE prompt was strengthened to require reading local governance docs, summarize assumptions before coding, and ask clarifying questions rather than guessing.

In the theme/color pass, BASE produced a clarification gate summary before coding:

- found the generated color CSS files
- identified light/dark selectors
- checked variable naming/collision risk
- confirmed files were not imported
- stated a merge strategy

The later curated repair pass strengthened this further:

- BASE surfaced blocking questions about source modeling and decision revision semantics before implementation.
- CORE corrected the issue register by adding explicit implementation contracts.
- SKY stopped/reoriented BASE before the partial implementation hardened.
- BASE reverted partial backend changes and replanned against the clarified contract.

This validates the clarification gate as an RBA governance mechanism, while still requiring continued use in future prompts.

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

### A25 - Visible UI Refinement

Decision:

Do not defer A25 merely because it does not affect backend correctness or app performance.

Rationale:

Technical progress and human-perceived progress are different.

Pagination, batch actions, source modeling, and backend decision semantics are substantial improvements, but many users, students, stakeholders, and ALPHA testers will not perceive that progress unless the interface visibly changes in a meaningful way.

The current pagination addition is functionally important but visually minimal. It may not register as progress unless the reviewer is specifically looking for pagination.

Recommendation:

After significant functional repair passes, include a bounded UI refinement pass when the visible surface does not yet communicate the improvement.

This is especially important for:

- stakeholder confidence
- student comprehension
- ALPHA tester trust
- product momentum
- showing that the app is becoming more real, not merely more correct internally

Guardrail:

Visible UI refinement should not become decorative drift. It should make the actual workflow state, scale, decisions, and user progress easier to see.

Implementation result:

Prompt 06b improved several component-level states:

- active navigation is clearer
- selected row state is clearer
- selected batch state is more visible
- email counts are more emphasized
- filter/search rhythm is cleaner
- table scan rhythm improved modestly

SKY review:

The result is better, but still not a decisive visual identity shift.

Likely reason:

The selected theme colors may be too close to the previous visual direction. BASE appears to have followed the rules, but the rules and palette did not create as much perceptual change as SKY expected.

Status:

Partially resolved. A25b improved visible workflow legibility, but a stronger visual identity/palette pass may be needed later if SANE needs a more distinct product feel.

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

### A26 - Internal Candidate Naming Debt

Decision:

Track as technical debt.

Rationale:

The ALPHA implementation retained the internal SQLAlchemy `Candidate` model/table name to avoid unnecessary churn during the repair pass.

This is acceptable for now because the external contract is source-oriented:

- `/api/sources`
- `source_id`
- `source_ids`
- source labels in UI
- source-oriented tests
- source-oriented project docs

Risk:

If this name remains too long, it may fossilize the older message/candidate concept and confuse future backend work.

Future action:

Rename internal persistence and service language toward `Source` or `EmailSource` before the data model hardens around Gmail ingestion, migrations, or publication.

### A27 - ALPHA Search / Indexing Risk

Decision:

Defer, but track before real mailbox volume.

Rationale:

The current SQLite search behavior is acceptable for seeded/demo ALPHA data.

It is not a final strategy for tens of thousands of real emails or source clusters.

Current risk:

- simple filtering
- casted JSON sender email search in SQLite
- no full-text index
- no source/domain search strategy

Future action:

Design the large-scale search/indexing approach before real Gmail ingestion is used against the full mailbox volume.

### A28 - SQLite vs PostgreSQL Under AI-Injected Compression

Decision:

Move SANE toward PostgreSQL sooner rather than later.

Observation:

SQLite made sense under a Native workforce model because it reduces setup friction during a longer early ALPHA period.

In the current RBA/HOMSP AI-assisted workflow, the ALPHA interval is brief because build-review-repair cycles are compressed into minutes. That reduces the practical value of a temporary database choice.

Risk:

The SQLite-first decision may create more friction than it saves:

- different behavior from the publication database
- migration churn
- JSON/search differences
- less realistic deployment preparation
- educational confusion if students see SQLite introduced and quickly replaced

Possible bias:

This may reflect training-model typicality bias: choosing SQLite because it is a common prototype default rather than because it is optimal for this AI-Injected development context.

Future action:

Create a focused PostgreSQL migration prompt before Gmail ingestion or real mailbox testing.

For future RBA app projects, evaluate database choice against expected AI-compressed ALPHA duration rather than using SQLite as the automatic default.

### A29 - Do Not Over-Defer UI Changes

Recommendation:

Do not automatically defer UI/visual refinement just because the app is technically functional.

Rationale:

In AI-assisted development, large internal changes can happen quickly and invisibly:

- backend model repair
- API contract improvements
- pagination
- decision revision semantics
- batch operation rules
- test expansion

These changes matter, but they may not be legible to a human reviewer from the screen.

Human progress perception often requires visible evidence.

Implication:

For user-facing apps, RBA repair planning should distinguish:

- functional correctness
- architectural correctness
- visible experiential progress

A repair loop that only improves invisible internals may be technically successful while feeling stagnant to a human observer.

Future prompt guidance:

When a repair pass makes important workflow changes, ask BASE to also make bounded visual changes that help the user see those changes, without adding new scope or decorative clutter.

Implementation note:

A29 is not a BASE implementation contract by itself.

It is a CORE/SKY process recommendation that informs when a UI refinement pass should be created. The actionable BASE work for the current SANE pass is A25.

### A30 - PostgreSQL Persistence Foundation

Decision:

Implement PostgreSQL-ready persistence as the next architecture foundation pass.

Rationale:

SANE is moving quickly from ALPHA into Tier 1/publication-shaped architecture. Under high AI-assisted development compression, the SQLite-only interval is too brief to justify carrying SQLite-specific assumptions forward.

Scope direction:

- support PostgreSQL as the intended development/publication database
- introduce or formalize migration support
- preserve local development ergonomics
- keep tests passing
- avoid Gmail/OAuth/API work in this pass

Guardrail:

This is a persistence foundation pass, not a product-expansion pass.

Implementation result:

Prompt 07 added PostgreSQL-ready configuration, Alembic migration support, PostgreSQL driver dependency, and a formal initial migration.

Validation:

- backend tests passed
- frontend regression tests/build passed
- Alembic path was exercised against a fresh SQLite file

Remaining gap:

Live PostgreSQL was not exercised in the current environment. A30 is therefore partially resolved rather than fully resolved.

### A31 - Basic User / Account Ownership Foundation

Decision:

Add a basic user/account ownership model in the same foundation pass as PostgreSQL.

Rationale:

Tier 1 requires user-owned settings, decisions, connected email accounts, subscription/account readiness, and OAuth ownership boundaries.

SANE should stop behaving internally like a single anonymous local workflow before Gmail/OAuth lands.

Scope direction:

- add a basic user/account model
- associate sources and decisions with a user/account
- keep a local ALPHA user seed/default path so existing local workflows still run
- preserve the visible `Local ALPHA User` concept until real authentication is implemented
- prepare for future OAuth without implementing live OAuth

Guardrail:

Do not implement full authentication, billing, subscriptions, or Gmail OAuth in this pass.

Implementation result:

Prompt 07 added a basic `User` model and local ALPHA user resolution.

Sources and decisions now have internal `user_id` ownership while the existing API contract remains unchanged.

Status:

Resolved for ALPHA.

### A32 - Gmail Ingestion Trigger Governance

Decision:

Gmail scanning/importing/analyzing must never run simply because the app opens.

Rationale:

Gmail access is not just an API call. It is a controlled ingestion workflow with privacy, trust, rate-limit, and user-intent implications.

Allowed future triggers:

- explicit user-requested scan
- scheduled/chrono-controlled scan
- bounded ALPHA/test scan

Not allowed:

- automatic scan/import/analyze on app load
- hidden background Gmail access without user intent or configured schedule

Future model direction:

Add an ingestion run concept when Gmail work begins.

Potential fields:

- `user_id`
- `gmail_connection_id`
- `trigger_type`: manual, scheduled, alpha_test
- `scope`
- `limit_count`
- `lookback_window`
- `started_at`
- `completed_at`
- `status`
- `message_count_scanned`
- `source_count_created`
- `error_summary`

### A33 - Gmail OAuth / API / Bounded Ingestion

Decision:

Defer live Gmail OAuth/API implementation until after A30/A31 are complete.

Rationale:

Gmail integration introduces external auth, scopes, token storage, Google Cloud setup, rate limits, privacy concerns, and real mailbox data.

First real Gmail data contact should be bounded.

Initial ingestion direction:

- connect through OAuth
- use minimal necessary Gmail scopes
- allow explicit manual scan
- optionally prepare scheduled scan structure
- import a bounded recent sample, such as latest 50 messages, not the full mailbox
- normalize messages into source/vendor/cluster review rows
- never execute external unsubscribe/archive/delete actions

Guardrail:

No Gmail ingestion should occur on app open.

### A34 - SANE Visual Identity / Palette Differentiation

Decision:

Track as a future visual identity consideration.

Observation:

The A25b pass followed the extracted visual rules and produced a modestly better UI, but the perceived change remained smaller than expected.

Possible cause:

The selected palette may be too close to the original visual direction. If the color system does not create enough contrast from the prior UI, BASE can satisfy the visual rules while the human reviewer still experiences the result as only slightly changed.

Future action:

Consider a stronger SANE visual identity pass after the PostgreSQL/user foundation work, unless SKY decides the current restrained operational style is sufficient for ALPHA.

Guardrail:

Do not reopen broad UI redesign during the immediate architecture foundation pass unless the UI blocks ALPHA review.

### A35 - User-Scoped Source Key

Decision:

Track before OAuth/multi-user hardening.

Observation:

Prompt 07 kept `source_key` globally unique to reduce ALPHA churn.

Risk:

In a real multi-user system, two users may have the same email source/vendor/source key. Global uniqueness would incorrectly prevent that.

Future action:

Before live OAuth or multi-user use, consider replacing the global unique constraint with a user-scoped unique constraint such as:

```text
unique(user_id, source_key)
```

Guardrail:

This does not need to block the current ALPHA local-user path, but it should not be forgotten before Gmail/account integration.

### A36 - Live PostgreSQL Validation

Decision:

Track as a validation gap.

Observation:

The codebase is now PostgreSQL-ready in configuration and migration structure, but validation was performed through SQLite-backed automated tests plus SQLite Alembic migration exercise.

Future action:

Run a live local PostgreSQL validation:

```powershell
SANE_DATABASE_URL=postgresql+psycopg://...
alembic upgrade head
python -m pytest
```

or a documented equivalent.

Status:

Open until a real PostgreSQL target has been exercised.

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

---

## Implementation Decision Contracts

This section translates curated SKY decisions into implementation-ready contracts for BASE.

These contracts reduce avoidable clarification questions while preserving the requirement that BASE stop and ask when true ambiguity remains.

### Contract A1 / A22 - ALPHA Source Review Unit

Decision:

For ALPHA, create an explicit source/vendor/cluster review model.

Do not infer real clustering logic yet.

ALPHA data contract:

Each source row should include:

- stable `source_key`
- display `source_name`
- one or more sender emails
- one or more Gmail/mailbox categories if useful
- `email_count`
- one representative message subject or summary
- candidate/source reason
- classifier/signal value
- suggested decision
- current processing/decision state

Behavior contract:

- The Review table row represents a source/vendor/cluster, not a single email message.
- Representative message fields may be shown as examples, but should not define the review unit.
- Multiple sender emails can belong to one source.
- Real source grouping/clustering can be refined later after Gmail ingestion exposes real patterns.

Deferred:

- real Gmail clustering
- domain-based inference
- per-message exceptions
- source merge/split tools

Test expectations:

- API returns source rows with email count.
- Source rows can contain multiple sender emails.
- UI displays email count.
- UI language does not imply the row is only one email message.

### Contract A5 / A23 - Decision Revision and Batch Decision Behavior

Decision:

Use a current-state plus append-only history model.

Behavior contract:

- latest decision wins for the current source state
- decision history remains append-only
- repeated identical decision is a no-op
- different decision appends a revision event
- explicit revision/correction is allowed
- batch decisions follow the same rules as single-source decisions
- batch decisions require human confirmation
- batch decisions do not execute external email actions

Data contract:

Each source should expose:

- current decision/state
- decision history entries or revision events
- enough timestamps/order fields to determine latest decision

Each decision event should include:

- source identifier
- decision value
- human confirmation
- external action status
- created/recorded timestamp
- optional note if already supported
- indicator or semantics showing whether it is a revision when applicable

Deferred:

- per-message exceptions inside a source
- revision history compaction/cleanup
- external batch action execution
- undo UX beyond explicit change/reconsideration

Test expectations:

- first decision sets current state and adds history.
- same decision repeated does not create duplicate decision noise.
- different decision updates current state and appends a revision event.
- batch decision applies to all selected sources.
- batch decision requires confirmation.
- no external action is executed for any batch decision.

### Contract A16 - Pagination / Page Size

Decision:

Pagination/page-size behavior is required before real data use.

Behavior contract:

- backend candidate/source listing should support page and page size, or equivalent offset/limit.
- response should include metadata such as total count, current page, page size, and total pages or has-next/has-previous.
- frontend should expose page-size and page navigation.
- filtering alone is not sufficient.

Deferred:

- infinite scroll
- server-side full text search optimization
- large-scale indexing strategy

Test expectations:

- API returns paginated items and metadata.
- page size affects number of returned rows.
- frontend renders pagination controls.
- frontend can move between pages or update page size.

### Contract A30 / A31 - PostgreSQL and User Ownership Foundation

Decision:

The next architecture foundation pass should combine PostgreSQL readiness and basic user/account ownership.

Reason:

These are tightly related Tier 1 foundations. PostgreSQL gives SANE the intended persistence base; user/account ownership gives future Gmail OAuth, settings, decisions, and subscription/account concepts somewhere correct to attach.

Active scope:

- add PostgreSQL-ready configuration
- preserve `.env`-driven database selection
- introduce or formalize migration support
- keep local development usable
- add a basic user/account persistence model
- associate source review rows and decisions with a user/account
- seed or resolve a local ALPHA user for existing demo/local workflows
- preserve existing source/decision behavior under that local ALPHA user
- update backend tests for user-owned data
- update docs and environment examples

Out of scope:

- Gmail OAuth
- Gmail API calls
- token storage for live Google credentials
- real authentication/login UI
- billing/subscription enforcement
- multi-account support
- PostgreSQL deployment hosting decisions
- external email actions

Implementation expectations:

- Existing API behavior should continue to work for ALPHA with a default/local user context.
- New model relationships should make future OAuth/account work straightforward.
- Tests should prove user ownership exists without requiring real login.
- The pass should not trigger Gmail ingestion.

### Contract A32 / A33 - Gmail Ingestion Governance

Decision:

Future Gmail integration must use controlled ingestion triggers.

Hard rule:

SANE must never scan, import, or analyze Gmail simply because the app opens.

Allowed trigger types:

- manual user-requested scan
- scheduled/chrono-controlled scan
- bounded ALPHA/test scan

Future ingestion run contract:

When Gmail work begins, represent each scan/import/analyze operation as an ingestion run or equivalent explicit workflow record.

Candidate fields:

- `user_id`
- `gmail_connection_id`
- `trigger_type`
- `scope`
- `limit_count`
- `lookback_window`
- `started_at`
- `completed_at`
- `status`
- `message_count_scanned`
- `source_count_created`
- `error_summary`

First Gmail API pass direction:

- implement OAuth and Gmail connection only after A30/A31
- use minimal necessary Gmail scopes
- expose an explicit manual scan action
- bound the first import by count and/or recency, such as latest 50 messages
- normalize imported messages into source/vendor/cluster review units
- preserve human-confirmed decision workflow
- preserve no external unsubscribe/archive/delete execution

Out of scope for the A30/A31 foundation pass:

- live OAuth
- live Gmail API calls
- ingestion run execution
- scheduled jobs
- real mailbox imports
