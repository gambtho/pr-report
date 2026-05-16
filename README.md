# headrep — Daily AI PR reviews for kubernetes-sigs/headlamp

Runs the [GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) once a day against open pull requests on [kubernetes-sigs/headlamp](https://github.com/kubernetes-sigs/headlamp), commits the structured output back to this repo, and renders a static [GitHub Pages](https://pages.github.com/) site so the reviews are easy to browse.

## Why

The `/review-prs` skill produces useful AI reviews locally but the output is just markdown files in `~/.claude/`. This repo wraps the same skill in a daily, headless, public workflow:

- Reviews are visible to the whole team.
- A history accumulates — the site renders every previous run.
- A `state/learnings.md` file accrues style observations and false-positive patterns so subsequent runs sharpen over time.
- Re-review detection (HEAD SHA tracking) means an updated PR gets a fresh look.

This is **AI commentary, not a substitute for human review**. The site footer says so on every page.

## Layout

```
.
├── prompts/review.md         # The headless prompt fed to Copilot CLI
├── scripts/build_site.py     # Static site generator (markdown → HTML)
├── scripts/requirements.txt
├── site/templates/           # Jinja2 HTML templates
├── site/static/style.css
├── reviews/YYYY-MM-DD/       # Committed each day by the Action
│   ├── index.json            # Per-run summary stats
│   ├── pr-NNN.md             # Human-readable review per PR
│   └── pr-NNN.json           # Machine-readable sidecar (verdict, findings)
├── state/                    # Persistent learning state
│   ├── learnings.md          # Auto-maintained: style guide, common issues, author notes
│   ├── config.md             # Human-authored: hard rules, known false positives
│   └── previously-reviewed.json
└── .github/workflows/daily-review.yml
```

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
# Locally, once you have copilot CLI installed and authenticated:
git clone https://github.com/kubernetes-sigs/headlamp.git
copilot --prompt "$(cat prompts/review.md)" --allow-all-tools
python scripts/build_site.py
python -m http.server -d site/_build 8000
```

Or trigger the Action manually: Actions → Daily PR Review → Run workflow.

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
