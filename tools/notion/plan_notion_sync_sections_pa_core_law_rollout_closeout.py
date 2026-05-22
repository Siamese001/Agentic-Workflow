#!/usr/bin/env python3
"""Mark sections-pa-core-law-rollout-c3a8f1 Completed in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "sections-pa-core-law-rollout-c3a8f1"
PLAN_PATH = ".cursor/plans/sections-pa-core-law-rollout-c3a8f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-22): PA core-law rollout for headline, competencies, Unify/IBM — "
    "pa_core_law_v1 refs, PRODUCT_SHAPE-only X2, drift ratchets (63 pytest), Brown REAL_LLM smoke. "
    "Receipt: docs/reports/apps_rg/sections_pa_core_law_rollout_closeout_receipt.md"
)

AI_SUMMARY = """- STATUS: Completed (W0–W6)
- W0: baseline fingerprints — sections_pa_core_law_rollout_w0_baseline.md
- W1: pa_core_law_v1 + w7 shell + section markers
- W2: headline_tailor_v1 slim (~66% static YAML)
- W3: competency_selector_v2.pa_slots slim
- W4: Unify/IBM _legacy_i0 + YAML oath trim
- W5: 63 pytest PASS — sections_pa_core_law_w5_pytest_gate.py
- W6: Brown smoke — 4/6 REAL_LLM; all lanes PRODUCT_SHAPE×1 + pa_core_law compile proof
- GAP-1: headline token budget EXEMPT (documented)
- GAP-3: X3_BLOCK + REAL_LLM acceptable for PA dedup DoD
- Operational follow-on (out of plan): narrative REAL_LLM after ACCEPTED_FINALIZED bullet companions in whole-run order
- Predecessor: exec-summary-pa-core-law-dedup-f8e2a1 (complete)"""


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
            print(json.dumps({"ok": True, "action": "patched", "page_id": page_id, "status": "Completed"}))
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
        print(json.dumps({"ok": True, "action": "created", "page_id": result.page_id, "status": "Completed"}))
        return 0 if result.ok else 1
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
