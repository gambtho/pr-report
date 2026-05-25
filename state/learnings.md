# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-05-25*

## Review Style Guide
- Commit subject format: `<area>: <SubArea>: Description` — description starts with capital letter (e.g. `frontend: NodeDetails: Fix drain status polling leak`, `backend: auth: Bound FuzzSanitizeClusterName input`).
- Keep commit subject under 72 characters (soft limit).
- Do NOT include `Fixes #NN`, `closes #NN`, or similar auto-close keywords in commit messages (PR body is acceptable).
- Approval style is warm and brief: `🎉 thanks!` is the standard merge acknowledgment from maintainers.
- Reviewer @illume is the primary maintainer and very responsive; issues CHANGES_REQUESTED for commit guideline violations before final APPROVE.
- copilot-pull-request-reviewer[bot] auto-reviews all PRs and posts a PR overview as a COMMENTED review — its presence does not indicate human review.
- PRs must fix a real bug, add a feature, or address a clear maintenance need — pure stylistic refactors without justification are not accepted per AGENTS.md.
- Frontend (TypeScript/React): fix `exhaustive-deps` lint violations rather than suppressing with `eslint-disable`; Material-UI v5 patterns used.
- Backend (Go): use comma-ok type assertions to avoid panics; structured logging via slog; test-first, risk-averse style per AGENTS.md.
- Tests required for both frontend (Vitest) and backend (Go test) when changing logic.
- CNCF CLA is a hard merge blocker in kubernetes-sigs repos.
- k8s-ci-robot posts IssueComment (not Review) on every PR — do not count as human review.

## Detected Stack
- **Languages:** TypeScript (frontend/), Go (backend/)
- **Runtimes:** Node.js >=20.11.1, npm >=10.0.0, Go 1.25.9 (per AGENTS.md / backend/go.mod)
- **Frontend framework:** React + Material-UI v5
- **Test frameworks:** Vitest (frontend), Go test (backend)
- **Build:** npm scripts (`npm run build`, `npm run frontend:build`, `npm run backend:build`)
- **CI:** GitHub Actions (.github/workflows/), Dockerfiles, Helm charts (charts/)
- **Other:** Electron desktop app (app/), plugin system (plugins/), i18n tooling (tools/i18n/)

## Common Issues
- Commit message format violations: `feat(area): ...` (Conventional Commits style) instead of `area: Component: Description` (seen in PR #5746, #5778; 4 sessions). PR #5778 by @Rohith-Saran persists after 3 re-reviews.
- Commit message missing SubArea segment: `area: Description` instead of `area: SubArea: Description` (seen in PR #5785, #5843, #5832; multiple sessions). @Rohith-Saran has had this issue across multiple PRs.
- Commit subject lowercase verb: `frontend: fix ...` instead of `frontend: Fix ...` (seen in PR #5841, #5842 by @Naga15; also #5786 by @vmridul).
- Commit subject exceeding 72-char soft limit (seen in PR #5785: 91 chars).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746; outstanding after 3 reviews). PR #5778 also missing `externalLinks` from `values.schema.json`.
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).
- Unresolved Git merge conflict markers in PRs (seen in PR #5778 — resolved in 2026-05-23 re-review).
- PRs where author cannot run tests locally (seen in PR #5777 — disk space; PR #5764 — no Go toolchain). CI must confirm green before merge.
- `useMemo(() => value, [])` anti-pattern used as a one-shot initialiser instead of lazy `useState(() => value)` (seen in PR #5767, #5803; 2 sessions).
- Render-phase state updates (`setState` called unconditionally during render body) causing React to drop and re-run the render (seen in PR #5805).
- Two sequential `setState` calls in the same render for the same piece of state (seen in PR #5804).
- Missing frontend Vitest tests for new behavioral flows (seen in PR #5764 — OIDC auto-login useEffect not tested).
- Helm `externalLinks`/feature config fields not added to `values.schema.json` (seen in PR #5778).
- PR body containing unresolved placeholder `#<issue-number>` or `#NAN` instead of real issue reference (seen in PR #5778, #5844).
- Storyshot files containing unrelated ARIA-element structural drift included in a PR diff (seen in PR #5843 — snapshots regenerated from base-branch changes unrelated to the actual fix).
- Trailing period in commit/PR title subject (seen in PR #5844 by @nikunjkumar05).
- Multi-area dependency bump PRs missing area prefix in commit subject (seen in PR #5772 by @skoeva — "Bump fast-uri, brace-expansion, ws, containerd" with no `deps:` prefix).

## False Positives / Project Conventions
- copilot-pull-request-reviewer[bot] auto-reviews every PR; this is NOT human review activity and should not count as a filter criterion for "has human review". The GraphQL review filter must check `author.__typename == "User"` to distinguish human from bot reviews.
- k8s-ci-robot posts automated comments (APPROVALNOTIFIER, welcome messages) on every PR — these are bot comments and do not count as human review activity.
- @illume reviews PRs very quickly after opening, so PRs that appear unreviewed often already have a review within hours.
- `addListener`/`removeListener` on MediaQueryList is pre-existing code in `frontend/src/lib/themes.ts` — fixed in PR #5785; no longer present.
- Theme names are displayed via `capitalize(it.name)` in Settings.tsx — no dedicated displayName/label field needed; 'auto' → 'Auto' is acceptable.
- `useCallback` with `[]` dep array wrapping a `ref.current` access is the correct pattern for the react-hooks/refs rule — not a stale closure issue since ref objects are stable.
- Redux `dispatch` from `useDispatch()` is guaranteed stable across renders; adding it to `useEffect`/`useMemo` deps is correct and does not cause extra re-runs.
- `IsAuthBypassURL` in the k8cache package returns `true` for paths that require full auth-error handling (i.e. normal Kubernetes resource API paths), contrary to what the name implies. Do not flag this as a bug — flag the naming as a Suggestion.
- `normalizedData = data ?? null` in SimpleTable is a render-body computation (not memoized); reference instability is a pre-existing concern. Do not flag as a new bug.
- URL key format in `useURLState` with prefix: manually reconstructed as `prefix.perPage`. If the key format mismatch is discovered, it's a Suggestion, not a Warning.
- `// eslint-disable-next-line react-hooks/exhaustive-deps` on `useEffect(() => { ... }, [])` in `usePrefersColorScheme` is intentional — the effect is mount-only and `mql` is stable; do not flag.
- The "at least one exporter" check in `backend/pkg/config/config.go` `validateTracing()` has a pre-existing logic issue (condition fires when stdout IS enabled, meaning it can't fire when all exporters are absent). Do not flag as a new bug — it pre-dates PR #5832.
- `emptyPluginExtensions` defined as a module-level constant in `registry.tsx` between export statements is intentional (stable reference for Redux selector memoization in `usePluginExtensions`) — not a style error.
- `safeValue` computed inline in `ContainerTextField` (PR #5822): `Array.isArray(value) ? value : []` creates a new ref when value is non-array, but safeValue.length is stable (0), so the useEffect dep is stable. Not a performance issue.

## Author Notes
- @illume: Primary maintainer; approves promptly but requests commit-guideline fixes first; warm/encouraging tone.
- @iashutoshyadav: Clean small fix style; good PR description with before/after code.
- @govindup63: Well-documented PR with detailed step-by-step test instructions and full backend test coverage; thorough author.
- @rforced: Feature contributor; needs reminder about project commit convention.
- @HarK-github: Helm chart contributor using Conventional Commits style (needs commit format guidance); PR #5746 pending for 5+ sessions — fieldRef/resourceFieldRef still missing.
- @YadavAkhileshh: Multiple PRs (#5785, #5783) — clean fixes, good PR descriptions, follows project conventions.
- @kishore08-07: Multiple PRs (#5774, #5768, #5767, #5820) — all hooks-cleanup sub-issues (#5183); clean targeted fixes, correct commit format.
- @ayushmaan-16: Five PRs in 2026-05-22/23 sessions (#5805, #5804, #5803) — all React hooks/render-phase fixes; all approved.
- @Rohith-Saran: PR #5775 clean fix (approved); PR #5778 persistent commit format violation after 3 re-reviews; PR #5843 missing SubArea in commit subject — pattern of commit format issues persists. REQUEST_CHANGES maintained on format violations.
- @sniok: Core contributor (maintainer-adjacent); PR #5779 adds experimental tsgo compiler as primary type-checker.
- @menardorama: Feature contributor (PR #5764 OIDC auto-login); deployed to production at their company.
- @vmridul: Small Go fix contributor; needs reminder about commit subject capitalization and SubArea format (PR #5786).
- @Nabsku: Backend contributor; PR #5777 and PR #5798 both approved. Strong test author.
- @harrshita123: Backend contributor; PR #5777 (approved), PR #5840 (approved — correct commit format with SubArea), PR #5832 (approved — missing SubArea in commit subject). Improving on commit format.
- @yu-heejin: Frontend contributor; PR #5809 (milli-bytes parsing fix) — clean fix with tests; approved.
- @joaquimrocha: Core maintainer/contributor.
- @Naga15: New contributor; PR #5842 and #5841 — correct React hooks fix technique but commit subjects have lowercase verb and missing SubArea. Both REQUEST_CHANGES.
- @RajPrakash681: New contributor (2026-05-25); three test-coverage PRs (#5829, #5830, #5831) — all well-structured, correct commit format, good fixture design; all approved.
- @WasThatRudy: Contributor; PR #5822 — well-analyzed crash fix with comprehensive test coverage and clear PR description; approved.
- @mahmoudmagdy1-1: New contributor; PR #5845 — well-implemented plugin extension registry feature; approved.
- @anurag-p6: New contributor; PR #5824 — minimal optional chaining fix; approved.
- @Swastik19Nit: New contributor; PR #5838 — minimal CSS fix for text clipping; approved.
- @nikunjkumar05: New contributor; PR #5844 — test-only improvement; trailing period in commit subject; approved.
- @skoeva: Contributor; PR #5772 — multi-area security dep bump; missing area prefix in commit subject; NEEDS_DISCUSSION.

## Session Log
### 2026-05-18
- Reviewed 0 PRs (0 candidates found)

### 2026-05-19
- Reviewed 4 PRs: #5731, #5538, #5408, #5748
- Skipped: 0
- New observations: copilot-pull-request-reviewer[bot] is not human review

### 2026-05-20
- Reviewed 3 PRs: #5779, #5781, #5748 (re-review)
- New observations: tsgo PR needs team discussion

### 2026-05-21
- Reviewed 7 PRs: #5786, #5774, #5768, #5767, #5764, #5746, #5820
- New observations: hooks cleanup PRs from issue #5183

### 2026-05-22
- Reviewed 9 PRs: #5809, #5795, #5794, #5805, #5804, #5803, #5798, #5775, #5778
- New observations: multiple React render-phase fix patterns

### 2026-05-23
- Reviewed 2 PRs: #5785 (re-review), #5783
- New observations: storyshot drift from base branch

### 2026-05-24
- Reviewed 1 PR: #5785 (re-review)
- Skipped: 20 (SHA unchanged)

### 2026-05-25
- Reviewed 20 PRs: #5809 (re-review), #5845, #5844, #5843, #5842, #5841, #5840, #5838, #5837, #5836, #5835, #5834, #5833, #5832, #5831, #5830, #5829, #5824, #5822, #5772
- Skipped: 21 (SHA unchanged) + 166 (human review activity)
- New observations: New wave of test-coverage PRs by @RajPrakash681 (all approved). @Naga15 fixing hooks violations with correct technique but wrong commit format. Plugin extension registry by @mahmoudmagdy1-1 approved. Security dep bump by @skoeva missing area prefix.
