#!/usr/bin/env python3
"""Mark graph-skills-quality-enhancement-c4e8a1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "graph-skills-quality-enhancement-c4e8a1"
PLAN_PATH = ".claude/plans/graph-skills-quality-enhancement-c4e8a1.md"
PAGE_ID = "36b27693-f55c-81c0-bb50-d8df6df2b60e"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-26): W0–W10-AG graph-skills quality — authority, capsules, v2, FEC/hybrid, "
    "CI ratchet, utilization, operator guide, W10-AG unified C0.3 bind (e27875b14e). "
    "Closeout PARTIAL (LIVE_X3 2/7). Proof burndown: graph-skills-deferred-followup-d7f2a8."
)

AI_SUMMARY = """- PLAN_STATUS: Completed (disk + Notion 2026-05-26)
- Waves W0–W10-AG DONE; W10-AG contract PASS (c0_graph_adapter, LIVE route_profiles)
- Follow-on: graph-skills-deferred-followup-d7f2a8 (D16 REAL_LLM, 7/7 LIVE_X3, CI GHA)
- Closeout: docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json
- W10-AG: docs/reports/apps_rg/graph_skills_c03_unified_pipeline_bind.json
- claims_release_eligible=false; release proof in follow-on plan"""


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
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: missing {PLAN_PATH}", file=sys.stderr)
        return 1
    page_id = _query_page_id() or PAGE_ID
    if _patch_page(page_id):
        print(json.dumps({"ok": True, "action": "completed", "page_id": page_id, "slug": SLUG}))
        print(f"PLAN_COMPLETED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
        return 0
    print("FAIL: Notion patch failed (check NOTION_TOKEN)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
