#!/usr/bin/env python3
"""Patch core-same-authority-incremental-regen-e7a4b1 to Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

SLUG = "core-same-authority-incremental-regen-e7a4b1"
PLAN_PATH = ".cursor/plans/core-same-authority-incremental-regen-e7a4b1.md"
PAGE_ID = "36b27693-f55c-81d2-a344-fded674227f6"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-25): Same-authority incremental regen chassis (L2 E4 Heal). "
    "W0–W3: ADR-085, core runner/receipt, apps_rg delegation, Brown live proof "
    "exec_summary_20260525_122058. W4 orchestrator DEFERRED (PD-8)."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETED (2026-05-25)
- Closeout: docs/reports/cursor/core_same_authority_regen_plan_closeout_20260525.md
- Brown: docs/reports/apps_rg/core_same_authority_regen_brown_20260525_122058_receipt.md
- W4: DEFERRED — JudgeDirectedRegenOrchestrator blocked per plan
- Proof: 33 pytest + boundary CI + compileall exit 0"""


def _patch_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        print(json.dumps({"ok": False, "error": "no_notion_token"}))
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
        print(json.dumps({"ok": True, "page_id": page_id, "slug": SLUG, "status": "Completed"}))
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    if not _patch_page(PAGE_ID):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
