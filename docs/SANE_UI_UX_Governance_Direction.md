# SANE UI/UX Governance Direction

## Purpose

This artifact records the UI/UX direction for SANE after review of the first Stage 1 ALPHA candidate.

It converts UI review findings into constraints for frontend refactor work.

This project-local copy exists so BASE coding agents can access the guidance without needing access to the separate RBA artifact workspace.

---

## Core UI Reframe

SANE should be designed as an operational email-source governance console.

It should not be designed as an expository AI-generated app page.

The next UI direction should prioritize:

- scanning
- comparison
- source/vendor review
- decision completion
- clear navigation
- high-volume usability

---

## Interface Type

Selected type:

- operational dashboard
- source/vendor review console
- inbox governance work surface

Not selected:

- marketing page
- explanatory product page
- generic dashboard
- individual email reader
- full email client

---

## Primary User Posture

The user is mainly:

- scanning
- comparing
- triaging
- deciding
- reviewing prior decisions

The UI should assume the user is there to work, not to learn what the product is from scratch every time.

---

## Density

Selected density:

- dense operational

Reason:

The real problem involves very high email volume.

Current reference volume:

- approximately 27,000 Gmail Promotions emails
- approximately 28,500 Gmail Updates emails

The UI must not depend on large individual email cards as the primary review surface.

---

## Primary Data Object

The primary review object should move toward:

```text
email source / vendor / sender cluster
```

rather than:

```text
single email message card
```

The system may still show representative message details, but the main work surface should summarize sources/clusters.

---

## Navigation Model

Use a persistent app shell.

Preferred structure:

- left sidebar navigation
- top toolbar for search/filter/status controls
- main content area

Initial views:

- Review
- Decisions
- Connections
- Settings

Optional later views:

- Sources
- Reports
- Help

Do not place all workflows on a single long scrolling page.

---

## Primary Layout Pattern

Preferred layout:

```text
summary metrics + source/vendor table + detail drawer or expandable row
```

The main Review view should include:

- compact summary tiles
- search
- category/status filters
- paginated source/vendor/cluster table
- row-level decision actions
- detail access for representative messages or reasoning

The Decisions view should contain prior decisions/history separately from the main review queue.

---

## Display Mode

Initial display mode:

- light mode first

Do not add theme switching yet unless it is trivial and does not distract from the workflow.

---

## Palette Direction

Preferred palette:

- neutral operational background
- restrained blue or teal primary
- cool gray structural neutrals
- green/success for completed or safe state
- amber/warning for attention or deferred action
- red/destructive only for high-risk or irreversible actions

Avoid:

- overly warm beige/sand dominance
- excessive purple unless explicitly justified
- decorative gradients/orbs
- visual noise that competes with source review

---

## Reference Screenshot

The local reference image is:

```text
docs/sample_image.png
```

Use it to communicate:

- sidebar + top toolbar app shell
- compact operational cards
- table/pagination structure
- status chips and row actions

Do not copy:

- project-management content
- finance widgets
- employee lists
- decorative chart density
- exact purple-heavy styling

---

## Explanatory Content Rule

Keep explanatory UI text sparse and contextual.

Avoid:

- large hero-like explanation panels
- repeated process-description cards
- long educational copy in the main workflow
- UI that teaches the app before letting the user operate it

Use short contextual labels, helper text, tooltips, empty states, and warnings only where they support action.

---

## Interaction Expectations

Include or preserve:

- search
- filtering
- pagination or page-size control
- status chips
- clear row actions
- loading states
- error states
- empty states
- explicit indication that no external email actions are executed

Consider but do not overbuild:

- detail drawer
- expandable rows
- undo/reconsideration

Do not add:

- bulk actions
- real unsubscribe
- Gmail OAuth
- Gmail API calls
- billing
- GTD workflow
- multi-account support

---

## Success Criteria

The refactored UI should:

- feel like a real operational application
- support high-volume review assumptions
- make the main work surface visible quickly
- separate review work from decision history
- avoid expository AI-generated page structure
- preserve Stage 1 ALPHA honesty
- keep external actions visibly not executed

