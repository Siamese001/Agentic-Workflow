#!/usr/bin/env python3
"""Register exec-summary-qwen-regen-token-budget-c4e8a1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-qwen-regen-token-budget-c4e8a1"
PLAN_PATH = ".claude/plans/exec-summary-qwen-regen-token-budget-c4e8a1.md"
RESEARCH_PATH = "docs/reports/apps_rg/executive_summary_qwen_regen_token_budget_research_20260525.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Regen/retry Qwen token budget for apps_rg executive_summary — "
    "per-call context guards, tiered max_tokens (scratch 2048 / regen 1024), "
    "judge thread cap, qwen_call_plan artifact. Builds on completed first-call trim (a8f3c2)."
)

AI_SUMMARY = """- Plan: exec-summary-qwen-regen-token-budget-c4e8a1
- Research: docs/reports/apps_rg/executive_summary_qwen_regen_token_budget_research_20260525.md
- P0 gaps: G1 no regen input budget; G2 judge thread stack; G3 regen uses 2048 output
- W1: estimate_regen_thread_tokens + fail-closed guard + APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS=1024
- W2: VLLM_MAX_MODEL_LEN SSOT + 85% first-pass headroom
- W3: executive_summary_qwen_call_plan.json + operator guide env table
- W4: optional APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS (512–768)
- Proof: Brown 3-cycle judge regen + unit tests; parity required for judge regen
- Related DONE: exec-summary-token-budget-a8f3c2 (first-call optional trim)"""


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


def main() -> int:
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: missing {PLAN_PATH}", file=sys.stderr)
        return 1
    existing = _query_page_id()
    if existing:
        print(json.dumps({"ok": True, "action": "exists", "page_id": existing, "slug": SLUG}))
        print(f"PLAN_EXISTS: slug={SLUG} notion_page={existing}")
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
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": page_id,
                "slug": SLUG,
                "plan_path": PLAN_PATH,
                "research_path": RESEARCH_PATH,
            },
            indent=2,
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Not Started notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
