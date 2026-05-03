# Prompt 09 - Live OAuth and Gmail Reality Contact

## Status

Ready for execution after Prompt 08 / 08b / 08c / 08d have been reviewed and validated.

Prompt 09 is a reality-contact pass, not a broad feature expansion pass.

Current validation baseline before Prompt 09:

```text
backend: python -m pytest -> 51 passed
frontend: npm run test:run -> 20 passed
frontend: npm run build -> passed
alembic head/current -> 0006_gmail_credential_storage
```

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this post-Prompt-08 live validation prompt.

## Active Execution Context

Active task:

- validate real Google sign-in
- validate real Gmail mailbox connection
- validate one bounded manual Gmail scan
- preserve all Prompt 08 / 08b / 08c / 08d governance boundaries

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, especially A32/A33/A40/A41/A42 and Prompt 08 notes
- `docs/08_BASE_Auth_Gmail_Manual_Ingestion_Prompt.md`
- `docs/08b_BASE_Local_Dev_Auth_Bypass_Prompt.md`
- `docs/08c_BASE_Auth_Status_UI_Polish_Prompt.md`
- `docs/08d_BASE_Authenticated_Empty_State_UX_Prompt.md`
- backend auth and Gmail routers/services
- backend config and `.env.example`
- Alembic migrations
- Connections view
- README setup instructions
- current backend and frontend tests

## Clarification Gate

Before executing implementation:

1. Confirm Prompt 08, 08b, 08c, and 08d are complete and validated.
2. State what is currently mocked and what can be live-tested.
3. State exactly what Google Cloud OAuth setup SKY must perform manually.
4. State the required redirect URIs.
5. State the required `.env` variables, using placeholders only.
6. State the live validation path for Google sign-in.
7. State the live validation path for Gmail connection.
8. State the live validation path for one bounded manual scan.
9. State how you will prevent scan-on-app-open or scan-on-sign-in.
10. State whether `SANE_AUTH_MODE` must be switched from `local_dev` to `google_oauth` for live validation.
11. Ask clarifying questions if live OAuth setup, redirect paths, credential handling, auth mode, or scan scope is ambiguous.
12. You must have human approval before implementation or live testing.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Move from mocked OAuth/Gmail behavior to first controlled live validation.

This pass should prove that SANE can:

- sign in with Google
- maintain an app session
- separately connect Gmail
- store Gmail credentials through the approved ALPHA credential path
- run one explicit manual Gmail scan
- create/update source review rows from live Gmail metadata
- record an `IngestionRun`

Prompt 09 should not replace the local-dev UI review path. Local-dev auth remains useful for UI/workflow inspection when Google OAuth is not configured.

## Hard Governance Rules

SANE must never scan, import, or analyze Gmail merely because:

- the app opens
- the user signs in
- Gmail is connected
- the Connections view renders

Only explicit manual scan is allowed.

No external email actions are allowed.

Do not request Gmail modify/delete/send scopes.

Do not store full email bodies.

Do not write real secrets into tracked files.

Do not remove or weaken local-dev auth, but do not use it as proof that live OAuth works.

## Manual Setup Documentation

Update project docs only as needed to guide the human through setup.

Document:

- how to create/configure the Google Cloud OAuth client
- which OAuth consent screen settings matter for local ALPHA
- required redirect URIs
- required local `.env` values
- how to generate a local credential encryption key
- how to run backend/frontend for live testing
- what live validation steps should be performed
- when to use `SANE_AUTH_MODE=local_dev` vs `SANE_AUTH_MODE=google_oauth`

Use placeholders only.

Never commit real:

- client secret
- JWT secret
- credential encryption key
- refresh token
- access token

## Live Validation Target

For live Google/Gmail validation, local `.env` should use:

```text
SANE_AUTH_MODE=google_oauth
SANE_DEBUG=true
```

`SANE_AUTH_MODE=local_dev` is for UI/workflow review only and does not validate Google OAuth or Gmail access.

Minimum live validation path:

```text
1. Start backend and frontend.
2. Open frontend.
3. Sign in with Google.
4. Confirm authenticated app shell and account menu.
5. Open Connections.
6. Connect Gmail through separate authorization.
7. Confirm Gmail account status is connected.
8. Select limit 50.
9. Run manual scan for CATEGORY_PROMOTIONS.
10. Confirm IngestionRun completed or failed with clear status.
11. Confirm Review shows source rows created from the connected Gmail account.
```

Expected first-run visual checks:

- If sign-in succeeds before Gmail connect, Review should show the authenticated empty state from A46.
- If Gmail connects before scan, Review should show the connected/no-scan empty state.
- After scan, Review should show source rows or the scan-complete/no-sources empty state.

If live validation cannot be completed in the current environment, report exactly why and leave clear manual steps.

## Testing

Automated tests should remain mocked and deterministic.

Do not make automated tests require real Google or Gmail network access.

Add or update tests only if the live validation pass changes code behavior.

Backend tests should still prove:

- no scan on app startup
- no scan on sign-in
- manual scan requires authenticated user
- manual scan requires connected Gmail account
- scan respects bounds
- IngestionRun records status
- source rows are scoped to the connected EmailAccount

Frontend tests should still prove:

- unauthenticated state shows sign-in path
- signed-in shell shows account surface
- Connections view is the Gmail control center
- scan occurs only from explicit user action

Prompt 09 is allowed to make small bug fixes discovered during live validation, but it must not broaden scope. If live validation exposes an architectural issue, stop and report before implementing a broad repair.

## Out Of Scope

Do not implement:

- full mailbox import
- scan-on-open
- scheduled scans
- unsubscribe/archive/delete actions
- AI provider classification
- GTD workflow
- billing/subscriptions
- Microsoft/IMAP integration
- multi-account management UI beyond what Prompt 08 already supports
- full email body storage
- local-dev auth redesign
- broad first-run UI redesign beyond small live-validation fixes

## Validation

Run:

```powershell
cd backend
python -m pytest

cd ../frontend
npm run test:run
npm run build
```

Also run Alembic validation:

```powershell
cd backend
python -m alembic current
python -m alembic upgrade head
```

If live validation is performed, report exactly what was live-tested.

If live validation is not performed, report exact manual validation instructions.

## Report

Report:

- files changed
- documentation added/updated
- Google Cloud setup assumptions
- redirect URIs
- live-tested behavior
- mocked-only behavior
- validation results
- any OAuth/Gmail errors encountered
- remaining risks before Prompt 10
