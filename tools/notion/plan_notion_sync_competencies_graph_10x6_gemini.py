#!/usr/bin/env python3
"""Register competencies-graph-10x6-gemini-924516 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "competencies-graph-10x6-gemini-924516"
PLAN_PATH = ".cursor/plans/competencies-graph-10x6-gemini-924516.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Competencies lane — graph-grounded 10→6 category selection (not base résumé "
    "facts.skills), colon+keyword format, single X1D judge gemini_pro (employment-bullet pool model)."
)

AI_SUMMARY = """- Gap: current 4-path Qwen pool, 6–8 categories, 3-judge panel
- W0: Baseline gap receipt (docs/reports/apps_rg/competencies_10x6_gemini_gap_receipt.md)
- W1: Prompt/PA SSOT — graph VERIFIED_SKILL_INVENTORY_PROJECTION only; remove BASE RESUME PARITY
- W2: COMPETENCIES_SC_PATH_COUNT=10 → top 6 with graph reality + min score
- W3: Single gemini_pro X1D (competencies_pool_x1d_judge_rows); default --x1d-judges gemini_pro
- W4: Contract tests + mock-judges smoke
- Disk: .cursor/plans/competencies-graph-10x6-gemini-924516.md
- Authority: augmented_skills_graph (P2-W1A) unchanged"""


def _query_page_id(slug: str) -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {"filter": {"property": "Slug", "title": {"equals": slug}}, "page_size": 1}
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
    existing = _query_page_id(SLUG)
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
                "status": result.status,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} notion_page={result.page_id} path={PLAN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
