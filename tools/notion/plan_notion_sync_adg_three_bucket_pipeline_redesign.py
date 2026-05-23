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
PLAN_PATH = ".cursor/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "ADR-079: remove mandatory three-bucket audit (OTel runtime view, registry lift, "
    "gap report, in-toto sign) from generate_full_adg hot path. Default regen = static graph "
    "+ MVs + P0. Opt-in via ADG_THREE_BUCKET=1, --three-bucket, or run_three_bucket_audit.py. "
    "W1 landed 2026-05-23; W2 static_edge_id join; W3 CI/docs; W4 weekly audit runbook."
)

AI_SUMMARY = """- Tier: T3 governance / ADG pipeline
- Problem: every regen paid triplet audit cost; 0% triplet health (broken static_edge_id join)
- W1 DONE: optional_three_bucket.py, generate_full_adg trim, run_three_bucket_audit.py, ADR-079
- W2 TODO: runtime_view_builder join fix + triplet proof on seeded OTel
- W3 TODO: contract gate hints, archive windsurf plan cross-refs
- W4 TODO: weekly audit operator doc
- Hot path: python -m tools.generate.generate_full_adg (three_bucket=OFF)
- Audit: ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py
- ADR: docs/architecture/adr/ADR-079-adg-pipeline-three-bucket-opt-in.md
- Disk SSOT: .cursor/plans/adg-three-bucket-pipeline-redesign-c8e4f1.md"""


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


def _patch_in_progress(page_id: str) -> bool:
    from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none
    import urllib.error
    import urllib.request

    token = get_notion_bearer_token_or_none()
    if not token:
        return False
    payload = {
        "properties": {
            "Status": {"select": {"name": "In Progress"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": PLAN_PATH}}]},
            "Summary": {
                "rich_text": [{"text": {"content": SUMMARY[:2000]}}],
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
        if _patch_in_progress(existing):
            print("PATCHED: Status=In Progress, Summary refreshed")
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
