#!/usr/bin/env python3
"""W4 closeout: mark competencies-graph-10x6-gemini-924516 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402

SLUG = "competencies-graph-10x6-gemini-924516"
PLAN_PATH = ".cursor/plans/competencies-graph-10x6-gemini-924516.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
GAP_RECEIPT = "docs/reports/apps_rg/competencies_10x6_gemini_gap_receipt.md"
W4_RECEIPT = "docs/reports/apps_rg/competencies_10x6_w4_closeout_receipt.md"

SUMMARY = (
    "COMPLETED (2026-05-27): Competencies graph_10x6 — 10 Qwen SC paths, top-6 graph-grounded "
    "categories, single gemini_pro X1D pool judge; taxonomy trim 7→6 emit."
)
AI_SUMMARY = """- PLAN_STATUS: COMPLETE (2026-05-27)
- W0–W4: graph proof authority + prompt SSOT + pool merge + gemini_pro judge
- DoD: test_competencies_10x6_pool.py + target contract (53 pytest)
- Closeout: docs/reports/apps_rg/competencies_10x6_w4_closeout_receipt.md
- Gap closed: docs/reports/apps_rg/competencies_10x6_gemini_gap_receipt.md
- Deferred: Brown all-lanes REAL_LLM (DS-10 register)"""


def _query_page_id(slug: str, token: str) -> str | None:
    payload = {"filter": {"property": "Slug", "title": {"equals": slug}}, "page_size": 1}
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query",
        data=json.dumps(payload).encode("utf-8"),
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL query: {exc}", file=sys.stderr)
        return None
    rows = data.get("results") or []
    return str(rows[0].get("id") or "") if rows else None


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN required", file=sys.stderr)
        return 1
    page_id = _query_page_id(SLUG, token)
    if not page_id:
        from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

        try:
            result = create_plan_in_notion(
                slug=SLUG,
                summary=SUMMARY,
                ai_summary=AI_SUMMARY,
                plan_file_path=PLAN_PATH,
                force_status="Completed",
            )
        except PlanCreationError as exc:
            print(f"FAIL create: {exc}", file=sys.stderr)
            return 1
        if not result.ok:
            print(f"FAIL create: {result.error}", file=sys.stderr)
            return 1
        page_id = result.page_id or ""
        print(f"PLAN_CREATED_COMPLETED: slug={SLUG} notion_page={page_id}")
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:2000]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}]},
        }
    }
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}",
        data=json.dumps(payload).encode("utf-8"),
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        print(f"FAIL patch: {exc.read().decode('utf-8', errors='replace')[:500]}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "slug": SLUG,
                "page_id": page_id,
                "status": "Completed",
                "plan_path": PLAN_PATH,
                "gap_receipt": GAP_RECEIPT,
                "w4_receipt": W4_RECEIPT,
            }
        )
    )
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
