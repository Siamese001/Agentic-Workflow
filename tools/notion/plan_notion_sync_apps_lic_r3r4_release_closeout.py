#!/usr/bin/env python3
"""Sync apps_lic spine convergence + R3R4 release blocker closeout to Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-lic-spine-product-convergence-b7e4a2"
PLAN_PATH = ".cursor/plans/apps-lic-spine-product-convergence-b7e4a2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "apps_lic spine product convergence (AG-8): canonical_dispatch CLI, bindings migration, "
    "R3R4 live AppsResearchBridge, release eligibility RELEASE_ELIGIBLE (2026-05-20). "
    "No mock research on proof path; fail-closed R3R4 on empty briefing."
)

AI_SUMMARY = """- STATUS: Completed (2026-05-20)
- OVERALL: RELEASE_ELIGIBLE (R4 + live R3R4 BriefingReady)
- Waves W0-W5: spine convergence DONE
- Release waves R-W1/R-W2/R-W3: EvidenceShaper, fail-closed, live proof DONE
- Proof run: artifacts/apps_lic/spine_convergence/runs/release_eligibility_r3r4_live_20260520_final
- Receipts: docs/reports/apps_lic/release_eligibility_verification_receipt.md
- Scope frozen: no GovernedLic, no mock bridge, no YAML L2 resurrection
- WAVE_COMPLETE: plan=apps-lic-spine-product-convergence-b7e4a2 waves=R-W1,R-W2,R-W3,W0-W5
- PLAN_COMPLETE: plan=apps-lic-spine-product-convergence-b7e4a2"""


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
    results = data.get("results") or []
    if not results:
        return None
    return str(results[0].get("id") or "")


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
            "Plan File Path": {
                "rich_text": [{"text": {"content": PLAN_PATH}}],
            },
            "Summary": {
                "rich_text": [{"text": {"content": SUMMARY[:2000]}}],
            },
            "AI Summary ": {
                "rich_text": [{"text": {"content": AI_SUMMARY[:2000]}}],
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
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "action": "created",
                    "page_id": result.page_id,
                    "status": result.status,
                    "slug": SLUG,
                }
            )
        )
        return 0 if result.ok else 1
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
