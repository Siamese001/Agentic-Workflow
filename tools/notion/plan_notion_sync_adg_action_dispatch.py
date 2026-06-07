#!/usr/bin/env python3
"""Create adg-action-dispatch-c9e4a2 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "adg-action-dispatch-c9e4a2"
PLAN_PATH = ".claude/plans/adg-action-dispatch-c9e4a2.md"

SUMMARY = (
    "Close ADG diagnosis-to-dispatch gap: post-run adg_action_queue.json, triage playbook, "
    "enriched app hotspot reports, burndown next-action link, optional Notion FIX backlog sync. "
    "Baseline 2026-05-25: FIX=8, TRACK=17."
)

AI_SUMMARY = """- Problem: GraphDB/MVs/reports sit idle; no ranked next action
- W0: playbook + adg-post-run-burndown.mdc (FIX-first ladder)
- W1: tools/reports/adg_action_queue.py + generate_full_adg hook
- W2: scan_apps_hotspots gate/tests columns; burndown ## Next action
- W3: Notion FIX-only backlog sync (idempotent)
- P7-first: refactor_accelerator candidates[] + impacted_tests
- Immediate: 10_infra_wiring, 1_critical_path_integrity, smallest REGR
- Disk: .claude/plans/adg-action-dispatch-c9e4a2.md
- Index: docs/reports/cursor/adg_action_dispatch_plan_index.md"""


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
