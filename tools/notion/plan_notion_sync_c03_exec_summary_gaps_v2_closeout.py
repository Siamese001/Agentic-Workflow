#!/usr/bin/env python3
"""Mark c03-exec-summary-gaps-v2-a8f2e1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "c03-exec-summary-gaps-v2-a8f2e1"
PLAN_PATH = ".claude/plans/c03-exec-summary-gaps-v2-a8f2e1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
NOTION_PAGE_ID = "36c27693-f55c-813b-87b8-f231ed2b6cf8"

SUMMARY = (
    "COMPLETED (2026-05-26): C03 exec-summary gap closeout v2 W0–W5 — vocabulary, utilization, "
    "digest/support_target SSOT, promotion candidates, hop-path parity, Brown REAL_LLM graph proof "
    "(exec_summary_20260526_222159). Judge quality deferred (GAP-6)."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETE (2026-05-26)
- W0–W4: vocabulary, utilization, digest, promotion, hop paths — DONE
- W5: 31+ pytest C03 slice; Brown exit 0; graph verifier PASS
- Live: exec_summary_20260526_222159 (C03 artifacts on disk)
- Closeout: docs/reports/apps_rg/c03_exec_summary_gaps_v2_closeout_20260526.md
- Deferred: X1D ≥4.0 judge floor (out of plan scope per GAP-6)"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return NOTION_PAGE_ID
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
        return NOTION_PAGE_ID
    rows = data.get("results") or []
    if rows:
        return str(rows[0].get("id") or "") or NOTION_PAGE_ID
    return NOTION_PAGE_ID


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
            return 200 <= getattr(resp, "status", 200) < 300
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return False


def main() -> int:
    page_id = _query_page_id()
    if page_id and _patch_page(page_id):
        print(f"patched notion page {page_id}")
        return 0
    try:
        row = create_plan_in_notion(
            slug=SLUG,
            plan_path=PLAN_PATH,
            summary=SUMMARY,
            status="Completed",
        )
        print(f"created notion row {row}")
        return 0
    except PlanCreationError as exc:
        print(f"notion sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
