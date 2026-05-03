# Prompt 15 - Deployment Readiness, Secrets, and Environment Hardening

## Status

Draft prompt. Do not execute until Tier 1 boundary is defined or intentionally deferred by SKY.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this deployment-readiness prompt.

## Context

SANE now has real OAuth, Gmail credentials, PostgreSQL, Alembic, JWT sessions, and environment-dependent behavior.

Prompt 15 focuses on deployment readiness and local/production environment hardening.

It does not choose a hosting provider unless SKY explicitly approves.

## Active Execution Context

Active task:

- inspect environment and secret requirements
- harden startup/config validation
- document local vs production setup
- reduce risk of unsafe debug/local-dev configuration

## Required Context

Inspect:

- README
- `.env.example`
- config/settings
- auth/security code
- Gmail credential encryption
- CORS setup
- Alembic setup
- database/session setup
- local dev auth bypass
- tests

## Clarification Gate

Before implementation:

1. Summarize current required environment variables.
2. Identify which values are local-only, production-required, or unsafe placeholders.
3. State current production guardrails.
4. Identify gaps in debug mode, CORS, JWT secret, Fernet key, OAuth redirect, and database validation.
5. Propose narrow hardening changes.
6. Ask clarifying questions if deployment target, secret handling, or environment policy is ambiguous.
7. Ask any other clarifying questions from code inspection, docs, tests, or prompt conflicts.
8. You must have human approval before implementation.

## Areas To Review

- `SANE_DEBUG`
- `SANE_AUTH_MODE`
- `SANE_DATABASE_URL`
- `SANE_TEST_DATABASE_URL`
- `SANE_JWT_SECRET`
- `SANE_CREDENTIAL_ENCRYPTION_KEY`
- `SANE_GOOGLE_CLIENT_ID`
- `SANE_GOOGLE_CLIENT_SECRET`
- OAuth redirect URI
- frontend URL
- CORS origins

## Desired Outcome

SANE should fail clearly if production-like mode is configured unsafely.

Examples:

- local-dev auth must not run in production
- placeholder secrets must be rejected in production
- weak JWT secret should be rejected in production
- missing Fernet key should fail clearly when Gmail credentials are enabled
- CORS should not be overly broad in production

## Out Of Scope

Do not implement:

- hosting provider deployment
- containerization unless SKY approves
- CI/CD
- billing
- infrastructure-as-code
- secret manager integration unless SKY approves

## Testing

Backend tests for config validation and guardrails.

Frontend tests only if UI changes.

## Validation

Run relevant tests and build.

## Report

Report files changed, guardrails added, validation results, and remaining deployment risks.
