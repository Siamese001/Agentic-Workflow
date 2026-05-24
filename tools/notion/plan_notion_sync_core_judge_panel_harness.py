#!/usr/bin/env python3
"""Register or patch core-judge-panel-harness-f3c8d1 plan in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "core-judge-panel-harness-f3c8d1"
PLAN_PATH = ".cursor/plans/core-judge-panel-harness-f3c8d1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
PLAN_STATUS = "Completed"

SUMMARY = (
    "COMPLETED: Agentic core multi-provider judge panel harness — CanonicalJudgeContract, "
    "JudgePanelRunner, transport parity, score law, gate-closure reconcile. apps_rg GRADE_ONLY "
    "path delegates via x1d_panel_bridge. GOV-JPH + drift gate green."
)

AI_SUMMARY = """- STATUS: Completed (W0–W3)
- Core: agentic_core/runtime/judges/panel/* + ADR-082
- apps_rg: x1d_panel_bridge, adapters/, core_gate_closure_map export
- CI: check_judge_panel_harness_boundary.py; drift invokes panel boundary
- Closeout: artifacts/apps_rg/core_judge_panel_harness_closeout_receipt.md
- Disk: .cursor/plans/core-judge-panel-harness-f3c8d1.md"""


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


def _patch_plan_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": PLAN_STATUS}},
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
            return 200 <= resp.status < 300
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return False


def main() -> int:
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    page_id = _query_page_id()
    if page_id:
        print(f"PLAN_EXISTS: slug={SLUG} page_id={page_id}")
        if _patch_plan_page(page_id):
            print(f"PATCHED: Status={PLAN_STATUS}, Summary refreshed")
            return 0
        print("WARN: patch failed (token or API)", file=sys.stderr)
        return 1

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

    if result.page_id and _patch_plan_page(result.page_id):
        print(f"CREATED+PATCHED: Status={PLAN_STATUS} page_id={result.page_id}")
    else:
        print(f"CREATED: page_id={result.page_id} (patch skipped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
