#!/usr/bin/env python3
"""Register whole-run-phase1-x3-dispatch-remediation plan in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "whole-run-phase1-x3-dispatch-remediation-f2a8c4"
PLAN_PATH = ".cursor/plans/whole-run-phase1-x3-dispatch-remediation-f2a8c4.md"

SUMMARY = (
    "Remediate integrated python -m apps_rg Phase-1 failure: executive_summary X3_ALLOW on disk "
    "but dispatch exit_status error (dict x3 vs getattr pass_), phase1_aborted skips resolve, "
    "all lanes PHASE1_NO_RUN_DIR. Waves: dict-safe X3 helper, resolve/abort decoupling, optional "
    "allow_non_allow flag, whole-run proof."
)

AI_SUMMARY = """- PLAN_STATUS: Not Started (2026-05-26)
- FAILED_RUN: artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966
- RC-1: executive_summary_lane x3=dict; section_cli_runners getattr(x3, pass_) -> False
- RC-2: phase1_aborted skips resolve_latest_lane_run_dir for all lanes
- WAVES: W1 X3 outcome helper + tests | W2 resolve/abort | W3 allow_non_allow parity | W4 whole-run proof
- PLAN: .cursor/plans/whole-run-phase1-x3-dispatch-remediation-f2a8c4.md
- SUPERSEDES_PARTIAL: fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2 (pointer/briefing only)
- PROOF: pytest + python -m apps_rg Brown & Brown SVP + verify_governed_spine_e2e.py --integrated-dir"""


def main() -> int:
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
