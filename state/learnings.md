# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-05-21*

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

## Detected Stack
- **Languages:** TypeScript (frontend/), Go (backend/)
- **Runtimes:** Node.js >=20.11.1, npm >=10.0.0, Go 1.25.9 (per AGENTS.md / backend/go.mod)
- **Frontend framework:** React + Material-UI v5
- **Test frameworks:** Vitest (frontend), Go test (backend)
- **Build:** npm scripts (`npm run build`, `npm run frontend:build`, `npm run backend:build`)
- **CI:** GitHub Actions (.github/workflows/), Dockerfiles, Helm charts (charts/)
- **Other:** Electron desktop app (app/), plugin system (plugins/), i18n tooling (tools/i18n/)

## Common Issues
- Commit message format violations: `feat(area): ...` (Conventional Commits style) instead of `area: Component: Description` (seen in PR #5746, #5778; 2 sessions).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746).
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).
- Commit title lowercase verb + missing SubArea (seen in PR #5786 — `backend: changed format verb` should be `backend: kubeconfig: Change format verb`).
- Unresolved Git merge conflict markers in PRs (seen in PR #5778 — `backend/cmd/server.go`, `backend/pkg/config/config.go`, `backend/pkg/headlampconfig/headlampConfig.go`).
- PRs where author cannot run tests locally (seen in PR #5777 — disk space; PR #5764 — no Go toolchain). CI must confirm green before merge.
- `sessionStorage` used for OIDC loop-prevention (PR #5764) needs careful scoping: flag should be cleared on explicit logout, not just on successful OIDC callback.

## False Positives / Project Conventions
- copilot-pull-request-reviewer[bot] auto-reviews every PR; this is NOT human review activity and should not count as a filter criterion for "has human review". The GraphQL review filter must check `author.__typename == "User"` to distinguish human from bot reviews.
- k8s-ci-robot posts automated comments (APPROVALNOTIFIER, welcome messages) on every PR — these are bot comments and do not count as human review activity.
- @illume reviews PRs very quickly after opening, so PRs that appear unreviewed often already have a review within hours.
- `addListener`/`removeListener` on MediaQueryList is pre-existing code in `frontend/src/lib/themes.ts` — not a new issue and is suppressed via eslint-disable already; do not flag as new issue (PR #5785 fixed it).
- Theme names are displayed via `capitalize(it.name)` in Settings.tsx — no dedicated displayName/label field needed; 'auto' → 'Auto' is acceptable.
- `useCallback` with `[]` dep array wrapping a `ref.current` access is the correct pattern for the react-hooks/refs rule — not a stale closure issue since ref objects are stable.
- Redux `dispatch` from `useDispatch()` is guaranteed stable across renders; adding it to `useEffect`/`useMemo` deps is correct and does not cause extra re-runs.

## Author Notes
- @illume: Primary maintainer; approves promptly but requests commit-guideline fixes first; warm/encouraging tone. Authored PR #5408 (large doc+e2e update for Dex/OAuth2-Proxy tutorial).
- @iashutoshyadav: Clean small fix style; good PR description with before/after code.
- @govindup63: Well-documented PR with detailed step-by-step test instructions and full backend test coverage; thorough author.
- @rforced: Feature contributor; needs reminder about project commit convention.
- @HarK-github: Helm chart contributor using Conventional Commits style (needs commit format guidance).
- @YadavAkhileshh: Two PRs in one session (#5785, #5783) — clean small fixes, good PR descriptions, follows project conventions.
- @kishore08-07: Three PRs in one session (#5774, #5768, #5767) — all hooks-cleanup sub-issues (#5183); clean targeted fixes, no commit format issues.
- @Rohith-Saran: Two PRs in one session (#5778, #5775) — #5775 was clean; #5778 had unresolved merge conflicts and Conventional Commits format.
- @sniok: Core contributor (maintainer-adjacent); PR #5779 adds experimental tsgo compiler as primary type-checker, which needs team discussion.
- @menardorama: Feature contributor (PR #5764 OIDC auto-login); deployed to production at their company; backend tests not run locally.
- @vmridul: Small Go fix contributor; needs reminder about commit subject capitalization and SubArea format.

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
