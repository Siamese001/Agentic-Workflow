"""CI gate NP2 -- Plans DB rows must use canonical Status option strings.

Paginate Plans DB via API-query-data-source, report rows with Status value
outside the canonical six-option set. Advisory by default; fail-closed via
NOTION_PLANS_STATUS_FAIL_CLOSED=1. Skips when NOTION_API_KEY/TOKEN unset.

Constitutional rule: .cursor/rules/notion-plans-taxonomy.md >
"CANONICAL Status option strings" (2026-05-03).
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
_WINDSURF_SCRIPTS = _REPO_ROOT / ".windsurf" / "scripts"
if str(_WINDSURF_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_WINDSURF_SCRIPTS))

try:
    from _notion_plans_status_check import (  # type: ignore
        CANONICAL_STATUSES,
        PLANS_DATA_SOURCE_ID,
        STALE_EQUIVALENTS,
    )
except ImportError:
    CANONICAL_STATUSES = frozenset(
        {"Live", "Draft", "Waiting", "Completed", "Retired", "Archived"}
    )
    PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
    STALE_EQUIVALENTS: dict[str, str] = {}

_NOTION_VERSION = "2025-09-03"
_QUERY_URL = f"https://api.notion.com/v1/data_sources/{PLANS_DATA_SOURCE_ID}/query"
_DRIFT_ARTIFACT = _REPO_ROOT / "artifacts" / "notion" / "plans_status_drift.json"


def _env_token() -> str | None:
    for key in ("NOTION_API_KEY", "NOTION_TOKEN"):
        v = os.environ.get(key)
        if v:
            return v
    return None


def _fail_closed() -> bool:
    return os.environ.get("NOTION_PLANS_STATUS_FAIL_CLOSED", "").strip() in {
        "1", "true", "TRUE", "yes",
    }


def _query_plans(token: str) -> Iterable[dict[str, Any]]:
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            _QUERY_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": _NOTION_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Notion API HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Notion API URL error: {exc.reason}") from exc
        for row in payload.get("results", []):
            yield row
        if not payload.get("has_more"):
            return
        cursor = payload.get("next_cursor") or None
        if not cursor:
            return


def _extract_status(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Status", {}) or {}
    sel = prop.get("select") or {}
    return str(sel.get("name") or "")


def _extract_slug(row: dict[str, Any]) -> str:
    prop = row.get("properties", {}).get("Slug", {}) or {}
    title = prop.get("title") or []
    if title and isinstance(title, list):
        first = title[0] or {}
        return str(first.get("plain_text") or "")
    return ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    token = _env_token()
    if not token:
        print("[check_notion_plans_status_drift] SKIP -- NOTION_API_KEY / NOTION_TOKEN unset")
        return 0

    try:
        rows = list(_query_plans(token))
    except RuntimeError as exc:
        print(f"[check_notion_plans_status_drift] ERROR -- {exc}")
        return 1 if _fail_closed() else 0

    drift: list[dict[str, Any]] = []
    total = 0
    for row in rows:
        total += 1
        status = _extract_status(row)
        if not status:
            continue
        if status in CANONICAL_STATUSES:
            continue
        drift.append(
            {
                "page_id": row.get("id", ""),
                "slug": _extract_slug(row),
                "status_value": status,
                "suggested": STALE_EQUIVALENTS.get(status, ""),
            }
        )

    try:
        _DRIFT_ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        _DRIFT_ARTIFACT.write_text(
            json.dumps({"total_rows": total, "drift": drift}, indent=2),
            encoding="utf-8",
        )
    except OSError:  # guardian: allow-silent-swallow -- artifact write non-fatal
        pass

    if drift:
        print(
            f"[check_notion_plans_status_drift] VIOLATION -- {len(drift)} of {total} "
            f"Plans rows use non-canonical Status values:"
        )
        for d in drift:
            suggestion = f" -> {d['suggested']}" if d["suggested"] else ""
            print(f"  - [{d['status_value']!r}{suggestion}] {d['slug']} ({d['page_id']})")
        print(
            f"\nCanonical set: {sorted(CANONICAL_STATUSES)}\n"
            f"Fix: API-patch-page each row with a canonical Status value.\n"
            f"See .cursor/rules/notion-plans-taxonomy.md > CANONICAL Status option strings."
        )
        if _fail_closed():
            return 1
        print("[check_notion_plans_status_drift] advisory mode -- exiting 0")
        return 0

    print(
        f"[check_notion_plans_status_drift] OK -- {total} Plans rows all use canonical "
        f"Status values (out of {sorted(CANONICAL_STATUSES)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
