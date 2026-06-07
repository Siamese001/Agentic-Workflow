#!/usr/bin/env python3
"""Patch exec-summary-qwen-regen-token-budget-c4e8a1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-qwen-regen-token-budget-c4e8a1"
PLAN_PATH = ".claude/plans/exec-summary-qwen-regen-token-budget-c4e8a1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-26): apps_rg exec-summary regen token budget — budgeted_qwen_regen_call SSOT, "
    "fail-closed pre-dispatch, call_id artifacts, 85% first-pass, context provenance, operator guide. "
    "D3 Brown budget soak deferred (unit/contract proof PASS)."
)

AI_SUMMARY = """- PLAN_STATUS: Completed (W1–W4)
- W1: budgeted_qwen_regen_call + regen_token_budget_receipt + executive_summary_qwen_call_plan.json
- W2: provider_context_window_source + TOKEN_BUDGET_EXCEEDED_FIRST_PASS_85PCT
- W3: executive_summary_operator_guide.md (budget soak vs judge-cert)
- W4: APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS → IncrementalRepairContract
- Proof: pytest unit + _apps_contract; D3 Brown REAL_LLM soak deferred
- Research: docs/reports/apps_rg/executive_summary_qwen_regen_token_budget_research_20260525.md
- touches_agentic_core: false"""


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
        print(f"PLAN_NOTION_COMPLETE: slug={SLUG} notion_page={page_id}")
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
    page_id = result.page_id or ""
    print(json.dumps({"ok": True, "action": "created", "page_id": page_id, "slug": SLUG}))
    print(f"PLAN_NOTION_COMPLETE: slug={SLUG} notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
