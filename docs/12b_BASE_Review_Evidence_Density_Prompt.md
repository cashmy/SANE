# Prompt 12b - Review Evidence Density Polish

## Status

Ready for BASE clarification gate after Prompt 12 and local reclassification command are complete.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this Review UI density prompt.

## Context

Prompt 11 added bounded expandable evidence rows in Review.

Prompt 12 improved classifier reason text and reclassified already-ingested local source rows.

Some visual redundancy was already present after Prompt 11, but it became excessive after Prompt 12 because the classifier reason text became more concrete and longer.

Current issue:

- collapsed Review rows and expanded evidence rows repeat too much information
- evidence expansion feels partly redundant rather than clarifying
- long reason text in the collapsed Source cell reduces scan density

This corresponds to A59.

## Active Execution Context

Active task:

- refine Review row/evidence density
- reduce redundant display text
- preserve existing Review workflow behavior
- preserve bounded evidence display
- avoid broad visual redesign

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- Prompt 11 and Prompt 12 reports/artifacts
- Review view
- App CSS
- frontend tests
- Playwright smoke fixtures/tests

## Clarification Gate

Before implementation:

1. Summarize the current collapsed Review row content.
2. Summarize the current expanded evidence row content.
3. Identify which fields are duplicated.
4. State what content will remain in the collapsed row.
5. State what content will move to or remain only in expanded evidence.
6. State what frontend tests/Playwright tests may need updating.
7. Ask clarifying questions if source/evidence meaning, density, accessibility, or test expectations are ambiguous.
8. Ask any other clarifying questions from code inspection, UI implications, tests, or conflicts between prompt and implementation.
9. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Product Direction

Collapsed Review row should communicate scan-priority essentials.

Expanded evidence should reveal supporting detail.

The user should not feel that `Show evidence` merely repeats the row.

## Preferred Layout Direction

Collapsed row should focus on:

- source name
- sender email(s)
- email count
- category
- signal
- suggested action
- state
- actions
- a short compact clue if needed

Collapsed row should avoid:

- long classifier reason paragraph
- full representative subject plus reason if both will appear in evidence
- repeated explanation that reduces table scan speed

Expanded evidence should focus on:

- mailbox scope
- sender domain
- representative subject
- classifier/evidence reason
- latest scan context
- current local decision if useful

Expanded evidence should avoid:

- repeating suggested local decision if it is already visible in the row
- repeating the same representative subject if it remains prominent in the collapsed row
- exposing full body/raw Gmail payloads

## Guardrails

Do not change:

- backend classifier logic
- Gmail ingestion
- source identity
- decision behavior
- pagination
- mailbox scoping
- reset behavior
- external action boundaries

This should be a frontend presentation/test pass unless code inspection reveals a necessary small type/test fixture adjustment.

## Testing

Frontend tests:

- Review row still renders source essentials
- evidence row still opens/closes
- evidence row shows supporting details
- removed/reduced duplicated content does not break accessibility queries

Playwright tests:

- update smoke fixture assertions only if visible text changes affect them
- E2E should still pass

## Validation

Run:

```powershell
cd frontend
npm run test:run
npm run test:e2e
npm run build
```

Backend tests are not required unless backend files change.

## Report

Report:

- files changed
- collapsed row content after change
- expanded evidence content after change
- duplicated content removed
- tests updated
- validation results
- remaining UI density risks
