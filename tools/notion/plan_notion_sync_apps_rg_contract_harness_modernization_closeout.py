#!/usr/bin/env python3
"""Mark apps-rg-contract-harness-modernization-f4e8b2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-contract-harness-modernization-f4e8b2"
PLAN_PATH = ".claude/plans/apps-rg-contract-harness-modernization-f4e8b2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-26): W0–W5 contract harness modernization — mock CLI removed, "
    "graph authority + PA/SRFS aligned, fast harness (APPS_RG_CONTRACT_HARNESS_FAST) ~2.5s spot; "
    "live CLI lanes via run_contract_harness_live.py."
)

AI_SUMMARY = """- Parent: graph-skills-deferred-followup-d7f2a8
- W0: failure register + junit
- W1–W3: mock policy, graph authority, front-spine bridge (receipts on disk)
- W4–W5: PA/SRFS restore, fast spot 218+ pass, module-scoped CLI (1 run/file)
- Fast: python ops_scripts/apps_rg/run_contract_harness_fast.py
- Live: python ops_scripts/apps_rg/run_contract_harness_live.py
- Receipt: docs/reports/apps_rg/contract_harness_modernization_w5_receipt.json
- Plan: .claude/plans/apps-rg-contract-harness-modernization-f4e8b2.md"""


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
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": page_id,
                    "slug": SLUG,
                    "status": "Completed",
                }
            )
        )
        print(f"PLAN_COMPLETE: slug={SLUG} notion_page={page_id}")
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
        print(json.dumps({"ok": False, "error": str(exc), "slug": SLUG}), file=sys.stderr)
        return 1
    if not result.ok:
        print(json.dumps({"ok": False, "error": result.error, "slug": SLUG}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": result.page_id,
                "slug": SLUG,
                "status": "Completed",
            }
        )
    )
    print(f"PLAN_COMPLETE: slug={SLUG} notion_page={result.page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
