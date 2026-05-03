# Prompt 08c - Auth and Status UI Polish

## Status

Execute after Prompt 08b if local-dev auth works but the auth/status UI needs cleanup.

This is a narrow frontend-focused repair prompt.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this Prompt 08c UI polish pass.

## Active Execution Context

Active task:

- A48 - auth/status UI polish
- optionally touch A46 empty-state polish only if the same files are already being touched and the change is small

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/Stage1_ALPHA_Review_Issue_Register.md`, only A46/A47/A48
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/AccountMenu.tsx`
- `frontend/src/components/ThemeToggle.tsx` if present
- `frontend/src/components/SignInScreen.tsx`
- `frontend/src/App.css`
- relevant frontend tests

## Clarification Gate

Before executing implementation:

1. Confirm local-dev auth from Prompt 08b is present.
2. Summarize the current top nav/auth/status/theme layout.
3. State how you will separate auth/runtime status from display mode controls.
4. State how you will simplify the sidebar/footer identity area.
5. State whether A46 empty-state polish is touched or left deferred.
6. State the frontend files and tests you expect to change.
7. Ask clarifying questions if control placement, labels, or status visibility are ambiguous.
8. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Make the authenticated shell visually clearer now that SANE has:

- Google OAuth mode
- local-dev auth mode
- app session identity
- Gmail connection status
- display mode toggle

The UI should not visually conflate these concepts.

## Required UI Direction

Separate:

```text
auth/runtime status
```

from:

```text
display mode preference
```

The top-right toolbar should not make `Local only` and `Dark mode` appear as one combined pill/card.

Acceptable approaches:

- separate adjacent controls with distinct spacing/borders
- place auth status in account menu/sidebar and keep theme toggle standalone
- show a compact `Local dev` status chip and a separate theme toggle

Use the existing design language and tokens.

Do not redesign the whole shell.

## Sidebar/Footer Direction

Simplify persistent identity/status display.

Avoid showing too much duplicated detail in the sidebar footer.

Preferred local-dev footer content:

```text
Local ALPHA User
Local dev
Sign out
```

The local email may be omitted from the persistent footer or moved to an account/menu detail surface.

Keep Stage 1 ALPHA visible only if it remains visually quiet and useful.

## Guardrails

Do not change:

- auth behavior
- local-dev auth behavior
- Google OAuth behavior
- Gmail connection behavior
- scan behavior
- backend APIs unless absolutely necessary
- token/credential handling

No Gmail scan should be triggered by UI render.

No external email actions are allowed.

## Testing

Frontend tests should prove:

- local-dev authenticated shell still renders
- sign-out remains available
- theme toggle remains available
- auth status and theme toggle are not dependent on each other
- no scan action is triggered by rendering the shell

Backend tests are not expected unless behavior changes, which should be avoided.

## Validation

Run:

```powershell
cd frontend
npm run test:run
npm run build
```

Run backend tests only if backend files change:

```powershell
cd backend
python -m pytest
```

## Report

Report:

- files changed
- layout/status changes
- whether A46 was touched or left deferred
- tests added/updated
- validation results
- any remaining UI review concerns

