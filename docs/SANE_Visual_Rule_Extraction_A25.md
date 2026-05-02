# SANE Visual Rule Extraction - A25b

## Purpose

This artifact converts SANE's UI direction, current screenshot review, and the reference dashboard screenshot into concrete visual rules for BASE implementation.

The prior A25 pass improved operational clarity but did not sufficiently translate the reference image into a stronger visual system.

This artifact narrows the next pass from "make it polished" to component-level visual rules.

The reference image should be interpreted as more than a sidebar/table example. It also suggests a future operational cockpit pattern. For A25b, SANE remains table-first, but the visual system should not block a later compact dashboard overview band.

## Design Intent

SANE should feel like a compact operational console for high-volume email-source governance.

The UI should communicate:

- scale
- scanning
- decision readiness
- local-only safety
- current work state
- previous decision history

It should not communicate:

- marketing
- tutorial/exposition
- generic AI dashboard
- decorative redesign
- individual email reading

## Token Application Rules

Use existing semantic tokens in `frontend/src/styles/theme.css`.

Do not add new palette families unless a missing token is truly blocking.

### Accent Role

Use the primary accent for:

- active navigation marker
- focus rings
- KPI emphasis
- current page indicator
- selected row marker
- selected count badge

Do not overuse the accent on every button or chip.

### Neutral Role

Use neutrals for:

- app background
- table surfaces
- toolbar structure
- inactive controls
- table borders
- secondary text

Neutral structure should create depth without beige/sand warmth.

### Semantic Status Role

Use semantic colors consistently:

- success/green: `Keep Source`
- warning/amber: `Mark as Low Value`
- danger/red: `Queue for Unsubscribe`
- neutral/gray: pending review, not executed, inactive states
- accent/blue: selected state, pagination/current progress, primary counts

## Typography Rules

Use compact operational typography.

Suggested hierarchy:

- app brand: 18px, 700, high contrast
- page title: 16-18px, 650, primary text
- stage label / section label: 11-12px, uppercase, muted, letter-spaced
- KPI number: 24-28px, 750, accent or semantic emphasis
- table header: 11-12px, uppercase, muted, 650
- source name: 14px, 650, primary text
- representative subject: 12-13px, muted
- source reason/supporting copy: 12px, subtle
- metadata: 11-12px, muted

Avoid large hero-scale typography.

## App Shell Rules

### Sidebar

The sidebar should feel anchored and product-specific.

Rules:

- keep the dark structural sidebar
- active nav should have a visible accent rail or accent marker
- active nav should have a stronger surface state than hover
- inactive nav should remain subdued
- local user area should look like an account/status block, not loose footer text
- Stage 1 ALPHA should remain visible but subdued

### Toolbar

The toolbar should show context and status.

Rules:

- keep page title compact but stronger than current
- keep stage label near the title
- local-only status and theme toggle should read as utility controls
- avoid turning the toolbar into a banner

## Summary / KPI Rules

The summary strip should communicate operational state at a glance.

Rules:

- KPI cards should be compact and visually aligned
- each KPI should have a left accent rail or top accent line
- Pending Review count should use primary accent
- Sources With Decision count should use success or accent
- External Actions should remain neutral/safety-oriented
- supporting KPI text should be short and operational
- cards should not become large dashboard tiles

## Future Dashboard Compatibility

Do not implement dashboard widgets in A25b.

However, preserve visual compatibility with a future compact dashboard/cockpit band.

The reference image was selected partly because it shows how an operational app can combine:

- navigation
- compact status surfaces
- work table
- filters
- pagination
- dense operational controls

SANE may later need dashboard-style summary widgets for:

- sources reviewed
- estimated email reduction
- high-volume sources
- pending review by category
- queued unsubscribe intents
- last Gmail scan
- ingestion run history
- decision trend over time
- future GTD conversion once Tier 2 exists

A25b should keep the current UI table-first while making the summary/KPI region visually disciplined enough that future compact dashboard widgets can be added without redesigning the app shell.

Guardrail:

Do not add charts, trend widgets, analytics cards, or fake dashboard data in this pass.

## Filter Bar Rules

The filter bar should read as a tool row.

Rules:

- visually group search, filters, and refresh as one control surface
- search should be the dominant control
- filters should have consistent height and width rhythm
- Refresh should be secondary
- avoid excess vertical space

## Batch Action Rules

Batch actions are important because they make high-volume work feel real.

Rules:

- batch bar should become visually active only when rows are selected
- selected count should be a compact accent badge
- when no rows are selected, batch actions should feel subdued
- when rows are selected, the bar should show stronger accent treatment
- action buttons should stay semantic:
  - Keep Source = success
  - Mark as Low Value = warning
  - Queue for Unsubscribe = danger
- confirmation behavior must remain unchanged

## Table Rules

The table is the main product surface.

Rules:

- header row should have stronger neutral structure than body rows
- row hover should be subtle but visible
- selected rows should be unmistakable:
  - accent left rail, tinted background, or both
- table rows should remain dense
- row separators should be visible but not heavy
- source name should be the strongest text in the row
- representative subject/reason should be readable but secondary
- sender emails should be compact and scannable
- email count should be visually emphasized as a prioritization metric
- state and signal chips should not overpower source names or counts

## Email Count Rules

Email count is a high-value prioritization signal.

Rules:

- display count as a compact metric, not plain table text
- count number should be accent-colored and tabular
- label should be tiny uppercase or muted
- count cell should align consistently down the column
- higher counts should be visually easy to find while scanning

## Pagination Rules

Pagination is functionally significant and must be visually legible.

Rules:

- pagination should look like a control cluster, not an afterthought
- page summary should be easy to find
- current page should be visually distinct
- previous/next controls should have clear enabled/disabled states
- page size should remain visible but secondary

## Decisions View Rules

Decision history should communicate current vs revision clearly.

Rules:

- current decision rows should read as current state
- superseded rows should be visually quieter
- revision marker should be visible but not alarming
- current/revision chips should have distinct treatment
- change-decision actions should remain grouped
- external action status should stay neutral and local-only

## Light / Dark Mode Rules

Both modes should look intentional.

Rules:

- do not tune only light mode
- selected row, active nav, chips, batch bar, and pagination must remain visible in dark mode
- avoid low-contrast muted text in dark mode
- semantic colors should remain readable without becoming neon

## Specific Non-Goals

Do not:

- add charts
- add analytics widgets
- add hero/explanatory panels
- create decorative gradients/orbs
- change backend behavior
- change API contracts
- add Gmail/OAuth/PostgreSQL work
- reduce table density
- replace the table with cards
- copy the sample image's purple-heavy palette

## A25b Success Criteria

A25b succeeds if a human can immediately see:

- the app shell is more intentional
- the table is the primary work surface
- email counts matter
- selected rows and batch state are obvious
- pagination is visible as part of scale handling
- decision history clearly separates current and revision states
- light and dark modes both feel designed
