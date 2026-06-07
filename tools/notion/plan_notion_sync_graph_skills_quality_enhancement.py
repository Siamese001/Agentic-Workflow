#!/usr/bin/env python3
"""Register graph-skills-quality-enhancement-c4e8a1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "graph-skills-quality-enhancement-c4e8a1"
PLAN_PATH = ".claude/plans/graph-skills-quality-enhancement-c4e8a1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started (hardened v2): MAXIMIZE augmented_skills_graph — W0–W10: JD subgraph, skill capsules "
    "all 7 lanes, graph v2, quality port, spine, hybrid boost, CI ratchet, utilization KPIs, 7/7 X3."
)

AI_SUMMARY = """- Plan: graph-skills-quality-enhancement-c4e8a1 (hardened 2026-05-26)
- W0–W10 maximize graph skills; DoD D1–D15; target 7/7 X3_ALLOW
- See plan file for wave detail; patch via plan_notion_sync_graph_skills_quality_enhancement_patch.py"""


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
    print(json.dumps({"ok": True, "action": "created", "page_id": page_id, "slug": SLUG}))
    print(f"PLAN_CREATED: slug={SLUG} notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
