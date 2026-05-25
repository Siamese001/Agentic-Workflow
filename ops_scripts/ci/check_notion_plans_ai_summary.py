"""CI gate — Plans DB rows must have non-empty AI Summary.

Constitutional rule: `.cursor/rules/notion-plans-taxonomy.md`
"Mandatory AI Summary" invariant (2026-05-03).

Contract
--------
Every Notion Plans row with ``Status ∈ {In Progress, Not Started, Lower Priority, Waiting, Completed}`` MUST have a
non-empty ``AI Summary`` (property id ``lNTq``, note trailing space in name).
Format: single sentence, ≤ 12 words, scope + why-it-matters. Soft-cap at
15 words (rows over that log an advisory WARN but do not fail even under
fail-closed mode).  Rows in ``Retired`` / ``Archived`` are exempt. Empty
``AI Summary`` is a reviewability violation — a reader scanning the DB
learns nothing from a row without one.

Modes
-----
- **Advisory (default)**: prints violations and exits 0.
- **Fail-closed**: set ``NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED=1`` → exit 1 on
  any violation.
- **Skip**: when ``NOTION_API_KEY`` (or ``NOTION_TOKEN``) is not set, the gate
  exits 0 with a SKIP message. This keeps local/offline CI runs unblocked.

SSOT
----
- Data source id: ``ac53d31b-3068-4039-9ebe-856c12caab32`` (Plans)
- Property id: ``lNTq`` (``AI Summary ``)
- Status enforced-set: ``{"In Progress", "Not Started", "Lower Priority", "Waiting", "Completed"}``

Exit codes
----------
- 0 — no violations, or advisory mode, or skipped
- 1 — fail-closed mode + at least one violation
- 2 — Notion API error while fetching (never blocks unless fail-closed)

Usage
-----
    python ops_scripts/ci/check_notion_plans_ai_summary.py
    NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED=1 python ops_scripts/ci/check_notion_plans_ai_summary.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CURSOR_SCRIPTS = _REPO_ROOT / ".cursor" / "scripts"
if str(_CURSOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CURSOR_SCRIPTS))

from _notion_plans_status_check import (  # noqa: E402
    PLANS_DATA_SOURCE_ID,
    PLANS_STATUSES_AI_SUMMARY_ENFORCED,
)

_PLANS_DATA_SOURCE_ID = PLANS_DATA_SOURCE_ID
_ENFORCED_STATUSES = PLANS_STATUSES_AI_SUMMARY_ENFORCED
_NOTION_VERSION = "2025-09-03"
_QUERY_URL = f"https://api.notion.com/v1/data_sources/{_PLANS_DATA_SOURCE_ID}/query"

# Format soft-cap: single sentence, ≤ 12 words target, ≤ 15 words hard advisory.
_WORD_SOFT_CAP = 15


def _env_token() -> str | None:
    for key in ("NOTION_API_KEY", "NOTION_TOKEN"):
        value = os.environ.get(key)
        if value:
            return value
    return None


def _fail_closed() -> bool:
    return os.environ.get("NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED", "").strip() in {
        "1",
        "true",
        "TRUE",
        "yes",
    }


def _query_plans(token: str) -> Iterable[dict[str, Any]]:
    """Paginate through all Plans rows. Yields each page (row) dict."""
    start_cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"page_size": 100}
        if start_cursor is not None:
            payload["start_cursor"] = start_cursor
        req = urllib.request.Request(
            _QUERY_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": _NOTION_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Notion API HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Notion API URL error: {exc.reason}") from exc

        for row in body.get("results", []):
            yield row
        if not body.get("has_more"):
            return
        start_cursor = body.get("next_cursor")
        if not start_cursor:
            return


def _extract_status(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Status", {})
    select = prop.get("select") or {}
    return str(select.get("name") or "")


def _extract_slug(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Slug", {})
    title = prop.get("title") or []
    if title and isinstance(title, list):
        first = title[0] or {}
        return str(first.get("plain_text") or "")
    return ""


def _extract_ai_summary(row: dict[str, Any]) -> str:
    # Notion property name has trailing space: "AI Summary "
    props = row.get("properties", {})
    prop = props.get("AI Summary ") or props.get("AI Summary") or {}
    rt = prop.get("rich_text") or []
    if not isinstance(rt, list):
        return ""
    parts = [str(chunk.get("plain_text") or "") for chunk in rt if isinstance(chunk, dict)]
    return "".join(parts).strip()


def main(argv: list[str] | None = None) -> int:
    _ = argv  # reserved
    token = _env_token()
    if not token:
        print("[check_notion_plans_ai_summary] SKIP — NOTION_API_KEY / NOTION_TOKEN unset")
        return 0

    try:
        rows = list(_query_plans(token))
    except RuntimeError as exc:
        print(f"[check_notion_plans_ai_summary] ERROR — {exc}")
        return 1 if _fail_closed() else 0

    violations: list[tuple[str, str]] = []
    verbose_rows: list[tuple[str, str, int]] = []
    total = 0
    for row in rows:
        status = _extract_status(row)
        if status not in _ENFORCED_STATUSES:
            continue
        total += 1
        summary = _extract_ai_summary(row)
        slug = _extract_slug(row) or row.get("id", "<unknown>")
        if not summary:
            violations.append((slug, status))
            continue
        word_count = len(summary.split())
        if word_count > _WORD_SOFT_CAP:
            verbose_rows.append((slug, status, word_count))

    if violations:
        print(
            f"[check_notion_plans_ai_summary] VIOLATION — {len(violations)} of {total} "
            f"enforced rows (Status in {sorted(_ENFORCED_STATUSES)}) have empty AI Summary:"
        )
        for slug, status in violations:
            print(f"  - [{status}] {slug}")
        print(
            "\nFix: patch each row with a single-sentence AI Summary (≤ 12 words) "
            "covering scope + why-it-matters.\n"
            "See `.cursor/rules/notion-plans-taxonomy.md` > Mandatory AI Summary."
        )
        if _fail_closed():
            return 1
        print("[check_notion_plans_ai_summary] advisory mode — exiting 0")
        return 0

    if verbose_rows:
        print(
            f"[check_notion_plans_ai_summary] WARN — {len(verbose_rows)} rows have "
            f"AI Summary > {_WORD_SOFT_CAP} words (target: ≤ 12):"
        )
        for slug, status, wc in verbose_rows:
            print(f"  - [{status}] {slug} ({wc} words)")
        print(
            "Not a failure — tighten when convenient. Target: one sentence, scope + why."
        )

    print(
        f"[check_notion_plans_ai_summary] OK — {total} enforced rows all carry "
        f"non-empty AI Summary ({len(verbose_rows)} over soft-cap {_WORD_SOFT_CAP} words)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
