#!/usr/bin/env python3
"""Register apps_rg hybrid live proof + JD selection plan in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "apps-rg-hybrid-live-jd-selection-f8e2b3"
PLAN_PATH = ".claude/plans/apps-rg-hybrid-live-jd-selection-f8e2b3.md"
PARENT_SLUG = "apps-rg-runtime-substitute-burndown-c4e8f1"
DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

SUMMARY = (
    "Post-W4.3: live exec-summary hybrid proof (BM25 seed + Brown & Brown), then JD-aware "
    "selected_fact_plan reorder (W2B default). Decouples product hybrid from APPS_RG_SPINE_CHROMA_ENRICH. "
    "Parent: apps-rg-runtime-substitute-burndown-c4e8f1."
)

AI_SUMMARY = """- W0/W0b DONE: product hybrid + contract pytest (32+)
- W1 PASS: LIVE_RUNTIME_PROOF ledger_plus_hybrid_retrieval
- W2/W2d PASS: H6 X2 + voice/bridge/filler + W2B hybrid_informed_order_v1
- W2e PASS: finalize coherence, meta filler strip, product_quality PASS
- Live closeout: hybrid_live_20260522_w2e_pass2 (REAL_LLM, product_quality PASS)
- W3/W4 DONE: operator docs + parent + Notion
- STATUS: Complete (no RELEASE_ELIGIBLE; X3 may REVIEW on soft judges)
- Receipts: apps_rg_hybrid_live_w2e_coherence_finalize_receipt.md, apps_rg_hybrid_live_jd_selection_closeout_receipt.md
- Parent: apps-rg-runtime-substitute-burndown-c4e8f1"""


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
    if not rows:
        return None
    return str(rows[0].get("id") or "") or None


def main() -> int:
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1

    existing = _query_page_id(SLUG)
    if existing:
        print(
            json.dumps(
                {
                    "ok": True,
                    "slug": SLUG,
                    "page_id": existing,
                    "action": "already_exists",
                    "parent_slug": PARENT_SLUG,
                }
            )
        )
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
                "parent_slug": PARENT_SLUG,
            }
        )
    )
    print(f"PLAN_CREATED: slug={SLUG} path={PLAN_PATH} status=Not Started")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
