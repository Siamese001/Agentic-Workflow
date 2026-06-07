#!/usr/bin/env python3
"""Register core-same-authority-incremental-regen-e7a4b1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "core-same-authority-incremental-regen-e7a4b1"
PLAN_PATH = ".claude/plans/core-same-authority-incremental-regen-e7a4b1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Core same-authority incremental regen chassis for vLLM/Qwen. "
    "Frozen compile + REGEN_DELTA turn (not H0 repair essay). "
    "Depends: core-judge-panel-harness DONE. W0–W4: contracts → thread → runner → apps_rg delegate."
)

AI_SUMMARY = """- Plan type: platform_core_change (touches agentic_core)
- North star: PROMPT_LOCK + ANCHOR_DRAFT + JUDGE_DELTA as pipeline DNA
- Problem: apps_rg prescriptive delta works; core has panel + HealReceipt but no generic regen thread
- Anti-pattern forbidden: rubric/X2/X3 in core
- Related DONE: core-judge-panel-harness-f3c8d1, exec-summary-x1d-transport-parity-d8f2a1
- W0: ADR + Author-Gate + boundary receipt
- W1: PromptMessages.append_same_authority_turn + vLLM messages[]
- W2: SameAuthorityRegenRunner + RemediationDeltaMapper protocol
- W3: apps_rg executive_summary_judge_remediation delegates to core
- W4: Optional JudgeDirectedRegenOrchestrator + CI
- Disk: .claude/plans/core-same-authority-incremental-regen-e7a4b1.md"""


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
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": result.page_id,
                "slug": SLUG,
                "url": f"https://www.notion.so/{SLUG.replace('-', '')}-{result.page_id.replace('-', '')}",
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} notion_page={result.page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
