#!/usr/bin/env python3
"""Register adg-three-bucket-pipeline-redesign-c8e4f1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "adg-three-bucket-pipeline-redesign-c8e4f1"
PLAN_PATH = ".claude/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "ADR-079 COMPLETE: three-bucket audit opt-in off generate_full_adg hot path. "
    "Join fix (path/name fallback), Windows safe_repo_scan for registry lift, "
    "stale gap-report sha256 guard, weekly runbook. Audit proof: triplet_attested=121, "
    "health_pct=0.02 on overlap-biased seed. No agentic_core / ADG_CERTIFIED strict changes."
)

AI_SUMMARY = """- Status: COMPLETE (2026-05-24)
- W1–W4 DONE: ADR-079, optional audit, contract tests, join fix, stale guard, archive pointers, runbook
- Windows: tools/adg/safe_repo_scan.py patches consumer resolver walk (.venv/lib64 junction safe)
- Proof: docs/reports/cursor/adg_three_bucket_pipeline_redesign_closeout.md (PASS)
- Operator: seed with --prefer-registry-overlap before audit for triplet proof
- Disk: .claude/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md"""


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


def _plan_status_name() -> str:
    plan_file = REPO / PLAN_PATH
    if plan_file.is_file():
        for line in plan_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("PLAN_STATUS:"):
                raw = line.split(":", 1)[1].strip()
                if raw.upper() == "COMPLETE":
                    return "Complete"
                if raw.upper() in ("IN_PROGRESS", "IN PROGRESS"):
                    return "In Progress"
    return "In Progress"


def _patch_plan_page(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": _plan_status_name()}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
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
            return 200 <= resp.status < 300
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        return False


def main() -> int:
    existing = _query_page_id()
    if existing:
        print(f"PLAN_EXISTS: slug={SLUG} page_id={existing}")
        status = _plan_status_name()
        if _patch_plan_page(existing):
            print(f"PATCHED: Status={status}, Summary refreshed")
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

    print(f"PLAN_CREATED: slug={SLUG} page_id={result.page_id} status={result.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
