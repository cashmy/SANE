# Prompt 10b - Account Local Data Reset

## Status

Ready for BASE clarification gate.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this reset/re-scan support prompt.

## Context

Prompt 09 completed live Google/Gmail reality contact.

Prompt 10 improved Gmail ingestion quality and rescan honesty:

- source identity remains sender-email keyed for ALPHA.
- scans now track `source_count_seen`.
- repeating the same bounded scan does not duplicate source rows.
- decision history is preserved across rescans.
- Connections now communicates that scans refresh local SANE review data only.

SKY now needs a clean way to reset local SANE data for a specific connected email account, then run a new bounded scan for continued ALPHA validation.

This corresponds primarily to A53.

## Active Execution Context

Active task:

- add an explicit per-email-account local data reset capability
- preserve Gmail connection and credentials
- support fresh re-scan validation
- keep all reset behavior local to SANE

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- Prompt 08, 09, 09b, 10 artifacts/reports
- Gmail account model
- Candidate/source model
- Decision model
- IngestionRun model
- Gmail routers/services
- workflow/source/decision services
- Connections view
- backend and frontend tests

## Clarification Gate

Before implementation:

1. Summarize the current EmailAccount -> Source/Candidate -> Decision -> IngestionRun relationships.
2. State exactly what will be deleted for each reset option.
3. State exactly what will be preserved for each reset option.
4. State whether ingestion run history will be cleared, preserved, or selectively handled.
5. State how decision deletion will be handled safely.
6. State how reset authorization will be restricted to the signed-in user and selected email account.
7. State the UI placement and confirmation flow.
8. State how the reset action will communicate that Gmail itself is not modified.
9. Ask any clarifying questions that arise from code inspection, data model constraints, cascade behavior, tests, UI implications, or conflicts between this prompt and the existing implementation.
10. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Product Decision

Reset belongs inside the existing Connections account card, not as a new drawer navigation item.

Reason:

- reset applies to a specific email account
- Connections already owns mailbox lifecycle controls
- Settings would separate reset from the mailbox it affects
- a standalone navigation item would make the action feel global and more dangerous

UI shape:

- keep primary visible actions:
  - `Scan Now`
  - `Disconnect`
- add a compact secondary control on each Gmail account card:
  - `More`
  - or a small overflow menu if the existing UI has that pattern
- menu item:
  - `Reset local data...`

Clicking `Reset local data...` should open a confirmation modal/dialog.

## Required Reset Options

Implement two reset choices:

1. Clear sources only
2. Clear sources and decisions

Definitions:

### Clear Sources Only

Delete local source/review rows for the selected email account.

Because decisions are attached to sources, BASE must inspect whether this can be safely implemented without orphaning decision rows.

If the current schema cascade means source deletion necessarily deletes related decisions, stop at the clarification gate and report that `Clear sources only` cannot honestly preserve decisions without a larger model change.

Do not silently implement misleading behavior.

### Clear Sources and Decisions

Delete local source/review rows and related decision history for the selected email account.

This is expected to be the clean re-scan path for ALPHA validation.

## IngestionRun Handling

Preferred direction:

- preserve ingestion run history by default if it remains meaningful and does not block fresh scanning.
- after reset, a new scan should create a new IngestionRun.
- if preserving run history makes Connections confusing, propose a minimal UI wording or a reset marker strategy in the clarification gate.

Do not delete ingestion run history unless SKY approves it after the clarification gate.

## Explicit Guardrails

Reset must not:

- modify Gmail
- unsubscribe
- archive
- delete Gmail messages
- disconnect Gmail
- revoke Gmail credentials
- clear Gmail OAuth tokens
- affect other email accounts
- affect other users
- clear app authentication

Reset is local SANE data cleanup only.

## Confirmation Copy

The dialog must make the boundary explicit:

```text
This only clears SANE's local data for this Gmail account. It does not modify Gmail, unsubscribe, delete, archive, or disconnect the mailbox.
```

The destructive option should require explicit confirmation.

Use the existing UI style; do not introduce a new modal library unless the project already has one.

If the project does not yet have modal/dialog patterns, implement the smallest accessible in-app confirmation dialog that fits the current React/CSS style.

## API Direction

Add a backend endpoint or endpoints for email-account local reset.

Possible shape:

```text
POST /api/gmail/accounts/{account_id}/reset-local-data
```

Possible payload:

```json
{
  "mode": "sources_only" | "sources_and_decisions",
  "confirmed": true
}
```

The exact route may differ if current router naming suggests a better local pattern.

Requirements:

- require authenticated user
- verify selected EmailAccount belongs to that user
- verify account provider/status as appropriate
- require `confirmed = true`
- return a clear summary:
  - sources deleted
  - decisions deleted
  - ingestion runs preserved/deleted
  - account id
  - account email

## Testing

Backend tests:

- reset requires authentication
- reset rejects accounts owned by another user
- reset requires explicit confirmation
- reset does not disconnect Gmail or clear credentials
- reset affects only the selected email account
- `sources_and_decisions` deletes sources and related decisions
- ingestion run history is preserved unless approved otherwise
- after reset, a new scan can create fresh source rows

If `sources_only` cannot preserve decisions because of cascade constraints, add tests for the approved adjusted behavior after SKY decision.

Frontend tests:

- Connections card exposes `Reset local data...` through the secondary control
- confirmation dialog explains local-only boundary
- user can cancel without API call
- destructive reset requires explicit confirmation
- successful reset shows a clear local-only status message
- Gmail remains connected in the UI after reset
- scan controls remain available after reset

## Out Of Scope

Do not implement:

- Gmail message deletion/archive/unsubscribe
- account delete/disassociation
- Gmail disconnect changes
- source merge/split
- decision history compaction beyond the reset option
- global user reset unless SKY explicitly approves expanding scope
- scheduled scans
- billing/subscriptions
- Microsoft/IMAP behavior

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If you perform live browser validation, keep it local-data-only:

- do not modify Gmail
- do not revoke Gmail
- do not run unbounded scans

## Report

Report:

- files changed
- API route/payload implemented
- reset modes implemented
- what each mode deletes
- what each mode preserves
- how Gmail safety is enforced
- tests added/updated
- validation results
- live-tested vs mocked behavior
- remaining risks
