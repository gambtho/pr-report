#!/usr/bin/env python3
"""Apply triage recommendations to PRs on kubernetes-sigs/headlamp.

Reads `state/triage.json` (produced by collect_triage.py) and
`state/actions.yaml`. For each PR row where:

  1. the bucket has an `auto_apply.label` or `auto_apply.comment` opt-in,
  2. the recommended action is not already applied on the PR,
  3. (for comments) no equivalent comment was posted within the
     bucket's `comment_cooldown_days` window per `state/applied.jsonl`,

…calls `gh pr edit --add-label` or `gh pr comment` against
kubernetes-sigs/headlamp, and appends an audit row to `applied.jsonl`.

Defaults to **dry-run**. Pass `--apply` to actually mutate.

Safety properties:
  - No flag in actions.yaml → no action. Nothing acts on a bucket
    until an opt-in is explicitly set.
  - `applied.jsonl` is append-only. Never edited, never rewritten.
  - Re-applying the same label is cheap and idempotent (gh tolerates
    it); we still skip the API call when the label is already there.
  - Comment dedupe is hash-based: the same exact comment text will not
    be re-posted within the cooldown window.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
TRIAGE_PATH = STATE_DIR / "triage.json"
ACTIONS_PATH = STATE_DIR / "actions.yaml"
APPLIED_PATH = STATE_DIR / "applied.jsonl"

REPO = "kubernetes-sigs/headlamp"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def load_applied() -> list[dict]:
    if not APPLIED_PATH.exists():
        return []
    rows = []
    for line in APPLIED_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            # Don't fail the run on a corrupt audit row — log and skip.
            print(f"WARN: skipping malformed applied.jsonl row: {line[:80]}…", file=sys.stderr)
    return rows


def append_applied(row: dict) -> None:
    APPLIED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with APPLIED_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def comment_recently_posted(
    applied: list[dict], pr_number: int, bucket: str, comment_hash: str, cooldown_days: int, now: datetime
) -> dict | None:
    """Return the most recent matching applied row within the cooldown window, or None."""
    cutoff = now - timedelta(days=cooldown_days)
    for row in reversed(applied):
        if row.get("pr_number") != pr_number:
            continue
        if row.get("bucket") != bucket:
            continue
        if row.get("action_type") != "comment":
            continue
        if row.get("comment_hash") != comment_hash:
            continue
        if row.get("dry_run"):
            # Dry-run rows shouldn't suppress real applications.
            continue
        ts = parse_iso(row.get("ts", ""))
        if ts >= cutoff:
            return row
    return None


def run_gh(args: list[str], dry_run: bool) -> tuple[int, str, str]:
    """Run a gh command unless dry-running. Returns (rc, stdout, stderr)."""
    if dry_run:
        return 0, f"[dry-run] gh {' '.join(args)}", ""
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def process_pr(
    pr: dict,
    bucket_cfg: dict,
    applied: list[dict],
    dry_run: bool,
    workflow_run_url: str,
    now: datetime,
) -> list[dict]:
    """Apply all opted-in actions for a single PR. Returns audit rows written."""
    rows: list[dict] = []
    bucket = pr["bucket"]
    pr_number = pr["number"]
    pr_url = pr["url"]
    auto = bucket_cfg.get("auto_apply") or {}

    # --- Label ---
    rec_label = bucket_cfg.get("label")
    if rec_label and auto.get("label"):
        already = rec_label in (pr.get("labels") or [])
        if already:
            print(f"  [skip] #{pr_number} label '{rec_label}' already applied")
        else:
            rc, out, err = run_gh(
                ["pr", "edit", str(pr_number), "--repo", REPO, "--add-label", rec_label],
                dry_run=dry_run,
            )
            ok = rc == 0
            row = {
                "ts": now.isoformat(timespec="seconds"),
                "pr_number": pr_number,
                "pr_url": pr_url,
                "bucket": bucket,
                "action_type": "label",
                "label": rec_label,
                "dry_run": dry_run,
                "success": ok,
                "workflow_run_url": workflow_run_url,
            }
            if not ok:
                row["error"] = (err or out)[:500]
            append_applied(row)
            rows.append(row)
            print(f"  [{'DRY' if dry_run else 'APPLY'}] #{pr_number} label '{rec_label}': {'ok' if ok else 'FAIL'}")

    # --- Comment ---
    rec_comment = bucket_cfg.get("comment")
    if rec_comment and auto.get("comment"):
        comment_text = rec_comment.strip()
        comment_hash = sha(comment_text)
        cooldown = int(bucket_cfg.get("comment_cooldown_days", 7))
        prior = comment_recently_posted(applied, pr_number, bucket, comment_hash, cooldown, now)
        if prior:
            days_ago = (now - parse_iso(prior["ts"])).days
            print(f"  [skip] #{pr_number} comment already posted {days_ago}d ago (cooldown {cooldown}d)")
        else:
            rc, out, err = run_gh(
                ["pr", "comment", str(pr_number), "--repo", REPO, "--body", comment_text],
                dry_run=dry_run,
            )
            ok = rc == 0
            row = {
                "ts": now.isoformat(timespec="seconds"),
                "pr_number": pr_number,
                "pr_url": pr_url,
                "bucket": bucket,
                "action_type": "comment",
                "comment_hash": comment_hash,
                "dry_run": dry_run,
                "success": ok,
                "workflow_run_url": workflow_run_url,
            }
            if not ok:
                row["error"] = (err or out)[:500]
            append_applied(row)
            rows.append(row)
            print(f"  [{'DRY' if dry_run else 'APPLY'}] #{pr_number} comment ({cooldown}d cooldown): {'ok' if ok else 'FAIL'}")

    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually mutate PRs. Without this flag, runs in dry-run mode.",
    )
    args = parser.parse_args()
    dry_run = not args.apply

    if not TRIAGE_PATH.exists():
        print(f"ERROR: {TRIAGE_PATH} not found — run collect_triage.py first", file=sys.stderr)
        return 1
    if not ACTIONS_PATH.exists():
        print(f"ERROR: {ACTIONS_PATH} not found", file=sys.stderr)
        return 1
    if not shutil.which("gh"):
        print("ERROR: gh CLI not on PATH", file=sys.stderr)
        return 1

    triage = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    actions = yaml.safe_load(ACTIONS_PATH.read_text(encoding="utf-8")) or {}
    applied = load_applied()
    now = datetime.now(timezone.utc)
    workflow_run_url = os.environ.get("GITHUB_SERVER_URL", "") and (
        f"{os.environ['GITHUB_SERVER_URL']}/{os.environ.get('GITHUB_REPOSITORY','')}"
        f"/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}"
    ) or "local"

    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"{mode} — repo={REPO}, triage from {triage.get('generated_at')}")

    total_actions = 0
    for bucket_name, prs in (triage.get("buckets") or {}).items():
        bucket_cfg = actions.get(bucket_name) or {}
        auto = bucket_cfg.get("auto_apply") or {}
        if not (auto.get("label") or auto.get("comment")):
            if prs:
                print(f"[bucket {bucket_name}] {len(prs)} PRs — no auto_apply opt-in, skipping")
            continue
        print(f"[bucket {bucket_name}] {len(prs)} PRs — opted-in: {auto}")
        for pr in prs:
            rows = process_pr(pr, bucket_cfg, applied, dry_run, workflow_run_url, now)
            total_actions += len(rows)
            # Keep `applied` in sync so a later PR in the same run sees
            # earlier rows (matters if you ever re-run within a job).
            applied.extend(rows)

    print(f"\n{mode} complete — {total_actions} action(s) recorded in {APPLIED_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
