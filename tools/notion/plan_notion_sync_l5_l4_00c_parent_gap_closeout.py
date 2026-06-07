#!/usr/bin/env python3
"""Mark l5-l4-00c-parent-gap-b8e4f2 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "l5-l4-00c-parent-gap-b8e4f2"
PLAN_PATH = ".claude/plans/l5-l4-00c-parent-gap-b8e4f2.md"
NOTION_PAGE_ID = "36927693-f55c-81c1-9831-c33eea84babd"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-23): W1–W5 closed gaps vs 00A/00B/00C parent REQ-ID packs. "
    "00C.7 SSOT (ADR); L5 bind+HITL on integrated safe-reuse; UWG l5 ref threading; "
    "CI validator aliases; proof JSON regen; edge-case tests. "
    "Evidence: docs/reports/plans/l5-l4-00c-parent-gap-evidence-b8e4f2.md"
)

AI_SUMMARY = """- STATUS: Completed (W1–W5 + edge hardening)
- 00C: 00C.7 SSOT; parent §5 export profile; G21–G24 doc reconcile; 21/21 MET
- 00A: runtime_certification_binding + l5_hitl_reclearance; CI cross-child + no-write
- 00B: UWG receipt l5_certification_ref; sole-admission + receipt CI aliases
- Proof: l4_uwg_runtime_proof.json + runtime_gates_runtime_proof.json PASS
- Tests: integrated L5 + export + exhaust + UWG edge suites (53+ passed)
- Disk SSOT: .claude/plans/l5-l4-00c-parent-gap-b8e4f2.md"""


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
    page_id = _query_page_id() or NOTION_PAGE_ID
    if _patch_page(page_id):
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": page_id,
                    "status": "Completed",
                    "slug": SLUG,
                }
            )
        )
        return 0
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
                    "ok": True,
                    "action": "created",
                    "page_id": result.page_id,
                    "status": "Completed",
                    "slug": SLUG,
                }
            )
        )
        return 0
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
