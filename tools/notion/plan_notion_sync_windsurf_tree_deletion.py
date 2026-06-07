#!/usr/bin/env python3
"""Register windsurf-tree-deletion-ci-parity-b8e4f1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "windsurf-tree-deletion-ci-parity-b8e4f1"
PLAN_PATH = ".claude/plans/windsurf-tree-deletion-ci-parity-b8e4f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Not Started: Deprecate then delete docs/archive/windsurf/legacy-tree/ mirror after CI parity. "
    "Prerequisite: windsurf-gha-cutover COMPLETED. deletion_safe=false today. "
    "W0–W5: ref burndown → content retirement → artifacts → gate flip → git rm."
)

AI_SUMMARY = """- Plan type: governance / CI parity
- SSOT: .cursor/ only after completion
- Prerequisite: windsurf-gha-cutover-d9f2a7 (COMPLETED)
- Today: deletion_safe false (artifacts/cursor/windsurf_deletion_readiness.json)
- W1: Retarget check_skill_frontmatter, check_hook_consolidation, pre-commit MCP
- W2: Remove duplicate docs/archive/windsurf/legacy-tree/plans scripts skills
- W3: artifacts/cursor namespace removal
- W4: Retire mirror gates; deletion_safe true
- W5: git rm -r docs/archive/windsurf/legacy-tree/
- Disk: .claude/plans/windsurf-tree-deletion-ci-parity-b8e4f1.md"""


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
    if _query_page_id():
        print(json.dumps({"ok": True, "action": "exists", "slug": SLUG}))
        print(f"PLAN_EXISTS: slug={SLUG}")
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
    print(json.dumps({"ok": True, "action": "created", "page_id": result.page_id, "slug": SLUG}))
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} notion_page={result.page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
