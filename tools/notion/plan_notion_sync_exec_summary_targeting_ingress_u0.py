#!/usr/bin/env python3
"""Register or patch exec-summary-targeting-ingress-u0-b8e4f1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-targeting-ingress-u0-b8e4f1"
PLAN_PATH = ".cursor/plans/exec-summary-targeting-ingress-u0-b8e4f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-24): Exec summary targeting ingress — cap/select briefing before U0/proof pool; "
    "lane parity (generation_material_digest == judge_material_digest). Live Brown proof "
    "exec_summary_20260524_233409 parity_match true."
)

AI_SUMMARY = """- PLAN_STATUS: COMPLETED (2026-05-24)
- Problem: judges saw full CLI briefing while L2 got capped compiled text (140149)
- W1–W3: targeting_ingress + section_proof_loader overrides + parity/X3 gates
- W4 live: exec_summary_20260524_233409 parity_match true (2596 chars gen == judge)
- Ingress: 15210 → 11788 chars pre_proof_pool_u0_aligned
- Evidence: U0 graph pool unchanged; briefing/JD non-proof only
- Disk: .cursor/plans/exec-summary-targeting-ingress-u0-b8e4f1.md
- Receipt: docs/reports/apps_rg/exec_summary_targeting_parity_live_proof_20260524_233409_receipt.md"""


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
    if rows:
        return str(rows[0].get("id") or "") or None
    return None


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
    if page_id and _patch_page(page_id):
        notion_url = f"https://www.notion.so/{page_id.replace('-', '')}"
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": page_id,
                    "notion_url": notion_url,
                    "status": "Completed",
                    "slug": SLUG,
                    "plan_path": PLAN_PATH,
                }
            )
        )
        print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
        return 0

    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
            force_status="Completed",
        )
    except PlanCreationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1

    page_id = result.page_id or ""
    notion_url = f"https://www.notion.so/{page_id.replace('-', '')}" if page_id else ""
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": page_id,
                "notion_url": notion_url,
                "status": result.status,
                "slug": SLUG,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
