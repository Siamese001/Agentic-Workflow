#!/usr/bin/env python3
"""Register apps_rg resume assembly debt burndown plan in Notion Plans DB (for review)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-resume-assembly-debt-burndown-56c022"
PLAN_PATH = ".cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "apps_rg resume assembly debt burndown: converge JSON SSOT (rg_output), demote offline "
    "rollup/package X3, safe ghost cleanup, execute DOCX child plan. W0 inventory done; "
    "W1-W5 pending review."
)

AI_SUMMARY = """- Parent plan for assembly simplification (review / Not Started)
- W0 DONE: inventory + delete-risk matrix in docs/reports/apps_rg/
- W1: safe ghosts (NarrativePassStep, policy paths, empty reports/)
- W2: DOCX removal — child plan apps-rg-docx-output-removal-4650ff W1-W4
- W3: direct lane→rg_output; drop assembler bridge (SSOT sign-off required)
- W4: build_rollup + package X3 test-only boundary
- W5: engines/reasoning eval boundary
- Key finding: package X3 not on integrated CLI; assembler redundant with rg_output merge
- Plan: .cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md
- Receipt: docs/reports/apps_rg/apps_rg_resume_assembly_debt_inventory.md"""


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
    return str(results[0].get("id") or "") if results else None


def _patch_for_review(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "Not Started"}},
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
        if _patch_for_review(page_id):
            print(
                json.dumps(
                    {
                        "ok": True,
                        "action": "patched",
                        "page_id": page_id,
                        "status": "Not Started",
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
