#!/usr/bin/env python3
"""Mark complete-open-scope-closeout-c9e4a1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402

PLAN_PAGE_ID = "36d27693-f55c-81e6-b0a7-ed964b7af164"
PLAN_PATH = ".cursor/plans/complete-open-scope-closeout-c9e4a1.md"
SLUG = "complete-open-scope-closeout-c9e4a1"
SUMMARY = (
    "COMPLETED (2026-05-27): Notion f8a3c2 Completed; b7e4f2 Retired; "
    "G2+C0 defects captured as backlog; implementation plan a4f8e2 spawned."
)
AI_SUMMARY = """- PLAN_STATUS: COMPLETE
- W1: f8a3c2 Notion Completed; b7e4f2 Retired
- W2: backlog G2 stuck-loop + C0 claim/proof split
- W3: docs/reports/cursor/complete_open_scope_closeout_20260526.md
- Follow-on: exec-summary-regen-stuck-c0-split-a4f8e2 (DONE)"""


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN required", file=sys.stderr)
        return 1
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
        f"https://api.notion.com/v1/pages/{PLAN_PAGE_ID}",
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
        print(f"FAIL: {exc.read().decode('utf-8', errors='replace')[:500]}", file=sys.stderr)
        return 1
    print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={PLAN_PAGE_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
