#!/usr/bin/env python3
"""Register exec-summary-pa-core-law-dedup-f8e2a1 plan in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-pa-core-law-dedup-f8e2a1"
PLAN_PATH = ".claude/plans/exec-summary-pa-core-law-dedup-f8e2a1.md"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Align apps_rg executive_summary prompts with core PA law by reference only: pa_core_law_v1 "
    "contracts, PRODUCT_SHAPE as sole gate catalog, slim I0/S0, SRFS/capsule diet, drift tests, "
    "Brown REAL_LLM token proof."
)

AI_SUMMARY = """- Target: executive_summary prompt slots (apps_rg) — not agentic_core jinja merge path
- Mental model: no full core PA restate; reference pa_truth_oath_v1 / pa_proof_binding_v1 / PRODUCT_SHAPE
- Keep: E0 style, north_star, graph_only, capped targeting, compact R0 JSON schema
- W1: pa_core_law_v1.yaml SSOT + reference-not-restate validator
- W2: slim template; remove gate triplication (_EXEC_SUMMARY_X2_GATE_REFS, R0 gate essay)
- W3: SRFS oneshot diet when capsule; drift ratchet tests
- W4: pytest + Brown & Brown smoke (token_budget PASS, REAL_LLM)
- Baseline proof: exec_summary_20260522_084114 (dedup v2 + capsule already landed)
- Out of scope: agentic_core edits, X2 weakening, premium tiering"""


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
