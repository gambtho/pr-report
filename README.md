# headrep — PR triage + AI reviews for kubernetes-sigs/headlamp

A static [GitHub Pages](https://pages.github.com/) site with two views of [kubernetes-sigs/headlamp](https://github.com/kubernetes-sigs/headlamp)'s open pull requests:

- **Triage dashboard (`/`)** — every open PR that needs maintainer attention, grouped by what's blocking it (rebase, CI, waiting on author/reviewer, stale, or ready to merge). Refreshes hourly. Each row shows a recommended label and/or comment so maintainers know exactly what to do.
- **AI reviews (`/reviews/`)** — daily Copilot CLI reviews of PRs that haven't received human review yet. Runs once a day. Accumulates style learnings across runs.

The triage view is **read-only today** — it shows recommendations but doesn't apply them. Wiring up automatic label/comment application is on the roadmap; the recommendations on the dashboard are designed to be what that future automation will do, so you can validate them now.

## Why

The `/review-prs` skill produces useful AI reviews locally but the output is just markdown files in `~/.claude/`. Maintainers also need a "what should I do *right now*" view that doesn't require an LLM. This repo combines both:

- **Triage** answers "where should I spend the next 10 minutes?"
- **AI reviews** answer "is there a PR with no human eyes on it that I should bring to a reviewer's attention?"
- Both run on GitHub Actions, both publish to the same Pages site, both keep their state in this repo so it's all auditable.

The AI reviews are commentary, not a substitute for human review. The site footer says so on every page.

## Layout

```
.
├── prompts/review.md              # Headless prompt for the daily AI review
├── scripts/
│   ├── build_site.py              # Static site generator
│   ├── collect_triage.py          # Hourly PR classifier
│   ├── apply_triage.py            # Optional write-side (dry-run by default)
│   ├── test_collect_triage.py     # Classifier unit tests (no network)
│   └── requirements.txt
├── site/templates/                # Jinja2 HTML
├── site/static/style.css
├── reviews/YYYY-MM-DD/            # Daily AI review output (committed by Action)
│   ├── index.json
│   ├── pr-NNN.md
│   └── pr-NNN.json
├── state/
│   ├── triage.json                # Hourly: classified open PRs
│   ├── actions.yaml               # Editable: label/comment recommendations + auto_apply opt-ins
│   ├── applied.jsonl              # Append-only audit log of every action (dry-run included)
│   ├── learnings.md               # Auto-maintained: AI review style guide etc.
│   ├── config.md                  # Human-authored: hard rules for AI reviewer
│   └── previously-reviewed.json
└── .github/workflows/
    ├── triage.yml                 # Hourly — classification only
    ├── daily-review.yml           # Daily — AI reviews
    └── apply-triage.yml           # Manual only — write-side, opt-in
```

## Triage categories

A PR is placed in its single highest-priority matching bucket:

| Priority | Bucket | Definition | Recommended action |
|---|---|---|---|
| 1 | **Needs rebase** | `mergeable == CONFLICTING` | Apply `needs-rebase` label + ask author to rebase |
| 2 | **CI failing** | Latest commit's check rollup is `FAILURE` | Comment asking author to fix CI |
| 3 | **Waiting on reviewer** | Author pushed commits after the latest human review | Apply `needs-review` label |
| 4 | **Waiting on author** | Reviewer requested changes or commented; no author response since | Friendly ping comment |
| 5 | **Stale** | No activity in 30+ days | Apply `lifecycle/stale`, comment about closing |
| 6 | **Ready to merge** | Approved, mergeable, CI green | Merge it |

The recommended labels and comments live in `state/actions.yaml`. **Edit that file** if any of the suggested labels don't match headlamp's actual vocabulary, or if you want different comment wording. The hourly triage workflow re-reads it on every run.

Each row on the dashboard also tells you whether the recommended label is *already applied* (green badge) or *not yet applied* (red badge). When the future write-side automation lands, it will only act on the "not yet applied" rows.

### What's not classified

A PR that doesn't match any of the six buckets — i.e. it's open, has no conflicts, CI is passing, it has a recent human review with no follow-up needed, and it's not stale — is **excluded from the dashboard entirely**. That's the goal: the dashboard is an action list, not a PR list. If you want the full open-PR list, [GitHub already provides that](https://github.com/kubernetes-sigs/headlamp/pulls).

## Setup

### 1. Create a Copilot PAT

Copilot CLI in headless mode authenticates via `GH_TOKEN`, which must be a
fine-grained Personal Access Token with the **Copilot Requests** permission.
The default `GITHUB_TOKEN` provided by Actions does **not** carry this scope.

- GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
- Resource owner: your account or org
- Repository access: **public repositories only** is enough (Copilot itself doesn't need write access to the headlamp repo)
- Permissions: enable **Copilot Requests**, plus **Contents: read** on public repos
- Expiration: as long as your policy allows; rotate on a calendar reminder

Store it in this repo as the secret `COPILOT_PAT`.

### 2. (Optional) Site push token

The workflow pushes the daily commit back to this repo using the default
`github.token`, which works as long as `permissions: contents: write` is set
(it is). If you want commits to come from a different bot identity, create a
PAT with `contents: write` on this repo and add it as `SITE_PUSH_TOKEN` — the
workflow will prefer it when set.

### 3. Enable GitHub Pages

Settings → Pages → Source: **GitHub Actions**. The first deploy will publish the site at `https://<owner>.github.io/<repo>/`.

### 4. Tweak the schedule (optional)

`.github/workflows/daily-review.yml` runs at `17 6 * * *` UTC. Change the cron line to whatever fits your timezone. Avoid `:00` and `:30` minute marks — every cron user picks those and runner queues stampede.

## Running it manually

```bash
# Triage (no Copilot needed — just gh auth):
python scripts/collect_triage.py
python scripts/build_site.py
python -m http.server -d site/_build 8000

# Full daily AI review (requires copilot CLI + auth):
git clone https://github.com/kubernetes-sigs/headlamp.git
copilot --prompt "$(cat prompts/review.md)" --allow-all-tools
python scripts/build_site.py
```

Trigger either Action manually from the Actions tab: **Hourly Triage → Run workflow**, or **Daily PR Review → Run workflow**.

## Write-side: optional automatic application

The triage dashboard is **read-only by default**. There is a separate, opt-in workflow that can actually apply the recommended labels/comments to PRs on headlamp. It is intentionally hard to fire accidentally:

- Manual trigger only (`workflow_dispatch`) — no cron.
- Dry-run is the default input.
- Every bucket's `auto_apply.label` and `auto_apply.comment` flag in `state/actions.yaml` defaults to `false`. Nothing acts on a bucket without an explicit opt-in.
- Real mutations require a separate `HEADLAMP_WRITE_PAT` secret. Without it, only dry-run is allowed.
- Every action — including dry-runs — is logged to an append-only audit file `state/applied.jsonl`.
- Comments have a per-bucket cooldown (`comment_cooldown_days` in `actions.yaml`) so the bot can never spam the same PR with the same comment within that window.

### Rollout sequence (recommended)

1. Let the read-only dashboard run for a week. Sanity-check that each PR is in the right bucket and the recommended action makes sense.
2. Create `HEADLAMP_WRITE_PAT` — fine-grained PAT scoped to `kubernetes-sigs/headlamp` with:
   - **Pull requests: Read and write** (for `gh pr edit --add-label`)
   - **Issues: Read and write** (for `gh pr comment` — PR comments are issue comments under the hood)
   - **Metadata: Read-only** (auto-selected)

   Add as repo secret `HEADLAMP_WRITE_PAT`.
3. In `state/actions.yaml`, flip `auto_apply.label: true` for one low-risk bucket (`needs_rebase` is a good first choice — the label is purely informational).
4. Actions → **Apply Triage** → Run workflow → dry_run **true**. Read the log: every line is exactly what would be applied.
5. Re-run with dry_run **false**. Open `state/applied.jsonl` and check the audit rows look right. Open one of the affected PRs and confirm the label appeared.
6. Repeat for the next bucket/action you want to enable. **Stop here** unless you're sure — a never-applied recommendation is fine; a wrongly-applied one is noise the project's maintainers have to clean up.

Only after several months of this should you consider adding a cron trigger to `apply-triage.yml`. The manual cycle is the safety mechanism — losing it is a one-way door.

### `state/applied.jsonl` schema

One JSON object per line, append-only. Never edit by hand — the cooldown logic depends on it being chronological.

```json
{
  "ts": "2026-05-16T01:19:34+00:00",
  "pr_number": 2101,
  "pr_url": "https://github.com/kubernetes-sigs/headlamp/pull/2101",
  "bucket": "needs_rebase",
  "action_type": "label",         // "label" or "comment"
  "label": "needs-rebase",        // present when action_type=label
  "comment_hash": "e5fc6e377cc0f826",  // sha256 prefix of body, when action_type=comment
  "dry_run": false,
  "success": true,
  "workflow_run_url": "https://github.com/owner/headrep/actions/runs/12345",
  "error": "…"                    // present only when success=false
}
```

Dry-run rows are logged too, so you can `grep -c '"dry_run":false' state/applied.jsonl` to see exactly how many real mutations the bot has ever performed across the project's history.

### Auditing

```bash
# Every real mutation, oldest first
grep '"dry_run":false' state/applied.jsonl | jq -s 'sort_by(.ts)'

# All actions against a specific PR
jq -c 'select(.pr_number == 2101)' state/applied.jsonl

# Failures only
jq -c 'select(.success == false)' state/applied.jsonl

# Count by bucket
jq -r 'select(.dry_run == false) | .bucket' state/applied.jsonl | sort | uniq -c
```

### Disabling automation in a hurry

If the bot misbehaves, fastest stop is to set all `auto_apply.*` flags in `state/actions.yaml` back to `false` and push. The dashboard keeps rendering, but the apply workflow becomes a no-op for every bucket. Then investigate the audit log.

## Output format

Each PR review has two files. The markdown is for humans; the JSON sidecar is for the site builder and any downstream tooling.

**`pr-NNN.md`** has YAML front matter:

```yaml
pr_number: 123
title: "..."
author: "..."
verdict: "APPROVE | REQUEST_CHANGES | NEEDS_DISCUSSION"
size_category: "Lockfile-only | Small | Medium | Large | Very Large"
findings_count: {critical: N, warning: N, suggestion: N, positive: N}
```

…followed by the human-readable review body (summary + findings grouped by severity).

**`pr-NNN.json`** is the same metadata plus a flat `findings` array of `{severity, confidence, file, line, description}` objects, suitable for trending across runs.

## How learning works

Two files in `state/` carry knowledge between runs. They're committed back to the repo at the end of each daily Action, so the full history lives in `git log state/`.

### `state/learnings.md` — auto-maintained

The prompt reads this at the start of every run and rewrites it at the end. It accumulates:

- A **review style guide** (5–10 bullets) synthesized from real review comments on recently-merged headlamp PRs. If this section has 8+ bullets and was updated within the last 7 days, the run skips re-deriving it — saving Copilot quota.
- **Common issues** seen across multiple PRs.
- **False positives / project conventions** the AI has inferred.
- **Author notes** — per-author patterns seen across 2+ PRs.
- A **session log** of what each run did.

The prompt is instructed to "consolidate and dedupe, do not just append," but LLMs are imperfect at that. Expect the file to drift over time. **Open it once a month and hand-prune it** — the next run will treat your cleaned-up version as ground truth.

### `state/config.md` — human-authored

This is your editorial channel. The prompt reads it as **authoritative** and never modifies it. Use it for:

- Hard project conventions ("we use `slog`, don't suggest `logrus`")
- Commit message / DCO / license header requirements
- Patterns the AI repeatedly flags incorrectly — promote them here from `learnings.md` once you're confident they're really conventions and not real issues
- Extra checklist items beyond the auto-detected stack defaults

The convention is: if you see the AI repeat a false positive two or three runs in a row, add a one-line entry to `config.md`. That's the durable fix — entries in `learnings.md` can drift, entries in `config.md` won't.

A starter `config.md` is included with examples commented out. Replace the examples with real ones as you learn what headlamp's conventions actually are.

### `state/previously-reviewed.json`

`[{number, head_sha, date, title}, …]`, capped at 100 entries. Used for:

- **Skip detection**: PRs whose stored `head_sha` matches the current GitHub `headRefOid` aren't re-reviewed.
- **Re-review detection**: PRs whose stored `head_sha` differs (i.e. force-pushed or new commits) are eligible for a fresh look and are preferred when filling the daily PR budget.

Safe to delete if you ever want a clean slate.

## Adapting from `/review-prs`

The headless prompt at `prompts/review.md` is a port of the local
`/review-prs` skill, with these changes:

| Local skill | Headless port |
|---|---|
| Parallel `Agent` sub-agent dispatch | Sequential, single Copilot session |
| State at `~/.claude/pr-reviews/{owner}/{repo}/` | State at `./state/`, committed |
| Output at `~/.claude/pr-reviews/{owner}/{repo}/review-{date}.md` | One file per PR under `./reviews/{date}/` + JSON sidecar + per-run `index.json` |
| `git worktree` per PR | Optional `git fetch + checkout` in the cloned `./headlamp` for Medium/Large PRs |
| Worktree cleanup | Branch reset at end of run |
| Implicit Claude tool budget | `--allow-all-tools` on Copilot CLI |

## Caveats

- GitHub doesn't yet publish a vetted CI pattern for Copilot CLI; the install/auth here is what the README on `github/copilot-cli` describes plus extrapolation. If GitHub ships an official action later, swap it in.
- `--allow-all-tools` is the right level of trust for an ephemeral runner with no secrets beyond `COPILOT_PAT`. Don't reuse this pattern on a self-hosted runner without sandboxing.
- Copilot CLI is subject to your Copilot subscription's rate limits. A daily run of ~10 PRs is well within normal usage; bursts may not be.
- Re-review detection deliberately accepts the slim risk of re-reviewing a PR whose only change was a force-push that happened to match a previously-seen SHA. The 100-entry `previously-reviewed.json` cap means very old PRs eventually fall out of the skip set entirely.
