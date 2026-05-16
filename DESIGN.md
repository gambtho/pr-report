# Design

Visual system for headrep. Pairs with PRODUCT.md. Every section here is a commitment, not a starting point: if a future change wants to break a rule below, update this file first.

## Aesthetic direction

A maintainer's printed queue, set in type. Closer to a well-typeset document or a `gh pr list` rendered with care than to a SaaS dashboard. Identifiers (PR numbers, commit SHAs, label names, bucket counts) are monospace because that is how they are read in the terminal and in GitHub URLs. Prose is a humanist sans. The page reads top to bottom; buckets are sections, not cards.

Three properties to optimize for, in order: legibility while glancing, density without crowding, calm. The page should feel like an inbox that has already been sorted.

## Theme

Light. The scene is a daylit laptop screen between meetings, not an SRE staring at incidents at 2am. Dark mode is the first-order Kubernetes-tooling reflex and is rejected on purpose.

No automatic dark variant in the first pass. If a maintainer pings for one later, build it then; do not pre-emptively ship two themes for a static site that gets opened for 90 seconds.

## Color

OKLCH throughout. Never `#000` or `#fff`. Every neutral carries a faint warm tint (the same hue as the accent, chroma 0.005-0.01) so the page does not read as cold paper.

```css
:root {
  /* Surface — warm tinted neutrals, hue 70 (ochre family) */
  --surface-page:    oklch(98.5% 0.005 70);   /* page background */
  --surface-raised:  oklch(99.5% 0.003 70);   /* row hover, sticky header */
  --surface-sunken:  oklch(96%   0.008 70);   /* code blocks, bucket-section headers */
  --rule:            oklch(90%   0.012 70);   /* hairline dividers */
  --rule-strong:     oklch(78%   0.018 70);   /* between bucket sections */

  /* Ink — near-black, faintly warm so it sits on the tinted page */
  --ink:             oklch(20%   0.015 70);
  --ink-muted:       oklch(45%   0.012 70);
  --ink-quiet:       oklch(62%   0.010 70);

  /* Accent — one warm ochre. Reserved for "this is the recommended next click." */
  --accent:          oklch(65%   0.16  68);
  --accent-strong:   oklch(52%   0.18  62);   /* hover / focused */
  --accent-tint:     oklch(94%   0.04  70);   /* row background when accent applies */

  /* Semantic tints — used as full pill/row backgrounds, never as side stripes */
  --fail:            oklch(46%   0.13  28);   /* rust, for CI failing / needs rebase */
  --fail-tint:       oklch(94%   0.03  28);
  --ready:           oklch(45%   0.10 145);   /* moss, for ready to merge */
  --ready-tint:      oklch(94%   0.03 145);
  --stale:           oklch(55%   0.04  70);   /* desaturated ochre, for stale */
  --stale-tint:      oklch(94%   0.015 70);

  /* Focus ring — accent at full chroma, never blue browser default */
  --focus-ring:      oklch(60%   0.20  68);
}
```

Color strategy is **Restrained**. The accent earns its place by being scarce: it appears on the single recommended action per row, on links, and on the focus ring. Nothing else. The semantic tints (rust, moss, desaturated ochre) appear only as bucket-row pill backgrounds and only when the bucket itself is that state. Headers and bodies use ink + neutrals only.

**Bucket distinction is not color-only.** Every bucket also carries a textual label, an ordinal priority (1-6), and a position in the page (priority 1 is highest, priority 6 lowest). A maintainer with red-green color blindness must still be able to tell "CI failing" from "ready to merge" by reading the section heading.

## Typography

Two families, fetched as woff2 with `font-display: swap`:

- **Prose:** Inter (variable, weights 400/500/600). Humanist sans, neutral, designed for UI at small sizes. Used for headings, body, and labels.
- **Identifier:** JetBrains Mono (variable, weights 400/500). Used for: PR numbers (`#1234`), commit SHAs, label names (`needs-rebase`), bucket counts, file paths in AI reviews, and anything that appears in a terminal or URL.

```css
:root {
  --font-prose: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono:  "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;

  /* Modular scale, ratio 1.25 between adjacent steps */
  --step--1: 0.80rem;   /* 12.8px — meta, badges */
  --step-0:  1.00rem;   /* 16px   — body */
  --step-1:  1.25rem;   /* 20px   — row title */
  --step-2:  1.563rem;  /* 25px   — bucket heading */
  --step-3:  1.953rem;  /* 31.25  — page heading */
  --step-4:  2.441rem;  /* 39px   — reserved, currently unused */

  --leading-tight: 1.2;
  --leading-snug:  1.4;
  --leading-body:  1.55;

  --tracking-tight: -0.011em;
  --tracking-mono:  -0.005em;  /* JetBrains Mono runs slightly wide */
}
```

Rules:

- Body line length capped at 70ch. The page has a wide-screen max-width of `min(72rem, 100vw - 3rem)`; on monitors wider than that, the page sits against the left margin rather than centering, like a document.
- Hierarchy through scale + weight, not color. Bucket headings: `--step-2`, weight 600, ink. Row titles: `--step-1`, weight 500. Body: `--step-0`, weight 400. Meta: `--step--1`, weight 400, `--ink-muted`.
- Numbers in bucket counts and PR identifiers use the mono face. The visual contrast between "Needs rebase" (prose) and "12" (mono) is part of the system, not a bug.
- No all-caps headings. No letter-spaced labels.

## Layout

The page has three altitudes:

1. **Sticky page header** (top, 64px tall): site title, last-updated timestamp, link to source commit. `--surface-raised`, hairline rule beneath.
2. **Main column**: bucket sections stacked vertically. No outer card. The page background IS the surface.
3. **Bucket section**: an `<h2>` heading at `--step-2` with the bucket name and count, a one-line description in `--ink-muted`, then rows.

Rows are not cards. They are table-like horizontal records separated by hairlines (`--rule`). On hover they take `--surface-raised`. Padding inside a row: 12px vertical, 20px horizontal at desktop; 10px / 16px at mobile.

Spacing scale, used with deliberate variation (no uniform-padding everywhere):

```css
:root {
  --space-1: 0.25rem;   /*  4px */
  --space-2: 0.5rem;    /*  8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.5rem;    /* 24px */
  --space-6: 2rem;      /* 32px */
  --space-8: 3rem;      /* 48px */
  --space-10: 4.5rem;   /* 72px */
}
```

Rhythm: 72px between bucket sections, 48px above each `<h2>`, 32px below each `<h2>`, 16px between rows of meta within a row. Vertical rhythm is deliberately uneven so the eye lands on bucket boundaries, not on a metronome of identical gaps.

Responsive:

- ≥1024px: row is a CSS grid, `grid-template-columns: 4rem 1fr auto auto`. Columns: PR number (mono), title + author + age, recommended action (chip), applied-status badge.
- 640-1023px: grid collapses; recommended action moves to its own line below the title, applied-status badge sits inline next to PR number.
- <640px: rows become two-line records; the chip is full-width below the title.

No horizontal scroll at 360px. Sticky header reduces to title + timestamp at mobile.

## Components

### Recommended-action chip

The most important component on the page. One per row.

- Inline-flex, padding `4px 10px`, border-radius 6px (not pill, not square).
- Background: `--accent-tint`. Border: 1px solid `oklch(85% 0.04 70)`. Text: `--accent-strong`. Font: prose, weight 500, `--step--1`.
- The label-name part inside the chip (e.g. `needs-rebase`) is mono, slightly darker.
- On the "ready to merge" bucket, swap background to `--ready-tint`, border + text to `--ready` variants.
- On "CI failing" / "needs rebase", swap to `--fail-tint` / `--fail`.
- On "stale", swap to `--stale-tint` / `--stale`.

Never a button shape; it is a recommendation, not an action. The whole row is a link to the PR; the chip is decorative-but-informative within it.

### Applied-status badge

Small pip that reads "applied" or "not applied" in mono, `--step--1`, weight 500.

- Applied: text `--ready`, no background, leading `●` glyph in `--ready`.
- Not applied: text `--fail`, no background, leading `○` glyph in `--fail`.

Filled-vs-hollow circle communicates state even if color is stripped. No traffic-light grids; no side stripes.

### Bucket section heading

```
┌─────────────────────────────────────────────
│ 2 · CI failing                           7  │
│ Latest commit's check rollup is FAILURE.    │
└─────────────────────────────────────────────
```

- The ordinal (`2 ·`) is mono `--ink-quiet`, `--step-0`.
- The bucket name is prose, weight 600, ink, `--step-2`.
- The count (`7`) right-aligned, mono, `--step-2`, `--ink-muted`. Same scale as the heading so it reads as a peer, not a badge.
- The description is `--step-0`, `--ink-muted`, on the line below.
- A 1px rule (`--rule-strong`) sits 24px below the description; rows begin under it.

No background tint on the heading itself. Headings are typographic, not panel-like.

### AI review finding (on `/reviews/`)

Findings are list items, not cards. Severity is communicated by a leading mono glyph and a textual label, not a side stripe and not a colored card:

```
✕ critical   src/foo.go:42
  Buffer is reused after the goroutine returns; race detected by …
○ warning    src/bar.go:18
✓ positive   docs/README.md  Good migration note for the rename.
```

The glyph column is fixed-width mono. The severity label is mono, `--step--1`, colored by semantic role (`--fail` for critical, ochre for warning, `--ink-muted` for suggestion, `--ready` for positive). The file path is mono. The description wraps to a 70ch measure beneath.

### Footer

One line, `--ink-quiet`, prose `--step--1`: source commit SHA (mono link), last build time, the explicit "AI reviews are commentary, not a substitute for human review" sentence required by PRODUCT.md.

## Motion

Almost none. The page is static; motion would be decoration.

- Row hover background transitions `120ms ease-out` (cubic-bezier `0.22, 1, 0.36, 1`, ease-out-quart). Nothing else animates by default.
- Respect `prefers-reduced-motion: reduce` by removing even the hover transition.
- No scroll-triggered reveals. No skeleton shimmer (the page is static HTML; there is nothing to skeleton).

## Iconography

Avoid icons where a word will do. The dashboard has exactly two glyphs in active use: the filled/hollow circle on the applied-status badge, and the severity glyphs (`✕`, `○`, `✓`) on findings. Both are Unicode, not an icon font. No Lucide / Heroicons / Phosphor dependency.

If a future view genuinely needs an icon (e.g. a "copy SHA" affordance), use inline SVG sized to the cap height of the surrounding text and inheriting `currentColor`.

## Accessibility commitments

- Color contrast: `--ink` on `--surface-page` exceeds 7:1 (AAA body). `--ink-muted` on `--surface-page` exceeds 4.5:1 (AA body). All chip text-on-tint combinations verified to ≥ 4.5:1.
- Focus ring: 2px outline in `--focus-ring`, 2px offset, on every focusable element. The browser default ring is replaced, not removed.
- Bucket distinction never relies on color alone; the ordinal number, textual label, and section position carry the same information.
- Sticky header stays usable when zoomed to 200%.
- All interactive elements reachable by keyboard in document order; the page's flat structure (no modals, no tabs, no dropdowns) makes this trivial to maintain.

## Anti-patterns, restated specifically for this project

Cross-referenced with PRODUCT.md anti-references and the impeccable shared design laws:

- No hero-metric tile at the top of the page. The bucket section IS the headline.
- No identical-card grid of buckets. Buckets are sections, not tiles, because their content and counts vary wildly.
- No side-stripe borders on rows or findings. State is communicated by chip, glyph, and label.
- No gradient text, anywhere. The site has no decorative typography.
- No glass / backdrop-blur. The page is opaque paper.
- No purple-to-pink "AI" framing on the reviews page. The reviews use the same restrained palette as triage; severity glyphs do the talking.
- No "Last updated 2 minutes ago" with a live-ticking counter. Show the timestamp; do not animate it.
- No dark mode in pass one. Revisit only on real user request.
