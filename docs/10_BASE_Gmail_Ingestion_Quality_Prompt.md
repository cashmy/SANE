# Prompt 10 - Gmail Ingestion Quality and Source Normalization

## Status

Ready for BASE clarification gate.

Prompt 09 live OAuth/Gmail reality contact is complete.

Observed live result:

- Google sign-in succeeded.
- Gmail readonly connection succeeded.
- manual `CATEGORY_PROMOTIONS` scan checked 50 messages.
- 32 source rows were created.
- Review loaded live rows from the connected Gmail account.
- A repeat scan over the same bounded page created no duplicate source rows and left decision history unchanged.

Prompt 10 uses this first real Gmail metadata contact to improve ingestion quality and scan/result semantics.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this post-reality-contact ingestion quality prompt.

## Active Execution Context

Active task:

- improve Gmail metadata normalization into source/vendor/cluster rows
- improve ingestion run reporting
- clarify and preserve rescan semantics
- preserve data minimization
- keep the scan bounded and manual

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- Prompt 08 and Prompt 09 reports/artifacts
- Prompt 09b if auth clock-skew handling affects live browser validation
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
8. State current repeat-scan behavior and what will be made explicit.
9. State whether current live ingestion can ever produce multiple sender emails for one source, or whether `source_key` currently prevents that by using sender email as identity.
10. State how A52 marketing-vs-transactional safety affects source grouping and future sender-level controls.
11. State how IngestionRun reporting will improve.
12. Ask clarifying questions if grouping, source identity, privacy, reset, sender-level action safety, or scan result semantics are ambiguous.
13. Ask any other clarifying questions that arise from code inspection, test expectations, data model constraints, UI implications, or conflicts between the prompt and the existing implementation.
14. You must have human approval before implementation.

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
- whether multiple sender emails should be grouped into one source in this pass
- Gmail category/label
- message count
- representative subject/snippet
- recent activity if available
- duplicate detection
- same-source sender/list heuristics if supported by metadata

Keep the model honest.

Do not pretend real source clustering is solved if this pass only groups by sender/domain.

If heuristic grouping is used, name it as heuristic.

Known current implementation constraint to inspect:

- the data model/API/UI support `sender_emails: list[str]`.
- the Review table displays all sender emails it receives.
- current live Gmail ingestion appears to generate `source_key` from the sender email.
- if `source_key == sender_email`, then live ingestion will usually produce one sender email per source even though the model can hold many.

Prompt 10 should report whether this is still true after code inspection and either preserve it intentionally for ALPHA or propose the smallest safe grouping improvement.

Do not collapse multiple sender emails into one source unless the rule is explainable and tested.

Do not collapse transactional/security senders with marketing senders merely because they share an organization or domain.

Known live behavior to preserve unless SKY approves a change:

- repeating the same bounded scan should not create duplicate source rows.
- repeating the same bounded scan should not clear decision history.
- repeating the same bounded scan should not execute external Gmail actions.
- scanning again should be described as refreshing/importing local SANE review data only.

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
- clear repeat-scan result language if nothing new was created

If `sources_updated` is not currently modeled and would be useful, propose it in the clarification gate before adding it.

If tracking `sources_unchanged`, `sources_seen`, or similar would make repeat-scan behavior more honest, propose the smallest useful option in the clarification gate before adding it.

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
- transactional/security senders are not collapsed into a marketing source solely by shared organization/domain

## Sender-Level Action Safety

A52 is a future action guardrail, but it affects Prompt 10 normalization.

Do not implement unsubscribe execution in this pass.

Do consider whether the source row should preserve enough sender/list evidence to support later user decisions such as:

- allow this sender
- block/queue this sender
- unsubscribe from this marketing stream
- preserve fraud/security/account alert streams

If sender-level allow/block controls are needed, propose them in the clarification gate. Do not implement them unless SKY approves pulling that scope into Prompt 10.

## Testing

Automated tests must not call real Google/Gmail APIs.

Use realistic mocked Gmail message payloads.

Backend test expectations:

- normalization creates source rows under the correct EmailAccount
- repeated scan does not create duplicate source rows
- repeated scan does not clear or alter existing decision history
- email counts are correct for grouped messages
- representative subject/snippet is selected deterministically
- scan bounds are respected
- IngestionRun status/counts are correct
- no full body storage occurs
- grouping tests include at least one case that protects against unsafe marketing/transactional collapse if grouping logic changes

Frontend test expectations:

- Connections view shows last scan summary
- Connections view makes clear that scanning refreshes local review data and does not modify Gmail
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
- account/user reset controls unless SKY explicitly approves pulling A53 into this pass
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
