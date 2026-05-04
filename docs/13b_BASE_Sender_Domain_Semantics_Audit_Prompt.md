# Prompt 13b - Sender Domain Semantics Audit and UI Cleanup

## Status

Ready for BASE clarification gate after Prompt 13.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this sender-domain semantics prompt.

## Context

Prompt 13 added bounded source evidence fields, including singular `sender_domain`.

Live UI review then showed both:

- `Sender domains`
- `Stored sender domain`

This surfaced possible conceptual drift.

The intended business/data concept is:

```text
one sender_domain per source
one or more stored sender_emails per source
```

The intended future grouping possibility is multiple sender addresses under the same domain/source, such as:

```text
no-reply@acme.com
info@acme.com
accounts@acme.com
```

The intended model is not arbitrary cross-domain grouping.

CORE/SKY correction:

- do not model or display plural stored sender domains for this stage
- do not infer that two different domains should be grouped into one source
- do preserve the ability for one source/domain to carry multiple sender email addresses
- if code inspection finds plural-domain or cross-domain grouping assumptions, report that as semantic drift before implementation

Do not treat this as a simple label cleanup until code inspection proves the issue is UI-only.

## Active Execution Context

Active task:

- audit sender-domain semantics across model, ingestion, classifier, commands, API, UI, and tests
- determine whether the fix is UI-only, helper/service cleanup, or schema/model refactor
- if approved after the gate, implement the smallest correct cleanup
- preserve Prompt 13 evidence safety and data minimization

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- Prompt 13 report/artifacts
- `Candidate.sender_emails`
- `Candidate.sender_domain`
- source/read schemas and frontend workflow types
- Gmail ingestion normalization/upsert code
- classifier service
- reclassification command/service
- `backfill_source_evidence` command/service
- Review evidence UI
- Vitest fixtures
- Playwright fixtures/tests
- Alembic migration added by Prompt 13

## Clarification Gate

Before implementation:

1. State whether the database/model currently has singular `sender_domain`, plural sender domains, or both.
2. State how `sender_emails` is stored and used.
3. State how Gmail ingestion sets `sender_domain`.
4. State how the backfill command derives `sender_domain`.
5. State whether the reclassification command depends on sender domain or only sender emails/source fields.
6. State whether classifier logic assumes one domain, many domains, or does not care.
7. State where the Review UI derives or displays `Sender domains`.
8. State whether any code or tests imply cross-domain grouping.
9. Classify the needed repair as one of:
   - UI-only cleanup
   - small helper/service cleanup
   - schema/model refactor
10. State the smallest correct implementation plan.
11. State what tests need updating.
12. Ask clarifying questions if domain semantics, data model implications, migration/backfill behavior, classifier behavior, or UI evidence display are ambiguous.
13. Ask any other clarifying questions from code inspection, tests, UI implications, or conflicts between prompt and implementation.
14. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Target Semantics

The intended source evidence model is:

```text
sender_domain: one domain for the source
sender_emails: one or more stored sender addresses for the source
```

UI should communicate one domain concept:

- label: `Sender domain`
- value: stored `sender_domain` when present
- fallback: derive from `sender_emails` if stored `sender_domain` is missing

UI should not show both:

- `Sender domains`
- `Stored sender domain`

Do not add a plural stored sender domains field.

Do not implement cross-domain grouping.

If current code contains a helper that derives multiple domains from `sender_emails`, that helper may still be useful for anomaly detection or fallback display, but it should not become the normal product concept unless SKY approves it. Normal evidence display should express singular `Sender domain` plus one-or-more `Sender emails`.

## Guardrails

Do not change unless the clarification gate proves it is necessary and SKY approves:

- backend schema
- Gmail ingestion source identity
- classifier behavior
- reclassification behavior
- backfill behavior
- source grouping semantics

Do not change:

- external Gmail action boundaries
- decision behavior
- reset behavior
- OAuth/auth behavior
- sender-email keyed ALPHA source identity unless SKY explicitly approves a larger source-identity refactor

## Likely Preferred Outcome

If inspection confirms the backend already has the correct singular field, the likely implementation is:

- UI-only cleanup
- show one `Sender domain` in expanded evidence
- prefer stored `sender_domain`
- derive fallback from `sender_emails`
- remove duplicate `Stored sender domain` display
- update tests/fixtures accordingly

But do not assume this until inspection is complete.

## Testing

Tests should match the actual repair category.

If UI-only:

- frontend evidence row shows one `Sender domain`
- stored domain is not duplicated under another label
- sender emails still display normally
- Playwright smoke still passes

If helper/service cleanup:

- backend tests for domain derivation helper
- frontend tests if display changes

If schema/model refactor:

- stop and ask before implementation unless explicitly approved in the gate

## Validation

For UI-only:

```powershell
cd frontend
npm run test:run
npm run test:e2e
npm run build
```

For backend/service changes, also run:

```powershell
cd backend
python -m pytest
```

If migration changes are needed, report Alembic current/head.

## Report

Report:

- semantic audit findings
- repair category
- files changed
- display rule implemented
- tests updated
- validation results
- remaining sender-domain risks
