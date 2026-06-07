#!/usr/bin/env python3
"""Register governance-dedup-closeout-e8a4c2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "governance-dedup-closeout-e8a4c2"
PLAN_PATH = ".claude/plans/governance-dedup-closeout-e8a4c2.md"
PARENT_SLUG = "cursor-governance-two-tier-b4e8f2"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Close governance dedup deferred scope from 2026-05-26 audit — "
    "retire obsolete post_agent hooks (7-day shadow), fix check_cursor_native_config, "
    "archive plan sprawl to ≤20 active, Windsurf always_on demotion map, closeout receipt."
)

AI_SUMMARY = """- Parent: cursor-governance-two-tier-b4e8f2 (Completed)
- Source: docs/reports/cursor/governance_dedup_audit_20260526.md
- W0: Hook matrix refresh + dispatch shadow metrics
- W1: Archive obsolete_candidate scripts; legacy AG hook
- W2: Native config allowlist + RULES_INDEX --check drift fix
- W3: Plan sprawl archive (86 → ≤20)
- W4: Windsurf always_on demotion map (Option A remainder)
- W5: governance_dedup_closeout_receipt.json + Notion Completed
- Disk: .claude/plans/governance-dedup-closeout-e8a4c2.md"""


def _query_page_id(slug: str) -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {"filter": {"property": "Slug", "title": {"equals": slug}}, "page_size": 1}
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
