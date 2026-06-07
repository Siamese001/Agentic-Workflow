#!/usr/bin/env python3
"""Register or patch notion-status-ssot-burndown-c4e7a1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "notion-status-ssot-burndown-c4e7a1"
PLAN_PATH = ".claude/plans/notion-status-ssot-burndown-c4e7a1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Burndown remaining Plans Status leaks: restore/CI/UPLM Deferred→Lower Priority; "
    "AI summary gate SSOT set; new-plan gate catches stale legacy names; doc fixes."
)

AI_SUMMARY = """- PLAN_STATUS: Completed (2026-05-25)
- Parent: notion-stale-status-leak-closeout-b8e4f2
- Receipt: docs/reports/plans/notion_status_ssot_burndown_receipt_20260525.md
- W1: restore_plan_statuses_from_cache, repair, plan_lifecycle_manager
- W2: CI gates + creation auditor + tests
- Disk: .claude/plans/notion-status-ssot-burndown-c4e7a1.md"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {"property": "Slug", "title": {"equals": SLUG}},
        "page_size": 1,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return None
    rows = data.get("results") or []
    if rows:
        return str(rows[0].get("id") or "") or None
    return None


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}]},
        }
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            json.loads(resp.read().decode("utf-8"))
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    page_id = _query_page_id()
    if page_id:
        ok = _patch_page(page_id)
        action = "patched"
    else:
        try:
            result = create_plan_in_notion(
                slug=SLUG,
                summary=SUMMARY,
                ai_summary=AI_SUMMARY,
                force_status="Completed",
            )
        except PlanCreationError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
            return 1
        ok = result.ok
        page_id = result.page_id
        action = "created"
    print(
        json.dumps(
            {
                "ok": ok,
                "action": action,
                "slug": SLUG,
                "page_id": page_id,
                "status": "Completed",
                "plan_path": PLAN_PATH,
            },
            indent=2,
        )
    )
    if ok:
        print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
