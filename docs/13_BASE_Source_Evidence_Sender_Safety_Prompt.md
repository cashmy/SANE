# Prompt 13 - Source Evidence and Sender Safety Modeling

## Status

Draft prompt. Do not execute until Prompt 12 is complete or intentionally deferred by SKY.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this source evidence and sender-safety prompt.

## Context

A52 established a critical future action guardrail:

Future unsubscribe/action logic must distinguish marketing/promotional streams from important transactional/security/account messages from the same organization.

Prompt 13 does not implement unsubscribe execution.

It prepares the source evidence model and UI/API contracts needed for safer future action design.

## Active Execution Context

Active task:

- inspect what Gmail metadata/evidence is available and currently stored
- determine the smallest useful evidence additions for source/sender safety
- support future marketing-vs-transactional distinction
- preserve data minimization
- preserve no external action execution

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`
- `docs/SANE_Data_Model_ERD.md`
- A52 section in the issue register
- Gmail metadata fetch/normalization code
- Candidate/source model
- IngestionRun model
- Review evidence UI from Prompt 11
- tests

## Clarification Gate

Before implementation:

1. Summarize currently stored source evidence.
2. State what Gmail metadata is available without fetching full bodies.
3. State whether list headers, unsubscribe headers, sender domain, provider message id, internal date, labels, or snippets should be stored.
4. State what data should still not be stored.
5. State how this supports future marketing-vs-transactional safety.
6. State whether a new evidence table is needed or whether source fields are sufficient for this pass.
7. Ask clarifying questions if privacy, retention, sender safety, or future action needs are ambiguous.
8. Ask any other clarifying questions from code inspection, tests, UI implications, or prompt/implementation conflicts.
9. You must have human approval before implementation.

## Goal

Give SANE enough bounded evidence to support safer future decisions without becoming an email archive or reader.

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

Do not store:

- full body
- attachments
- complete thread content
- unnecessary recipients
- broad message archives

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

## Testing

Backend tests:

- evidence extraction from mocked Gmail metadata
- no full body storage
- transactional and marketing examples remain distinguishable in stored evidence
- repeated scan remains deduped/source-safe

Frontend tests if evidence display changes.

## Validation

Run backend and frontend validation suites.

## Report

Report files changed, evidence stored, evidence not stored, tests, validation, and remaining sender/action safety risks.
