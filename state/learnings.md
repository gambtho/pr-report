# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-06-03*

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
- Commit message missing SubArea segment: `area: Description` instead of `area: SubArea: Description` (seen in PR #5785, #5843, #5832, #5842, #5841, #5775, #5783, #5844, #5804, #5877 partial, #5895, #5903, #5902; multiple sessions).
- Commit subject lowercase verb: `frontend: fix ...` instead of `frontend: Fix ...` (seen in PR #5841, #5842 by @Naga15 — now fixed; also #5843 by @Rohith-Saran; also #5786 by @vmridul; also #5903 by @codeurluce).
- Commit subject exceeding 72-char soft limit (seen in PR #5785: >90 chars; PR #5785 still unfixed in 2026-05-29 re-review).
- Helm schema `additionalProperties: false` with incomplete field coverage (fieldRef/resourceFieldRef missing from valueFrom in PR #5746; outstanding after 3 reviews). PR #5778 also missing `externalLinks` from `values.schema.json` — now fixed.
- React shorthand `<>` fragments receiving `key` props (seen in PR #5538 — fix was to use `<React.Fragment key={...}>`).
- CI workflow `push` triggers without `paths` filter causing unnecessary full-stack e2e runs on unrelated commits (seen in PR #5408).
- Missing storyshot regeneration when `defaultAppThemes` array changes (seen in PR #5748).
- Unresolved Git merge conflict markers in PRs (seen in PR #5778 — resolved in 2026-05-23 re-review).
- PRs where author cannot run tests locally (seen in PR #5777 — disk space; PR #5764 — no Go toolchain). CI must confirm green before merge.
- `useMemo(() => value, [])` anti-pattern used as a one-shot initialiser instead of lazy `useState(() => value)` (seen in PR #5767, #5803; 2 sessions — both now fixed).
- Render-phase state updates (`setState` called unconditionally during render body) causing React to drop and re-run the render (seen in PR #5805 — now resolved with render-phase derived-state pattern using stable filteredData from useMemo).
- Two sequential `setState` calls in the same render for the same piece of state (seen in PR #5804 — now fixed with Map consolidation).
- Missing frontend Vitest tests for new behavioral flows (seen in PR #5764 — OIDC auto-login AuthChooser useEffect still not tested after 7 re-reviews).
- Helm `externalLinks`/feature config fields not added to `values.schema.json` (seen in PR #5778 — now added).
- PR body containing unresolved placeholder `#<issue-number>` or `#NAN` instead of real issue reference (seen in PR #5778, #5844 — #5844 still has #NAN after 4 re-reviews).
- Storyshot files containing unrelated ARIA-element structural drift included in a PR diff (seen in PR #5843 — resolved in 2026-05-27 re-review).
- Trailing period in commit/PR title subject (seen in PR #5844 by @nikunjkumar05; persistent after 4 re-reviews).
- Multi-area dependency bump PRs missing area prefix in commit subject (seen in PR #5772 by @skoeva — "Bump fast-uri, brace-expansion, ws, containerd" with no `deps:` prefix).
- Vague "Address Copilot review comments" commit subjects without describing the actual change (seen in PR #5764 by @menardorama; persistent after 8 re-reviews).
- Merge commit "Merge branch 'main' into ..." included in PR branch (seen in PR #5809 by @yu-heejin — resolved 2026-05-27; PR #5764 by @menardorama — still present in 2026-06-01 re-review (2 merge commits); PR #5844 by @nikunjkumar05 — still present after 4 re-reviews).
- Unrelated single-line fix bundled into a feature PR (seen in PR #5764: `ThemeProviderNexti18n.tsx` fallback lang change unrelated to OIDC auto-login — now rationalized as related race condition fix).
- Vitest major version bump (3.x → 4.x): dependabot PRs for vitest 4 require explicit CI-green verification before merge due to breaking changes in vi.mock hoisting, snapshot serialization, and browser mode (seen in PRs #5901, #5899; 2026-06-02).
- New feature PRs without error-state UI: when a useQuery/useEffect can fail (e.g., 403, 404), the failure must surface to the user via Alert or similar — a silent empty state is misleading (seen in PR #5886 Permissions.tsx rulesQuery.error; 2026-06-02).
- Namespace state initialised to 'default' in new namespace-selector components causes a premature API call before the namespace list loads; initialise to null and gate queries on namespace !== null (seen in PR #5886; 2026-06-02).
- Dead code: `os.IsExist(err)` branch unreachable when using `os.O_CREATE|os.O_WRONLY` (no O_EXCL) — `OpenFile` with this combination never returns `EEXIST`. Seen in PR #5783; still present in 2026-05-29, 2026-06-02 re-reviews.
- URL-lowercasing bug: `safeLinkUrl` returns `url.toLowerCase()` instead of original `url` for case-sensitive path components (seen in PR #5778 — still open, SHA unchanged).
- Duplicate YAML key in values.yaml from bad merge/rebase (seen in PR #5764 — duplicate `clusterInventory:` key persists in 2026-05-30 re-review).
- Extra `}` in values.schema.json making JSON schema invalid (seen in PR #5764 — persists in 2026-05-30 re-review).
- `.cmd` shims on Windows require `shell: true` in Node.js `spawnSync`/`execFileSync` — adding `.cmd` extension alone is not sufficient (seen in PR #5861 by @skoeva — fixed).
- `list.kind.replace('List', '')` removes first occurrence rather than trailing suffix — use `/List$/` regex to avoid mangling names containing 'List' mid-string (seen in PR #5880 by @sniok — fixed).
- Abandoned OIDC state tokens never evicted from `oauthRequestMap` — use a background goroutine with TTL-based eviction (seen in PR #5866 by @ayushmaan-16 — fixed).
- GitHub Actions workflow using `inputs.*` directly in shell here-strings without sanitization — potential metacharacter injection (seen in PR #5881 by @skools-here — minor, approve with suggestion).
- CACert pointer regression: `CACert: &oidcCACert` passes pointer to empty string instead of nil when no cert is configured; downstream nil-checks will incorrectly see non-nil (seen in PR #5764 in 2026-05-30 re-review — still open).
- Removal of all godoc comments from exported/internal functions (seen in PR #5764 clusterinventory.go — in-progress).
- PR description says `useEffect` but implementation uses render-phase setState (seen in PR #5805 — approved, minor cosmetic mismatch only).
- Makefile target missing `npm ci` for a sub-package when that package was previously using `npm install`; CI jobs install deps independently but local `make <target>` will fail on fresh checkout (seen in PR #5895 by @skoeva — flagged in 2026-06-02 and 2026-06-03; still unresolved).
- i18n contributor opening separate PRs for the same language/session (PR #5902 and #5903 both by @codeurluce, both French translations opened on same day) — suggest consolidation to reduce review overhead.

## False Positives / Project Conventions
- `sessionStorage` usage in `AuthChooser` for OIDC auto-login loop prevention (PR #5764) is intentional — sessionStorage (not localStorage) correctly clears on tab close, so the auto-login fires once per session per cluster per tab.
- `koanf` env var mapping: `HEADLAMP_CONFIG_EXTERNAL_LINKS` maps to `external-links` key via the koanf env provider (uppercase `_` → lowercase `-` transformation with `HEADLAMP_CONFIG_` prefix stripped). This is a project convention, not a bug.
- `os.O_CREATE|os.O_WRONLY` without `O_EXCL` never returns EEXIST — `os.IsExist(err)` guard after such OpenFile call is dead code. Flag as Warning in any PR that adds this pattern.
- Helm variable reassignment `{{- $matched = true }}` inside a range block is valid Helm 3.1+ syntax — not a bug.
- `winShell = process.platform === 'win32'` in headlamp-plugin: glob patterns passed as execFileSync args with `shell: true` on Windows are handled by the downstream tool (i18next-scanner) rather than cmd.exe glob expansion. Do not flag as a bug.
- `CACert: &oidcCACert` (pointer to empty string when no cert configured) in `kubeconfig.newInClusterContextFromConfig` — all current consumers use `caCert != nil && *caCert != ""` double-guard, so no observable functional regression. Still flag as Suggestion for convention clarity (nil should mean absence for optional pointer fields).
- Storyshot MUI class-hash changes (e.g. `css-1d0cpfm-MuiTypography-root` → `css-1yibb5c-MuiTypography-root`) that accompany a `labelProps` or `sx` change are expected MUI behavior — the hash changes when the generated style changes. Not a bug.

## Author Notes
- @Utkarshpandey0001: PR #5886 (RBAC access inspector, 2026-06-02) — strong algorithmic implementation (permissionUtils.ts with full wildcard coverage + unit tests) but missing error-state UI, namespace default 'default' causes spurious API call, commit SubArea missing in both commits, no component-level tests. First reviewed PR; shows promise.
- @kishore08-07: Multiple PRs (#5774, #5768, #5767, #5820, #5887) — all hooks-cleanup sub-issues (#5183); clean targeted fixes, correct commit format. Consistently high quality.
- @ayushmaan-16: Multiple PRs — all React hooks/render-phase fixes or backend memory fixes. PRs #5803, #5804, #5805 approved across multiple sessions. PR #5866 (OIDC state eviction) approved — very strong technical author with correct commit format and production-quality tests.
- @Rohith-Saran: PR #5775 (listener leak — SubArea missing in 2/3 commits); PR #5778 (external links — commit format still Conventional Commits after 4 re-reviews + safeLinkUrl bug); PR #5843 (ApiError export — lowercase verb in commit). Pattern of commit format issues persists across all PRs.
- @sniok: Core contributor (maintainer-adjacent); PR #5779 adds experimental tsgo compiler as primary type-checker — awaiting team discussion. PR #5880 (kind name regex fix) approved — clean and precise.
- @menardorama: Feature contributor (PR #5764 OIDC auto-login + cluster inventory wiring); deployed to production at their company. Vague commit subjects and merge-main commits persist after 8 re-reviews; AuthChooser component-level test still missing; structural bugs (duplicate YAML key, extra JSON brace, CACert pointer regression) unresolved through 2026-06-01. New cluster inventory commits added but also have commit format issues (missing SubArea, non-standard area prefix).
- @vmridul: Small Go fix contributor; needs reminder about commit subject capitalization and SubArea format (PR #5786).
- @Nabsku: Backend contributor; PR #5777 and PR #5798 both approved. Strong test author. PR #5798 fix for k8cache non-API path bypass squashed cleanly (re-approved 2026-06-01 after SHA update — added tests and server.go bypass condition).
- @harrshita123: Backend contributor; PR #5777 (approved), PR #5840 (approved — correct commit format with SubArea), PR #5832 (approved — missing SubArea in commit subject). Improving on commit format.
- @yu-heejin: Frontend contributor; PR #5809 — approved in 2026-05-27 re-review (rebase done + decimal milli-bytes support added).
- @joaquimrocha: Core maintainer/contributor.
- @nikunjkumar05: PR #5844 — trailing period + #NAN placeholder + merge commit persist after 4+ re-reviews. Author may need direct maintainer intervention.
- @skoeva: PRs #5861 (Windows .cmd fix, approved), #5895 (CI parallelization, approved). Consistent commit format issue: uppercase area prefix (`CI:` instead of `ci:`) and missing SubArea. Pattern seen across multiple PRs.
- @codeurluce: PR #5902 and #5903 — French i18n contributor, translations are high quality and idiomatic. Both PRs share commit format issues (lowercase verb, missing SubArea). Opened two PRs on the same day for the same language; should consolidate in future.
- @Swastik19Nit: PR #5838 (ObjectEventList Age-clipping fix) — CLA now signed; PR approved after CLA blocker cleared. Fix is minimal and correct.

## Session Log
### 2026-06-03
- Reviewed 4 PRs: #5895 (re-review, APPROVE), #5838 (re-review, APPROVE), #5903 (APPROVE), #5902 (APPROVE)
- Skipped: 42 SHA-unchanged + 170 human-reviewed + 48 drafts
- New observations: PR #5838 (@Swastik19Nit) CLA blocker cleared — now approved. PR #5895 (@skoeva) re-review: SHA changed but commit format and Makefile npm-ci issues still unaddressed; still APPROVE. PRs #5902 and #5903 both by @codeurluce (new author), both French i18n, both with missing SubArea/lowercase-verb commit format; translations are high quality. Pattern: i18n contributors frequently miss SubArea in commit subjects.

### 2026-06-02
- Reviewed 11 PRs: #5783 (re-review, REQUEST_CHANGES), #5887 (APPROVE), #5898 (APPROVE), #5895 (APPROVE), #5894 (APPROVE), #5893 (APPROVE), #5900 (APPROVE), #5884 (APPROVE), #5901 (NEEDS_DISCUSSION), #5899 (NEEDS_DISCUSSION), #5886 (NEEDS_DISCUSSION)
- Skipped: 34 SHA-unchanged re-review candidates + 48 drafts + ~170 candidates with human review activity
- New observations: PR #5886 (@Utkarshpandey0001): first RBAC inspector PR — missing error Alert on SelfSubjectRulesReview failure (shows all-denied silently), namespace initialised to 'default' causing spurious API call before namespace list loads, missing SubArea in both commit subjects, no component-level Vitest tests. PRs #5901/#5899: vitest 3.x→4.x major bumps need explicit CI verification before merge and should be coordinated. PRs #5900/#5884: duplicate tmp 0.2.6 bumps — 5900 (comprehensive, all workspaces) supersedes 5884 (dependabot pluginctl only). PR #5887 (@kishore08-07): clean Chart useRef fix (continuing hooks-cleanup #5183 streak). PR #5898 (@YadavAkhileshh): NumRowsInput lazy state init — commit subject still exceeds 72-char limit.

### 2026-06-01
- Reviewed 2 PRs (all re-reviews): #5764 (REQUEST_CHANGES), #5798 (APPROVE)
- Skipped: 33 SHA unchanged + 48 drafts + 175 new candidates (all had human review activity)
- New observations: @Nabsku PR #5798 re-approved — author squashed into single clean commit with new tests and actual server.go bypass condition. @menardorama PR #5764 still REQUEST_CHANGES after 8th re-review: duplicate YAML key, extra JSON brace, vague commits, merge-main commits all persist. New cluster-inventory commits added with additional format issues. The `if ('oidcAutoLogin' in action.payload)` guard in configSlice and OIDCAuth popup/redirect disambiguation are now solid positives.

### 2026-05-31
- Reviewed 0 PRs (all candidates had SHA-unchanged or human review activity)
- Skipped: 38 SHA unchanged + 48 drafts + 171 new candidates with human review activity

### 2026-05-30
- Reviewed 2 PRs (re-reviews): #5764 (REQUEST_CHANGES), #5881 (APPROVE)
- Skipped: 33 SHA unchanged + ~180 with human activity

### 2026-05-29
- Reviewed 3 PRs: #5783 (REQUEST_CHANGES), #5777 (APPROVE), #5785 (REQUEST_CHANGES)
- New observations: #5783 dead code pattern; #5785 commit >90 chars and missing SubArea

### 2026-05-28
- Reviewed 6 PRs: #5880 (APPROVE), #5874 (APPROVE), #5866 (APPROVE), #5877 (APPROVE), #5764 (REQUEST_CHANGES), #5861 (APPROVE)

### 2026-05-27
- Reviewed 8 PRs: #5838 (NEEDS_DISCUSSION), #5843 (APPROVE), #5844 (REQUEST_CHANGES), #5809 (APPROVE), #5805 (APPROVE), #5804 (APPROVE), #5803 (APPROVE), #5822 (APPROVE)

### 2026-05-26
- Reviewed 6 PRs: #5838 (NEEDS_DISCUSSION), #5820 (APPROVE), #5822 (APPROVE), #5779 (NEEDS_DISCUSSION), #5778 (REQUEST_CHANGES), #5764 (REQUEST_CHANGES)
