#!/usr/bin/env python3
"""Register sections-pa-core-law-rollout-c3a8f1 plan in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "sections-pa-core-law-rollout-c3a8f1"
PLAN_PATH = ".cursor/plans/sections-pa-core-law-rollout-c3a8f1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Roll out exec-summary PA core-law dedup to headline, competencies, and Unify/IBM "
    "(bullets + narratives): pa_core_law_v1 references, PRODUCT_SHAPE-only X2 catalogs, "
    "I0/YAML diet, drift ratchets, per-lane REAL_LLM proof."
)

AI_SUMMARY = """- Predecessor COMPLETE: exec-summary-pa-core-law-dedup-f8e2a1 (CORE_LAW_V3, 50 pytest, Brown token PASS)
- Mental model: agentic_core = generic PA/jinja; apps_rg = section prose + X2 + compile append (INPUT_AUTHORITY, PRODUCT_SHAPE)
- P0 token debt: headline_tailor_v1 ~18k chars; ibm_position_narrative_v1 ~19.5k; unify narrative ~17k
- Unify/IBM bullets compile via w7 shell + _legacy_i0 in *_pa.py (YAML tailor files are spec drift risk)
- W0: baseline fingerprints; W1: shared pa_core_law + w7 shell; W2 headline; W3 competencies; W4 four Unify/IBM lanes
- W5: drift ratchets; W6: Brown smoke per section + closeout receipt
- Out of scope: agentic_core edits, X2 weakening, other resume sections"""


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
    if not rows:
        return None
    return str(rows[0].get("id") or "") or None


def main() -> int:
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    existing = _query_page_id()
    if existing:
        print(json.dumps({"ok": True, "slug": SLUG, "page_id": existing, "action": "already_exists"}))
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
                "slug": result.slug,
                "page_id": result.page_id,
                "status": result.status,
                "plan_path": PLAN_PATH,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Not Started")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
