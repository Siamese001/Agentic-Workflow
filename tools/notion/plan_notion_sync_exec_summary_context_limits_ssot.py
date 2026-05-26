#!/usr/bin/env python3
"""Register or patch exec-summary-context-limits-ssot-b7e4a1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-context-limits-ssot-b7e4a1"
PLAN_PATH = ".cursor/plans/exec-summary-context-limits-ssot-b7e4a1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-26): Exec-summary 24k context limits SSOT in "
    "executive_summary_context_limits.py; live Brown X3_ALLOW exec_summary_20260526_203341."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETE (2026-05-26)
- SSOT: apps_rg/runtime/sections/executive_summary_context_limits.py
- Unit: 38 pytest PASS
- E2E: docs/reports/apps_rg/exec_summary_context_limits_ssot_e2e_20260526.md
- Live: exec_summary_20260526_203341 token_budget 24576 dispatch_allowed true X3_ALLOW
- Closeout: docs/reports/apps_rg/executive_summary_context_limits_ssot_closeout_20260526.md"""


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
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1
    page_id = _query_page_id()
    if page_id:
        ok = _patch_page(page_id)
        print(
            json.dumps(
                {"ok": ok, "action": "patched" if ok else "patch_failed", "page_id": page_id, "slug": SLUG},
                indent=2,
            )
        )
        if ok:
            print(f"PLAN_COMPLETED: slug={SLUG} notion_page={page_id}")
        return 0 if ok else 1
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
    ok = _patch_page(page_id) if page_id else False
    print(json.dumps({"ok": ok, "action": "created_and_patched", "page_id": page_id, "slug": SLUG}, indent=2))
    print(f"PLAN_CREATED: slug={SLUG} notion_page={page_id} path={PLAN_PATH}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
