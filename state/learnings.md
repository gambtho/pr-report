# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-05-20*

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
- Commit message format violations: `feat(area): ...` (Conventional Commits style) instead of `area: Component: Description` (seen in PR #5746; 1/5 PRs 2026-05-19 session).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746).
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).

## False Positives / Project Conventions
- copilot-pull-request-reviewer[bot] auto-reviews every PR; this is NOT human review activity and should not count as a filter criterion for "has human review". The GraphQL review filter must check `author.__typename == "User"` to distinguish human from bot reviews.
- @illume reviews PRs very quickly after opening, so PRs that appear unreviewed often already have a review within hours.
- `addListener`/`removeListener` on MediaQueryList is pre-existing code in `frontend/src/lib/themes.ts` — not a new issue and is suppressed via eslint-disable already; do not flag as new issue.
- Theme names are displayed via `capitalize(it.name)` in Settings.tsx — no dedicated displayName/label field needed; 'auto' → 'Auto' is acceptable.

## Author Notes
- @illume: Primary maintainer; approves promptly but requests commit-guideline fixes first; warm/encouraging tone. Authored PR #5408 (large doc+e2e update for Dex/OAuth2-Proxy tutorial).
- @iashutoshyadav: Clean small fix style; good PR description with before/after code.
- @govindup63: Well-documented PR with detailed step-by-step test instructions and full backend test coverage; thorough author.
- @rforced: Feature contributor; needs reminder about project commit convention.
- @HarK-github: Helm chart contributor using Conventional Commits style (needs commit format guidance).

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
