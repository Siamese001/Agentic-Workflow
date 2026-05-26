#!/usr/bin/env python3
"""W0: Register exec-summary-regen-voice-repair-unblock-e7c4a2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-regen-voice-repair-unblock-e7c4a2"
PLAN_PATH = ".cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Unblock executive-summary judge regen: remove voice_repair hardcoded S5/S6 that "
    "judges fail; composite delta_class routing; per-cycle regen anchor; S5/S6 fact "
    "pinning; per-cycle X2 receipts; Brown SVP E2E proof."
)

AI_SUMMARY = """- PLAN_STATUS: Not Started (W0 registration 2026-05-26)
- Parent: exec-summary-anthropic-surgical-regen-f3c8d2
- Baseline run: exec_summary_20260526_213359 (10 regen cycles, regen_not_accepted)
- Root cause: voice_repair _S5_CREDENTIAL_REPLACEMENT = judge failure text
- Waves: W1 voice repair | W2 delta_class | W3 incremental anchor | W4 composition | W5 observability | W6 E2E
- Disk: .cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md"""


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
    if rows:
        return str(rows[0].get("id") or "") or None
    return None


def main() -> int:
    existing = _query_page_id()
    if existing:
        print(f"ALREADY_REGISTERED slug={SLUG} page_id={existing}")
        return 0
    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
        )
    except PlanCreationError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1
    if not result.ok:
        print(f"FAIL: {result.error}", file=sys.stderr)
        return 1
    print(f"PLAN_CREATED slug={SLUG} page_id={result.page_id} status={result.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
