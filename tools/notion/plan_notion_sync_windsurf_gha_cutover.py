#!/usr/bin/env python3
"""Register windsurf-gha-cutover-d9f2a7 plan in Notion Plans DB (Not Started)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "windsurf-gha-cutover-d9f2a7"
PLAN_PATH = ".cursor/plans/windsurf-gha-cutover-d9f2a7.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "COMPLETED (2026-05-23): Windsurf GHA cutover + deferred scope implemented. "
    "Removed _deleted/ workflows; migrated CI/workflows to .cursor/ SSOT; Notion plan paths "
    "403+24 patched; artifact dual-write; mirror health + deletion readiness gates. "
    "Full .windsurf/ tree deletion assessed NOT SAFE (mirror required). "
    "Closeout: docs/reports/cursor/windsurf_gha_deferred_scope_closeout.md"
)

AI_SUMMARY = """- Tier: T3 governance / CI
- W0: Workflow matrix + branch protection audit (no “Windsurf Governance Health” required check)
- W1: Remove .github/workflows/_deleted/ (windsurf-governance-health calls missing script)
- W2: Migrate author-gate-gates, notion-plan-drift, apps-e2e workflow paths
- W3: PLANS_DIR → .cursor/plans in drift + plan registration gates
- W4: Author-Gate schemas/scripts/state SSOT under .cursor/
- W5: docs/reports/cursor/windsurf_gha_cutover_closeout.md
- Keep: check_windsurf_config_schema.py until .windsurf/hooks.json retired
- Out of scope: delete entire .windsurf/ tree
- Disk SSOT: .cursor/plans/windsurf-gha-cutover-d9f2a7.md"""


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


def _patch_completed(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    summary = (
        "COMPLETED (migration scope): Windsurf GHA cutover W0–W5 + W5.D1–D4. "
        "Metadata reconcile 2026-05-25 — phase ledger DONE; DoD-4 PARTIAL (graph_layer external). "
        "W1.D1 tree deletion OUT_OF_BAND. "
        "Receipt: docs/reports/cursor/windsurf_gha_metadata_reconcile_20260525_receipt.md"
    )
    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
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
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    existing = _query_page_id()
    if existing and _patch_completed(existing):
        print(
            json.dumps(
                {
                    "ok": True,
                    "action": "patched",
                    "page_id": existing,
                    "status": "Completed",
                    "slug": SLUG,
                    "plan_path": PLAN_PATH,
                }
            )
        )
        print(f"PLAN_COMPLETE: slug={SLUG} path={PLAN_PATH} status=Completed notion_page={existing}")
        return 0

    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
        )
    except PlanCreationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "action": "created",
                "page_id": result.page_id,
                "status": result.status,
                "slug": SLUG,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(
        f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Not Started notion_page={result.page_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
