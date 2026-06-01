# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: 2026-06-01*

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
- Dead code: `os.IsExist(err)` branch unreachable when using `os.O_CREATE|os.O_WRONLY` (no O_EXCL) — `OpenFile` with this combination never returns `EEXIST`. Seen in PR #5783; still present in 2026-05-29 re-review (SHA unchanged).
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

## False Positives / Project Conventions
- `sessionStorage` usage in `AuthChooser` for OIDC auto-login loop prevention (PR #5764) is intentional — sessionStorage (not localStorage) correctly clears on tab close, so the auto-login fires once per session per cluster per tab.
- `koanf` env var mapping: `HEADLAMP_CONFIG_EXTERNAL_LINKS` maps to `external-links` key via the koanf env provider (uppercase `_` → lowercase `-` transformation with `HEADLAMP_CONFIG_` prefix stripped). This is a project convention, not a bug.
- `os.O_CREATE|os.O_WRONLY` without `O_EXCL` never returns EEXIST — `os.IsExist(err)` guard after such OpenFile call is dead code. Flag as Warning in any PR that adds this pattern.
- Helm variable reassignment `{{- $matched = true }}` inside a range block is valid Helm 3.1+ syntax — not a bug.
- `winShell = process.platform === 'win32'` in headlamp-plugin: glob patterns passed as execFileSync args with `shell: true` on Windows are handled by the downstream tool (i18next-scanner) rather than cmd.exe glob expansion. Do not flag as a bug.
- `CACert: &oidcCACert` (pointer to empty string when no cert configured) in `kubeconfig.newInClusterContextFromConfig` — all current consumers use `caCert != nil && *caCert != ""` double-guard, so no observable functional regression. Still flag as Suggestion for convention clarity (nil should mean absence for optional pointer fields).

## Author Notes
- @kishore08-07: Multiple PRs (#5774, #5768, #5767, #5820) — all hooks-cleanup sub-issues (#5183); clean targeted fixes, correct commit format. Consistently high quality.
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

## Session Log
### 2026-06-01
- Reviewed 2 PRs (all re-reviews): #5764 (REQUEST_CHANGES), #5798 (APPROVE)
- Skipped: 33 SHA unchanged + 48 drafts + 175 new candidates (all had human review activity)
- New observations: @Nabsku PR #5798 re-approved — author squashed into single clean commit with new tests and actual server.go bypass condition. @menardorama PR #5764 still REQUEST_CHANGES after 8th re-review: duplicate YAML key, extra JSON brace, vague commits, merge-main commits all persist. New cluster-inventory commits added with additional format issues. The `if ('oidcAutoLogin' in action.payload)` guard in configSlice and OIDCAuth popup/redirect disambiguation are now solid positives.

### 2026-05-31
- Reviewed 0 PRs
- Skipped: 257 total (48 drafts, 35 sha_unchanged, 174 had human review activity)
- New observations: No new reviewable PRs again — @illume continues to review all new PRs before daily job runs. Only stale re-review candidates remain open (SHA unchanged). The pattern from 2026-05-30 and earlier sessions continues: this repo has a very active reviewer, and daily automation only catches edge cases.

### 2026-05-30
- Reviewed 5 PRs (all re-reviews): #5764, #5767, #5768, #5805, #5820
- Skipped: 30 (SHA unchanged) + 173+ (all new candidates had human review activity)
- New observations: @illume continues to review all new PRs before daily job runs — only re-reviews remain actionable. PR #5764 (@menardorama) now has CACert pointer regression (new) plus persistent structural bugs (duplicate YAML key, extra JSON brace) — still REQUEST_CHANGES after 7 re-reviews. @kishore08-07 PRs #5767 and #5768 approved cleanly. @ayushmaan-16 PR #5805 approved — render-phase derived-state pattern is valid React. @kishore08-07 PR #5820 approved — module-scope pure getNumReplicas with proper parseInt radix.

### 2026-05-29
- Reviewed 12 PRs: #5764 (re-review), #5785 (re-review), #5803 (re-review), #5804 (re-review), #5822 (re-review), #5844 (re-review), #5861, #5866, #5874, #5877, #5880, #5881
- Skipped: 28 (SHA unchanged) + ~150 (human review activity on new candidates)
- New observations: @WasThatRudy PR #5822 fully approved — all tests implemented. @ayushmaan-16 #5803 and #5804 approved. @sniok PR #5880 regex fix approved. @ayushmaan-16 #5866 (OIDC state eviction) approved. @skoeva PR #5877 approved. @skoeva PR #5861 approved. @kahirokunn PR #5874 approved. @skools-here PR #5881 approved. @menardorama PR #5764 still REQUEST_CHANGES. @YadavAkhileshh PR #5785 still REQUEST_CHANGES. @nikunjkumar05 PR #5844 still REQUEST_CHANGES.

### 2026-05-28
- Reviewed 6 PRs (all re-reviews): #5783, #5785, #5803, #5804, #5805, #5844
- Skipped: 26 (SHA unchanged) + 178 (all new candidates had human review activity)
- New observations: @ayushmaan-16 all three SimpleTable/useKubeObjectList PRs (#5803, #5804, #5805) now approved after solid fixes. @YadavAkhileshh still not fixing SubArea and commit length in #5785 or dead os.IsExist in #5783 despite repeated flagging. @nikunjkumar05 PR #5844 still has trailing period + #NAN after 3 re-reviews.

### 2026-05-27
- Reviewed 12 PRs (all re-reviews): #5764, #5775, #5778, #5779, #5783, #5785, #5798, #5809, #5830, #5838, #5843, #5844
- Skipped: 4 (SHA unchanged: #5822, #5841, #5842, #5845) + 150 (all new candidates had human review activity)
- New observations: PR #5798 (@Nabsku) approved. PR #5809 (@yu-heejin) approved — rebase done. PR #5838 (@Swastik19Nit) NEEDS_DISCUSSION — `cncf-cla: no` hard blocker. Dead `os.IsExist` code found in PR #5783. URL-lowercasing bug found in PR #5778.

### 2026-05-26
- Reviewed 5 PRs (re-reviews only): #5842, #5841, #5822, #5809, #5764
- Skipped: 35 (SHA unchanged) + 169 (human review activity)
- New observations: @illume reviews PRs so promptly that by the time the daily job runs, essentially all new PRs have human review.

### 2026-05-22
- Reviewed 9 PRs: #5809, #5795, #5794, #5805, #5804, #5803, #5798, #5775, #5778
- New observations: multiple React render-phase fix patterns

### 2026-05-21
- Reviewed 7 PRs: #5786, #5774, #5768, #5767, #5764, #5746, #5820
- New observations: hooks cleanup PRs from issue #5183
