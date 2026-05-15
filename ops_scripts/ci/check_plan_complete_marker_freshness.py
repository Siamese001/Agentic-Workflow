#!/usr/bin/env python3
"""
check_plan_complete_marker_freshness.py — CI gate NP13.

Detects Plans DB rows that have been ``In Progress`` for more than
``_STALE_DAYS`` days without a corresponding ``PLAN_COMPLETE`` marker event
recorded in ``artifacts/cursor/wave_lifecycle_capture.jsonl``.

Advisory by default. Fail-closed: ``NOTION_PLAN_COMPLETE_FAIL_CLOSED=1``.
Bypass: ``NOTION_PLAN_COMPLETE_BYPASS=1``.
Skips silently when ``NOTION_API_KEY`` / ``NOTION_TOKEN`` are unset (offline CI).

Exit codes:
    0 — no violations (or offline / bypass)
    1 — violations found AND ``NOTION_PLAN_COMPLETE_FAIL_CLOSED=1``

Plan: plan-complete-marker-enforcement-d2e9f1 W2.1
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_STALE_DAYS: int = 7

_PLANS_DS_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
_NOTION_API_BASE = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"

_LIFECYCLE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "wave_lifecycle_capture.jsonl"
_REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "plan_complete_marker_freshness.json"

_STATUS_IN_PROGRESS = "In Progress"


def _token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY") or None


def _notion_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": _NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _post_json(url: str, body: dict, token: str) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers=_notion_headers(token),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc


def _fetch_in_progress_plans(token: str) -> list[dict]:
    """Fetch all Plans DB rows with Status = In Progress (paginated)."""
    url = f"{_NOTION_API_BASE}/databases/{_PLANS_DS_ID}/query"
    results: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {
            "filter": {
                "property": "Status",
                "select": {"equals": _STATUS_IN_PROGRESS},
            },
            "page_size": 100,
        }
        if cursor:
            body["start_cursor"] = cursor
        resp = _post_json(url, body, token)
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
        if not cursor:
            break
    return results


def _extract_slug(page: dict) -> str | None:
    try:
        title_items = page["properties"]["Slug"]["title"]
        if title_items:
            return title_items[0]["plain_text"].strip()
    except (KeyError, IndexError, TypeError):
        pass
    return None


def _extract_last_edited(page: dict) -> datetime | None:
    raw = page.get("last_edited_time", "")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_completed_slugs_from_lifecycle_log() -> set[str]:
    """Return slugs that have a PLAN_COMPLETE / plan_complete event in the log."""
    slugs: set[str] = set()
    if not _LIFECYCLE_LOG.exists():
        return slugs
    try:
        with _LIFECYCLE_LOG.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                reason = entry.get("reason", "")
                slug = entry.get("slug", "")
                if slug and "plan_complete" in reason:
                    slugs.add(slug)
    except OSError:
        pass
    return slugs


def _write_report(violations: list[dict], total_checked: int) -> None:
    report = {
        "gate": "NP12",
        "checked": total_checked,
        "violations": len(violations),
        "stale_days_threshold": _STALE_DAYS,
        "rows": violations,
    }
    try:
        _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _REPORT_PATH.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass


def main() -> int:
    if os.environ.get("NOTION_PLAN_COMPLETE_BYPASS") == "1":
        print("[NP13] bypass active — skipping", file=sys.stderr)
        return 0

    token = _token()
    if not token:
        print("[NP13] NOTION_TOKEN/NOTION_API_KEY unset — skipping (offline CI)", file=sys.stderr)
        return 0

    fail_closed = os.environ.get("NOTION_PLAN_COMPLETE_FAIL_CLOSED") == "1"
    cutoff = datetime.now(timezone.utc) - timedelta(days=_STALE_DAYS)

    try:
        pages = _fetch_in_progress_plans(token)
    except RuntimeError as exc:
        print(f"[NP13] Notion API error: {exc}", file=sys.stderr)
        return 0

    completed_in_log = _load_completed_slugs_from_lifecycle_log()

    violations: list[dict] = []
    for page in pages:
        slug = _extract_slug(page)
        if not slug:
            continue
        last_edited = _extract_last_edited(page)
        if last_edited is None:
            continue
        if last_edited > cutoff:
            continue
        if slug in completed_in_log:
            continue
        age_days = (datetime.now(timezone.utc) - last_edited).days
        violations.append({"slug": slug, "age_days": age_days, "last_edited": last_edited.isoformat()})

    _write_report(violations, len(pages))

    if not violations:
        print(f"[NP13] OK — {len(pages)} In Progress plans checked, none stale without PLAN_COMPLETE marker", file=sys.stderr)
        return 0

    print(
        f"[NP13] WARN — {len(violations)} plan(s) have been In Progress for >{_STALE_DAYS}d "
        f"with no PLAN_COMPLETE marker in wave_lifecycle_capture.jsonl:",
        file=sys.stderr,
    )
    for v in violations:
        print(f"  {v['slug']}  (age={v['age_days']}d, last_edited={v['last_edited']})", file=sys.stderr)
    print(
        f"  Remedy: emit 'PLAN_COMPLETE: plan=<slug>' in the next response, "
        f"or run: python tools/windsurf/wave_execution_state.py complete --plan <slug>",
        file=sys.stderr,
    )

    if fail_closed:
        print("[NP13] fail-closed mode active — exiting 1", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
