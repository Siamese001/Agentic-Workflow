#!/usr/bin/env python3
"""Register or patch exec-summary-anthropic-surgical-regen-f3c8d2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-anthropic-surgical-regen-f3c8d2"
PLAN_PATH = ".claude/plans/exec-summary-anthropic-surgical-regen-f3c8d2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
NOTION_PAGE_ID = "36c27693-f55c-81bc-a4a3-de1022a6e532"

SUMMARY = (
    "COMPLETED (2026-05-26): Anthropic-aligned surgical judge regen — W1 delta token env "
    "removed; W2 3-stage contract; W3 G5v2 allowlist; W4 delta_class routing; W5 Brown "
    "REAL_LLM infra PASS (exec_summary_20260526_202438); 123 pytest."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETE (2026-05-26)
- Parent: exec-summary-judge-regen-prompt-loop-b9e4c3
- W5: docs/reports/apps_rg/executive_summary_anthropic_surgical_regen_w5_brown_20260526.md
- Live: exec_summary_20260526_202438 (G5v2 cycle1 pass; regen_outcome=no_acceptable_candidate)
- Verifier: tools/cursor/verify_exec_summary_anthropic_surgical_regen.py
- Guide: docs/apps_rg/executive_summary_operator_guide.md
- Disk: .claude/plans/exec-summary-anthropic-surgical-regen-f3c8d2.md"""


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
        return NOTION_PAGE_ID or None
    rows = data.get("results") or []
    if rows:
        return str(rows[0].get("id") or "") or None
    return NOTION_PAGE_ID or None


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
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1

    page_id = result.page_id or NOTION_PAGE_ID
    if page_id and result.status != "Completed":
        _patch_page(page_id)

    notion_url = f"https://www.notion.so/{page_id.replace('-', '')}" if page_id else ""
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": page_id,
                "notion_url": notion_url,
                "status": "Completed",
                "slug": SLUG,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
