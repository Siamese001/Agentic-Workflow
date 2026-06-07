#!/usr/bin/env python3
"""Create or sync apps-rg-reasoning-deletion-d4e8f1 in Notion Plans DB."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-reasoning-deletion-d4e8f1"
PLAN_PATH = ".claude/plans/apps-rg-reasoning-deletion-d4e8f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-23): Deleted legacy apps_rg/reasoning/ agent swarm; migrated "
    "rg_orchestrator_facade + apps_eval scenarios; 37 scoped contract tests passed. "
    "Product path: python -m apps_rg → canonical_dispatch → section lanes."
)

AI_SUMMARY = """- STATUS: Completed (W0–W3 executed)
- Deleted: apps_rg/reasoning/ (10 modules) + tests/unit/apps_rg/reasoning/
- Migrated: rg_orchestrator_facade (canonical dispatch only); eval hop scenarios → SKIP
- Proof: pytest 37 passed (quarantine + facade + authority); python -m apps_rg --help OK
- Receipt: artifacts/apps_rg/reasoning_deletion_receipt.md
- Disk SSOT: .claude/plans/apps-rg-reasoning-deletion-d4e8f1.md"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {"filter": {"property": "Slug", "title": {"equals": SLUG}}, "page_size": 1}
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
    return str(rows[0].get("id") or "") if rows else None


def _patch_page(page_id: str, *, status: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": status}},
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completed", action="store_true", help="Mark plan Completed in Notion")
    args = parser.parse_args()
    status = "Completed" if args.completed else "Not Started"

    page_id = _query_page_id()
    if page_id:
        ok = _patch_page(page_id, status=status)
        print(json.dumps({"ok": ok, "action": "patched", "page_id": page_id, "slug": SLUG, "status": status}))
        return 0 if ok else 1
    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            force_status="Completed" if args.completed else None,
        )
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": result.ok,
                "action": "created",
                "page_id": result.page_id,
                "slug": SLUG,
                "status": result.status,
            }
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
