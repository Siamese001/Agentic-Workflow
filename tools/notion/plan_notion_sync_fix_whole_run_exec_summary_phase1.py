#!/usr/bin/env python3
"""Sync fix-whole-run-executive-summary-phase1-no-run-dir closeout to Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2"
PLAN_PATH = ".cursor/plans/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Fix canonical whole-run executive_summary PHASE1_NO_RUN_DIR: align modular_r4/sections "
    "run_dir pointers with section-mode materialization; briefing inline threading; pre-run "
    "failure surfacing; native C0.3 unchanged."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETED (2026-05-20)
- ROOT_CAUSE: dispatch ok + missing_pointer under modular_r4/sections/executive_summary (cli_c61c8be7fc9c)
- WAVES W1-W5: investigate, forensics, fix+W8C tests, runtime proof matrix, closeout
- SCOPE: executive_summary whole-run only; no C0.3 schema change; no shadow runner restore
- RECEIPT: docs/reports/apps_rg/fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md
- NON-CLAIM: product/Fort Knox/L7 PASS without integrated_product_proof_gate PASS"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {"property": "Slug", "title": {"equals": SLUG}},
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
    rows = data.get("results") or []
    if not rows:
        return None
    return str(rows[0].get("id") or "") or None


def _patch_completed(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"status": {"name": "Completed"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {
                "rich_text": [{"text": {"content": PLAN_PATH}}],
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
            resp.read()
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return False


def main() -> int:
    page_id = _query_page_id()
    if page_id:
        if _patch_completed(page_id):
            print(json.dumps({"ok": True, "action": "patched", "page_id": page_id, "slug": SLUG}))
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
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": result.ok,
                "action": "created",
                "page_id": result.page_id,
                "slug": SLUG,
                "status": result.status,
            }
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
