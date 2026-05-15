"""CI gate NP4 — Plans DB freshness vs on-disk plan files.

Detects drift between on-disk plan files (`.cursor/plans/*.md`) and their
Notion Plans DB row's ``last_edited_time``. If a plan file has been edited
recently but the Notion row hasn't been touched within ``--threshold-hours``
(default 168 = 7 days) of the file's mtime, the row is flagged as stale.

This is the backstop for the wave-lifecycle auto-sync chain (see plan
``notion-wave-lifecycle-autosync-f4a2b8``). When the chain is healthy, every
``WAVE_COMPLETE:`` / ``PLAN_COMPLETE:`` marker triggers a Notion patch via
``post_cursor_agent_wave_lifecycle_capture.py`` or ``wave_execution_state.py``,
keeping the row fresh. Drift surfacing here means the chain failed somewhere.

Modes
-----
- **Advisory (default)**: prints violations and exits 0.
- **Fail-closed**: set ``NOTION_PLANS_WAVE_FAIL_CLOSED=1`` → exit 1 on any
  violation.
- **Skip**: when ``NOTION_API_KEY`` / ``NOTION_TOKEN`` is unset, the gate
  exits 0 with a SKIP message (keeps local/offline CI runs unblocked).
- **Bypass**: ``NOTION_PLANS_WAVE_BYPASS=1`` → exit 0, log skip reason.

SSOT
----
- Plans DB data source: ``ac53d31b-3068-4039-9ebe-856c12caab32``
- On-disk plans dir: ``.cursor/plans/``
- Active-statuses (filtered set): ``In Progress``, ``Not Started``

Out of scope
------------
Plans in ``Completed``, ``Retired``, ``Archived``, ``Waiting``,
``Deprioritized`` are excluded — they shouldn't be churning on disk anyway,
and a stale Completed row is not drift.

Exit codes
----------
- 0 — no violations, advisory mode, skipped, or bypassed
- 1 — fail-closed mode + at least one violation
- 2 — Notion API error (never blocks unless fail-closed)

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W4.P4.1).
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
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    PLANS_DATA_SOURCE_ID,
    query_url,
)

PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "plan_notion_wave_freshness.json"

_ACTIVE_STATUSES: frozenset[str] = frozenset({"In Progress", "Not Started"})
_DEFAULT_THRESHOLD_HOURS = 168  # 7 days


def _env_token() -> str | None:
    for key in ("NOTION_API_KEY", "NOTION_TOKEN"):
        value = os.environ.get(key)
        if value:
            return value
    return None


def _fail_closed() -> bool:
    return os.environ.get("NOTION_PLANS_WAVE_FAIL_CLOSED", "").strip() in {
        "1",
        "true",
        "TRUE",
        "yes",
    }


def _bypass() -> bool:
    return os.environ.get("NOTION_PLANS_WAVE_BYPASS") == "1"


def _query_plans(token: str) -> Iterable[dict[str, Any]]:
    """Paginate through all Plans rows. Yields each row dict."""
    start_cursor: str | None = None
    url = query_url(PLANS_DATA_SOURCE_ID)
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_API_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        for row in payload.get("results", []):
            yield row
        if not payload.get("has_more"):
            return
        start_cursor = payload.get("next_cursor")


def _slug_from_row(row: dict[str, Any]) -> str | None:
    props = row.get("properties") or {}
    slug_prop = props.get("Slug") or {}
    title = slug_prop.get("title") or []
    if not title:
        return None
    plain = title[0].get("plain_text") or ""
    return plain.strip() or None


def _status_from_row(row: dict[str, Any]) -> str | None:
    props = row.get("properties") or {}
    status_prop = props.get("Status") or {}
    sel = status_prop.get("select") or {}
    name = sel.get("name")
    return name if isinstance(name, str) else None


def _last_edited_from_row(row: dict[str, Any]) -> datetime | None:
    raw = row.get("last_edited_time")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _file_mtime(slug: str) -> datetime | None:
    path = PLANS_DIR / f"{slug}.md"
    if not path.exists():
        return None
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None


def evaluate(threshold_hours: int) -> dict[str, Any]:
    """Run the freshness check. Returns a structured report."""
    token = _env_token()
    if not token:
        return {
            "status": "skipped",
            "reason": "NOTION_TOKEN/NOTION_API_KEY unset",
            "threshold_hours": threshold_hours,
            "violations": [],
        }

    try:
        rows = list(_query_plans(token))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        return {
            "status": "api_error",
            "reason": repr(exc),
            "threshold_hours": threshold_hours,
            "violations": [],
        }

    threshold_seconds = threshold_hours * 3600
    now = datetime.now(timezone.utc)
    violations: list[dict[str, Any]] = []
    checked = 0

    for row in rows:
        slug = _slug_from_row(row)
        if not slug:
            continue
        status = _status_from_row(row)
        if status not in _ACTIVE_STATUSES:
            continue
        file_mtime = _file_mtime(slug)
        if file_mtime is None:
            continue  # File doesn't exist; that's a separate gate (NP3 / plan-registration).
        notion_edited = _last_edited_from_row(row)
        if notion_edited is None:
            continue
        checked += 1

        skew_seconds = (file_mtime - notion_edited).total_seconds()
        if skew_seconds > threshold_seconds:
            violations.append(
                {
                    "slug": slug,
                    "status": status,
                    "file_mtime": file_mtime.isoformat(),
                    "notion_last_edited": notion_edited.isoformat(),
                    "skew_hours": round(skew_seconds / 3600, 1),
                    "threshold_hours": threshold_hours,
                }
            )

    return {
        "status": "ok" if not violations else "violations",
        "threshold_hours": threshold_hours,
        "checked_count": checked,
        "violation_count": len(violations),
        "violations": violations,
        "evaluated_at": now.isoformat(),
    }


def _write_report(report: dict[str, Any]) -> None:
    try:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold-hours",
        type=int,
        default=int(os.environ.get("NOTION_PLANS_WAVE_THRESHOLD_HOURS", _DEFAULT_THRESHOLD_HOURS)),
        help="File-mtime-vs-Notion-edit skew threshold in hours (default 168).",
    )
    args = parser.parse_args(argv)

    if _bypass():
        print("[NP4] NOTION_PLANS_WAVE_BYPASS=1 — skipping", file=sys.stderr)
        _write_report({"status": "bypassed"})
        return 0

    report = evaluate(args.threshold_hours)
    _write_report(report)

    status = report["status"]
    if status == "skipped":
        print(f"[NP4] SKIP: {report['reason']}", file=sys.stderr)
        return 0
    if status == "api_error":
        print(f"[NP4] API_ERROR: {report['reason']}", file=sys.stderr)
        return 1 if _fail_closed() else 0
    if status == "ok":
        print(
            f"[NP4] OK: {report['checked_count']} active plans within "
            f"{args.threshold_hours}h freshness threshold",
            file=sys.stderr,
        )
        return 0

    # status == "violations"
    print(
        f"[NP4] {len(report['violations'])} stale Notion row(s) "
        f"(threshold {args.threshold_hours}h):",
        file=sys.stderr,
    )
    for v in report["violations"]:
        print(
            f"  {v['slug']} status={v['status']} "
            f"skew={v['skew_hours']}h",
            file=sys.stderr,
        )
    print(f"  Report: {REPORT_PATH}", file=sys.stderr)
    return 1 if _fail_closed() else 0


if __name__ == "__main__":
    sys.exit(main())
