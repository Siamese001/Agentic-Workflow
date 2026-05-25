#!/usr/bin/env python3
"""Register or patch apps-rg-x2-dead-gates-burndown-c4e8f2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-x2-dead-gates-burndown-c4e8f2"
PLAN_PATH = ".cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-24): X2 dead/deprecated gates burndown W1–W4 DONE. "
    "Registry/audit alignment; retired SRFS stack; single proof-pool gate ID per section; "
    "SRFS skip-PASS removed on golden path. Receipts under docs/reports/apps_rg/apps_rg_x2_dead_gates_*."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETE (2026-05-24)
- W1: lane_registry + audit SSOT — ghost gate IDs removed
- W2: retired exec-summary SRFS X2/repair modules removed
- W3: collapse *_within_srfs_slice → active proof-pool gate IDs
- W4: SRFS skip-PASS emission removed + live executive_summary proof
- Evidence: docs/reports/apps_rg/apps_rg_x2_dead_gates_w4_receipt.md (+ w1_w2, w3)
- Disk: .cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md
- Parent context: apps-rg-spine-only-unification-d8f4a2 (section X2 hygiene)"""


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
    return str(rows[0].get("id") or "") if rows else None


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
                },
                indent=2,
            )
        )
        print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
        return 0

    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
            force_status="Completed",
        )
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    if not result.ok:
        print(json.dumps({"ok": False, "error": result.error}), file=sys.stderr)
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
            },
            indent=2,
        )
    )
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
