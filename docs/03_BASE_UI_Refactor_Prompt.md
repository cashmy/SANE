# BASE Prompt 03 - UI/UX Refactor

## Role

You are the BASE coding LLM for SANE.

You may be a different model from the one that created the current scaffold and Stage 1 ALPHA candidate.

Assume prior chat context may be incomplete.

Do not infer missing product intent from the current UI alone.

Before making changes, read the referenced project docs and summarize your understanding.

If anything is unclear, ask clarifying questions before implementing.

---

## Required Reading

Read these project-local docs first:

```text
docs/RBA_HOMSP_BASE_Primer.md
docs/00_BASE_Context_and_Guardrails.md
docs/Stage1_ALPHA_Review_Issue_Register.md
```

Also use this governing UI direction from the RBA artifact workspace:

```text
D:\@Artifact_Generation\109_RBA_Refaction_Based_Architecture\SANE-RBA\12_SANE_UI_UX_Governance_Direction.md
```

Preferred project-local copy:

```text
docs/SANE_UI_UX_Governance_Direction.md
```

If external workspace paths are unavailable, use the project-local copy. If both are unavailable, ask for the UI governance artifact instead of guessing.

Use this local reference image for visual/layout direction:

```text
docs/sample_image.png
```

If your environment allows image viewing, inspect it before implementing. If you cannot view images, say so in your report and rely on the textual reference intent below.

---

## Current Problem

The current Stage 1 ALPHA UI is functionally successful but visually and structurally too expository.

It resembles common AI-generated app pages:

- large explanatory panels
- process-description cards
- low-density review cards
- all workflow pieces on one long page

This does not fit SANE's real operating problem.

SANE must support high-volume email-source governance.

Known volume context:

- approximately 27,000 Gmail Promotions emails
- approximately 28,500 Gmail Updates emails

Therefore, the UI must move toward an operational console that summarizes sources/vendors/clusters rather than presenting individual email cards as the primary review surface.

---

## Refactor Goal

Refactor the frontend into an operational Stage 1 ALPHA console.

The result should support:

- scanning
- filtering
- source/vendor comparison
- decision completion
- separate decision history
- high-volume review assumptions

Do not change backend behavior unless the frontend refactor requires small API-safe adjustments.

If backend changes appear necessary, ask before implementing.

---

## Required UI Direction

Implement an app shell with:

- persistent left sidebar navigation
- top toolbar
- main content area

Initial views:

- Review
- Decisions
- Connections
- Settings

The Review view should include:

- compact summary tiles
- search control
- category/status filters
- paginated or page-size-controlled source/vendor table
- clear row actions for Stage 1 decisions
- explicit indication that external actions are not executed

The Decisions view should include:

- prior decision history separate from the Review queue
- compact table/list presentation
- external action status visible as not executed

Connections and Settings may be placeholder views, but they should look like intentional app views, not large explanatory marketing panels.

---

## Data Interpretation

The current backend candidate shape is message-like.

For this refactor, adapt the frontend presentation toward source/vendor/cluster review without requiring backend schema changes.

You may group or present the existing demo candidates as source rows using available fields:

- sender_name
- sender_email
- mailbox_category
- candidate_reason
- classifier_signal
- suggested_decision
- processing_state

Do not pretend real clustering exists yet.

Label the ALPHA behavior honestly.

---

## Visual Direction

Use a light operational interface.

Preferred visual qualities:

- compact
- calm
- professional
- table-first
- clear status chips
- restrained color
- minimal explanatory copy

Palette direction:

- neutral operational background
- restrained blue or teal primary
- cool gray structural neutrals
- green/success for completed or safe state
- amber/warning for attention or deferred action
- red/destructive only for high-risk or irreversible actions

Avoid:

- oversized explanatory cards
- landing-page hero sections
- decorative gradients/orbs
- excessive purple
- beige/sand-dominant theme
- visual clutter from irrelevant charts/widgets

---

## Reference Intent

A Figma-style operational dashboard reference was used during review.

The local reference image is:

```text
docs/sample_image.png
```

Borrow the idea of:

- sidebar + toolbar app shell
- compact operational cards
- table/pagination structure
- status chips
- row actions

Do not copy:

- project-management content
- finance widgets
- employee lists
- exact styling
- chart-heavy dashboard clutter

---

## Preserve Stage 1 Guardrails

Do not implement:

- Gmail OAuth
- Gmail API access
- real unsubscribe/archive/delete actions
- external AI provider calls
- GTD workflow
- billing or subscription enforcement
- multi-account support
- analytics dashboards

Do not imply that external email actions occurred.

All decisions still update local ALPHA state only.

---

## Testing Requirements

Update frontend tests to reflect the new app shell and views.

Tests should verify:

- sidebar navigation renders
- Review view displays source/vendor rows
- Decisions view is separate from Review
- decision controls still require user action
- external actions remain visibly not executed
- loading and error states still work where practical

Run:

```bash
cd frontend
npm run test:run
npm run build
```

If you change backend code, also run:

```bash
cd backend
python -m pytest
```

---

## Reporting Back

After implementation, report:

- your understanding after reading the docs
- files changed
- UI structure implemented
- tests changed or added
- commands run and results
- assumptions made
- any clarifying questions that remain
- any areas where the current backend shape limits the UI

If you are uncertain about a design or product decision, stop and ask instead of guessing.
