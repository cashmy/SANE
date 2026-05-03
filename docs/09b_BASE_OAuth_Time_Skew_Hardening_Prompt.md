# Prompt 09b - OAuth Time-Skew Hardening

## Context

Prompt 09 completed first live Google/Gmail reality contact:

- Google sign-in succeeded.
- Separate Gmail readonly connection succeeded.
- Manual `CATEGORY_PROMOTIONS` scan checked 50 messages.
- 32 live source rows were created.

During follow-up browser validation in Chrome, the Google auth callback produced a backend 500 error:

```text
jwt.exceptions.ImmatureSignatureError: The token is not yet valid (iat)
```

SKY synchronized Windows time, retried the flow, and the issue was resolved.

This confirms the root cause was local machine/server clock skew, not Google OAuth configuration, browser cache, or the SANE OAuth client setup.

However, the app should be hardened so small clock skew does not produce a raw Starlette debugger page or an unrecoverable auth experience.

## Execution Contract

You are implementing a narrow repair pass.

Do not change the OAuth product flow, Gmail scopes, auth model, database schema, ingestion behavior, source review behavior, or UI shell structure.

Preserve these existing boundaries:

- Google app sign-in remains separate from Gmail authorization.
- Gmail readonly remains the only Gmail scope.
- Gmail scans remain explicit/manual only.
- No scan runs on app open, sign-in, Gmail connect, or Connections render.
- No external email actions are executed.
- Local dev auth behavior remains unchanged.

## Required Fixes

### 1. Add JWT clock-skew leeway for Google ID token verification

Find the Google ID token verification path, currently surfaced in the traceback around:

```text
backend/app/services/auth_service.py
verify_google_id_token
```

Allow a small amount of clock skew when validating Google ID token time claims.

Preferred value:

```text
120 seconds
```

The value may be a named constant in the auth service. It does not need to be environment-configurable for this ALPHA pass unless the existing settings pattern makes that cleaner.

### 2. Gracefully handle immature/not-yet-valid token errors

The auth callback must not expose a raw Starlette debugger page for this case.

If Google token validation fails because of clock skew or an immature `iat`/time claim:

- log or preserve a useful backend-side error message if the project already has a logging pattern
- return or redirect to the frontend with a friendly auth failure state, consistent with the existing auth error handling
- do not create or link a user
- do not create an AuthIdentity
- do not connect Gmail
- do not create an IngestionRun

The user-facing message can be simple, such as:

```text
Google sign-in could not be completed because this device clock appears out of sync. Sync your system time and try again.
```

If the current frontend/auth callback flow already has an error-display mechanism, use that rather than inventing a broad new UI pattern.

### 3. Preserve successful live OAuth behavior

Do not break the already-working path:

- valid Google sign-in still succeeds
- `/api/auth/me` still returns the signed-in user
- Gmail connect still remains separate
- Gmail scan still remains manual

## Tests

Add or update backend tests for:

- Google ID token verification accepts a token with small clock skew within the configured leeway.
- An immature/not-yet-valid token outside allowable behavior is handled gracefully by the auth callback or auth service rather than causing an unhandled 500.
- No user/AuthIdentity/Gmail account/ingestion side effects occur on that failed auth path.

Add or update frontend tests only if you change frontend behavior or visible auth error handling.

## Validation

Run:

```text
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

If no frontend files change, frontend validation is still preferred because this touches auth flow behavior that gates the app shell.

## Report Back

Report:

- files changed
- exact clock-skew leeway value
- how the failed clock-skew callback is handled
- tests added/updated
- validation results
- whether any live browser retest was performed

## Clarification Gate

Before implementation, provide a concise plan.

You must have human approval before executing the implementation.

If you find that the current auth library does not support leeway cleanly, stop and ask rather than hand-rolling fragile JWT parsing.
