# Prompt 13 - Source Evidence and Sender Safety Modeling

## Status

Ready for BASE clarification gate.

Prompt 12 and Prompt 12b are complete.

Current state:

- sender-email keyed ALPHA source identity is intentional.
- classifier heuristics are more conservative and metadata-specific.
- local reclassification command refreshed existing source rows without Gmail contact.
- Review evidence display is bounded and less redundant after Prompt 12b.
- A60 mailbox-scope layout density is tracked separately and is not the active Prompt 13 scope.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this source evidence and sender-safety prompt.

## Context

A52 established a critical future action guardrail:

Future unsubscribe/action logic must distinguish marketing/promotional streams from important transactional/security/account messages from the same organization.

Prompt 13 does not implement unsubscribe execution.

It prepares the source evidence model and UI/API contracts needed for safer future action design.

Prompt 13 may add bounded stored evidence if needed, but it should not broaden into unsubscribe execution, source merge/split, sender allow/block controls, or broad UI redesign.

## Active Execution Context

Active task:

- inspect what Gmail metadata/evidence is available and currently stored
- determine the smallest useful evidence additions for source/sender safety
- support future marketing-vs-transactional distinction
- preserve data minimization
- preserve no external action execution
- preserve sender-email source identity unless SKY explicitly approves otherwise

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- A52 section in the issue register
- A60 section in the issue register only to avoid accidentally mixing layout scope into evidence modeling
- Prompt 10, 12, and 12b reports/artifacts
- Gmail metadata fetch/normalization code
- classifier service and reclassification command
- Candidate/source model
- IngestionRun model
- Review evidence UI after Prompt 12b
- Playwright smoke fixtures if visible evidence output changes
- tests

## Clarification Gate

Before implementation:

1. Summarize currently stored source evidence.
2. State what Gmail metadata is available without fetching full bodies.
3. State whether list headers, unsubscribe headers, sender domain, provider message id, internal date, labels, or snippets should be stored.
4. State what data should still not be stored.
5. State how this supports future marketing-vs-transactional safety.
6. State whether a new evidence table is needed or whether source fields are sufficient for this pass.
7. State whether this pass requires a schema migration.
8. State whether existing stored rows need a local backfill/reclassification/update command after any evidence fields are added.
9. State whether Review evidence UI needs small display updates or whether this is backend-only evidence preparation.
10. Ask clarifying questions if privacy, retention, sender safety, evidence display, migration/backfill, or future action needs are ambiguous.
11. Ask any other clarifying questions from code inspection, tests, UI implications, or prompt/implementation conflicts.
12. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Give SANE enough bounded evidence to support safer future decisions without becoming an email archive or reader.

The goal is evidence quality, not action execution.

## Preferred Evidence Candidates

Consider:

- sender email
- sender display name
- sender domain
- provider message id for dedupe/reference
- Gmail labels/categories
- representative subject/snippet
- internal date / recent activity
- List-ID header if available
- List-Unsubscribe header presence/value if safe to store

If storing complete header values creates privacy or retention concerns, propose a safer representation such as:

- boolean presence flag
- normalized domain/list id
- truncated value
- hashed/reference value
- representative-only metadata

Do not store:

- full body
- attachments
- complete thread content
- unnecessary recipients
- broad message archives
- raw Gmail payloads
- OAuth/token data outside the existing credential storage path

## A52 Safety Principle

Do not collapse or act on:

```text
all messages from this organization
```

when evidence indicates separate streams such as:

- marketing/promotions
- fraud/security alerts
- account notices
- transactional receipts
- service updates

## Out Of Scope

Do not implement:

- unsubscribe execution
- archive/delete/modify Gmail actions
- AI provider calls
- full message body storage
- source merge/split UI
- sender allow/block controls unless SKY explicitly approves expansion
- mailbox-scope layout compression from A60
- classifier heuristic changes unless required to consume newly approved evidence and explicitly approved
- real Gmail scan unless SKY explicitly approves it after the clarification gate

## Testing

Backend tests:

- evidence extraction from mocked Gmail metadata
- no full body storage
- transactional and marketing examples remain distinguishable in stored evidence
- repeated scan remains deduped/source-safe
- existing decisions and processing state are preserved if any backfill/update command is added

Frontend tests if evidence display changes.

Playwright tests if visible evidence output changes.

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If frontend evidence display or Playwright fixtures change, also run:

```powershell
cd frontend
npm run test:e2e
```

If a migration is added, report Alembic current/head.

Do not run a live Gmail scan unless SKY explicitly approves it.

## Report

Report:

- files changed
- evidence stored
- evidence deliberately not stored
- schema/migration changes if any
- backfill/reclassification/update command if any
- Review evidence display changes if any
- tests added/updated
- validation results
- live-tested vs mocked behavior
- remaining sender/action safety risks
