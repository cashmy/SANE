# Prompt 08 - Gmail OAuth and Controlled Bounded Ingestion

## Status

Deferred until Prompt 07 / A30-A31 is complete and validated.

Do not execute this prompt before PostgreSQL-ready persistence and basic user/account ownership are in place.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this Gmail integration prompt for a later pass.

## Active Execution Context

Active task:

- A32 - Gmail ingestion trigger governance
- A33 - Gmail OAuth/API bounded ingestion

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, but only sections A32, A33, and `Contract A32 / A33`
- backend config and environment handling
- user/account ownership models from Prompt 07
- source/decision persistence and services
- existing Connections view
- existing Review view
- existing tests

## Clarification Gate

Before executing implementation:

1. Confirm A30/A31 are already implemented and validated.
2. Summarize the Gmail ingestion governance rule.
3. List the Google/Gmail scopes you believe are needed and why.
4. State how credentials and tokens will be represented in development without exposing secrets.
5. List the files you expect to touch.
6. State how Gmail behavior will be tested without calling the real Gmail API in automated tests.
7. Ask clarifying questions if any ambiguity affects OAuth, scopes, token handling, ingestion limits, or privacy expectations.
8. You must have human approval before executing implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Hard Governance Rule

SANE must never scan, import, or analyze Gmail merely because the app opens.

Gmail ingestion must be triggered only by:

- explicit user-requested scan
- scheduled/chrono-controlled scan
- bounded ALPHA/test scan

For this first Gmail pass, prefer explicit manual scan only unless SKY approves scheduled behavior.

## Goal

Add a safe Gmail connection and bounded ingestion foundation.

The first real-data contact should be intentionally small and reversible in product meaning:

- connect through OAuth
- allow an explicit manual scan action
- import a bounded recent sample, such as latest 50 messages or another approved limit
- normalize imported messages into source/vendor/cluster review rows
- preserve human-confirmed decisions
- never execute external unsubscribe/archive/delete actions

## Required Backend Concepts

Add or prepare:

- Gmail connection model associated with a user/account
- OAuth state handling
- token metadata representation
- ingestion run model or equivalent explicit scan record
- manual scan endpoint
- bounded scan parameters:
  - `limit_count`
  - optional `lookback_window`
  - optional mailbox/category/label scope
- status/error fields for ingestion runs

Potential ingestion run fields:

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

## Required Frontend Concepts

Update the UI only enough to support the safe workflow:

- Connections view shows Gmail connection status
- manual scan action is explicit
- Review view can show last scan status or last scan time if useful
- no scan happens on app load
- UI clearly states ALPHA import is bounded and local decision actions remain not executed externally

## Testing

Automated tests must not call the real Gmail API.

Use mocks/fakes for:

- OAuth callback handling
- Gmail message listing
- Gmail message metadata/content normalization
- ingestion errors

Test expectations:

- app load does not trigger scan/import
- manual scan endpoint requires a user-owned Gmail connection
- scan respects `limit_count`
- ingestion creates or updates source review units
- ingestion records an ingestion run
- no external unsubscribe/archive/delete action executes
- frontend only triggers scan after explicit user action

## Out Of Scope

Do not implement:

- full mailbox import
- scan-on-app-open
- autonomous unsubscribe/archive/delete
- AI provider calls
- GTD workflow
- billing/subscription enforcement
- multi-account Gmail support unless already approved
- scheduled job execution unless explicitly approved by SKY

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If manual live OAuth validation is not possible in this environment, report that clearly and provide the exact manual validation steps needed.

## Report

Report:

- files changed
- OAuth/Gmail scopes selected
- connection/token storage approach
- ingestion trigger behavior
- ingestion limits
- test strategy
- validation results
- what was mocked vs live-tested
- remaining privacy/security risks

