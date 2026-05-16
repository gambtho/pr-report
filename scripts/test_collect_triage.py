"""Smoke test for the classifier — runs without network."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from collect_triage import classify, summarize_pr  # noqa: E402

NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


def pr(
    number=1,
    title="t",
    is_draft=False,
    mergeable="MERGEABLE",
    review_decision=None,
    author="alice",
    labels=(),
    last_commit_at=None,
    check_state=None,
    reviews=(),
    comments=(),
    updated_at=None,
):
    return {
        "number": number,
        "title": title,
        "url": f"https://github.com/x/y/pull/{number}",
        "isDraft": is_draft,
        "createdAt": "2026-04-01T00:00:00Z",
        "updatedAt": updated_at or "2026-05-14T00:00:00Z",
        "mergeable": mergeable,
        "reviewDecision": review_decision,
        "author": {"login": author},
        "labels": {"nodes": [{"name": n} for n in labels]},
        "commits": {
            "nodes": [
                {
                    "commit": {
                        "committedDate": last_commit_at or "2026-05-10T00:00:00Z",
                        "oid": "deadbeef",
                        "statusCheckRollup": (
                            {"state": check_state} if check_state else None
                        ),
                    }
                }
            ]
        },
        "reviews": {
            "nodes": [
                {
                    "state": r["state"],
                    "submittedAt": r["at"],
                    "author": {
                        "login": r.get("login", "bob"),
                        "__typename": r.get("type", "User"),
                    },
                }
                for r in reviews
            ]
        },
        "comments": {
            "nodes": [
                {
                    "createdAt": c["at"],
                    "author": {
                        "login": c.get("login", "bob"),
                        "__typename": c.get("type", "User"),
                    },
                }
                for c in comments
            ]
        },
    }


def assert_bucket(p, expected):
    got = classify(p, NOW)
    assert got == expected, f"PR #{p['number']}: expected {expected!r}, got {got!r}"
    print(f"OK  #{p['number']}: {expected}")


def main():
    # 1. Draft is excluded
    assert_bucket(pr(number=1, is_draft=True, mergeable="CONFLICTING"), None)

    # 2. needs_rebase beats everything
    assert_bucket(
        pr(number=2, mergeable="CONFLICTING", check_state="FAILURE"),
        "needs_rebase",
    )

    # 3. ci_failing beats waiting_on_reviewer
    assert_bucket(
        pr(
            number=3,
            check_state="FAILURE",
            last_commit_at="2026-05-13T00:00:00Z",
            reviews=[{"state": "COMMENTED", "at": "2026-05-10T00:00:00Z"}],
        ),
        "ci_failing",
    )

    # 4. waiting_on_reviewer: author pushed after review
    assert_bucket(
        pr(
            number=4,
            check_state="SUCCESS",
            last_commit_at="2026-05-13T00:00:00Z",
            reviews=[{"state": "CHANGES_REQUESTED", "at": "2026-05-10T00:00:00Z"}],
        ),
        "waiting_on_reviewer",
    )

    # 5. waiting_on_author: CHANGES_REQUESTED, no author response
    assert_bucket(
        pr(
            number=5,
            check_state="SUCCESS",
            author="alice",
            last_commit_at="2026-05-08T00:00:00Z",
            reviews=[
                {
                    "state": "CHANGES_REQUESTED",
                    "at": "2026-05-10T00:00:00Z",
                    "login": "bob",
                }
            ],
        ),
        "waiting_on_author",
    )

    # 6. stale
    assert_bucket(
        pr(
            number=6,
            check_state="SUCCESS",
            updated_at="2026-04-01T00:00:00Z",
        ),
        "stale",
    )

    # 7. approved_mergeable
    assert_bucket(
        pr(
            number=7,
            mergeable="MERGEABLE",
            review_decision="APPROVED",
            check_state="SUCCESS",
        ),
        "approved_mergeable",
    )

    # 8. Bot reviews are ignored
    assert_bucket(
        pr(
            number=8,
            check_state="SUCCESS",
            last_commit_at="2026-05-13T00:00:00Z",
            reviews=[
                {
                    "state": "COMMENTED",
                    "at": "2026-05-12T00:00:00Z",
                    "login": "github-actions",
                    "type": "Bot",
                }
            ],
        ),
        None,  # no human review, doesn't qualify for waiting_on_reviewer
    )

    # 9. Action recommendations roundtrip
    actions = {
        "needs_rebase": {
            "label": "needs-rebase",
            "comment": "rebase pls",
            "priority": "ask author",
        }
    }
    summary = summarize_pr(
        pr(number=9, mergeable="CONFLICTING"), "needs_rebase", NOW, actions
    )
    assert summary["action"]["recommended_label"] == "needs-rebase"
    assert summary["action"]["label_already_applied"] is False

    summary2 = summarize_pr(
        pr(number=10, mergeable="CONFLICTING", labels=["needs-rebase"]),
        "needs_rebase",
        NOW,
        actions,
    )
    assert summary2["action"]["label_already_applied"] is True
    print("OK  action recommendation logic")

    print("\nAll classifier tests passed.")


if __name__ == "__main__":
    main()
