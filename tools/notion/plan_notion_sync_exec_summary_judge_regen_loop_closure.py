#!/usr/bin/env python3
"""Create exec-summary-judge-regen-loop-closure-d8f3a1 in Notion Plans DB."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools.notion.plan_creation_helper import PlanCreationError, create_plan_in_notion

SLUG = "exec-summary-judge-regen-loop-closure-d8f3a1"
PLAN_PATH = ".cursor/plans/exec-summary-judge-regen-loop-closure-d8f3a1.md"

SUMMARY = (
    "Follow-up to COMPLETED core-same-authority-incremental-regen-e7a4b1 (W4 deferred). "
    "Close judge→regen→X2→rescore loop: lane core-bridge only, post-regen X2 acceptance, "
    "optional JudgeDirectedRegenOrchestrator, Brown re-proof with accepted cycle."
)

AI_SUMMARY = """- Parent: core-same-authority-incremental-regen-e7a4b1 (Completed W0-W3)
- North star: X2 green after regen BEFORE judge rescore (parent unblock #4 failed on Brown 122058)
- DS-1..DS-8: orchestrator, dual-path, X2 snapshots, env defaults
- Waves: W0 AG placement, W1 lane unify, W2 X2 accept, W3 orchestrator, W4 artifacts, W5 Brown
- Out of scope: semantic ceiling >1, 3/3 CERTIFIED (operator-ship)
- Disk: .cursor/plans/exec-summary-judge-regen-loop-closure-d8f3a1.md"""


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
