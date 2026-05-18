# Daily PR Review — kubernetes-sigs/headlamp

You are running non-interactively inside a GitHub Action to produce a daily AI
review of open pull requests on **kubernetes-sigs/headlamp** that have not yet
received human review comments. Your output is committed to this repository
(the "site repo") and rendered as a static GitHub Pages site.

You have already been launched from the site repo's working directory. The
target project (kubernetes-sigs/headlamp) has been cloned to `./headlamp/`
and `gh` is authenticated against it.

---

## Constants

- `OWNER` = `kubernetes-sigs`
- `REPO` = `headlamp`
- `REPO_URL` = `https://github.com/kubernetes-sigs/headlamp`
- `TARGET_DIR` = `./headlamp` (working tree of the project under review)
- `STATE_DIR` = `./state` (committed back into the site repo)
- `OUTPUT_DIR` = `./reviews/{YYYY-MM-DD}` (created fresh each run)
- `MAX_PRS` = value of the `MAX_PRS` environment variable, or `300` if unset

All paths are relative to the site repo root, which is your current working
directory.

---

## Phase 0: Preflight

1. Verify `gh auth status` succeeds. If not, **STOP** with a non-zero exit
   message printed to stdout: `ERROR: gh not authenticated`.
2. Check rate limit: `gh api rate_limit --jq '.rate.remaining'`.
   - If < 100, set `RATE_LIMITED=true` and reduce work where noted.
   - If < 20, **STOP** with `ERROR: rate limit exhausted`.
3. Ensure `STATE_DIR` and today's `OUTPUT_DIR` exist (`mkdir -p`).
4. Print: `Reviewing PRs for: kubernetes-sigs/headlamp`.

---

## Phase 1: Load State

Read these if they exist; otherwise treat as empty:

- `state/learnings.md` — accumulated style guide, common issues, false
  positives, author notes. **Auto-maintained** by this prompt: read at the
  start of each run, rewritten at the end.
- `state/config.md` — **human-authored** review rules that should never be
  overwritten. Treat anything in this file as authoritative — it overrides
  inferences from `learnings.md` when they conflict. Typical contents:
  hard project conventions, commit message rules, accepted patterns the AI
  keeps flagging as false positives. If it exists, fold its checklist items
  into the review checklist (Phase 2) and pass its false-positive list to
  every PR review (Phase 5). **Do not modify this file under any
  circumstances** — if you would normally promote an observation to a
  "convention," instead note it in `learnings.md` under "False Positives /
  Project Conventions" so a human can later decide whether to promote it
  into `config.md`.
- `state/previously-reviewed.json` — `[{number, head_sha, date, title}, ...]`
  capped at 100 most recent entries.

From `previously-reviewed.json`, build:

- `SKIP_SET` = set of PR numbers whose stored `head_sha` matches the current
  `headRefOid` on GitHub (truly nothing to re-review).
- `REREVIEW_SET` = set of PR numbers whose stored `head_sha` differs from the
  current `headRefOid` (these are eligible for a re-review and should be
  preferred when filling the MAX_PRS budget).

If `state/learnings.md` exists and its "Review Style Guide" section has 8+
bullets **and** "Last updated" is within 7 days, set `SKIP_STYLE_LEARNING=true`.

---

## Phase 2: Detect Stack (in `./headlamp`)

Walk the project root for stack markers: `go.mod`, `package.json`, `Makefile`,
`Dockerfile`, `.github/workflows/*`, `CONTRIBUTING.md`, `CLAUDE.md`,
`AGENTS.md`.

Compose a checklist of universal items plus stack-specific items. Keep this
in memory; you will pass it to yourself when reviewing each PR. The headlamp
project is Go (backend) + TypeScript/React (frontend) — emphasize both.

If `./headlamp/CONTRIBUTING.md`, `./headlamp/CLAUDE.md`, or
`./headlamp/AGENTS.md` exist, their guidance is authoritative for items they
cover.

---

## Phase 3: Learn Review Style

**Skip if** `SKIP_STYLE_LEARNING=true`. Otherwise:

1. Fetch the 10 most recently merged PRs that have review comments:
   ```
   gh -R kubernetes-sigs/headlamp pr list --state merged --limit 30 \
     --json number,title,reviews,reviewDecision
   ```
2. For each of the top 10 with comments, fetch reviews + inline comments:
   ```
   gh api repos/kubernetes-sigs/headlamp/pulls/{n}/reviews
   gh api repos/kubernetes-sigs/headlamp/pulls/{n}/comments
   ```
3. Synthesize a 5-10 bullet **Review Style Guide** capturing tone, common
   feedback categories, level of detail, and notable phrases.

---

## Phase 4: Discover Candidates

1. `gh -R kubernetes-sigs/headlamp pr list --state open --limit "$MAX_PRS" \
   --json number,title,author,createdAt,labels,body,headRefName,headRefOid,changedFiles,additions,deletions,isDraft`
2. Drop drafts, drop PRs in `SKIP_SET`. Keep PRs from `REREVIEW_SET` (mark
   them `re_review=true`).
3. For the remaining candidates, batch-check for human review activity via
   one GraphQL request (split into batches of 30 if needed):
   ```
   gh api graphql -f query='
     query {
       repository(owner: "kubernetes-sigs", name: "headlamp") {
         prN: pullRequest(number: N) {
           number
           reviews(first: 1, states: [COMMENTED, CHANGES_REQUESTED, APPROVED]) { totalCount }
           comments(first: 1) { totalCount }
         }
         ...
       }
     }
   '
   ```
   A PR has human activity if either count > 0. Filter to those with both at
   zero, **unless** the PR is in `REREVIEW_SET` (re-reviews bypass this
   filter because you already reviewed them once).
4. Select up to `MAX_PRS` PRs, preferring re-reviews first, then newest open
   PRs by `createdAt`.
5. Categorize by total `additions + deletions`:
   - Lockfile-only (all paths match `*lock*`/`*.sum`)
   - Small: < 100
   - Medium: 100–500
   - Large: 500–1500
   - Very Large: > 1500

If 0 candidates remain after filtering, write an empty report (see Phase 7)
and exit 0 cleanly.

---

## Phase 5: Review Each PR

Process PRs **sequentially**. For each PR:

1. Gather:
   - PR metadata (number, title, author, body, branch, file count, +/-)
   - Linked issues parsed from body
   - Diff: `gh -R kubernetes-sigs/headlamp pr diff {n}`. If > 3000 lines,
     truncate to the most impactful non-test, non-generated files and note
     what was omitted with their line counts.
   - For Medium/Large only: check out the branch in `./headlamp` (use
     `git fetch origin pull/{n}/head:pr-{n} && git checkout pr-{n}`) so you
     can read full file context. Reset back to the default branch when done.
2. Apply the review checklist from Phase 2. Apply the style guide from
   Phase 3 / learnings.
3. For Lockfile-only / Small / Very Large: review from the diff only; skip
   worktree checkout.
4. Produce findings in the exact severity/confidence taxonomy:
   - `[Critical|HIGH]`, `[Critical|MEDIUM]`, `[Warning|HIGH]`,
     `[Warning|MEDIUM]`, `[Warning|LOW]`, `[Suggestion|MEDIUM]`,
     `[Suggestion|LOW]`, `[Positive]`
5. Decide verdict: `APPROVE`, `REQUEST_CHANGES`, or `NEEDS_DISCUSSION`.

### Per-PR output

Write **two files** per PR into `reviews/{YYYY-MM-DD}/`:

**A. Markdown** at `reviews/{YYYY-MM-DD}/pr-{number}.md`:

```markdown
---
pr_number: {number}
title: "{title}"
author: "{author}"
url: "{REPO_URL}/pull/{number}"
verdict: "{APPROVE|REQUEST_CHANGES|NEEDS_DISCUSSION}"
size_category: "{Lockfile-only|Small|Medium|Large|Very Large}"
files_changed: {count}
additions: {n}
deletions: {n}
re_review: {true|false}
date: "{YYYY-MM-DD}"
findings_count:
  critical: {n}
  warning: {n}
  suggestion: {n}
  positive: {n}
---

# PR #{number}: {title}

**Author**: [@{author}](https://github.com/{author}) ·
**Branch**: `{branch}` ·
**Changes**: +{additions} / -{deletions} across {files_changed} files ·
**Size**: {category} ·
{Re-review since {date}, if applicable}

[View on GitHub →]({REPO_URL}/pull/{number})

## Verdict: {APPROVE | REQUEST_CHANGES | NEEDS_DISCUSSION}

## Summary
{2–3 sentences}

## Findings

### Critical
- **[HIGH]** `{file}:{line}` — {description}
- **[MEDIUM]** ...

### Warnings
- **[HIGH]** `{file}:{line}` — ...

### Suggestions
- ...

### Positive
- ...

## Linked Issues
- #{issue} — {title}
```

Omit any empty section.

**B. JSON sidecar** at `reviews/{YYYY-MM-DD}/pr-{number}.json` containing the
same data as the YAML front matter plus a `findings` array of
`{severity, confidence, file, line, description}` objects. The site builder
reads these JSON files to compute statistics without parsing markdown.

---

## Phase 6: Run Index

Write `reviews/{YYYY-MM-DD}/index.json`:

```json
{
  "date": "{YYYY-MM-DD}",
  "generated_at": "{ISO-8601 UTC}",
  "repo": "kubernetes-sigs/headlamp",
  "prs_reviewed": [
    {"number": N, "title": "...", "verdict": "...", "size": "..."}
  ],
  "skipped": [{"number": N, "reason": "..."}],
  "stats": {
    "total": N,
    "verdicts": {"approve": N, "request_changes": N, "needs_discussion": N},
    "findings": {"critical": N, "warning": N, "suggestion": N, "positive": N},
    "sizes": {"lockfile_only": N, "small": N, "medium": N, "large": N, "very_large": N}
  },
  "style_guide": ["bullet 1", "bullet 2", ...],
  "skip_style_learning": {true|false}
}
```

---

## Phase 7: Update State

Rewrite `state/learnings.md` (do NOT just append — consolidate and dedupe):

```markdown
# PR Review Learnings — kubernetes-sigs/headlamp

*Last updated: {YYYY-MM-DD}*

## Review Style Guide
- ...

## Detected Stack
- ...

## Common Issues
- {issue} (seen in N/M PRs reviewed across {K} sessions)

## False Positives / Project Conventions
- ...

## Author Notes
- @{user}: {tendency seen in 2+ PRs}

## Session Log
### {YYYY-MM-DD}
- Reviewed N PRs: #..., #...
- Skipped: N ({reasons})
- New observations: ...
```

Rewrite `state/previously-reviewed.json` as a JSON array of
`{number, head_sha, date, title}`, keeping the **100 most recent** entries
(add this run's PRs, then truncate).

---

## Phase 8: Cleanup

If you checked out any PR branches in `./headlamp`, restore to the default
branch and delete the temporary `pr-{n}` branches.

Print a one-line summary to stdout: `Reviewed N PRs (A approve, R request, D discuss); state updated; output at reviews/{date}/`.

---

## Rules

- Do NOT post comments to GitHub. All output is files in this repo.
- Do NOT run builds, tests, or linters.
- Use `gh` for all GitHub API access.
- Never include `@username` mentions or GitHub auto-close keywords
  (`fix`, `fixes`, `close`, `closes`, `resolve`, `resolves`) in commit
  messages — the site repo follows Kubernetes-org commit conventions.
- If a phase fails, log the failure and continue with the next phase where
  possible. Only hard-stop on Phase 0 errors.
