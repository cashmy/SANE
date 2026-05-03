# Prompt 16 - Action Execution Design, Not Implementation

## Status

Draft prompt. Do not execute until source evidence/sender safety and Tier 1 boundary work are complete or intentionally deferred by SKY.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this action-execution design prompt.

## Context

SANE currently records local decisions and queued intent only.

It does not execute unsubscribe, archive, delete, or Gmail modify actions.

Prompt 16 is a design prompt, not an implementation prompt.

The goal is to define a safe future action-execution contract before any code modifies Gmail.

## Active Execution Context

Active task:

- inspect current decision/action model
- design future action execution boundaries
- preserve A52 sender safety
- identify Gmail scope implications
- define audit/dry-run/human-confirmation requirements

Do not implement Gmail modifying actions.

## Required Context

Inspect:

- issue register, especially A52
- decision model
- external action status model
- Gmail scopes currently requested
- source evidence model
- Connections and Review/Decisions UI
- auth/security constraints

## Clarification Gate

Before producing the design artifact:

1. Summarize current decision/action state.
2. Identify what new Gmail scopes would be required for each possible action.
3. Identify risks for unsubscribe/archive/delete/modify behavior.
4. State how A52 marketing-vs-transactional safety should constrain execution.
5. Propose a dry-run/action-preview model.
6. Propose audit log requirements.
7. Propose human confirmation requirements.
8. Ask clarifying questions if action semantics, legal/privacy concerns, or Gmail scope implications are ambiguous.
9. Ask any other clarifying questions from code/docs inspection or prompt conflicts.
10. You must have human approval before creating the final design artifact.

## Output

Create or update a design artifact in `docs`, such as:

```text
docs/SANE_Action_Execution_Design.md
```

The artifact should cover:

- action types
- required Gmail scopes
- user confirmation model
- dry-run behavior
- audit log
- rollback limitations
- per-sender/per-stream safety
- disconnect/delete implications
- what remains explicitly out of scope

## Hard Guardrail

Do not implement:

- Gmail modify scopes
- unsubscribe calls
- archive/delete behavior
- external email actions
- scheduled actions
- background jobs

This is design only.

## Validation

Docs-only pass unless SKY approves code changes.

## Report

Report created/updated artifact, key design conclusions, and open questions before any future action-execution implementation.
