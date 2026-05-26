#!/usr/bin/env python3
"""Register graph-skills-deferred-followup-d7f2a8 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "graph-skills-deferred-followup-d7f2a8"
PLAN_PATH = ".cursor/plans/graph-skills-deferred-followup-d7f2a8.md"
PARENT_SLUG = "graph-skills-quality-enhancement-c4e8a1"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Follow-up to COMPLETED graph-skills-quality-enhancement-c4e8a1. "
    "Burndown PARTIAL closeout — D16 REAL_LLM spine proof, LIVE_X3 7/7, utilization REAL_LLM, "
    "CI GHA URLs, lane X2 remediations. W10-AG contract bind shipped on main."
)

AI_SUMMARY = """- Parent: graph-skills-quality-enhancement-c4e8a1 (Completed 2026-05-26)
- Register: docs/reports/apps_rg/graph_skills_deferred_scope_register_20260526.md
- W10-AG on main: c0_graph_adapter + LIVE route_profiles + maybe_run_graph_rag (contract PASS)
- DS-1: D16 REAL_LLM c0_graph_lane_receipt (exec_summary pilot)
- DS-2–10: 7/7 LIVE_X3, lane X2 fixes, artifact checklists
- DS-7: CI GHA ratchet URLs (D10/D13)
- DS-12: claims_release_eligible only after W5
- Disk: .cursor/plans/graph-skills-deferred-followup-d7f2a8.md"""


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
                "parent": PARENT_SLUG,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} notion_page={result.page_id} path={PLAN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
