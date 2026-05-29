# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-05-29*

## Review Style Guide
- Commit subject format: `<area>: <SubArea>: Description` — description starts with capital letter (e.g. `frontend: NodeDetails: Fix drain status polling leak`, `backend: auth: Bound FuzzSanitizeClusterName input`).
- Keep commit subject under 72 characters (soft limit).
- Do NOT include `Fixes #NN`, `closes #NN`, or similar auto-close keywords in commit messages (PR body is acceptable).
- Approval style is warm and brief: `🎉 thanks!` is the standard merge acknowledgment from maintainers.
- Reviewer @illume is the primary maintainer and very responsive; issues CHANGES_REQUESTED for commit guideline violations before final APPROVE. Consistently requests rebase to remove merge-main commits.
- copilot-pull-request-reviewer[bot] auto-reviews all PRs and posts a PR overview as a COMMENTED review — its presence does not indicate human review.
- PRs must fix a real bug, add a feature, or address a clear maintenance need — pure stylistic refactors without justification are not accepted per AGENTS.md.
- Frontend (TypeScript/React): fix `exhaustive-deps` lint violations rather than suppressing with `eslint-disable`; Material-UI v5 patterns used.
- Backend (Go): use comma-ok type assertions to avoid panics; structured logging via slog; test-first, risk-averse style per AGENTS.md.
- Tests required for both frontend (Vitest) and backend (Go test) when changing logic.
- CNCF CLA is a hard merge blocker in kubernetes-sigs repos.
- k8s-ci-robot posts IssueComment (not Review) on every PR — do not count as human review.
- @illume reviews PRs very quickly after opening; by the time the daily job runs, essentially all new PRs have human review. Only re-review candidates remain as actionable.

## Detected Stack
- **Languages:** TypeScript (frontend/), Go (backend/)
- **Runtimes:** Node.js >=20.11.1, npm >=10.0.0, Go 1.25.9 (per AGENTS.md / backend/go.mod)
- **Frontend framework:** React + Material-UI v5
- **Test frameworks:** Vitest (frontend), Go test (backend)
- **Build:** npm scripts (`npm run build`, `npm run frontend:build`, `npm run backend:build`)
- **CI:** GitHub Actions (.github/workflows/), Dockerfiles, Helm charts (charts/)
- **Other:** Electron desktop app (app/), plugin system (plugins/), i18n tooling (tools/i18n/)

## Common Issues
- Commit message format violations: `feat(area): ...` (Conventional Commits style) instead of `area: Component: Description` (seen in PR #5746, #5778; 5 sessions). PR #5778 by @Rohith-Saran persists after 4 re-reviews.
- Commit message missing SubArea segment: `area: Description` instead of `area: SubArea: Description` (seen in PR #5785, #5843, #5832, #5842, #5841, #5775, #5783, #5844, #5804, #5877 partial; multiple sessions).
- Commit subject lowercase verb: `frontend: fix ...` instead of `frontend: Fix ...` (seen in PR #5841, #5842 by @Naga15 — now fixed; also #5843 by @Rohith-Saran; also #5786 by @vmridul).
- Commit subject exceeding 72-char soft limit (seen in PR #5785: >90 chars; PR #5785 still unfixed in 2026-05-29 re-review).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746; outstanding after 3 reviews). PR #5778 also missing `externalLinks` from `values.schema.json` — now fixed.
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).
- Unresolved Git merge conflict markers in PRs (seen in PR #5778 — resolved in 2026-05-23 re-review).
- PRs where author cannot run tests locally (seen in PR #5777 — disk space; PR #5764 — no Go toolchain). CI must confirm green before merge.
- `useMemo(() => value, [])` anti-pattern used as a one-shot initialiser instead of lazy `useState(() => value)` (seen in PR #5767, #5803; 2 sessions — #5803 now fixed in 2026-05-29 re-review).
- Render-phase state updates (`setState` called unconditionally during render body) causing React to drop and re-run the render (seen in PR #5805).
- Two sequential `setState` calls in the same render for the same piece of state (seen in PR #5804 — now fixed with Map consolidation in 2026-05-29 re-review).
- Missing frontend Vitest tests for new behavioral flows (seen in PR #5764 — OIDC auto-login AuthChooser useEffect still not tested after 6 re-reviews).
- Helm `externalLinks`/feature config fields not added to `values.schema.json` (seen in PR #5778 — now added).
- PR body containing unresolved placeholder `#<issue-number>` or `#NAN` instead of real issue reference (seen in PR #5778, #5844 — #5844 still has #NAN after 4 re-reviews).
- Storyshot files containing unrelated ARIA-element structural drift included in a PR diff (seen in PR #5843 — resolved in 2026-05-27 re-review).
- Trailing period in commit/PR title subject (seen in PR #5844 by @nikunjkumar05; persistent after 4 re-reviews).
- Multi-area dependency bump PRs missing area prefix in commit subject (seen in PR #5772 by @skoeva — "Bump fast-uri, brace-expansion, ws, containerd" with no `deps:` prefix).
- Vague "Address Copilot review comments" commit subjects without describing the actual change (seen in PR #5764 by @menardorama; persistent after 6 re-reviews).
- Merge commit "Merge branch 'main' into ..." included in PR branch (seen in PR #5809 by @yu-heejin — resolved 2026-05-27; PR #5764 by @menardorama — still present in 2026-05-29 re-review; PR #5844 by @nikunjkumar05 — still present after 4 re-reviews).
- Unrelated single-line fix bundled into a feature PR (seen in PR #5764: `ThemeProviderNexti18n.tsx` fallback lang change unrelated to OIDC auto-login).
- Dead code: `os.IsExist(err)` branch unreachable when using `os.O_CREATE|os.O_WRONLY` (no O_EXCL) — `OpenFile` with this combination never returns `EEXIST`. Seen in PR #5783; still present in 2026-05-29 re-review (SHA unchanged).
- URL-lowercasing bug: `safeLinkUrl` returns `url.toLowerCase()` instead of original `url` for case-sensitive path components (seen in PR #5778 — still open, SHA unchanged).
- Duplicate YAML key in values.yaml from bad merge/rebase (seen in PR #5764 — duplicate `clusterInventory:` key introduced in 2026-05-29 re-review).
- Extra `}` in values.schema.json making JSON schema invalid (seen in PR #5764 — introduced in 2026-05-29 re-review).
- `.cmd` shims on Windows require `shell: true` in Node.js `spawnSync`/`execFileSync` — adding `.cmd` extension alone is not sufficient (seen in PR #5861 by @skoeva — fixed).
- `list.kind.replace('List', '')` removes first occurrence rather than trailing suffix — use `/List$/` regex to avoid mangling names containing 'List' mid-string (seen in PR #5880 by @sniok — fixed).
- Abandoned OIDC state tokens never evicted from `oauthRequestMap` — use a background goroutine with TTL-based eviction (seen in PR #5866 by @ayushmaan-16 — fixed).
- GitHub Actions workflow using `inputs.*` directly in shell here-strings without sanitization — potential metacharacter injection (seen in PR #5881 by @skools-here — minor, approve with suggestion).

## False Positives / Project Conventions
- copilot-pull-request-reviewer[bot] auto-reviews every PR; this is NOT human review activity and should not count as a filter criterion for "has human review". The GraphQL review filter must check `author.__typename == "User"` to distinguish human from bot reviews. Note: even with `__typename: "User"` filtering, all recently-opened PRs receive a review from @illume within hours, so effectively all new PRs have human review quickly.
- k8s-ci-robot posts automated comments (APPROVALNOTIFIER, welcome messages) on every PR — these are bot comments and do not count as human review activity. Its `__typename` in GraphQL is "User" (not "Bot"), so it must be filtered by login.
- @illume reviews PRs very quickly after opening, so PRs that appear unreviewed often already have a review within hours.
- `addListener`/`removeListener` on MediaQueryList is pre-existing code in `frontend/src/lib/themes.ts` — being fixed in PR #5785; legacy fallback still needed for older WebViews.
- Theme names are displayed via `capitalize(it.name)` in Settings.tsx — no dedicated displayName/label field needed; 'auto' → 'Auto' is acceptable.
- `useCallback` with `[]` dep array wrapping a `ref.current` access is the correct pattern for the react-hooks/refs rule — not a stale closure issue since ref objects are stable.
- Redux `dispatch` from `useDispatch()` is guaranteed stable across renders; adding it to `useEffect`/`useMemo` deps is correct and does not cause extra re-runs.
- `IsAuthBypassURL` in the k8cache package returns `true` for paths that require full auth-error handling (i.e. normal Kubernetes resource API paths), contrary to what the name implies. Do not flag as a bug — flag the naming as a Suggestion.
- `normalizedData = data ?? null` in SimpleTable is a render-body computation (not memoized); reference instability is a pre-existing concern. Do not flag as a new bug.
- URL key format in `useURLState` with prefix: manually reconstructed as `prefix.perPage`. If the key format mismatch is discovered, it's a Suggestion, not a Warning.
- `// eslint-disable-next-line react-hooks/exhaustive-deps` on `useEffect(() => { ... }, [])` in `usePrefersColorScheme` is intentional — the effect is mount-only and `mql` is stable; do not flag.
- The "at least one exporter" check in `backend/pkg/config/config.go` `validateTracing()` has a pre-existing logic issue (condition fires when stdout IS enabled, meaning it can't fire when all exporters are absent). Do not flag as a new bug — it pre-dates PR #5832.
- `emptyPluginExtensions` defined as a module-level constant in `registry.tsx` between export statements is intentional (stable reference for Redux selector memoization in `usePluginExtensions`) — not a style error.
- `safeValue` computed inline in `ContainerTextField` (PR #5822): `Array.isArray(value) ? value : []` creates a new ref when value is non-array, but safeValue.length is stable (0), so the useEffect dep is stable. Not a performance issue.
- `sessionStorage` usage in `AuthChooser` for OIDC auto-login loop prevention (PR #5764) is intentional — sessionStorage (not localStorage) correctly clears on tab close, so the auto-login fires once per session per cluster per tab.
- `koanf` env var mapping: `HEADLAMP_CONFIG_EXTERNAL_LINKS` maps to `external-links` key via the koanf env provider (uppercase `_` → lowercase `-` transformation with `HEADLAMP_CONFIG_` prefix stripped). This is a project convention, not a bug.
- `os.O_CREATE|os.O_WRONLY` without `O_EXCL` never returns EEXIST — `os.IsExist(err)` guard after such OpenFile call is dead code. Flag as Warning in any PR that adds this pattern.
- Helm variable reassignment `{{- $matched = true }}` inside a range block is valid Helm 3.1+ syntax — not a bug.
- `winShell = process.platform === 'win32'` in headlamp-plugin: glob patterns passed as execFileSync args with `shell: true` on Windows are handled by the downstream tool (i18next-scanner) rather than cmd.exe glob expansion. Do not flag as a bug.

## Author Notes
- @illume: Primary maintainer; approves promptly but requests commit-guideline fixes first; warm/encouraging tone. Consistently requests rebase to remove merge-main commits.
- @iashutoshyadav: Clean small fix style; good PR description with before/after code.
- @govindup63: Well-documented PR with detailed step-by-step test instructions and full backend test coverage; thorough author.
- @rforced: Feature contributor; needs reminder about project commit convention.
- @HarK-github: Helm chart contributor using Conventional Commits style (needs commit format guidance); PR #5746 pending for 5+ sessions — fieldRef/resourceFieldRef still missing.
- @YadavAkhileshh: Multiple PRs (#5785, #5783) — clean fixes, good PR descriptions, follows project conventions. Persistent SubArea omissions in commit subjects; commit subject length also an issue in #5785. Not making progress on commit format despite repeated feedback. First commit in #5785 still missing SubArea after 5+ re-reviews.
- @kishore08-07: Multiple PRs (#5774, #5768, #5767, #5820) — all hooks-cleanup sub-issues (#5183); clean targeted fixes, correct commit format.
- @ayushmaan-16: Six PRs — all React hooks/render-phase fixes or backend memory fixes. All 2026-05-28 SimpleTable/useKubeObjectList PRs (#5803, #5804, #5805) approved in 2026-05-29 re-review after fixes. New PR #5866 (OIDC state eviction) approved — very strong technical author with correct commit format and production-quality tests.
- @Rohith-Saran: PR #5775 (listener leak — SubArea missing in 2/3 commits); PR #5778 (external links — commit format still Conventional Commits after 4 re-reviews + safeLinkUrl bug); PR #5843 (ApiError export — lowercase verb in commit). Pattern of commit format issues persists across all PRs.
- @sniok: Core contributor (maintainer-adjacent); PR #5779 adds experimental tsgo compiler as primary type-checker — awaiting team discussion. PR #5880 (kind name regex fix) approved — clean and precise.
- @menardorama: Feature contributor (PR #5764 OIDC auto-login); deployed to production at their company. Vague commit subjects and merge-main commits persist after 6 re-reviews; component-level test still missing; new structural bugs (duplicate YAML key, extra JSON brace) introduced in latest iteration.
- @vmridul: Small Go fix contributor; needs reminder about commit subject capitalization and SubArea format (PR #5786).
- @Nabsku: Backend contributor; PR #5777 and PR #5798 both approved. Strong test author. PR #5798 is a well-structured refactoring of the k8cache URL path handling.
- @harrshita123: Backend contributor; PR #5777 (approved), PR #5840 (approved — correct commit format with SubArea), PR #5832 (approved — missing SubArea in commit subject). Improving on commit format.
- @yu-heejin: Frontend contributor; PR #5809 — approved in 2026-05-27 re-review (rebase done + decimal milli-bytes support added).
- @joaquimrocha: Core maintainer/contributor.
- @Naga15: Persistent commit format issue — PRs #5842 and #5841 skipped (SHA unchanged) in 2026-05-29 session.
- @RajPrakash681: New contributor (2026-05-25); four test-coverage PRs (#5829, #5830, #5831 all approved); PR #5830 had merge-main commit.
- @WasThatRudy: Contributor; PR #5822 approved in 2026-05-29 re-review — all changes implemented including five tests. Strong follow-through.
- @mahmoudmagdy1-1: New contributor; PR #5845 — SHA unchanged in 2026-05-29 session.
- @anurag-p6: New contributor; PR #5824 — SHA unchanged.
- @Swastik19Nit: New contributor; PR #5838 — SHA unchanged in 2026-05-29 session. CLA not signed (`cncf-cla: no`); hard merge blocker.
- @nikunjkumar05: New contributor; PR #5844 — trailing period, #NAN placeholder, and merge commit persist after 4 re-reviews. Code quality (exact path assertions) is strong but commit hygiene remains completely unaddressed.
- @skoeva: Contributor; PR #5772 — merged. PR #5877 (extract IncrementRequestCounter) approved — clean refactoring with improved nil safety and comprehensive tests. PR #5861 (Windows .cmd shim fix) approved — targeted and correct.
- @skools-here: New contributor; PR #5881 (CI SHA validation) approved — good security improvement with correct commit format.
- @kahirokunn: Contributor; PR #5874 (Cluster Inventory image update) approved — thorough documentation and test fixture updates; Helm template validation improvement.

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

### 2026-05-26
- Reviewed 5 PRs (re-reviews only): #5842, #5841, #5822, #5809, #5764
- Skipped: 35 (SHA unchanged) + 169 (human review activity — @illume reviews all new PRs quickly)
- New observations: @illume reviews PRs so promptly that by the time the daily job runs, essentially all new PRs have human review. Only re-review candidates remain. @Naga15 improved verb capitalization in #5842/#5841 but SubArea still missing. @WasThatRudy added tests to #5822 — approved. @yu-heejin added decimal milli-bytes support to #5809 — approved with suggestion to rebase merge commit. @menardorama PR #5764 still needs commit squash and component-level test.

### 2026-05-27
- Reviewed 12 PRs (all re-reviews): #5764, #5775, #5778, #5779, #5783, #5785, #5798, #5809, #5830, #5838, #5843, #5844
- Skipped: 4 (SHA unchanged: #5822, #5841, #5842, #5845) + 150 (all new candidates had human review activity)
- New observations: PR #5798 (@Nabsku) approved — well-structured k8cache refactor; PR #5809 (@yu-heejin) approved — rebase done + decimal support. PR #5838 (@Swastik19Nit) NEEDS_DISCUSSION — `cncf-cla: no` hard blocker. Dead `os.IsExist` code found in PR #5783. URL-lowercasing bug found in PR #5778 `safeLinkUrl`. PR #5843 (@Rohith-Saran) REQUEST_CHANGES for lowercase commit verb.

### 2026-05-28
- Reviewed 6 PRs (all re-reviews): #5783, #5785, #5803, #5804, #5805, #5844
- Skipped: 26 (SHA unchanged) + 178 (all new candidates had human review activity)
- New observations: @ayushmaan-16 all three SimpleTable/useKubeObjectList PRs (#5803, #5804, #5805) now approved after solid fixes — functional state updates, pure getSortData, useMemo filteredData, useEffect page-reset, direct defaultRowsPerPage call. @YadavAkhileshh still not fixing SubArea and commit length in #5785 or dead os.IsExist in #5783 despite repeated flagging. @nikunjkumar05 PR #5844 still has trailing period + #NAN after 3 re-reviews.

### 2026-05-29
- Reviewed 12 PRs: #5764 (re-review), #5785 (re-review), #5803 (re-review), #5804 (re-review), #5822 (re-review), #5844 (re-review), #5861, #5866, #5874, #5877, #5880, #5881
- Skipped: 28 (SHA unchanged) + ~150 (human review activity on new candidates)
- New observations: @WasThatRudy PR #5822 fully approved — all tests implemented. @ayushmaan-16 #5803 and #5804 approved (SimpleTable URL sync and Map consolidation both correct). @sniok PR #5880 regex fix for kind name approved — clean minimal fix. @ayushmaan-16 #5866 (OIDC state eviction) approved — strong backend work with correct TTL goroutine and production-path test. @skoeva PR #5877 approved — improved nil safety and ManualReader-based metric tests. @skoeva PR #5861 approved — Windows .cmd shim fix. @kahirokunn PR #5874 approved — Cluster Inventory image update with improved Helm path validation. @skools-here PR #5881 approved — CI SHA validation. @menardorama PR #5764 still REQUEST_CHANGES — new structural bugs (duplicate YAML key, extra JSON brace) introduced. @YadavAkhileshh PR #5785 still REQUEST_CHANGES — first commit SubArea still missing. @nikunjkumar05 PR #5844 still REQUEST_CHANGES — trailing period + #NAN + merge commit all unresolved after 4 re-reviews.
