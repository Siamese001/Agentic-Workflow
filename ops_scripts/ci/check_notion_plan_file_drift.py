#!/usr/bin/env python3
"""check_notion_plan_file_drift.py — CI drift gate for Notion ↔ disk plan files.

Queries the Wave/Phase Convergence Notion DB for open rows (Status not in
``{Done, Closed, Cancelled, Archived}``) and verifies that each row's
``Plan File`` property resolves to an existing file under
``.cursor/plans/``. Orphan rows (Notion says file X, disk lacks X) are
reported; missing Notion rows for on-disk plans are **not** flagged here
(that's the inverse direction and a separate concern).

Policy SSOT: ``.cursor/rules/deferred-scope-capture.md`` §Auto-scaffold.
Notion data source: ``fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7``.

Behavior:

- Exits 0 with a per-row stderr report when orphans are found (advisory default).
- Exits 1 when orphans are found **and** ``STRICT_DRIFT=1`` (fail-closed).
- Exits 0 with a "skipped" message when NOTION_TOKEN is not set (safe for
  local dev, pre-commit on fresh clones). CI should set the token.
- Exits 0 on any transport/parse error ("fail-open on transient failure")
  unless ``STRICT_DRIFT=1`` is set (CI may use strict mode).

Bypass: ``PLAN_FILE_DRIFT_BYPASS=1`` — logs a bypass line and exits 0.

Usage:
    python ops_scripts/ci/check_notion_plan_file_drift.py
    STRICT_DRIFT=1 python ops_scripts/ci/check_notion_plan_file_drift.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._governance_paths import (  # noqa: E402
    CURSOR_SCRIPTS_DIR,
    PLANS_DIR,
    governance_artifact_log,
)

import sys as _sys

_sys.path.insert(0, str(CURSOR_SCRIPTS_DIR))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    WAVE_PHASE_DATA_SOURCE_ID as WAVE_PHASE_DS_ID,
)


# Wave/Phase Convergence — read from data_source_id (not database_id).

NOTION_QUERY_URL = f"https://api.notion.com/v1/data_sources/{WAVE_PHASE_DS_ID}/query"

NOTION_HTTP_TIMEOUT_S = 20.0
NOTION_PAGE_SIZE = 100
NOTION_MAX_PAGES = 20  # 2000 rows safety cap

CLOSED_STATUSES = {"Done", "Closed", "Cancelled", "Archived"}

AUDIT_LOG = governance_artifact_log("plan_file_drift.jsonl")


def _log(record: dict[str, Any]) -> None:
    try:
        from ops_scripts.ci._governance_paths import append_governance_artifact_jsonl  # noqa: PLC0415

        append_governance_artifact_jsonl("plan_file_drift.jsonl", record)
    except OSError:
        pass  # fail-open; audit log is best-effort


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _query_open_rows(token: str) -> list[dict[str, Any]]:
    """Paginated query for rows whose Status is not in CLOSED_STATUSES.

    Notion doesn't have a ``not in`` filter for select, so we fetch all
    non-archived rows and filter status-side. Caps at NOTION_MAX_PAGES.
    """

    results: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(NOTION_MAX_PAGES):
        body: dict[str, Any] = {
            "filter": {"property": "Plan File", "rich_text": {"is_not_empty": True}},
            "page_size": NOTION_PAGE_SIZE,
        }
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            NOTION_QUERY_URL,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_API_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8") or "{}")
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return results


def _extract_plan_file(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Plan File", {})
    for chunk in prop.get("rich_text", []):
        text = chunk.get("text", {}).get("content", "")
        if text:
            return text.strip()
    return ""


def _extract_status(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Status", {}).get("select") or {}
    return prop.get("name", "")


def _extract_phase_title(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Phase Title", {})
    for chunk in prop.get("title", []):
        text = chunk.get("text", {}).get("content", "")
        if text:
            return text.strip()
    return ""


def _plan_file_exists(filename: str) -> bool:
    """Check for a plan file. Accepts exact filename or slug-without-suffix."""

    if not filename:
        return False
    name = Path(filename).name  # reject path traversal
    if not name.endswith(".md"):
        name = f"{name}.md"
    if (PLANS_DIR / name).is_file():
        return True
    # Slug-only match: allow ``<slug>.md`` to resolve to ``<slug>-<6hex>.md``.
    base = name[:-3]
    for candidate in PLANS_DIR.glob(f"{base}-*.md"):
        if candidate.is_file():
            return True
    return False


def main() -> int:  # noqa: PLR0911
    if os.environ.get("PLAN_FILE_DRIFT_BYPASS") == "1":
        _log({"kind": "bypass", "reason": "PLAN_FILE_DRIFT_BYPASS=1"})
        print("[plan_file_drift] BYPASS engaged", file=sys.stderr)
        return 0

    strict = os.environ.get("STRICT_DRIFT") == "1"

    token = _notion_token()
    if not token:
        msg = (
            "[plan_file_drift] NOTION_TOKEN not set — skipping check "
            "(use STRICT_DRIFT=1 to fail in this state)."
        )
        print(msg, file=sys.stderr)
        _log({"kind": "skipped_no_token"})
        return 1 if strict else 0

    try:
        rows = _query_open_rows(token)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        _log({"kind": "query_transport_error", "error": str(exc)})
        msg = f"[plan_file_drift] Notion query failed: {exc}"
        print(msg, file=sys.stderr)
        return 1 if strict else 0
    except (json.JSONDecodeError, ValueError) as exc:
        _log({"kind": "query_parse_error", "error": str(exc)})
        print(f"[plan_file_drift] Notion response parse failed: {exc}", file=sys.stderr)
        return 1 if strict else 0

    orphans: list[dict[str, str]] = []
    open_checked = 0
    for row in rows:
        if row.get("archived") or row.get("in_trash"):
            continue
        status = _extract_status(row)
        if status in CLOSED_STATUSES:
            continue
        plan_file = _extract_plan_file(row)
        if not plan_file:
            continue  # Notion rich_text filter should have caught this
        open_checked += 1
        if not _plan_file_exists(plan_file):
            orphans.append(
                {
                    "plan_file": plan_file,
                    "row_id": row.get("id", ""),
                    "phase_title": _extract_phase_title(row),
                    "status": status,
                }
            )

    _log(
        {
            "kind": "summary",
            "open_rows_checked": open_checked,
            "orphan_count": len(orphans),
        }
    )

    if not orphans:
        print(
            f"[plan_file_drift] OK — {open_checked} open rows; all Plan File values resolve on disk.",
            file=sys.stderr,
        )
        return 0

    print("", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(
        f"DRIFT: {len(orphans)} Notion Wave/Phase rows reference missing plan files",
        file=sys.stderr,
    )
    print("=" * 72, file=sys.stderr)
    for orphan in orphans[:50]:
        print(
            f"  Plan File: {orphan['plan_file']!s:<60} "
            f"Status: {orphan['status']:<10} "
            f"Row: {orphan['phase_title'][:40]}",
            file=sys.stderr,
        )
    if len(orphans) > 50:
        print(f"  ... and {len(orphans) - 50} more.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Fix options:", file=sys.stderr)
    print(
        "  1. Create the plan file at .cursor/plans/<plan_file> (SSOT location).",
        file=sys.stderr,
    )
    print(
        "  2. Close the Notion row (set Status to Done/Closed/Cancelled) if the scope is no longer relevant.",
        file=sys.stderr,
    )
    print(
        "  3. Emergency bypass: PLAN_FILE_DRIFT_BYPASS=1 ...",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    if strict:
        print("[plan_file_drift] STRICT_DRIFT=1 — failing closed on drift.", file=sys.stderr)
        return 1
    print(
        "[plan_file_drift] Advisory mode — drift reported; exiting 0 (set STRICT_DRIFT=1 to fail).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
