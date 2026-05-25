#!/usr/bin/env python3
"""Register agent-inventory-spine-taxonomy-b4e9f2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "agent-inventory-spine-taxonomy-b4e9f2"
PLAN_PATH = ".cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Close the gap between function-based product spine truth and "
    "118 *Agent inventory candidates. E2E artifact-proven spine invocation = 0. "
    "W0 canon/ADR; W1 taxonomy inventory_role + 56 off-spine registrations; "
    "W2 shim archive; W3 live proof DEFERRED."
)

AI_SUMMARY = """- Evidence: agentic_core_agent_inventory_runtime_assessment.md (PARTIAL, 2026-05-25)
- Decision 1: Function/stage spine; taxonomy ≠ runtime graph unless receipt proves invocation
- Decision 2: Four orthogonal taxonomy axes (agenthood, inventory_role, product_spine_invocation_status, runtime_proof_class)
- W1: Inventory-only gap fill (~56 rows); defaults NOT_ARTIFACT_PROVEN + NONE; registration ≠ spine participation
- A2: No taxonomy row may imply E2E invocation; ARTIFACT_PROVEN requires spine_proof_ref artifact
- W0 ADR: mandatory spine/taxonomy separation statements
- W2: Archive RootCustomsAgent; preserve L6 snapshot shim as report-gen-only (not arch evidence)
- W3 DEFERRED: no backfill from mock harness (_spine_proof_run)
- Disk: .cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md"""


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


def main() -> int:
    if not (REPO / PLAN_PATH).is_file():
        print(f"BLOCKED: missing {PLAN_PATH}", file=sys.stderr)
        return 1
    existing = _query_page_id()
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
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} notion_page={result.page_id} path={PLAN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
