#!/usr/bin/env python3
"""Mark pa-exec-flowchart-gap-f2a8c3 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "pa-exec-flowchart-gap-f2a8c3"
PLAN_PATH = ".claude/plans/pa-exec-flowchart-gap-f2a8c3.md"
NOTION_PAGE_ID = "36927693-f55c-8138-afb7-fe72202f206a"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-23): apps_rg governed spine U0→L6+PA — one pipeline, no dual-path bypass. "
    "W8 CI: span checklist + spine-convergence gate. Follow-up: section core PA sign, l2_handoff, "
    "one-pipeline E2E 20/20. Audit p0_count=0. Receipt: docs/reports/apps_rg/pa_exec_flowchart_gap_closeout_receipt.md"
)

AI_SUMMARY = """- STATUS: Completed (W0–W8 + W8-followup)
- One pipeline: section_front_spine_bridge → FEC → governed PA/L2/Exit → exhaust → L6 gate
- CI: APPS-RG-SINGLE-SPINE + APPS-RG-SPINE-CONVERGENCE PASS
- Tests: test_apps_rg_one_pipeline_e2e + certification_w8 + no_two_path_w9 (20 passed, harness)
- Audit: artifacts/apps_rg/plans/apps_rg_spine_req_gap_audit.json p0_count=0
- Deferred: full OTEL SDK, C0.3 graph RAG, L6 promotion, live LLM all-lanes
- Disk SSOT: .claude/plans/pa-exec-flowchart-gap-f2a8c3.md"""


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
    page_id = _query_page_id() or NOTION_PAGE_ID
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
                    "ok": True,
                    "action": "created",
                    "page_id": result.page_id,
                    "status": "Completed",
                    "slug": SLUG,
                }
            )
        )
        return 0
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
