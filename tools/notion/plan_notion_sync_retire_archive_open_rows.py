#!/usr/bin/env python3
"""Retire Notion Plans rows that point at archived plan files (not active .claude/plans SSOT)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

RETIREMENTS: tuple[tuple[str, str, str], ...] = (
    (
        "ag-purity-open-work-remediation-roadmap",
        ".claude/plans/_archive/windsurf_legacy/ag-purity-open-work-remediation-roadmap.md",
        "RETIRED 2026-05-24: Windsurf legacy archive only — AG-PURITY remediation roadmap superseded by "
        "adg-ci workstreams; not active .claude/plans SSOT. Do not execute from Notion backlog.",
    ),
    (
        "nist-ai-rmf-l5-profile-e7a3c1",
        ".claude/plans/_archive/windsurf_legacy/nist-ai-rmf-l5-profile-e7a3c1.md",
        "RETIRED 2026-05-24: Windsurf legacy archive only — NIST AI RMF L5 profile gap plan parked; "
        "no active disk plan under .claude/plans/. Re-open only via new registered plan if revived.",
    ),
)


def _query_page_id(slug: str) -> str | None:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return None
    payload = {
        "filter": {"property": "Slug", "title": {"equals": slug}},
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
    return str(rows[0].get("id") or "") if rows else None


def _patch_retired(page_id: str, *, plan_path: str, summary: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    on_disk = (REPO / plan_path).is_file()
    payload = {
        "properties": {
            "Status": {"select": {"name": "Retired"}},
            "Exists On Disk": {"checkbox": on_disk},
            "Plan File Path": {"rich_text": [{"text": {"content": plan_path}}]},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
            "AI Summary ": {
                "rich_text": [
                    {
                        "text": {
                            "content": (
                                "- NOTION_STATUS: Retired (archive hygiene 2026-05-24)\n"
                                f"- Archive path: {plan_path}\n"
                                "- Action: do not schedule waves; migrate to new plan if work resumes"
                            )[:2000]
                        }
                    }
                ]
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return False


def main() -> int:
    results: list[dict[str, object]] = []
    exit_code = 0
    for slug, plan_path, summary in RETIREMENTS:
        page_id = _query_page_id(slug)
        if not page_id:
            results.append({"ok": False, "slug": slug, "error": "notion_row_not_found"})
            exit_code = 1
            continue
        if not _patch_retired(page_id, plan_path=plan_path, summary=summary):
            results.append({"ok": False, "slug": slug, "page_id": page_id, "error": "patch_failed"})
            exit_code = 1
            continue
        results.append(
            {
                "ok": True,
                "slug": slug,
                "page_id": page_id,
                "status": "Retired",
                "plan_path": plan_path,
                "notion_url": f"https://www.notion.so/{page_id.replace('-', '')}",
            }
        )
        print(f"PLAN_RETIRED: slug={slug} path={plan_path} notion_page={page_id}")
    print(json.dumps({"results": results}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
