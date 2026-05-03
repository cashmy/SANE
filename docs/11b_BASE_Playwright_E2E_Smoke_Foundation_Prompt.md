# Prompt 11b - Playwright E2E Smoke Test Foundation

## Status

Ready for BASE clarification gate after Prompt 11 is implemented.

Prompt 11b may produce follow-up Prompt 11c/11d repair prompts if Playwright setup reveals environment-specific friction.

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has curated this E2E smoke-test foundation prompt.

## Context

Prompt 11 implemented the real-data Review/Decisions workflow usability pass.

Current validation includes backend tests, frontend Vitest tests, build validation, and manual/live browser validation by BASE/SKY.

However, the project does not yet have repeatable Playwright tests committed into the repo.

Prompt 11b adds a small, educational, repeatable browser E2E test layer.

## Active Execution Context

Active task:

- install/configure Playwright for the frontend/project
- add a small number of repeatable browser smoke tests
- avoid real Google OAuth/Gmail dependency
- document how to run E2E tests
- preserve existing Vitest/backend validation

Do not treat the full issue register as the active contract. The full register is CORE/SKY governance memory.

## Required Context

Before proposing or implementing changes, inspect:

- frontend `package.json`
- current frontend test setup
- current backend auth modes
- local-dev auth behavior
- Review, Decisions, and Connections views
- API/client behavior
- README
- issue register

## Clarification Gate

Before implementation:

1. State whether Playwright is already installed/configured.
2. State where the Playwright config and tests will live.
3. State how tests will start or connect to frontend/backend servers.
4. State how tests will set or isolate required environment variables without requiring SKY to manually edit `.env`.
5. State whether tests will use local-dev auth, mocked API, seeded backend data, or another deterministic setup.
6. State which 2-3 E2E smoke tests will be added.
7. State why real Google/Gmail OAuth will not be tested by Playwright in this pass.
8. Ask clarifying questions if auth mode, server startup, seeded data, environment variables, or CI assumptions are ambiguous.
9. Ask any other clarifying questions from code inspection, test expectations, tooling constraints, or conflicts between prompt and implementation.
10. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Goal

Create a small repeatable E2E testing layer that demonstrates the testing ladder:

```text
backend unit/API tests
-> frontend component tests
-> Playwright browser smoke tests
-> manual SKY live OAuth/Gmail reality validation
```

This is partly product quality and partly student demonstration value.

## Required Test Direction

Add 2-3 smoke tests.

Preferred tests:

### 1. Local-Dev Auth Shell Smoke

Verify:

- app loads in local-dev auth mode
- user can enter through local-dev auth if needed
- app shell renders
- Review / Decisions / Connections navigation works

### 2. Connections Safety Smoke

Verify:

- Connections page renders
- local-only scan/reset safety copy is visible
- reset UI can open and cancel without destructive API action
- no real Gmail OAuth flow is required

### 3. Review / Decisions Workflow Smoke

Verify one or more:

- Review source table loads with deterministic/local data
- expandable evidence row opens/closes if available
- Decisions pagination controls render if deterministic data exists
- no external action copy remains visible

If deterministic data setup makes one of these impractical, propose the smallest reliable alternative in the clarification gate.

## What Not To Test With Playwright Yet

Do not automate:

- real Google login
- real Gmail OAuth consent
- real Gmail scans
- real mailbox reset against SKY's Gmail account
- CAPTCHA/Google account flows
- production billing/subscription

Rationale:

Those flows are credential-dependent, brittle, and inappropriate for student/CI repeatability. They remain manual SKY reality-contact checks.

## Implementation Notes

Possible implementation:

- add `@playwright/test`
- add `playwright.config.ts`
- add `frontend/e2e/*.spec.ts` or project-consistent equivalent
- add scripts such as:

```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui"
```

If Playwright browser binaries need installation, document the command.

Do not overbuild CI/CD integration in this pass.

## Environment Safety

Playwright tests must not require real secrets.

Preferred:

- local-dev auth mode for E2E only
- deterministic backend test/dev data
- or frontend-level API mocking if that is cleaner and explicit

Do not require SKY to manually change the normal development `.env` from `google_oauth` to `local_dev`.

The E2E setup should isolate auth mode by one of these approaches:

- use Playwright `webServer` commands that set `SANE_AUTH_MODE=local_dev` only for the spawned backend process
- use a dedicated `.env.e2e` / test environment loading approach if consistent with the backend settings pattern
- use frontend/API mocking if a backend-backed local-dev flow is too invasive

If the current backend settings system cannot support an isolated E2E auth mode cleanly, stop in the clarification gate and propose the smallest safe approach.

E2E local-dev auth should be treated as a separate test/development identity from SKY's real Google OAuth user. It must not connect to, scan, reset, or mutate SKY's live Gmail account.

If using backend live server:

- do not point at production
- do not use SKY's live Gmail scan path
- do not mutate real Gmail
- do not rely on SKY's active browser session or real auth cookies
- do not require real Google OAuth secrets

## Documentation

Update README or a project docs file with:

- how to install Playwright browsers if needed
- how to run E2E tests
- what environment mode the E2E tests use
- whether the E2E user is local-dev/mock/test-only
- what the tests cover
- what they intentionally do not cover

## Validation

Run:

```powershell
cd frontend
npm run test:e2e
npm run test:run
npm run build
```

Run backend tests if backend files/config/test data are changed:

```powershell
cd backend
python -m pytest
```

If Playwright cannot run in the current environment, report the exact blocker and leave the test setup as close to runnable as possible.

## Report

Report:

- files changed
- Playwright version/tooling installed
- E2E test files added
- how tests start/connect to app
- validation results
- any environment/browser install blockers
- why real OAuth/Gmail is not automated
- recommended 11c/11d follow-up if needed
