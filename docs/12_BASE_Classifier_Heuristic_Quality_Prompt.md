# Prompt 12 - Classifier / Heuristic Quality Review

## Status

Draft prompt. Do not execute until Prompt 11 is complete and SKY has reviewed the real-data Review/Decisions workflow.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this classifier/heuristic quality prompt.

## Context

SANE currently uses deterministic local classification heuristics to suggest source decisions.

Prompt 12 focuses on whether those suggestions are useful against live Gmail-derived source rows.

This pass should improve deterministic heuristic quality and human-facing explanation quality without introducing external AI provider calls.

## Active Execution Context

Active task:

- review current classifier behavior against realistic/live source rows
- improve deterministic classification heuristics if needed
- improve classifier reasons and signal labels if needed
- preserve human authority
- preserve no external action execution

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- Prompt 10 and Prompt 11 reports/artifacts
- classifier service
- Gmail normalization service
- source/candidate model and schemas
- Review view display of signal/reason/suggested decision
- backend and frontend tests

## Clarification Gate

Before implementation:

1. Summarize the current classifier heuristic.
2. Identify where live/realistic source suggestions appear useful.
3. Identify where live/realistic source suggestions appear weak, misleading, or overly generic.
4. State which deterministic heuristic changes are proposed.
5. State whether any data model or API changes are needed.
6. State how human authority remains clear.
7. Ask clarifying questions if classification meaning, decision vocabulary, or evidence requirements are ambiguous.
8. Ask any other clarifying questions from code inspection, test expectations, UI implications, or conflicts between prompt and implementation.
9. You must have human approval before implementation.

## Goal

Improve the quality and honesty of SANE's ALPHA suggestions.

The app should help the user triage sources, but it must not imply final authority.

## Direction

Prefer:

- deterministic rules
- transparent reasons
- conservative suggestions
- clear ambiguity labeling
- testable behavior

Avoid:

- external AI calls
- fake confidence
- over-specific claims not supported by metadata
- treating sender/domain alone as enough to infer unsubscribe safety

## Data and Safety Guardrails

Preserve:

- sender-email keyed source identity for ALPHA
- A52 marketing-vs-transactional safety
- no full email body storage
- no external Gmail action execution
- human-confirmed decisions

Do not introduce:

- AI provider calls
- full-message analysis
- unsubscribe execution
- source merge/split
- sender-level allow/block controls unless SKY explicitly approves expansion

## Testing

Backend tests:

- heuristic examples produce expected signals/suggestions
- ambiguous cases remain conservative
- transactional/security/account-alert examples are not classified as marketing unsubscribe candidates solely by domain
- classifier reasons are stable and human-readable

Frontend tests only if display behavior changes.

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

## Report

Report:

- files changed
- heuristic changes
- examples covered
- tests added/updated
- validation results
- remaining classifier risks
