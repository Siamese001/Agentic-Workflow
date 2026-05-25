#!/usr/bin/env python3
"""Create l6-reorg-deferred-followup-f3a9c2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "l6-reorg-deferred-followup-f3a9c2"
PLAN_PATH = ".cursor/plans/l6-reorg-deferred-followup-f3a9c2.md"

SUMMARY = (
    "Follow-up to COMPLETED l6-repo-reorganization-mental-model-c4e8f2. "
    "Owns W4/W6 deferred scope: promotion/ move, eval consolidation ADR, L_OPS gravity burndown, "
    "_shared Category A spike, engines chapter map. Parent E2E 21/21 PASS."
)

AI_SUMMARY = """- Parent: l6-repo-reorganization-mental-model-c4e8f2 (Completed 2026-05-25)
- Register: docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.md
- DS-1..DS-8: passive D1-D3, L_OPS eval moves, _shared spike, engines map
- Gravity: 86 edges documented; target ≤24 in W2 or amend ADR-085
- Author-Gate per physical move wave
- Disk: .cursor/plans/l6-reorg-deferred-followup-f3a9c2.md"""


def main() -> int:
    try:
        result = create_plan_in_notion(slug=SLUG, summary=SUMMARY, ai_summary=AI_SUMMARY)
    except PlanCreationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "ok": result.ok,
                "action": "created",
                "page_id": result.page_id,
                "slug": SLUG,
                "status": result.status,
                "plan_file_path": PLAN_PATH,
            }
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
