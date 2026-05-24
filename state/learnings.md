# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-05-24*

## Review Style Guide
- Commit subject format: `<area>: <SubArea>: Description` — description starts with capital letter (e.g. `frontend: NodeDetails: Fix drain status polling leak`, `backend: auth: Bound FuzzSanitizeClusterName input`).
- Keep commit subject under 72 characters (soft limit).
- Do NOT include `Fixes #NN`, `closes #NN`, or similar auto-close keywords in commit messages.
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
- Commit message missing SubArea segment: `area: Description` instead of `area: SubArea: Description` (seen in PR #5785 squashed commit — commit had `frontend: Replace deprecated...` while PR title correctly had `frontend: themes: Replace deprecated...`).
- Commit subject exceeding 72-char soft limit (seen in PR #5785: 91 chars).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746; outstanding after 3 reviews). PR #5778 also missing `externalLinks` from `values.schema.json`.
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).
- Commit title lowercase verb + missing SubArea (seen in PR #5786 — `backend: changed format verb %v with %w` should be `backend: kubeconfig: Change format verb %v to %w`).
- Unresolved Git merge conflict markers in PRs (seen in PR #5778 — resolved in 2026-05-23 re-review).
- PRs where author cannot run tests locally (seen in PR #5777 — disk space; PR #5764 — no Go toolchain). CI must confirm green before merge.
- `useMemo(() => value, [])` anti-pattern used as a one-shot initialiser instead of lazy `useState(() => value)` (seen in PR #5767, #5803; 2 sessions). Fix is to use direct computation when the value should be reactive.
- Render-phase state updates (`setState` called unconditionally during render body) causing React to drop and re-run the render (seen in PR #5805 — setPage(0); fix: move to useEffect).
- Two sequential `setState` calls in the same render for the same piece of state, causing the second to overwrite the first (seen in PR #5804 — useKubeObjectList; fix: use functional updater + structural identity comparison).
- Missing frontend Vitest tests for new behavioral flows (seen in PR #5764 — OIDC auto-login useEffect not tested).
- Helm `externalLinks`/feature config fields not added to `values.schema.json` (seen in PR #5778; schema lacks `additionalProperties: false` for config so won't hard-fail, but IDE auto-complete broken).
- PR body containing unresolved placeholder `#<issue-number>` instead of real issue reference (seen in PR #5778).

## False Positives / Project Conventions
- copilot-pull-request-reviewer[bot] auto-reviews every PR; this is NOT human review activity and should not count as a filter criterion for "has human review". The GraphQL review filter must check `author.__typename == "User"` to distinguish human from bot reviews.
- k8s-ci-robot posts automated comments (APPROVALNOTIFIER, welcome messages) on every PR — these are bot comments and do not count as human review activity.
- @illume reviews PRs very quickly after opening, so PRs that appear unreviewed often already have a review within hours.
- `addListener`/`removeListener` on MediaQueryList is pre-existing code in `frontend/src/lib/themes.ts` — fixed in PR #5785; no longer present.
- Theme names are displayed via `capitalize(it.name)` in Settings.tsx — no dedicated displayName/label field needed; 'auto' → 'Auto' is acceptable.
- `useCallback` with `[]` dep array wrapping a `ref.current` access is the correct pattern for the react-hooks/refs rule — not a stale closure issue since ref objects are stable.
- Redux `dispatch` from `useDispatch()` is guaranteed stable across renders; adding it to `useEffect`/`useMemo` deps is correct and does not cause extra re-runs.
- `IsAuthBypassURL` in the k8cache package returns `true` for paths that require full auth-error handling (i.e. normal Kubernetes resource API paths), contrary to what the name implies. Do not flag this as a bug — flag the naming as a Suggestion.
- `normalizedData = data ?? null` in SimpleTable is a render-body computation (not memoized); reference instability is a pre-existing concern from before the PR and is not introduced by the fix. Do not flag as a new bug — flag only as a low-priority suggestion for callers to stabilize the data prop.
- URL key format in `useURLState` with prefix: manually reconstructed as `prefix.perPage`. If the key format mismatch is discovered, it's a Suggestion, not a Warning.
- `// eslint-disable-next-line react-hooks/exhaustive-deps` on `useEffect(() => { ... }, [])` in `usePrefersColorScheme` is intentional — the effect is mount-only and `mql` is stable; do not flag.

## Author Notes
- @illume: Primary maintainer; approves promptly but requests commit-guideline fixes first; warm/encouraging tone. Authored PR #5408 (large doc+e2e update for Dex/OAuth2-Proxy tutorial).
- @iashutoshyadav: Clean small fix style; good PR description with before/after code.
- @govindup63: Well-documented PR with detailed step-by-step test instructions and full backend test coverage; thorough author.
- @rforced: Feature contributor; needs reminder about project commit convention.
- @HarK-github: Helm chart contributor using Conventional Commits style (needs commit format guidance); PR #5746 pending for 5 sessions — fieldRef/resourceFieldRef still missing.
- @YadavAkhileshh: Multiple PRs (#5785, #5783) — clean fixes, good PR descriptions, follows project conventions; PR #5783 resolved properly with `os.IsExist` race guard. PR #5785 has correct code but commit message missing SubArea and too long on latest squash.
- @kishore08-07: Multiple PRs (#5774, #5768, #5767, #5820) — all hooks-cleanup sub-issues (#5183); clean targeted fixes, correct commit format.
- @ayushmaan-16: Five PRs in 2026-05-22/23 sessions (#5805, #5804, #5803) — all React hooks/render-phase fixes; clean descriptions with clear before/after rationale; correct commit format. All approved.
- @Rohith-Saran: PR #5775 clean fix (approved); PR #5778 persistent commit format violation (feat: Conventional Commits style instead of project format) after 3 re-reviews — REQUEST_CHANGES maintained. Merge conflicts resolved in 2026-05-23 re-review.
- @sniok: Core contributor (maintainer-adjacent); PR #5779 adds experimental tsgo compiler as primary type-checker, which needs team discussion.
- @menardorama: Feature contributor (PR #5764 OIDC auto-login); deployed to production at their company; backend tests not run locally. PR updated with sessionStorage fixes.
- @vmridul: Small Go fix contributor; needs reminder about commit subject capitalization and SubArea format (PR #5786).
- @Nabsku: Backend contributor; PR #5777 (cache invalidation fix, solid tests) and PR #5798 (k8cache bypass, comprehensive refactor + tests) — both approved. Strong test author.
- @harrshita123: Backend contributor; PR #5777 (all-namespace cache invalidation) updated with `DeleteKeys` delegation and regression test — approved 2026-05-23.
- @yu-heejin: New contributor; PR #5809 (milli-bytes parsing fix) — clean fix with tests.
- @joaquimrocha: Core maintainer/contributor; PR #5795 simplifies Mac notarization CI — merged.
- @beep-boopp: New contributor; PR #5794 (empty OIDC CA cert fix) — merged.

## Session Log
### 2026-05-18
- Reviewed 0 PRs (0 candidates found)
- Skipped: 182 non-draft open PRs — all had human review activity (illume actively reviews; copilot-pull-request-reviewer[bot] auto-reviews); 46 additional PRs were drafts
- New observations: Headlamp project has bot auto-reviewer on all PRs; primary maintainer reviews rapidly; commit format is `area: SubArea: Description`

### 2026-05-19
- Reviewed 5 PRs: #5538 (APPROVE), #5731 (APPROVE), #5746 (REQUEST_CHANGES), #5748 (NEEDS_DISCUSSION), #5408 (APPROVE)
- Skipped: 178 non-draft open PRs had human review activity; 46 were drafts
- New observations: Human review filter must use `author.__typename == "User"` in GraphQL, not just totalCount of reviews. 5 PRs had only bot reviews. Commit format violations caught in 2/5 PRs. Helm schema incomplete valueFrom coverage pattern. React Fragment key prop best practice fix.

### 2026-05-20
- Reviewed 1 PR: #5748 (REQUEST_CHANGES — re-review, head_sha updated)
- Skipped: 4 PRs in SKIP_SET (head_sha unchanged); 177 other non-draft PRs all had human review activity
- New observations: PR #5748 regenerated storyshots (−3183 lines mostly snapshots), resolving prior gap. Pattern: large PRs touching `defaultAppThemes` always produce large storyshot diffs. `eslint-disable-next-line` comments can become stale after dependency-array fixes; verify suppressions are still needed. CNCF CLA is a hard merge blocker in kubernetes-sigs repos.

### 2026-05-21
- Reviewed 13 PRs: #5786 (APPROVE), #5785 (APPROVE), #5783 (APPROVE), #5781 (APPROVE), #5779 (NEEDS_DISCUSSION), #5778 (REQUEST_CHANGES), #5777 (NEEDS_DISCUSSION), #5775 (APPROVE), #5774 (APPROVE), #5769 (APPROVE), #5768 (APPROVE), #5767 (APPROVE), #5764 (NEEDS_DISCUSSION)
- Skipped: 5 PRs in SKIP_SET (head_sha unchanged); ~178 other non-draft PRs had human review activity (k8s-ci-robot bot comments only on the 13 reviewed PRs, all with no formal User reviews)
- New observations: k8s-ci-robot posts IssueComment (not Review) on every PR — do not count as human review. Unresolved merge conflicts found in PR #5778 (critical). Large hooks-cleanup initiative (#5183) spawning many small sub-issue PRs. Experimental tsgo compiler being introduced as dev tooling (PR #5779 — needs maintainer discussion). OIDC auto-login feature (PR #5764) well-structured but sessionStorage logout edge case needs attention.

### 2026-05-22
- Reviewed 17 PRs: #5786 (APPROVE re-review), #5785 (APPROVE re-review), #5783 (APPROVE re-review), #5777 (APPROVE re-review), #5774 (APPROVE re-review), #5768 (APPROVE re-review), #5767 (APPROVE re-review), #5764 (NEEDS_DISCUSSION re-review), #5746 (REQUEST_CHANGES re-review), #5820 (APPROVE), #5809 (APPROVE), #5805 (APPROVE), #5804 (APPROVE), #5803 (APPROVE), #5798 (APPROVE), #5795 (APPROVE), #5794 (APPROVE)
- Skipped: 7 PRs in SKIP_SET (head_sha unchanged: #5408, #5538, #5731, #5775, #5778, #5779, #5781); ~171 other non-draft PRs had human review activity
- New observations: Render-phase setState anti-pattern cluster: 3 new PRs by @ayushmaan-16 fix different forms of the same issue. k8cache bypass fix (#5798) introduces `IsKubernetesResourceAPIPath` — potentially confusing `IsAuthBypassURL` naming. Mac notarization CI simplified by maintainer (#5795). OIDC empty CA cert was a silent breakage for all public OIDC providers (#5794).

### 2026-05-23
- Reviewed 8 PRs: #5783 (APPROVE re-review), #5777 (APPROVE re-review), #5775 (APPROVE re-review), #5805 (APPROVE re-review), #5804 (APPROVE re-review), #5803 (APPROVE re-review), #5798 (APPROVE re-review), #5778 (REQUEST_CHANGES re-review)
- Skipped: 15 PRs in SKIP_SET (head_sha unchanged); 2 merged (#5795, #5794); 1 closed (#5769); 178 new non-draft PRs all had human review activity
- New observations: @Rohith-Saran's PR #5778 resolved merge conflicts but retains `feat:` Conventional Commits format — 3rd REQUEST_CHANGES for same format issue. PR #5778 also missing `externalLinks` from Helm values.schema.json. @harrshita123's PR #5777 (all-namespace cache invalidation) updated with DeleteKeys delegation and regression test — clean approval. @ayushmaan-16's three SimpleTable/useKubeObjectList PRs all updated (APPROVE on re-review). @Nabsku's PR #5798 refactored with DRY kubernetesResourceAPIPathIndex helper — strong improvement. PR body placeholders (`#<issue-number>`) should be flagged as Warning.

### 2026-05-24
- Reviewed 1 PR: #5785 (APPROVE re-review)
- Skipped: 21 PRs in SKIP_SET (head_sha unchanged); 182 new/other non-draft PRs had human review activity
- New observations: PR #5785 squashed commit message missing SubArea (`frontend: Replace...` instead of `frontend: themes: Replace...`) and exceeds 72-char limit (91 chars). Code and tests are correct. Test improvement is notable: verifies event name `'change'` and handler reference equality on cleanup.
