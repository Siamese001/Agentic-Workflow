#!/usr/bin/env python3
"""Mark unify-bullets-graph-compose-prompt-a3f7e2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "unify-bullets-graph-compose-prompt-a3f7e2"
PLAN_PATH = ".cursor/plans/unify-bullets-graph-compose-prompt-a3f7e2.md"
PAGE_ID = "36c27693-f55c-8122-9714-fd02e06b923c"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-26): W1 unify_bullets graph-compose Qwen prompts — "
    "GRAPH_BULLET_EVIDENCE_PACK C0, compose I0/U0, PATH_FRAMING per SC path, pytest guards. "
    "W2 LIVE REAL_LLM deferred to graph-skills-deferred-followup-d7f2a8."
)

AI_SUMMARY = """- PLAN_STATUS: Completed (disk + Notion 2026-05-26)
- W1 DONE: unify_bullets_graph_evidence.py, unify_bullets_pa.py, unify_bullet_tailor_v1.yaml
- W2 DEFERRED: LIVE unify_bullets path diversity → graph-skills-deferred-followup-d7f2a8
- DoD D1–D5: compile guards + test_unify_bullets_graph_compose_prompt.py PASS"""


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
