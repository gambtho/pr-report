# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-05-18*

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
- (no issues yet — no PRs reviewed)

## False Positives / Project Conventions
- copilot-pull-request-reviewer[bot] auto-reviews every PR; this is NOT human review activity and should not count as a filter criterion for "has human review". The current prompt's GraphQL review filter catches bot reviews too, causing 0 candidates on very active projects.
- @illume reviews PRs very quickly after opening, so PRs that appear unreviewed often already have a review within hours.

## Author Notes
- @illume: Primary maintainer; approves promptly but requests commit-guideline fixes first; warm/encouraging tone.

## Session Log
### 2026-05-18
- Reviewed 0 PRs (0 candidates found)
- Skipped: 182 non-draft open PRs — all had human review activity (illume actively reviews; copilot-pull-request-reviewer[bot] auto-reviews); 46 additional PRs were drafts
- New observations: Headlamp project has bot auto-reviewer on all PRs; primary maintainer reviews rapidly; commit format is `area: SubArea: Description`
