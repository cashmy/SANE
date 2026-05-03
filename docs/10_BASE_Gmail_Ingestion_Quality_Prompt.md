# Prompt 10 - Gmail Ingestion Quality and Source Normalization

## Status

Draft prompt. Do not execute until Prompt 09 live OAuth/Gmail reality contact is complete or intentionally deferred by SKY.

Prompt 10 uses first real Gmail metadata to improve ingestion quality.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this post-reality-contact ingestion quality prompt.

## Active Execution Context

Active task:

- improve Gmail metadata normalization into source/vendor/cluster rows
- improve ingestion run reporting
- preserve data minimization
- keep the scan bounded and manual

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- Prompt 08 and Prompt 09 reports/artifacts
- Gmail service and ingestion code
- Candidate/source model and schemas
- IngestionRun model and schemas
- Connections view scan status UI
- Review view source table
- backend and frontend tests

## Clarification Gate

Before executing implementation:

1. Summarize the current live or mocked Gmail ingestion behavior.
2. State the current source normalization strategy.
3. Identify known quality issues from real or sample Gmail metadata.
4. State how source keys will be generated or refined.
5. State how sender/domain grouping will work for this pass.
6. State what metadata will be stored and what will not be stored.
7. State how duplicate messages/sources will be handled.
8. State how IngestionRun reporting will improve.
9. Ask clarifying questions if grouping, source identity, privacy, or scan result semantics are ambiguous.
10. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Improve how SANE turns Gmail metadata into reviewable source rows.

The user should be able to understand:

- which source/vendor/sender cluster was found
- how many messages contributed to it
- why it appears in the review queue
- what representative metadata supports it
- what scan created or updated it

## Ingestion Quality Direction

Improve source normalization around:

- sender email
- sender display name
- sender domain
- Gmail category/label
- message count
- representative subject/snippet
- recent activity if available
- duplicate detection

Keep the model honest.

Do not pretend real source clustering is solved if this pass only groups by sender/domain.

If heuristic grouping is used, name it as heuristic.

## Data Minimization

Do not store full email bodies.

Prefer storing:

- provider message id if needed for dedupe/reference
- sender email
- sender display name if available
- sender domain
- Gmail labels/categories
- subject/snippet only as representative evidence
- internal timestamp/date if needed for recency

Avoid storing:

- full message body
- attachments
- unnecessary recipients
- unnecessary thread content

## IngestionRun Reporting

Improve IngestionRun reporting as needed so the Connections view can show:

- last scan status
- started/completed time
- scan scope
- limit count
- messages scanned
- sources created
- sources updated if tracked
- failure/error summary

If `sources_updated` is not currently modeled and would be useful, propose it in the clarification gate before adding it.

## Source Identity

Source uniqueness remains:

```text
unique(email_account_id, source_key)
```

Do not introduce global or user-scoped source identity.

If source key generation changes, add tests proving:

- duplicate messages from the same source update the same source row
- the same source key can exist in different EmailAccounts
- unrelated sources do not collapse incorrectly under obvious cases

## Testing

Automated tests must not call real Google/Gmail APIs.

Use realistic mocked Gmail message payloads.

Backend test expectations:

- normalization creates source rows under the correct EmailAccount
- repeated scan does not create duplicate source rows
- email counts are correct for grouped messages
- representative subject/snippet is selected deterministically
- scan bounds are respected
- IngestionRun status/counts are correct
- no full body storage occurs

Frontend test expectations:

- Connections view shows last scan summary
- Review view shows source rows with email counts
- error/partial failure status is legible

## Out Of Scope

Do not implement:

- AI classifier calls
- full mailbox import
- full-text search overhaul
- scheduled scans
- unsubscribe/archive/delete actions
- source merge/split UI
- per-message exception workflow
- full message body storage
- Microsoft/IMAP integration
- billing/subscriptions

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If live Gmail validation is repeated, keep it bounded and report exactly what was live-tested.

## Report

Report:

- files changed
- source normalization strategy
- source key strategy
- metadata stored
- metadata deliberately not stored
- ingestion reporting changes
- tests added/updated
- validation results
- live-tested vs mocked behavior
- remaining risks before Prompt 11

