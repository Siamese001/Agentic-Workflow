#!/usr/bin/env python3
"""Set graph-skills-deferred-followup-d7f2a8 to In Progress in Notion."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
SLUG = "graph-skills-deferred-followup-d7f2a8"
PAGE_ID = "36c27693-f55c-8131-a2c2-f2ad66da13b4"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "In Progress: W0–W1 DONE (closeout refresh, spine C0.3 authority DS-11 contract). "
    "W2 7/7 LIVE_X3 burndown open. W4 BLOCKED without gh locally."
)

AI_SUMMARY = """- W0 PASS: graph_skills_deferred_followup_w0_receipt.json
- W1 PASS (contract): spine_c03_authority, c0_graph_lane unified claims
- W2 PARTIAL: 2/7 LIVE_X3 until Brown reruns
- Parent: graph-skills-quality-enhancement-c4e8a1 Completed"""


def _patch(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "In Progress"}},
            "Exists On Disk": {"checkbox": True},
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    if _patch(PAGE_ID):
        print(f"PLAN_IN_PROGRESS: slug={SLUG} notion_page={PAGE_ID}")
        return 0
    print("FAIL: Notion patch", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
