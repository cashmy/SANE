# Prompt 11 - Real-Data Review Workflow Usability

## Status

Draft prompt. Do not execute until Prompt 10 ingestion quality is complete or intentionally deferred by SKY.

Prompt 11 focuses on making the review workflow usable with real Gmail-derived source rows.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this real-data review workflow prompt.

## Active Execution Context

Active task:

- improve the Review and Decisions workflow after real Gmail ingestion
- preserve source-oriented review
- improve visibility of real-data context
- keep external actions disabled

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- Prompt 08/09/10 reports/artifacts
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
4. State whether backend API changes are needed for sorting/filtering/details.
5. State how connected mailbox context will be shown.
6. State how source detail/evidence will be surfaced without storing full bodies.
7. State how Decisions view should distinguish current vs revised decisions.
8. Ask clarifying questions if workflow meaning, decision semantics, or source evidence display is ambiguous.
9. You must have human approval before implementation.

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

If backend API changes are needed for sorting/filtering, keep them narrow and tested.

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

- current decision vs revision history
- source name and mailbox context
- decision timestamp
- external action status
- revision/correction affordance
- filtering by decision type if useful

Do not implement revision history compaction unless SKY explicitly approves in this pass.

## Workflow Guardrails

Preserve:

- human-confirmed decisions
- append-only decision history
- repeated identical decision no-op
- explicit revision behavior
- batch confirmation
- no external unsubscribe/archive/delete actions
- local data scoped to the authenticated user / connected mailbox

## Testing

Backend tests if API behavior changes:

- sorting/filtering returns expected source rows
- mailbox scoping is preserved
- decision actions remain user/account scoped
- no external action executes

Frontend tests:

- real-data source rows render clearly
- mailbox context is visible
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

