#!/usr/bin/env python3
"""check_notion_plans_no_duplicates.py — fail-closed CI gate for Plans DB dedup.

Loads the local plan_registration_cache.json snapshot (refreshed by
ops_scripts/ci/check_plan_registration_freshness.py --refresh) and groups
rows by slug. Fails when any slug has ≥2 active rows.

Why cache-based and not live-API: the live-Notion query would be slow,
flaky, and require a token. The cache is refreshed by the freshness gate
and is good enough for "the dedup story didn't break this commit".

Usage:
    python ops_scripts/ci/check_notion_plans_no_duplicates.py
    python ops_scripts/ci/check_notion_plans_no_duplicates.py --json
    python ops_scripts/ci/check_notion_plans_no_duplicates.py --live   # query Notion directly

Exit codes:
    0 — no duplicates
    1 — duplicates detected (fail)
    2 — cache missing AND --live not specified (fail-closed)

Bypass: NOTION_PLANS_DUP_BYPASS=1 (logged via violations.jsonl).

RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B.
Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2d).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"))

from _notion_constants import NOTION_API_VERSION, query_url  # noqa: E402
from _plans_dup_detector import (  # noqa: E402
    DuplicateGroup,
    PLANS_DATA_SOURCE_ID,
    find_duplicate_groups,
)

CACHE_PATH = REPO_ROOT / ".claude" / "state" / "plan_registration_cache.json"
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "governance" / "notion_plans_dup_violations.jsonl"
)
TIMEOUT_S = 30.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_bypass() -> bool:
    return os.environ.get("NOTION_PLANS_DUP_BYPASS", "").strip() == "1"


def _log_violation(rec: dict[str, Any]) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def load_cache_snapshot() -> dict[str, list[dict]] | None:
    """Read plan_registration_cache.json and return slug -> [row, ...] mapping.

    Returns None when the cache is missing or malformed.
    """
    if not CACHE_PATH.exists():
        return None
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    plans = data.get("plans") if isinstance(data, dict) else None
    if not isinstance(plans, dict):
        return None

    # The freshness cache flattens to slug -> single dict. The cache
    # cannot detect duplicates by itself — `--live` is required for that.
    out: dict[str, list[dict]] = {}
    for slug, entry in plans.items():
        if not isinstance(entry, dict):
            continue
        out[slug] = [entry]
    return out


def fetch_live_plans(token: str) -> dict[str, list[dict]]:
    """Query Notion directly for ALL Plans rows. Groups by slug."""
    url = query_url(PLANS_DATA_SOURCE_ID)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }
    by_slug: dict[str, list[dict]] = {}
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for page in data.get("results", []):
            if page.get("in_trash") or page.get("archived"):
                continue
            slug_chunks = (
                page.get("properties", {}).get("Slug", {}).get("title", [])
            )
            slug = "".join(c.get("plain_text", "") for c in slug_chunks)
            if not slug:
                continue
            status_prop = page.get("properties", {}).get("Status", {}).get("select")
            status = (status_prop or {}).get("name", "")
            by_slug.setdefault(slug, []).append({
                "id": page.get("id", ""),
                "status": status,
            })
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return by_slug


def report(groups: list[DuplicateGroup], *, json_out: bool) -> None:
    if json_out:
        print(json.dumps({
            "duplicates": [
                {"slug": g.slug, "page_ids": list(g.page_ids), "statuses": list(g.statuses)}
                for g in groups
            ],
            "duplicate_count": len(groups),
        }, indent=2))
        return
    print(f"Found {len(groups)} duplicate slug groups:\n")
    for g in groups:
        print(f"  {g.slug}: {len(g.page_ids)} active rows")
        for pid, status in zip(g.page_ids, g.statuses):
            print(f"    - {pid} [{status or '?'}]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Query Notion directly instead of using the local cache",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON report",
    )
    args = parser.parse_args(argv)

    if _is_bypass():
        _log_violation({
            "timestamp": _now_iso(),
            "severity": "info",
            "violation_type": "ci_bypass",
            "reason": "NOTION_PLANS_DUP_BYPASS=1",
            "gate": "check_notion_plans_no_duplicates",
        })
        print("[plans_dup] NOTION_PLANS_DUP_BYPASS=1 — passing without checking")
        return 0

    snapshot: dict[str, list[dict]] | None
    if args.live:
        token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
        if not token:
            print(
                "[plans_dup] ERROR: --live requires NOTION_TOKEN/NOTION_API_KEY",
                file=sys.stderr,
            )
            return 2
        try:
            snapshot = fetch_live_plans(token)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            print(f"[plans_dup] live fetch failed: {exc!r}", file=sys.stderr)
            return 2
    else:
        snapshot = load_cache_snapshot()
        if snapshot is None:
            print(
                "[plans_dup] ERROR: cache missing/malformed at "
                f"{CACHE_PATH}. Run "
                "`python ops_scripts/ci/check_plan_registration_freshness.py --refresh` "
                "or pass --live.",
                file=sys.stderr,
            )
            return 2

    groups = find_duplicate_groups(snapshot)
    if not groups:
        if args.json:
            print(json.dumps({"duplicates": [], "duplicate_count": 0}, indent=2))
        else:
            print("[plans_dup] OK — no duplicate Plans rows.")
        return 0

    report(groups, json_out=args.json)
    for g in groups:
        _log_violation({
            "timestamp": _now_iso(),
            "severity": "error",
            "violation_type": "ci_duplicate_group",
            "slug": g.slug,
            "page_ids": list(g.page_ids),
            "statuses": list(g.statuses),
            "gate": "check_notion_plans_no_duplicates",
            "rule": "constitutional.md §36",
            "plan": "notion-plans-status-rca-followups-b8e3f2",
        })
    print(
        f"\n[plans_dup] FAIL — {len(groups)} duplicate slug groups detected. "
        "Resolve via tools/notion/triage scripts.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
