#!/usr/bin/env python3
"""Sync apps_rg DOCX removal plan (W0 complete) to Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-docx-output-removal-4650ff"
PLAN_PATH = ".cursor/plans/apps-rg-docx-output-removal-4650ff.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "apps_rg DOCX output removal: W0 inventory+roadmap complete (2026-05-22). "
    "Retire dual DOCX pipelines (integrated outputs/resume.docx + runtime_proofs/docx). "
    "JSON-only product truth; W1-W4 deferred (gates, emission, modules, tests/CI)."
)

AI_SUMMARY = """- W0 DONE: inventory, plan, receipt on disk
- Dual pipelines: DocxExportStep vs docx_manifest_builder/docx_renderer
- Package X3 hard-couples docx_manifest_x2 + docx_render_x2 + on-disk .docx
- Section lanes: docx_render_ref already null
- W1 TODO: JSON-only artifact gate + package disposition
- W2 TODO: remove DocxExportStep + offline _run_docx_emit
- W3 TODO: delete internal docx modules + prompt cleanup
- W4 TODO: contract tests + W7 CI gate
- Plan: .cursor/plans/apps-rg-docx-output-removal-4650ff.md
- Receipt: docs/reports/apps_rg/apps_rg_docx_removal_inventory_receipt.md"""


def _query_page_id() -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {
            "property": "Slug",
            "title": {"equals": SLUG},
        },
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
