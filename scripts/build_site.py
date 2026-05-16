#!/usr/bin/env python3
"""Build the static GitHub Pages site from reviews/.

Reads reviews/YYYY-MM-DD/*.json (PR sidecars) and reviews/YYYY-MM-DD/index.json
(run summary), renders one HTML page per PR plus per-run index pages and a
top-level index that lists every daily run newest-first.

Output is written to site/_build/, ready to be uploaded as a Pages artifact.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
REVIEWS_DIR = ROOT / "reviews"
SITE_DIR = ROOT / "site"
TEMPLATE_DIR = SITE_DIR / "templates"
STATIC_DIR = SITE_DIR / "static"
BUILD_DIR = SITE_DIR / "_build"

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class PRReview:
    date: str
    number: int
    title: str
    author: str
    url: str
    verdict: str
    size_category: str
    files_changed: int
    additions: int
    deletions: int
    re_review: bool
    findings_count: dict[str, int]
    body_html: str
    md_path: Path

    @property
    def slug(self) -> str:
        return f"pr-{self.number}"


@dataclass
class DailyRun:
    date: str
    generated_at: str
    stats: dict[str, Any]
    style_guide: list[str]
    reviews: list[PRReview]
    skipped: list[dict[str, Any]]
    skip_style_learning: bool


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


def load_pr(md_path: Path, date: str) -> PRReview:
    text = md_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    body_html = markdown.markdown(
        body,
        extensions=["fenced_code", "tables", "toc"],
    )
    return PRReview(
        date=date,
        number=int(meta.get("pr_number")),
        title=str(meta.get("title", "")),
        author=str(meta.get("author", "")),
        url=str(meta.get("url", "")),
        verdict=str(meta.get("verdict", "")),
        size_category=str(meta.get("size_category", "")),
        files_changed=int(meta.get("files_changed", 0)),
        additions=int(meta.get("additions", 0)),
        deletions=int(meta.get("deletions", 0)),
        re_review=bool(meta.get("re_review", False)),
        findings_count=dict(meta.get("findings_count", {})),
        body_html=body_html,
        md_path=md_path,
    )


def load_runs() -> list[DailyRun]:
    runs: list[DailyRun] = []
    if not REVIEWS_DIR.exists():
        return runs
    for run_dir in sorted(REVIEWS_DIR.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        if not re.match(r"\d{4}-\d{2}-\d{2}", run_dir.name):
            continue
        index_path = run_dir / "index.json"
        if not index_path.exists():
            continue
        with index_path.open(encoding="utf-8") as f:
            index = json.load(f)
        reviews = [
            load_pr(md_path, run_dir.name)
            for md_path in sorted(run_dir.glob("pr-*.md"))
        ]
        runs.append(
            DailyRun(
                date=run_dir.name,
                generated_at=index.get("generated_at", ""),
                stats=index.get("stats", {}),
                style_guide=index.get("style_guide", []),
                reviews=reviews,
                skipped=index.get("skipped", []),
                skip_style_learning=bool(index.get("skip_style_learning", False)),
            )
        )
    return runs


def render(env: Environment, runs: list[DailyRun]) -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, BUILD_DIR / "static")

    # Top-level index (at root, depth 0)
    index_tmpl = env.get_template("index.html")
    (BUILD_DIR / "index.html").write_text(
        index_tmpl.render(
            runs=runs,
            generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            static_prefix="",
            home_prefix="./",
        ),
        encoding="utf-8",
    )

    # Per-run pages (depth 2) and per-PR pages (depth 2)
    run_tmpl = env.get_template("run.html")
    pr_tmpl = env.get_template("pr.html")
    deep_prefix = "../../"
    for run in runs:
        run_out = BUILD_DIR / "reviews" / run.date
        run_out.mkdir(parents=True, exist_ok=True)
        (run_out / "index.html").write_text(
            run_tmpl.render(
                run=run, static_prefix=deep_prefix, home_prefix=deep_prefix
            ),
            encoding="utf-8",
        )
        for pr in run.reviews:
            (run_out / f"{pr.slug}.html").write_text(
                pr_tmpl.render(
                    pr=pr,
                    run=run,
                    static_prefix=deep_prefix,
                    home_prefix=deep_prefix,
                ),
                encoding="utf-8",
            )

    # 404 (root depth)
    (BUILD_DIR / "404.html").write_text(
        env.get_template("404.html").render(
            static_prefix="/", home_prefix="/"
        ),
        encoding="utf-8",
    )


def main() -> int:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["verdict_class"] = lambda v: {
        "APPROVE": "verdict-approve",
        "REQUEST_CHANGES": "verdict-request",
        "NEEDS_DISCUSSION": "verdict-discuss",
    }.get(v, "verdict-unknown")

    runs = load_runs()
    render(env, runs)
    print(f"Built {len(runs)} daily runs to {BUILD_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
