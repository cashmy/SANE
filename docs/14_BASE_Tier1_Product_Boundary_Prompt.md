# Prompt 14 - Tier 1 Product Boundary and Subscription Readiness

## Status

Draft prompt. Do not execute until Prompt 13 is complete or intentionally deferred by SKY.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this Tier 1 boundary prompt.

## Context

SANE is intended to become a subscription-based service with multiple tiers.

Current rough tier thinking:

- Tier 1: Stage 1 source review and manual Gmail scan for one Gmail account
- Tier 2: possible GTD/workflow expansion
- Tier 3: multiple email accounts/providers

Prompt 14 focuses on making the Tier 1 product boundary explicit.

This may produce documentation, configuration flags, UI copy, and possibly light entitlement scaffolding, but should not implement billing unless SKY explicitly approves.

## Active Execution Context

Active task:

- define Tier 1 included/excluded capabilities
- align current ALPHA functionality with likely Tier 1
- identify what is needed before subscription/product publication
- preserve deferred boundaries

## Required Context

Inspect:

- README
- issue register
- SANE Data Model ERD
- auth/Gmail/ingestion/review flows
- Settings view
- current navigation
- docs related to tiering or product direction

## Clarification Gate

Before implementation:

1. Summarize current ALPHA capabilities.
2. Propose Tier 1 included capabilities.
3. Propose Tier 1 exclusions/deferred capabilities.
4. Identify whether any code scaffolding is needed now or whether documentation is enough.
5. Identify UI copy/settings changes needed to avoid overpromising.
6. Ask clarifying questions if product tier boundaries or subscription assumptions are ambiguous.
7. Ask any other clarifying questions from code inspection, docs, UI implications, or conflicts.
8. You must have human approval before implementation.

## Likely Tier 1 Boundary

Possible Tier 1 includes:

- Google sign-in
- one Gmail account
- manual bounded scan
- source review
- local decision history
- no external email actions
- no scheduled scan
- no AI-provider classifier calls

Possible Tier 1 excludes:

- multi-email account support
- Outlook/IMAP
- GTD
- unsubscribe execution
- scheduled automation
- organization/team accounts
- billing enforcement if not ready

## Output Options

Depending on SKY approval, this pass may:

- update README/product docs
- update Settings placeholder
- add tier boundary documentation in `docs`
- add lightweight config constants or display labels
- avoid billing code entirely

## Out Of Scope

Do not implement:

- Stripe/payment provider
- subscription enforcement
- production account plans
- GTD workflows
- Gmail modify actions
- Microsoft/IMAP

## Validation

Run tests/build if code changes. Docs-only changes do not require full validation unless the repo convention says otherwise.

## Report

Report changed files, Tier 1 boundary, deferred items, and remaining productization risks.
