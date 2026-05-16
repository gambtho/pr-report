#!/usr/bin/env python3
"""Classify every open non-draft PR on kubernetes-sigs/headlamp into a
triage bucket and write state/triage.json.

Runs hourly from a GitHub Action. Uses `gh api graphql` (so it inherits
the workflow's GH_TOKEN auth). No AI / Copilot involved — this is pure
metadata classification.

Buckets (priority order, highest first):
  1. needs_rebase         - mergeable conflicts
  2. ci_failing           - latest commit's check rollup is FAILURE
  3. waiting_on_reviewer  - author pushed after latest review
  4. waiting_on_author    - reviewer requested changes / commented, no
                            author response since
  5. stale                - >30 days since updatedAt
  6. approved_mergeable   - APPROVED, MERGEABLE, all checks green

A PR is placed in its single highest-priority matching bucket. PRs that
match none of the above are excluded from the dashboard entirely.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

OWNER = "kubernetes-sigs"
REPO = "headlamp"
STALE_DAYS = 30

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "state" / "triage.json"
ACTIONS_PATH = ROOT / "state" / "actions.yaml"

# GraphQL paged query. We ask for everything needed by the classifier in
# one round trip per page so we don't blow rate limits on big repos.
QUERY = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(
      states: OPEN,
      first: 50,
      after: $cursor,
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        url
        isDraft
        createdAt
        updatedAt
        mergeable
        reviewDecision
        author { login }
        labels(first: 20) { nodes { name } }
        commits(last: 1) {
          nodes {
            commit {
              committedDate
              oid
              statusCheckRollup { state }
            }
          }
        }
        reviews(last: 20) {
          nodes {
            state
            submittedAt
            author { login __typename }
          }
        }
        comments(last: 20) {
          nodes {
            createdAt
            author { login __typename }
          }
        }
      }
    }
  }
}
"""


def gh_graphql(query: str, **vars_: Any) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in vars_.items():
        if v is None:
            cmd += ["-F", f"{k}=null"]
        else:
            cmd += ["-f", f"{k}={v}"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def fetch_open_prs() -> list[dict[str, Any]]:
    prs: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        data = gh_graphql(QUERY, owner=OWNER, repo=REPO, cursor=cursor)
        page = data["data"]["repository"]["pullRequests"]
        prs.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return prs


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    # GitHub returns Z-suffixed UTC.
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def latest_commit_date(pr: dict) -> datetime | None:
    nodes = pr["commits"]["nodes"]
    if not nodes:
        return None
    return parse_iso(nodes[0]["commit"]["committedDate"])


def latest_check_state(pr: dict) -> str | None:
    nodes = pr["commits"]["nodes"]
    if not nodes:
        return None
    rollup = nodes[0]["commit"].get("statusCheckRollup")
    return rollup["state"] if rollup else None


def latest_human_review(pr: dict) -> dict | None:
    """Most recent review by a non-bot, with submittedAt populated."""
    candidates = [
        r
        for r in pr["reviews"]["nodes"]
        if r.get("submittedAt")
        and r.get("author")
        and r["author"].get("__typename") != "Bot"
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda r: r["submittedAt"], reverse=True)
    return candidates[0]


def latest_human_comment(pr: dict, exclude_login: str | None = None) -> dict | None:
    candidates = [
        c
        for c in pr["comments"]["nodes"]
        if c.get("author")
        and c["author"].get("__typename") != "Bot"
        and (exclude_login is None or c["author"].get("login") != exclude_login)
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda c: c["createdAt"], reverse=True)
    return candidates[0]


def latest_author_activity(pr: dict, author_login: str | None) -> datetime | None:
    """Most recent of: author's last commit, author's last PR comment."""
    times: list[datetime] = []
    commit_dt = latest_commit_date(pr)
    if commit_dt:
        times.append(commit_dt)
    if author_login:
        author_comments = [
            parse_iso(c["createdAt"])
            for c in pr["comments"]["nodes"]
            if c.get("author") and c["author"].get("login") == author_login
        ]
        times.extend(t for t in author_comments if t)
    return max(times) if times else None


def classify(pr: dict, now: datetime) -> str | None:
    """Return the bucket name, or None if PR doesn't match any bucket."""
    if pr.get("isDraft"):
        return None

    # 1. needs_rebase
    if pr.get("mergeable") == "CONFLICTING":
        return "needs_rebase"

    # 2. ci_failing
    if latest_check_state(pr) == "FAILURE":
        return "ci_failing"

    author_login = (pr.get("author") or {}).get("login")
    last_review = latest_human_review(pr)
    commit_dt = latest_commit_date(pr)

    # 3. waiting_on_reviewer
    # Author pushed after the most recent human review.
    if last_review and commit_dt:
        review_dt = parse_iso(last_review["submittedAt"])
        if review_dt and commit_dt > review_dt:
            return "waiting_on_reviewer"

    # 4. waiting_on_author
    # Most recent review asked for changes (or there's a non-author human
    # comment after the latest review) AND author hasn't pushed/commented
    # since.
    if last_review:
        review_dt = parse_iso(last_review["submittedAt"])
        author_activity = latest_author_activity(pr, author_login)
        is_changes_requested = last_review["state"] == "CHANGES_REQUESTED"
        # Also count a recent non-author human comment as a "request for
        # author attention" if it's newer than the last review.
        latest_other_comment = latest_human_comment(pr, exclude_login=author_login)
        latest_other_dt = parse_iso(latest_other_comment["createdAt"]) if latest_other_comment else None
        attention_dt = max(
            d for d in [review_dt, latest_other_dt] if d is not None
        )
        if is_changes_requested or (latest_other_dt and latest_other_dt > (review_dt or latest_other_dt)):
            if author_activity is None or author_activity < attention_dt:
                return "waiting_on_author"

    # 5. stale
    updated_at = parse_iso(pr.get("updatedAt"))
    if updated_at and (now - updated_at) > timedelta(days=STALE_DAYS):
        return "stale"

    # 6. approved_mergeable
    if (
        pr.get("reviewDecision") == "APPROVED"
        and pr.get("mergeable") == "MERGEABLE"
        and latest_check_state(pr) == "SUCCESS"
    ):
        return "approved_mergeable"

    return None


def summarize_pr(
    pr: dict, bucket: str, now: datetime, actions: dict
) -> dict[str, Any]:
    """Strip GraphQL payload to the fields the site template needs."""
    author = (pr.get("author") or {}).get("login") or "unknown"
    updated_at = parse_iso(pr.get("updatedAt"))
    days_stale = (now - updated_at).days if updated_at else None
    labels = [l["name"] for l in pr["labels"]["nodes"]]
    action = actions.get(bucket, {}) or {}
    recommended_label = action.get("label")
    recommended_comment = action.get("comment")
    return {
        "number": pr["number"],
        "title": pr["title"],
        "url": pr["url"],
        "author": author,
        "bucket": bucket,
        "updated_at": pr.get("updatedAt"),
        "days_since_update": days_stale,
        "labels": labels,
        "mergeable": pr.get("mergeable"),
        "review_decision": pr.get("reviewDecision"),
        "check_state": latest_check_state(pr),
        "action": {
            "priority": action.get("priority"),
            "recommended_label": recommended_label,
            "label_already_applied": (
                recommended_label is not None and recommended_label in labels
            ),
            "recommended_comment": recommended_comment,
        },
    }


BUCKET_ORDER = [
    "needs_rebase",
    "ci_failing",
    "waiting_on_reviewer",
    "waiting_on_author",
    "stale",
    "approved_mergeable",
]


def main() -> int:
    # Sanity: gh must be available and authed.
    if not shutil.which("gh"):
        print("ERROR: gh CLI not found on PATH", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc)
    actions: dict = {}
    if ACTIONS_PATH.exists():
        actions = yaml.safe_load(ACTIONS_PATH.read_text(encoding="utf-8")) or {}
    prs = fetch_open_prs()

    buckets: dict[str, list[dict]] = {b: [] for b in BUCKET_ORDER}
    classified = 0
    for pr in prs:
        bucket = classify(pr, now)
        if bucket is None:
            continue
        buckets[bucket].append(summarize_pr(pr, bucket, now, actions))
        classified += 1

    # Sort each bucket: oldest-updated first (so the most-stuck rises).
    for bucket in buckets.values():
        bucket.sort(key=lambda p: p["updated_at"] or "")

    out = {
        "generated_at": now.isoformat(timespec="seconds"),
        "repo": f"{OWNER}/{REPO}",
        "open_prs_total": sum(1 for pr in prs if not pr.get("isDraft")),
        "open_drafts_total": sum(1 for pr in prs if pr.get("isDraft")),
        "actionable_total": classified,
        "buckets": buckets,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT_PATH.relative_to(ROOT)} — "
        f"{classified} actionable / {out['open_prs_total']} open"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
