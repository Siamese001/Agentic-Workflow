#!/usr/bin/env python3
"""Register exec-summary-failed-run-persistence-notion-e7c4b2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-failed-run-persistence-notion-e7c4b2"
PLAN_PATH = ".claude/plans/exec-summary-failed-run-persistence-notion-e7c4b2.md"

SUMMARY = (
    "Apps_* scope: persist failed/review runs for ANY lane with X1D judge regen — "
    "candidate_pool/ on disk (scratch + regen cycles + reject gates), cross-lane "
    "failed_judge_regen_runs_index.jsonl, L6/exhaust refs, Notion review sync. "
    "Reference impl: executive_summary. No L4 on X3_REVIEW. Sibling: f8a3c2."
)

AI_SUMMARY = """- Hardened 2026-05-26: receipt-bound pool (refs+hashes), LIVE vs BACKFILL proof_class
- Scope: all apps_* lanes with X1D judge regen; exec_summary reference impl
- W3 mirrors f8a3c2 publish only — no parallel selector; Notion read-only index
- Contract test: no UWG/L4 commit on REVIEW; atomic writer; candidate lineage enum
- Closeout: pytest candidate_pool + contract test + backfill + notion sync --dry-run"""


def main() -> int:
    plan_file = REPO / PLAN_PATH
    if not plan_file.is_file():
        print(f"BLOCKED: plan file missing: {plan_file}", file=sys.stderr)
        return 1
    try:
        result = create_plan_in_notion(
            slug=SLUG,
            summary=SUMMARY,
            ai_summary=AI_SUMMARY,
            plan_file_path=PLAN_PATH,
        )
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    out = {
        "ok": result.ok,
        "page_id": result.page_id,
        "slug": result.slug,
        "status": result.status,
        "error": result.error,
        "plan_path": PLAN_PATH,
    }
    print(json.dumps(out, indent=2))
    if result.ok and result.page_id:
        print(
            f"\nPatch plan header:\n"
            f"NOTION_PAGE_ID: {result.page_id}\n"
            f"NOTION_PLAN_URL: https://www.notion.so/{SLUG.replace('-', '')}-{result.page_id.replace('-', '')}",
            file=sys.stderr,
        )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
