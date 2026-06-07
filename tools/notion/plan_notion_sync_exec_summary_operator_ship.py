#!/usr/bin/env python3
"""Register or patch exec-summary-operator-ship-a3f7c2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-operator-ship-a3f7c2"
PLAN_PATH = ".claude/plans/exec-summary-operator-ship-a3f7c2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
NOTION_PAGE_ID = "36a27693-f55c-81ab-8c4a-e867ea5f5bfe"

SUMMARY = (
    "COMPLETED (2026-05-24): Executive summary operator ship — DRAFT_READY vs CERTIFIED, "
    "exit 0 on X2 PASS + soft-fail judges, default judge regen on product CLI. "
    "W5 minimum ship PASS (exec_summary_20260524_001344). Certified 3/3 deferred."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETED (2026-05-24)
- W5 minimum ship: DRAFT_READY, exit 0, X2 PASS (exec_summary_20260524_001344)
- Certified tier: NOT achieved — best live 2/3 (125852); Claude synthesis residual FAIL
- W0–W3: disposition, judge regen default, operator matrix tests
- W4 P1: repair_summary consolidation — deferred
- Disk: .claude/plans/exec-summary-operator-ship-a3f7c2.md
- Guide: docs/apps_rg/executive_summary_operator_guide.md"""


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
    return NOTION_PAGE_ID


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
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    page_id = _query_page_id()
    if page_id and _patch_page(page_id):
        notion_url = f"https://www.notion.so/{page_id.replace('-', '')}"
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": page_id,
                    "notion_url": notion_url,
                    "status": "Completed",
                    "slug": SLUG,
                    "plan_path": PLAN_PATH,
                }
            )
        )
        print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
        return 0

    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
        )
    except PlanCreationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1

    page_id = result.page_id or ""
    notion_url = f"https://www.notion.so/{page_id.replace('-', '')}" if page_id else ""
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": page_id,
                "notion_url": notion_url,
                "status": result.status,
                "slug": SLUG,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
