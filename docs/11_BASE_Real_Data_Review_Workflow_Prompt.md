# Prompt 11 - Real-Data Review Workflow Usability

## Status

Ready for BASE clarification gate.

Prompt 10 and Prompt 10b are complete.

Current live ALPHA state:

- Google sign-in works.
- Gmail readonly connection works.
- manual bounded `CATEGORY_PROMOTIONS` scans work.
- sender-email source identity is intentionally preserved for ALPHA.
- rescans are honest and report `source_count_seen`.
- repeating a scan does not duplicate source rows.
- local account reset works for `sources_and_decisions`.
- live reset and fresh scan recreated pending source rows.

Prompt 11 focuses on making the Review and Decisions workflow usable with real Gmail-derived source rows.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this real-data review workflow prompt.

## Active Execution Context

Active task:

- improve the Review and Decisions workflow after real Gmail ingestion
- add Decisions view pagination/page-size behavior
- preserve source-oriented review
- improve visibility of real-data context
- preserve rescan/reset safety boundaries
- keep external actions disabled

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- Prompt 08/09/09b/10/10b reports/artifacts
- Review view
- Decisions view
- Connections view
- frontend types and API client
- backend source/decision schemas and endpoints
- source normalization behavior
- existing frontend and backend tests

## Clarification Gate

Before executing implementation:

1. Summarize the current Review workflow against real or realistic Gmail-derived source rows.
2. Identify what becomes hard to use with real source volume.
3. State which UI changes are necessary for usability and which are deferred.
4. State how A50 Decisions pagination/page-size will be implemented.
5. State whether backend API changes are needed for sorting/filtering/details.
6. State how connected mailbox context will be shown.
7. State how source detail/evidence will be surfaced without storing full bodies.
8. State how Decisions view should distinguish current vs revised decisions.
9. State how any new controls avoid implying external Gmail action execution.
10. Ask clarifying questions if workflow meaning, decision semantics, source evidence display, mailbox context, pagination, or action boundaries are ambiguous.
11. Ask any other clarifying questions that arise from code inspection, test expectations, data model constraints, UI implications, or conflicts between this prompt and the existing implementation.
12. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Make SANE feel usable as a real Stage 1 / Tier 1 review tool after Gmail ingestion.

The user should be able to:

- see which mailbox/source scope they are reviewing
- prioritize high-volume sources
- inspect enough evidence to make a decision
- decide on one source
- decide on multiple selected sources
- revise a decision if needed
- understand what has and has not been externally executed

## Review View Direction

Improve the Review view around:

- connected mailbox context
- source count and pagination clarity
- sorting by email count and/or recent activity
- filtering by Gmail category/label
- filtering by connected mailbox if multiple exist in data
- search across source name, sender email, and domain
- selected-row/batch state
- explicit no-external-action boundary
- post-reset / fresh-scan clarity if visible in the current workflow

If backend API changes are needed for sorting/filtering, keep them narrow and tested.

Do not implement broad dashboard redesign in this pass.

Do not implement source merge/split or sender-level allow/block controls unless SKY explicitly approves expanding scope.

## Source Detail / Evidence Direction

Add a bounded way to inspect source evidence if needed.

Possible patterns:

- detail drawer
- compact expandable row
- modal

Evidence may include:

- sender emails
- sender domain
- representative subject/snippet
- message count
- labels/categories
- recent message date if available
- ingestion run reference/status

Do not store or display full email bodies.

Do not turn the app into an email reader.

## Decisions View Direction

Improve Decisions view around:

- pagination and page-size controls
- current decision vs revision history
- source name and mailbox context
- decision timestamp
- external action status
- revision/correction affordance
- filtering by decision type if useful

Do not implement revision history compaction unless SKY explicitly approves in this pass.

A50 requirement:

- backend decision listing should support page and page size, or equivalent offset/limit.
- response should include pagination metadata.
- frontend Decisions view should expose page-size and page navigation.
- current/revision semantics must remain visible.
- no external email actions should be introduced.
- filtering/search can be deferred unless it is low-risk and clearly useful.

## Workflow Guardrails

Preserve:

- human-confirmed decisions
- append-only decision history
- repeated identical decision no-op
- explicit revision behavior
- batch confirmation
- no external unsubscribe/archive/delete actions
- local data scoped to the authenticated user / connected mailbox
- sender-email keyed ALPHA source identity unless SKY explicitly approves changing it
- A52 marketing-vs-transactional action safety guardrail
- rescan as local SANE refresh only
- reset as local SANE cleanup only

## Testing

Backend tests if API behavior changes:

- Decisions pagination returns expected metadata and page-size behavior
- sorting/filtering returns expected source rows
- mailbox scoping is preserved
- decision actions remain user/account scoped
- no external action executes

Frontend tests:

- real-data source rows render clearly
- mailbox context is visible
- Decisions pagination/page-size controls render and work
- sort/filter controls work if added
- source detail/evidence surface opens and closes if added
- batch decision confirmation still works
- Decisions view shows current/revision state clearly

## Out Of Scope

Do not implement:

- Gmail scan scheduling
- AI classifier provider calls
- unsubscribe/archive/delete execution
- GTD workflow
- billing/subscription enforcement
- full email reader behavior
- full body storage
- broad dashboard/analytics redesign
- Microsoft/IMAP integration
- Connections reset redesign
- Gmail ingestion normalization changes unless required to support Review/Decisions display

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If browser validation is performed, report what was manually reviewed.

## Report

Report:

- files changed
- Review workflow changes
- Decisions workflow changes
- backend API changes if any
- source evidence/display approach
- tests added/updated
- validation results
- remaining usability risks before Tier 1 productization
