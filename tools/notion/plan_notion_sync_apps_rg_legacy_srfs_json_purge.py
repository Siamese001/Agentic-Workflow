#!/usr/bin/env python3
"""Sync apps-rg-legacy-srfs-json-purge-a8f3c1 plan to Notion Plans DB (Completed)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-legacy-srfs-json-purge-a8f3c1"
PLAN_PATH = ".claude/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-22): Delete SRFS JSON file-envelope authority; product proof = "
    "augmented_skills_graph only. Waves D1–D5 + closeout receipt on disk."
)

AI_SUMMARY = """- STATUS: Completed (D1–D5)
- D1: delete srfs_binding/integration/judge_safe; fail-closed JSON capsule load
- D2: RuntimeError loaders; strip srfs_integration from lanes; GRAPH_ONLY judge
- D3: delete srfs_receipt_aggregator + audit judge; metadata purge
- D4: fold exec_summary_srfs_arsenal into w4b; offline JSON write gated
- D5: GRAPH_PROOF_POOL_APPENDIX; capsule/token-budget graph-only; pytest 29 pass
- Closeout: docs/reports/apps_rg/apps_rg_legacy_srfs_json_purge_closeout_receipt.md
- Follow-on: live qwen_vllm proof when stub_only unset (not plan-blocking)
- Plan: .claude/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md"""


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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    page_id = _query_page_id()
    if page_id:
        if _patch_page(page_id):
            print(
                json.dumps(
                    {
                        "ok": True,
                        "action": "patched",
                        "page_id": page_id,
                        "status": "Completed",
                        "slug": SLUG,
                    }
                )
            )
            return 0
        print(json.dumps({"ok": False, "error": "patch_failed"}), file=sys.stderr)
        return 1
    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
            force_status="Completed",
        )
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "action": "created",
                    "page_id": result.page_id,
                    "status": result.status,
                    "slug": SLUG,
                }
            )
        )
        return 0 if result.ok else 1
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
