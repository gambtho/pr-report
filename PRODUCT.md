# Product

## Register

product

## Users

kubernetes-sigs/headlamp maintainers and reviewers, sitting at a desktop between other tasks, asking "where should I spend the next 10 minutes on this repo?" They already live in GitHub; this site exists because GitHub's native PR list does not separate "needs my attention right now" from "open." Secondary users: contributors curious why their PR is in a given bucket, and other Kubernetes SIG maintainers evaluating whether to adopt the same pattern.

The job to be done is triage, not browsing. A maintainer opens the page, scans one or two bucket sections, clicks through to GitHub, and leaves. Sessions are short, repeated, and interrupted. The AI reviews view serves a slower job: "is there a PR with no human eyes on it I should escalate?"

## Product Purpose

Headrep gives headlamp maintainers two views of open PRs that GitHub does not provide natively:

1. A triage dashboard that classifies every actionable open PR into exactly one of six buckets (needs rebase, CI failing, waiting on reviewer, waiting on author, stale, ready to merge) and shows the recommended label or comment for each. Refreshes hourly. Read-only today; the same recommendations will drive future write-side automation.
2. A daily AI review index covering PRs that have not yet received human review, with severity-grouped findings and accumulated style learnings per repo.

Success is measured by maintainers using the dashboard as the entry point to their PR queue instead of GitHub's default list, and by the recommended actions being trustworthy enough to eventually auto-apply.

## Brand Personality

Three words: maintainer-grade, terse, auditable.

Voice is the same voice that writes good commit messages and good CI failure summaries. State the bucket, state the recommended action, link out. No hype, no exclamation, no "AI-powered" framing. The AI reviews are explicitly labeled as commentary, not a substitute for human review, on every page that shows them.

Emotional goal: relief. The page should feel like an inbox that has already been sorted, not another tool demanding attention.

## Anti-references

- SaaS marketing dashboards with hero-metric tiles, gradient accents, and "your PRs this week" framing. This is a queue, not a KPI.
- GitHub's own PR list. We exist because that view is too flat; copying it defeats the purpose.
- AI-product aesthetics: purple-to-pink gradients, sparkle icons, "✨ AI" badges, glass cards. The AI reviews are a feature, not the brand.
- Generic open-source project pages with a centered logo, big tagline, and three feature cards. There is no landing page here; the homepage IS the dashboard.
- Observability-tool dark mode by reflex (Grafana, Datadog). The category-reflex check applies: a Kubernetes-adjacent tool defaulting to dark blue is the first training-data answer.

## Design Principles

1. **Bucket first, PR second.** The user came to find a bucket to clear, not to browse PRs. The bucket label, count, and recommended action should be legible before any individual row.
2. **The recommended action is the headline.** For each row, the recommended label or comment is more important than the title or author. Treat it as primary content, not metadata.
3. **Honest about state.** Read-only today, write-side later: the UI says so. Green "already applied" vs red "not yet applied" badges make the gap between recommendation and reality visible per row.
4. **No interactivity it cannot back up.** A static site cannot apply labels. So nothing on the page should look like a button that would. Links go to GitHub; the rest is text.
5. **Auditable by default.** Every classification, every recommendation, every AI finding traces back to a file in the repo. Surface freshness (last updated timestamp, source commit) so a skeptical maintainer can verify, not just trust.

## Accessibility & Inclusion

Target WCAG 2.1 AA. The dashboard will be opened on a wide range of monitors and occasionally on phones during on-call; layout must work down to 360px without horizontal scroll. Bucket distinction must not rely on color alone: each bucket gets a textual label and ideally a distinct shape or position cue, so red-green color blindness does not erase the "CI failing" vs "ready to merge" distinction. Respect `prefers-reduced-motion`; the site has no motion needs that justify ignoring it. Body copy targets a 65-75ch measure even on wide screens.
