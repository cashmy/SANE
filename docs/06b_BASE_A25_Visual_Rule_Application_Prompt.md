# Prompt 06b - A25 Visual Rule Application

## Role

You are the BASE implementation LLM for the SANE project.

SKY is the human product/governance authority.

CORE has translated the UI review into concrete visual rules.

## Why This Pass Exists

The first A25 pass improved operational clarity, but it did not sufficiently apply a concrete visual design grammar.

The issue is not functionality.

The issue is that the UI still needs stronger component-level visual intent so human reviewers can clearly see product progress.

## Required Context

Read only:

- `docs/RBA_HOMSP_BASE_Primer.md`
- `docs/SANE_UI_UX_Governance_Direction.md`
- `docs/SANE_Visual_Rule_Extraction_A25.md`
- `frontend/src/styles/theme.css`
- `frontend/src/App.css`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/views/ReviewView.tsx`
- `frontend/src/components/views/DecisionsView.tsx`
- `frontend/src/App.test.tsx`

Do not read the full issue register unless human asks you to. The full register is CORE/SKY governance memory.

## Active Task

Apply the visual rules in:

```text
docs/SANE_Visual_Rule_Extraction_A25.md
```

This is still A25 only.

## Clarification Gate

Before executing implementation:

1. Summarize the most important visual rule changes you will apply.
2. List files you expect to touch.
3. State whether markup changes are needed or whether CSS is sufficient.
4. State whether frontend tests need updates.
5. Ask clarifying questions if any visual rule conflicts with the current implementation.
6. You must have human approval before implementation.

Do not treat post-hoc assumption reporting as a substitute for this gate.

## Implementation Requirements

Apply concrete visual improvements for:

- active navigation
- toolbar hierarchy
- local user/status block
- KPI cards
- filter bar
- batch action bar
- selected row state
- email count treatment
- table header/body scan rhythm
- pagination control cluster
- Decisions current/revision states
- light and dark mode consistency
- future dashboard compatibility through disciplined summary/KPI structure

Use existing semantic tokens where possible.

Prefer CSS and small markup refinements.

Do not add new product functionality.

## Preserve Existing Behavior

Preserve:

- source-oriented review table
- email count field
- pagination/page size behavior
- filtering/search behavior
- batch selection and confirmation
- single-row decision actions
- Decisions view revision behavior
- light/dark toggle
- Local ALPHA User
- local-only external action boundary

## Hard Scope Boundaries

Do not modify:

- backend files
- database files
- API contracts
- service logic
- environment config

Do not add:

- Gmail
- OAuth
- PostgreSQL
- billing
- GTD
- analytics dashboards
- charts
- fake dashboard widgets
- analytics cards
- hero panels
- large explanatory copy

Do not reduce table density.

Do not turn rows into cards.

The visual rule artifact notes future dashboard/cockpit potential. For this pass, preserve compatibility with that future direction through layout discipline only. Do not implement dashboards now.

## Testing

Run:

```powershell
cd frontend
npm run test:run
npm run build
```

If visible text/accessibility names change, update frontend tests only where necessary.

## Report

Report:

- files changed
- visual rules applied
- whether behavior changed
- test/build results
- whether A25 is now resolved or still needs SKY browser review
- any remaining visual limitations
