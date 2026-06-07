#!/usr/bin/env python3
"""Mark apps-rg-env-kill-switch-cleanup-f8e2a3 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-env-kill-switch-cleanup-f8e2a3"
PLAN_PATH = ".claude/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md"
PARENT_SLUG = "apps-rg-runtime-substitute-burndown-c4e8f1"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-22): Remove APPS_RG_SPINE_CHROMA_ENRICH + spine merge; positive "
    "c02_vector_query truth fields; FEC mandatory on product; forbidden env fail-closed. "
    "W4 LIVE_RUNTIME_PROOF: env_kill_switch_w4_validate_20260522 (hybrid PASS, X3_BLOCK quality). "
    "Receipt: docs/reports/apps_rg/apps_rg_env_kill_switch_cleanup_closeout_receipt.md"
)

AI_SUMMARY = """- STATUS: Completed (W0–W4)
- W1: deleted spine enrich env + merge_canonical_c0
- W2: c02_hybrid_receipt_truth; no spine_chroma_enrich_disabled
- W3: product_runtime_guards + FEC mandatory + apps_rg_runtime_proof.md
- W4: LIVE hybrid — product_hybrid_attempted=true, bm25_available=true
- pytest: 64 passed (env kill-switch bundle)
- NOT CLAIMED: RELEASE_ELIGIBLE (X3_BLOCK on quality)
- Artifact: artifacts/.../env_kill_switch_w4_validate_20260522
- Parent: apps-rg-runtime-substitute-burndown-c4e8f1"""


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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def main() -> int:
    page_id = _query_page_id()
    if page_id:
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
        print(json.dumps({"ok": False, "error": "patch_failed"}), file=sys.stderr)
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
                    "ok": True,
                    "action": "created",
                    "page_id": result.page_id,
                    "status": "Completed",
                    "slug": SLUG,
                }
            )
        )
        return 0 if result.ok else 1
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
