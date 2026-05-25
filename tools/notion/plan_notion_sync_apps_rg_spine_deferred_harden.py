#!/usr/bin/env python3
"""Create or sync apps-rg-spine-deferred-harden-c8f1a2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-spine-deferred-harden-c8f1a2"
PLAN_PATH = ".cursor/plans/apps-rg-spine-deferred-harden-c8f1a2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-23): apps_rg spine deferred harden W1–W7 — span coverage U0-L6, OTEL dual-write, "
    "c0_graph_lane + l6_eval receipts, live smoke BLOCKED/dry-run, 42/42 harness pytest. "
    "Receipt: docs/reports/apps_rg/apps_rg_spine_deferred_harden_closeout_receipt.md"
)

AI_SUMMARY = """- STATUS: Completed (W1–W7 + edge-harden)
- Parent: pa-exec-flowchart-gap-f2a8c3 (COMPLETED)
- Proof: test_apps_rg_spine_harden_edge_cases (29) + test_apps_rg_spine_waves_w4_w7 (9) + one_pipeline_e2e (4)
- CI: APPS-RG-SPINE-CONVERGENCE + SPAN-EMIT-SITES PASS
- Deferred (honest): core C0.3 Graph RAG, L6 promotion gauntlet, live all-lanes provider
- Disk SSOT: .cursor/plans/apps-rg-spine-deferred-harden-c8f1a2.md"""


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


def _patch_page(page_id: str, *, status: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": status}},
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--completed", action="store_true", help="Mark plan Completed in Notion")
    args = parser.parse_args()
    status = "Completed" if args.completed else "Not Started"

    page_id = _query_page_id()
    if page_id:
        ok = _patch_page(page_id, status=status)
        print(json.dumps({"ok": ok, "action": "patched", "page_id": page_id, "slug": SLUG}))
        return 0 if ok else 1
    try:
        result = create_plan_in_notion(slug=SLUG, summary=SUMMARY, ai_summary=AI_SUMMARY)
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
