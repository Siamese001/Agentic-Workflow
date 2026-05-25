#!/usr/bin/env python3
"""Register agent-inventory-deferred-followup-c2a8f1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "agent-inventory-deferred-followup-c2a8f1"
PLAN_PATH = ".cursor/plans/agent-inventory-deferred-followup-c2a8f1.md"
PARENT_SLUG = "agent-inventory-spine-taxonomy-b4e9f2"

SUMMARY = (
    "Not Started: Follow-up to COMPLETED agent-inventory-spine-taxonomy-b4e9f2. "
    "DS-1 integrated R4 live proof; DS-2 HOW class identity (product-gated); "
    "DS-3 misplacement physical moves; DS-4 RootCustoms shim removal. "
    "Maintains ARTIFACT_PROVEN=0 unless approved proof exists."
)

AI_SUMMARY = """- Parent: agent-inventory-spine-taxonomy-b4e9f2 (Completed 2026-05-25)
- Register: docs/reports/cursor/agent_inventory_deferred_scope_register_20260525.md
- DS-1: PYTEST_APPS_RG_INTEGRATED_LIVE / python -m apps_rg whole-run
- DS-2: Decision 1 — invoked_class on HOW (ADR or permanent defer)
- DS-3: SemanticGatekeeper, Bootstrap, PreCommitSovereign, GospelSync moves
- DS-4: Delete RootCustomsAgent thin shim after consumer burndown
- DS-5: A2 taxonomy proof discipline (no mock backfill)
- Disk: .cursor/plans/agent-inventory-deferred-followup-c2a8f1.md"""


def _query_page_id(slug: str) -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    data_source_id = "ac53d31b-3068-4039-9ebe-856c12caab32"
    payload = {"filter": {"property": "Slug", "title": {"equals": slug}}, "page_size": 1}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{data_source_id}/query",
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


def main() -> int:
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: missing {PLAN_PATH}", file=sys.stderr)
        return 1
    existing = _query_page_id(SLUG)
    if existing:
        print(json.dumps({"ok": True, "action": "exists", "page_id": existing, "slug": SLUG}))
        print(f"PLAN_EXISTS: slug={SLUG} notion_page={existing}")
        return 0
    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
        )
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "slug": SLUG}), file=sys.stderr)
        return 1
    if not result.ok:
        print(json.dumps({"ok": False, "error": result.error, "slug": SLUG}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": result.page_id,
                "slug": SLUG,
                "status": result.status,
                "parent": PARENT_SLUG,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} notion_page={result.page_id} path={PLAN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
