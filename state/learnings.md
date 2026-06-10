# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-06-10*

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
- Commit message format violations: `feat(area): ...` (Conventional Commits style) instead of `area: Component: Description` (seen in PR #5746, #5778; 6 sessions). PR #5778 by @Rohith-Saran persists after 5 re-reviews.
- Commit message missing SubArea segment: `area: Description` instead of `area: SubArea: Description` (seen in PR #5785, #5843, #5832, #5842, #5841, #5775, #5783, #5844, #5804, #5877 partial, #5895, #5903, #5902, #5777; multiple sessions).
- Commit subject lowercase verb: `frontend: fix ...` instead of `frontend: Fix ...` (seen in PR #5841, #5842 by @Naga15 — now fixed; also #5843 by @Rohith-Saran; also #5786 by @vmridul; also #5903 by @codeurluce).
- Commit subject exceeding 72-char soft limit (seen in PR #5785: >90 chars; PR #5785 still unfixed in 2026-05-29 re-review).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746; outstanding after 3 reviews). PR #5778 missing `externalLinks` from `values.schema.json` (config.additionalProperties is not false so not a hard block, but still a best-practice gap).
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).
- Unresolved Git merge conflict markers in PRs (seen in PR #5778 — resolved in 2026-05-23 re-review).
- PRs where author cannot run tests locally (seen in PR #5777 — disk space; PR #5764 — no Go toolchain). CI must confirm green before merge.
- `useMemo(() => value, [])` anti-pattern used as a one-shot initialiser instead of lazy `useState(() => value)` (seen in PR #5767, #5803; 2 sessions — both now fixed).
- Render-phase state updates (`setState` called unconditionally during render body) causing React to drop and re-run the render (seen in PR #5805 — now resolved).
- Two sequential `setState` calls in the same render for the same piece of state (seen in PR #5804 — now fixed with Map consolidation).
- Missing frontend Vitest tests for new behavioral flows (seen in PR #5764 — OIDC auto-login AuthChooser useEffect still not tested after 7 re-reviews).
- Helm `externalLinks`/feature config fields not added to `values.schema.json` (seen in PR #5778 — additionalProperties not false so no hard failure, but best practice gap remains).
- PR body containing unresolved placeholder `#<issue-number>` or `#NAN` instead of real issue reference (seen in PR #5778, #5844 — #5778 still has placeholder after 5 re-reviews; #5775 references its own PR number instead of issue #5417).
- Trailing period in commit/PR title subject (seen in PR #5844 by @nikunjkumar05; persistent after 4 re-reviews).
- Multi-area dependency bump PRs missing area prefix in commit subject (seen in PR #5772 by @skoeva).
- Vague "Address Copilot review comments" commit subjects without describing the actual change (seen in PR #5764 by @menardorama; persistent after 8 re-reviews).
- Merge commit "Merge branch 'main' into ..." included in PR branch (seen in PR #5809 by @yu-heejin — resolved; PR #5764 by @menardorama — still present; PR #5844 by @nikunjkumar05 — still present; PR #5832 by @harrshita123 — resolved 2026-06-06).
- Vitest major version bump (3.x → 4.x): dependabot PRs for vitest 4 require explicit CI-green verification before merge (seen in PRs #5901, #5899; 2026-06-02).
- New feature PRs without error-state UI: when a useQuery/useEffect can fail (e.g., 403, 404), failure must surface via Alert — silent empty state is misleading (seen in PR #5886; 2026-06-02).
- Namespace state initialised to 'default' in new namespace-selector components causes premature API calls; initialise to null (seen in PR #5886; 2026-06-02).
- Dead code: `os.IsExist(err)` branch unreachable when using `os.O_CREATE|os.O_WRONLY` (no O_EXCL) — seen in PR #5783; still present in multiple re-reviews.
- URL-lowercasing bug: `safeLinkUrl` was returning `url.toLowerCase()` instead of original `url` for case-sensitive paths (seen in PR #5778 — fixed in 2026-06-09 commit; now correctly lowercases only the scheme).
- Duplicate YAML key in values.yaml from bad merge/rebase (seen in PR #5764 — persists).
- Extra `}` in values.schema.json making JSON schema invalid (seen in PR #5764 — persists).
- Abandoned OIDC state tokens never evicted from `oauthRequestMap` — use background goroutine with TTL-based eviction (seen in PR #5866 — fixed).
- CACert pointer regression: `CACert: &oidcCACert` passes pointer to empty string instead of nil when no cert (seen in PR #5764 — still open).
- PR description left stale after iterative commits (seen in PR #5803 — approved 2026-06-06; always verify description matches final diff).
- `resourceModifiedWarning` state not cleared after successful save in EditorDialog — persists until manually closed (seen in PR #5894 — suggestion flagged 2026-06-08 and 2026-06-10; non-blocking UX rough edge).
- Storybook story description text that mischaracterises triggering conditions (seen in PR #5893 PodEvict story — Evict renders for any Pod, not only when useEvict setting is enabled; flagged 2026-06-08).
- Helm template mountPath not normalized before prefix-match validation: `printf "%s/" $mountPath` produces double-slash when mountPath has a trailing slash, causing validation to fail for legitimate configs (seen in PR #5874 — flagged 2026-06-10).
- root `package-lock.json` changes that add unrelated dev dependencies without matching `package.json` update: can introduce major-version mismatches with workspace sub-packages (seen in PR #5775 — cross-env@10.1.0 added to root lock while frontend/package.json pins ^7.0.3; flagged 2026-06-10).

## False Positives / Project Conventions
- `sessionStorage` usage in `AuthChooser` for OIDC auto-login loop prevention is intentional — clears on tab close.
- `koanf` env var mapping: `HEADLAMP_CONFIG_EXTERNAL_LINKS` maps to `external-links` via koanf env provider. Project convention.
- `os.O_CREATE|os.O_WRONLY` without `O_EXCL` never returns EEXIST — `os.IsExist(err)` guard is dead code. Flag as Warning in any PR adding this pattern.
- Helm variable reassignment `{{- $matched = true }}` inside a range block is valid Helm 3.1+ syntax.
- Storyshot MUI class-hash changes that accompany a `labelProps` or `sx` change are expected MUI behavior — the hash changes when the generated style changes. Not a bug.
- PR #5895 (CI parallelization): `test-headlamp-plugin.js` runs `npm ci` internally so removing outer `npm install` in the Makefile `plugins-test` target is safe. Do not re-flag.
- In `validateTracing()` (PR #5832): the new implementation correctly checks all exporter conditions. PR approved 2026-06-06.
- `CACert: &oidcCACert` (pointer to empty string) — all current consumers use double-guard `caCert != nil && *caCert != ""`. Flag as Suggestion for convention clarity only.
- MUI sx array merging (`sx={[defaultSx, ...(Array.isArray(labelSx) ? labelSx : labelSx ? [labelSx] : [])]}`) in PRs touching `HoverInfoLabel` is the correct MUI v5 pattern for merging sx props. Not a bug.
- `!IsKubernetesResourceAPIPath || !IsAuthBypassURL` condition in cache middleware (PR #5798): `IsAuthBypassURL` returns false for `/version`, `/healthz`, `/selfsubjectrulesreviews`, `/selfsubjectaccessreviews` — these should also bypass caching even under `/apis/` paths. The `||` is intentional and correct.
- `values.schema.json` `config` section has no `additionalProperties: false` — adding new fields to `values.yaml` without updating the schema will not cause `helm lint` to fail. Still good practice to update the schema.

## Author Notes
- @sudhidutta7694: PRs #5894 and #5893. PR #5894 (EditorDialog conflict-detection) — APPROVE 2026-06-10 (i18n update only since last APPROVE 2026-06-08). PR #5893 (DeleteButton stories) — APPROVE 2026-06-08. Strong upward trajectory; thorough test coverage.
- @Swastik19Nit: PR #5838 (ObjectEventList Age-clipping fix) — CLA cleared; approved 2026-06-08. Fix is minimal and correct using MUI sx array merging.
- @kishore08-07: Multiple PRs (#5774, #5768, #5767, #5820, #5887) — hooks-cleanup sub-issues (#5183); clean targeted fixes, correct commit format. Consistently high quality.
- @ayushmaan-16: Multiple PRs — React hooks/render-phase fixes and backend memory fixes. PR #5866 (OIDC state eviction) approved — strong technical author. PR #5803 (NEEDS_DISCUSSION 2026-06-06 re-review) — implementation diverged from PR description.
- @Rohith-Saran: PRs #5775, #5778 — commit format issues persist across both PRs (Conventional Commits style on first commit of #5778, `#<issue-number>` placeholder, wrong issue reference in #5775 body). Core fixes are technically correct but always requires format cleanup.
- @sniok: Core contributor; PR #5779 adds experimental tsgo compiler; PR #5880 (kind name regex fix) approved.
- @menardorama: PR #5764 OIDC auto-login — vague commit subjects, merge-main commits, structural bugs persist after 8+ re-reviews.
- @harrshita123: PRs #5777, #5840, #5832 — responds to rebase requests; SubArea still missing; overall improving.
- @skoeva: PRs #5861, #5895, #5877, #5900 — consistently solid quality; SubArea usage improving.
- @codeurluce: PRs #5902, #5903 — French i18n, high quality translations; commit format issues (lowercase verb, missing SubArea).
- @nikunjkumar05: PR #5844 — trailing period + #NAN placeholder + merge commit persist after 4+ re-reviews.
- @vmridul: Small Go fix contributor; needs reminder about commit subject capitalization and SubArea format.
- @Nabsku: Backend contributor; PRs #5777, #5798 both approved. Strong test author. PR #5798 SHA changed due to rebase 2026-06-10 — content verified unchanged.
- @kahirokunn: PR #5874 (Cluster Inventory charts) — NEEDS_DISCUSSION 2026-06-10 due to potential trailing-slash bug in Helm validation. PR was substantially reworked 2026-06-10 with 4 new commits. Previously approved 2026-05-28 (different content).

## Session Log
### 2026-06-10
- Reviewed 5 PRs: #5894 (re-review, APPROVE), #5874 (re-review, NEEDS_DISCUSSION), #5798 (re-review, APPROVE), #5778 (re-review, REQUEST_CHANGES), #5775 (re-review, REQUEST_CHANGES)
- Skipped: 30 SHA-unchanged + 179 new candidates all had human review activity (reviews or comments > 0) + 44 drafts
- New observations: PR #5874 substantially reworked today with 4 commits; potential Helm mountPath trailing-slash normalization bug. PR #5775 has unexplained root package-lock.json changes adding cross-env@10.1.0 (major version mismatch with frontend ^7.0.3). PR #5778 safeLinkUrl bug fixed in new commit but commit format and placeholder issues persist. PR #5798 SHA change is pure rebase — content verified correct.

### 2026-06-09
- Reviewed 0 PRs
- Skipped: 33 SHA-unchanged + 176 new candidates all had human review activity (reviews or comments > 0) + 44 drafts
- New observations: No actionable PRs found. All non-draft, non-previously-reviewed open PRs had human review activity. REREVIEW_SET was empty (no SHA changes since yesterday's run).

### 2026-06-08
- Reviewed 3 PRs: #5894 (re-review, APPROVE), #5893 (re-review, APPROVE), #5838 (re-review, APPROVE)
- Skipped: 32 SHA-unchanged + 171 candidates all had human review activity (reviews or comments > 0) + 44 drafts
- New observations: PR #5894 (@sudhidutta7694) — SHA updated since 2026-06-07 REQUEST_CHANGES; now properly memoizes handleSave/onClose with useCallback, adds comprehensive Vitest test for conflict scenario. All prior issues resolved — APPROVE. Minor suggestion: resourceModifiedWarning not cleared after successful save. PR #5893 (@sudhidutta7694) — SHA changed, additive stories still clean; minor PodEvict story description nit. APPROVE. PR #5838 (@Swastik19Nit) — SHA changed to include all storyshot updates from sx merge; fix itself unchanged and correct. APPROVE.

### 2026-06-07
- Reviewed 1 PR: #5894 (re-review, REQUEST_CHANGES)
- Skipped: 34 SHA-unchanged + 165 non-re-review candidates all had human review activity + ~42 drafts
- New observations: PR #5894 — SHA updated to add ResourceWatcher component refactor; eslint-disable exhaustive-deps suppression (missing deps: onClose, handleSave, setErrorMessage, activityId); Vitest tests absent.

### 2026-06-06
- Reviewed 4 PRs: #5832 (re-review, APPROVE), #5861 (re-review, APPROVE), #5900 (re-review, APPROVE), #5803 (re-review, NEEDS_DISCUSSION)
- Skipped: 31 SHA-unchanged + 165 non-draft PRs all had human review activity + 43 drafts

### 2026-06-05
- Reviewed 2 PRs: #5832 (re-review, REQUEST_CHANGES), #5877 (re-review, APPROVE)
- Skipped: 39 SHA-unchanged + 178 new PRs all had human review activity + 42 drafts

### 2026-06-04
- Reviewed 4 PRs: #5895 (re-review, APPROVE), #5840 (re-review, APPROVE), #5832 (re-review, REQUEST_CHANGES), #5777 (re-review, APPROVE)
- Skipped: 38 SHA-unchanged + 174 new PRs all had human review activity + 43 drafts

### 2026-06-03
- Reviewed 4 PRs: #5895 (re-review, APPROVE), #5838 (re-review, APPROVE), #5903 (APPROVE), #5902 (APPROVE)
- Skipped: 42 SHA-unchanged + 170 human-reviewed + 48 drafts

### 2026-06-02
- Reviewed 11 PRs: #5783 (re-review, REQUEST_CHANGES), #5887 (APPROVE), #5898 (APPROVE), #5895 (APPROVE), #5894 (APPROVE), #5893 (APPROVE), #5900 (APPROVE), #5884 (APPROVE), #5901 (NEEDS_DISCUSSION), #5899 (NEEDS_DISCUSSION), #5886 (NEEDS_DISCUSSION)
- Skipped: 34 SHA-unchanged re-review candidates + 48 drafts + ~170 candidates with human review activity

### 2026-06-01
- Reviewed 2 PRs (all re-reviews): #5764 (REQUEST_CHANGES), #5798 (APPROVE)
- Skipped: 33 SHA unchanged + 48 drafts + 175 new candidates (all had human review activity)

### 2026-05-30
- Reviewed 2 PRs (re-reviews): #5764 (REQUEST_CHANGES), #5881 (APPROVE)

### 2026-05-29
- Reviewed 3 PRs: #5783 (REQUEST_CHANGES), #5777 (APPROVE), #5785 (REQUEST_CHANGES)

### 2026-05-28
- Reviewed 6 PRs: #5880 (APPROVE), #5874 (APPROVE), #5866 (APPROVE), #5877 (APPROVE), #5764 (REQUEST_CHANGES), #5861 (APPROVE)

### 2026-05-27
- Reviewed 8 PRs: #5838 (NEEDS_DISCUSSION), #5843 (APPROVE), #5844 (REQUEST_CHANGES), #5809 (APPROVE), #5805 (APPROVE), #5804 (APPROVE), #5803 (APPROVE), #5822 (APPROVE)

### 2026-05-26
- Reviewed 6 PRs: #5838 (NEEDS_DISCUSSION), #5820 (APPROVE), #5822 (APPROVE), #5779 (NEEDS_DISCUSSION), #5778 (REQUEST_CHANGES), #5764 (REQUEST_CHANGES)
