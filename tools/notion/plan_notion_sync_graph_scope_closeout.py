#!/usr/bin/env python3
"""Sync phase2 graph-scope closeout to Notion Plans DB (query + patch or create)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "phase2-gtm-presales-remaining-f7a2c9"
PLAN_PATH = ".claude/plans/phase2-gtm-presales-remaining-f7a2c9.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Phase 2 GTM/pre-sales + senior-role skills graph: GRAPH_SCOPE_COMPLETE (2026-05-20). "
    "Taxonomy, pillars/skills/bridges, 7 fixtures, W14/W14b traversal, W4/W14 section projection 49/49. "
    "Non-graph: W1 HITL, W4 runtime, W2a/2b/3/5/6/7."
)

AI_SUMMARY = """- GRAPH_SCOPE_STATUS: GRAPH_SCOPE_COMPLETE
- Waves done: W0, W0.5, W0.5b, W8-W11, W12, W13, W14, W14b, W4/W14 projection
- Graph: 29 pillars, 162 skills, 16 bridge edges; augmented_skills_graph authority
- W14b: 7/7 traversal without weight_override
- Section projection: 49/49 PASS (offline)
- Deferred: brokerage pillar (no evidence — do not fabricate)
- Next: W1 HITL packet or python -m apps_rg --section <lane> runtime proof
- Receipt: docs/reports/apps_rg/phase2_graph_scope_closeout_receipt.json"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {
            "property": "Slug",
            "title": {"equals": SLUG},
        },
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
    results = data.get("results") or []
    if not results:
        return None
    return str(results[0].get("id") or "")


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
            "Plan File Path": {
                "rich_text": [{"text": {"content": PLAN_PATH}}],
            },
            "Summary": {
                "rich_text": [{"text": {"content": SUMMARY[:2000]}}],
            },
            "AI Summary ": {
                "rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}],
            },
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    page_id = _query_page_id()
    if page_id:
        if _patch_page(page_id):
            print(json.dumps({"ok": True, "action": "patched", "page_id": page_id, "status": "Completed"}))
            return 0
        print(json.dumps({"ok": False, "error": "patch_failed", "page_id": page_id}), file=sys.stderr)
        return 1
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
                    "ok": result.ok,
                    "action": "created",
                    "page_id": result.page_id,
                    "status": result.status,
                }
            )
        )
        return 0 if result.ok else 1
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
