"""CI gate NP3 -- Backlog Items rows must each have a Plan relation.

Paginate Backlog Items DB, report rows missing a Plan relation AND missing
a Plan File value (true orphan = no linkage at all). Advisory by default;
fail-closed via BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1. Skips when
NOTION_API_KEY / NOTION_TOKEN unset (offline CI safe).

Emits artifacts/notion/backlog_plan_linkage.json with:
  total_rows, linked_rows, plan_file_only_rows, orphan_rows, violations[]

Constitutional rule: .cursor/rules/notion-backlog-plan-linkage.md
Plan: backlog-plan-linkage-enforcement-a4b2f1 W5.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WINDSURF_SCRIPTS = _REPO_ROOT / ".windsurf" / "scripts"
if str(_WINDSURF_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_WINDSURF_SCRIPTS))

try:
    from _notion_constants import (  # type: ignore
        NOTION_API_VERSION,
        NOTION_BASE,
        WAVE_PHASE_DATA_SOURCE_ID,
    )
except ImportError:
    NOTION_API_VERSION = "2025-09-03"
    NOTION_BASE = "https://api.notion.com/v1"
    WAVE_PHASE_DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"

_QUERY_URL = f"{NOTION_BASE}/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query"
_ARTIFACT = _REPO_ROOT / "artifacts" / "notion" / "backlog_plan_linkage.json"


def _env_token() -> str | None:
    for key in ("NOTION_API_KEY", "NOTION_TOKEN"):
        v = os.environ.get(key)
        if v:
            return v
    return None


def _fail_closed() -> bool:
    return os.environ.get("BACKLOG_PLAN_LINKAGE_FAIL_CLOSED", "").strip() in {
        "1", "true", "TRUE", "yes",
    }


def _query_all(token: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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
                "Notion-Version": NOTION_API_VERSION,
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
        rows.extend(payload.get("results") or [])
        if not payload.get("has_more"):
            return rows
        cursor = payload.get("next_cursor") or None
        if not cursor:
            return rows


def _has_relation(row: dict[str, Any], field: str) -> bool:
    prop = (row.get("properties") or {}).get(field) or {}
    if prop.get("type") != "relation":
        return False
    return bool(prop.get("relation"))


def _rich_text_val(row: dict[str, Any], field: str) -> str:
    prop = (row.get("properties") or {}).get(field) or {}
    t = prop.get("type")
    if t == "rich_text":
        parts = prop.get("rich_text") or []
    elif t == "title":
        parts = prop.get("title") or []
    else:
        return ""
    return "".join((r.get("plain_text") or "") for r in parts).strip()


def _title(row: dict[str, Any]) -> str:
    for name in ("Phase Title", "Title", "Name"):
        v = _rich_text_val(row, name)
        if v:
            return v
    return (row.get("id") or "")[:8]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    token = _env_token()
    if not token:
        print(
            "[check_notion_backlog_plan_linkage] SKIP -- "
            "NOTION_API_KEY / NOTION_TOKEN unset"
        )
        return 0

    try:
        rows = _query_all(token)
    except RuntimeError as exc:
        print(f"[check_notion_backlog_plan_linkage] ERROR -- {exc}")
        return 1 if _fail_closed() else 0

    total = len(rows)
    linked_rows: list[dict[str, Any]] = []
    plan_file_only_rows: list[dict[str, Any]] = []
    orphan_rows: list[dict[str, Any]] = []

    for row in rows:
        has_plan_rel = _has_relation(row, "Plan")
        has_plan_file = bool(_rich_text_val(row, "Plan File"))

        if has_plan_rel:
            linked_rows.append(
                {"page_id": row.get("id", ""), "title": _title(row)}
            )
        elif has_plan_file:
            plan_file_only_rows.append(
                {
                    "page_id": row.get("id", ""),
                    "title": _title(row),
                    "plan_file": _rich_text_val(row, "Plan File"),
                }
            )
        else:
            orphan_rows.append(
                {"page_id": row.get("id", ""), "title": _title(row)}
            )

    result = {
        "total_rows": total,
        "linked_rows": len(linked_rows),
        "plan_file_only_rows": len(plan_file_only_rows),
        "orphan_rows": len(orphan_rows),
        "violations": orphan_rows,
    }

    try:
        _ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        _ARTIFACT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except OSError:  # guardian: allow-silent-swallow -- artifact write non-fatal
        pass

    if orphan_rows:
        pct = 100.0 * len(linked_rows) / total if total else 0.0
        print(
            f"[check_notion_backlog_plan_linkage] VIOLATION -- "
            f"{len(orphan_rows)} of {total} Backlog rows have NO Plan relation "
            f"AND NO Plan File ({pct:.1f}% linked):"
        )
        for v in orphan_rows[:20]:
            print(f"  - {v['title']} ({v['page_id']})")
        if len(orphan_rows) > 20:
            print(f"  ... and {len(orphan_rows) - 20} more (see artifact)")
        print(
            f"\nFix: run tools/notion/backfill_backlog_plan_relation.py to re-link.\n"
            f"See .cursor/rules/notion-backlog-plan-linkage.md for invariant details."
        )
        if _fail_closed():
            return 1
        print("[check_notion_backlog_plan_linkage] advisory mode -- exiting 0")
        return 0

    pct = 100.0 * len(linked_rows) / total if total else 0.0
    print(
        f"[check_notion_backlog_plan_linkage] OK -- "
        f"{len(linked_rows)}/{total} rows linked ({pct:.1f}%), "
        f"{len(plan_file_only_rows)} plan-file-only, "
        f"0 true orphans"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
