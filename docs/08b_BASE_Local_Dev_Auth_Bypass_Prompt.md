# Prompt 08b - Local Development Auth Bypass

## Status

Execute after Prompt 08 when local UI/workflow review is blocked by missing Google OAuth configuration.

This is a narrow repair prompt.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this Prompt 08b repair.

## Active Execution Context

Active task:

- A47 - development-only Local ALPHA auth bypass

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, only A47 plus A32/A33 guardrails
- Prompt 08 auth code and report context
- backend auth router/service
- backend security/session helper
- backend config and `.env.example`
- frontend `SignInScreen`
- frontend auth service/client
- app shell/account menu
- current auth tests

## Clarification Gate

Before executing implementation:

1. Confirm Prompt 08 auth is already present.
2. State the current behavior when Google OAuth is not configured.
3. State the proposed local-dev auth mode and environment variable names.
4. State how local-dev auth will be blocked outside development.
5. State how local-dev auth differs from Gmail authorization.
6. State how the frontend will expose the local-dev path.
7. State which tests will prove the bypass is safe and bounded.
8. Ask clarifying questions if auth mode, production guardrails, or UI behavior is ambiguous.
9. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Restore local UI/workflow review before live Google OAuth setup.

The app should support an explicit development-only path:

```text
Continue as Local ALPHA User
```

This path should create or reuse the existing Local ALPHA User session.

It must not connect Gmail.

It must not scan Gmail.

It must not weaken production auth.

## Auth Mode Direction

Add an explicit backend setting such as:

```text
SANE_AUTH_MODE=local_dev
```

Allowed values should be narrow, for example:

```text
local_dev
google_oauth
```

Default should be conservative. Prefer `google_oauth` unless the existing development setup clearly requires `local_dev`.

Document the intended local setting in `.env.example` using a placeholder or safe development value.

## Local Dev Behavior

When local-dev auth is enabled:

- frontend sign-in screen shows `Continue as Local ALPHA User`
- backend endpoint creates/uses the Local ALPHA User
- backend issues the normal HttpOnly SameSite=Lax session cookie
- app shell shows Local ALPHA User / local-dev status
- Review and Decisions can be inspected with Local ALPHA data

When local-dev auth is disabled:

- local-dev endpoint should return 404 or 403
- sign-in screen should show Google sign-in only

## Production Guardrails

Local-dev auth must be blocked if production mode is active.

Use the existing settings if there is already a production/debug indicator.

If needed, add a small explicit environment setting such as:

```text
SANE_ENV=development | production
```

Do not overbuild environment management.

Guardrails:

- no local-dev auth in production
- no real secrets written to tracked files
- no SQLite guidance
- no Gmail authorization
- no ingestion trigger
- no external email actions

## Friendly OAuth Error

When Google OAuth is not configured and Google sign-in is attempted, show a friendly app-facing message instead of leaving the user at raw JSON.

The message should make clear that OAuth is not configured for this local environment.

Do not add marketing/expository content.

## Testing

Backend tests should prove:

- local-dev auth endpoint issues a valid session when enabled
- local-dev auth endpoint is blocked when disabled
- local-dev auth endpoint is blocked in production mode
- local-dev auth creates/uses Local ALPHA User
- local-dev auth does not create Gmail EmailAccount credentials
- local-dev auth does not create IngestionRun
- Google OAuth missing-config behavior remains safe

Frontend tests should prove:

- local-dev sign-in button appears only when enabled or advertised by backend config
- clicking local-dev sign-in authenticates the app through the normal auth state
- Google OAuth missing-config error is shown in the app, not as raw JSON

## Out Of Scope

Do not implement:

- live Google OAuth setup
- Gmail connect changes
- Gmail scan changes
- token storage changes
- server-side session table
- production auth hardening beyond local-dev blocking
- UI redesign

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
- auth mode setting
- local-dev endpoint behavior
- production guardrails
- frontend sign-in behavior
- tests added/updated
- validation results
- remaining auth/OAuth risks

