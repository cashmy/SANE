# BASE Prompt 04 - Theme and Color Token Integration

## Role

You are the BASE coding LLM for SANE.

Your task is to implement the SANE theme/color token system.

This pass is intended to resolve issue A19 from:

```text
docs/Stage1_ALPHA_Review_Issue_Register.md
```

It may also support A18 if light/dark mode plumbing is needed, but do not expand beyond theme/color/display-mode work.

---

## Required Reading

Before coding, read:

```text
docs/RBA_HOMSP_BASE_Primer.md
docs/00_BASE_Context_and_Guardrails.md
docs/SANE_UI_UX_Governance_Direction.md
docs/Stage1_ALPHA_Review_Issue_Register.md
```

---

## Clarification Gate

Before implementing, inspect the available CSS color files in the root folder and summarize:

- file names found
- whether they appear to be light or dark mode
- whether variable names collide
- whether variables are already namespaced
- your proposed merge strategy

If the file contents or naming are ambiguous, stop and ask clarifying questions before editing.

Do not treat reporting assumptions after implementation as a substitute for clarification.

Proceed only if the merge strategy is clear.

---

## Context

Radix UI custom color CSS was generated outside the app and copied into the project.

Expected files may include names similar to:

```text
Colors-accent-light.css
Colors-background-light.css
Colors-grey-light.css
Colors-accent-dark.css
Colors-background-dark.css
Colors-grey-dark.css
```

Do not assume exact file names. Inspect the workspace.

---

## Goal

Merge the generated color CSS into a clean project theme system.

Preferred result:

```text
frontend/src/styles/theme.css
```

or another clearly named theme file if the project already has a better convention.

The theme system should include:

- raw palette scale variables
- semantic SANE UI tokens
- light mode definitions
- dark mode definitions
- no Radix package dependency unless already present and necessary

---

## Required Theme Structure

Use a two-layer approach.

Layer 1: raw palette scales.

Example:

```css
:root {
  --accent-1: ...;
  --accent-2: ...;
  --gray-1: ...;
  --background-1: ...;
}

[data-theme="dark"] {
  --accent-1: ...;
  --accent-2: ...;
  --gray-1: ...;
  --background-1: ...;
}
```

Layer 2: semantic SANE tokens.

Example:

```css
:root,
[data-theme="light"] {
  --color-bg: var(--background-1);
  --color-surface: var(--background-2);
  --color-surface-muted: var(--gray-2);
  --color-border: var(--gray-6);
  --color-text: var(--gray-12);
  --color-text-muted: var(--gray-10);
  --color-primary: var(--accent-9);
  --color-primary-hover: var(--accent-10);
  --color-focus: var(--accent-8);
  --color-success: ...;
  --color-warning: ...;
  --color-danger: ...;
}
```

You may define success/warning/danger with existing palette values or stable explicit values if the generated files do not include those scales.

---

## Required Semantic Tokens

Define at least:

```text
--color-bg
--color-app-shell
--color-sidebar
--color-sidebar-text
--color-sidebar-active
--color-surface
--color-surface-muted
--color-border
--color-text
--color-text-muted
--color-primary
--color-primary-hover
--color-accent
--color-focus
--color-success
--color-success-bg
--color-warning
--color-warning-bg
--color-danger
--color-danger-bg
```

Add additional tokens only if they simplify the current CSS.

---

## Display Mode

If the app does not yet support light/dark mode, add a small display-mode toggle.

Preferred:

- visible in the app shell toolbar or user/account area
- defaults to light mode
- toggles `data-theme="light"` / `data-theme="dark"` on the document root or app root
- persists in `localStorage` if simple

Do not build a complex settings system.

---

## CSS Refactor

Update the current frontend CSS to use semantic tokens instead of hardcoded colors where practical.

Do not redesign the UI layout in this pass.

Do not change backend code.

Do not add unrelated frontend features.

Do not add Gmail/OAuth/AI/billing/GTD/multi-account behavior.

---

## Cleanup

After merging:

- remove or archive the separate generated color CSS files if they are no longer imported or needed
- ensure the final theme file is imported by the frontend
- avoid leaving duplicate/conflicting color definitions

If removal feels risky because file usage is unclear, ask before deleting.

---

## Tests and Validation

Update or add frontend tests if display-mode behavior is added.

Run:

```bash
cd frontend
npm run test:run
npm run build
```

Backend tests are not required unless backend files are changed.

---

## Reporting Back

Report:

- files inspected
- merge strategy used
- files changed
- files removed or left intentionally
- semantic tokens created
- whether light/dark mode was added
- tests/build commands and results
- assumptions made
- any unresolved questions

