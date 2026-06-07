#!/usr/bin/env python3
"""Register or patch c03-skills-graph-exec-summary-f9a2c4 plan in Notion Plans DB (Completed)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "c03-skills-graph-exec-summary-f9a2c4"
PLAN_PATH = ".claude/plans/c03-skills-graph-exec-summary-f9a2c4.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
NOTION_PAGE_ID = "36927693-f55c-81cf-becb-f80666292408"

SUMMARY = (
    "COMPLETED (2026-05-24): C0.3 skills graph executive_summary — DG-1=A pool-wins allowlist, "
    "SQLite C03 attach, GRAPH_TARGETING_CAPSULE (non-proof), brushstroke bindings, native C03 "
    "parity, pre-L2 fail-closed. Brown exec_summary_20260523_215732: X2 PASS, allowlist coherent, "
    "X3_BLOCK (judge). Closeout: docs/reports/apps_rg/c03_exec_summary_enhancement_closeout_receipt.md"
)

AI_SUMMARY = """- STATUS: Completed (W0–W5)
- DG-1: A pool-wins only (no promotion)
- W1: filter_c03_evidence_to_allowed_pool; pre-L2 block; X2 c03_selected_fact_ids subset gate
- W2: attach_sqlite_context; graph_targeting_capsule.json; non-proof PA banner
- W3: bind_facts_to_brushstrokes; brushstroke receipt fields
- W4: enrich_proof_pool_with_native_c03; section_metric_receipt digest fields
- W5: Brown sample exec_summary_20260523_215732 — LIVE_RUNTIME_PROOF; 22 pytest passed
- Deferred follow-up: 2 more Brown runs for ≥2/3 X1D ≥4.0 quality evidence
- Disk SSOT: .claude/plans/c03-skills-graph-exec-summary-f9a2c4.md"""


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
        return NOTION_PAGE_ID
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
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": page_id,
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

    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": result.page_id,
                "status": "Completed",
                "slug": SLUG,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={result.page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
