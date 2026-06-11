"""Plan-mint gate (Operating Model 2026-06-10) — block NEW plan-file creation by reflex.

Standing order: agents execute existing wave items; findings become backlog rows. Creating a
new plan file requires explicit user authorization in the same turn, expressed mechanically by
setting ``PLAN_MINT_OK=1`` in the environment for that write.

Scope: blocks creation of files matching ``plans/*.md`` or ``.claude/plans/*.md`` (any worktree)
that do not already exist on disk. Edits to EXISTING plan files pass through untouched (status
updates, inventory rows, supersession headers are the encouraged path).

Fail-soft: any internal error exits 0 (never blocks unrelated work). Block signal = exit 2 +
reason on stderr, per house hook contract.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_PLAN_PATH_RE = re.compile(r"(^|[\\/])(\.claude[\\/])?plans[\\/][^\\/]+\.md$", re.IGNORECASE)


def main() -> int:
    try:
        if os.environ.get("PLAN_MINT_OK", "").strip().lower() in ("1", "true", "yes"):
            return 0
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        tool_input = data.get("tool_input") or {}
        file_path = str(tool_input.get("file_path") or "").strip()
        if not file_path or not _PLAN_PATH_RE.search(file_path):
            return 0
        # Templates/archives are not plan mints.
        lowered = file_path.replace("\\", "/").lower()
        if "/_archive/" in lowered or "/templates/" in lowered:
            return 0
        if Path(file_path).exists():
            return 0  # editing an existing plan is allowed (rows, statuses, headers)
        print(
            "PLAN-MINT GATE: creating a NEW plan file is blocked (operating model 2026-06-10).\n"
            "\n"
            "Classify the work first (.claude/rules/work-item-classification.md):\n"
            "  BUG_IMMEDIATE     → fix directly, proof receipt is the artifact (no plan)\n"
            "  BUG_DEFERRED      → spawn_task chip (no plan)\n"
            "  FINDING_APPS_RG   → row in Master Gap Inventory (no plan)\n"
            "  PLAN_MICRO        → native plan mode only, no disk file, no Notion\n"
            "  PLAN_MULTI_WAVE   → disk file allowed ONLY with explicit user authorization\n"
            "\n"
            "Master Gap Inventory: plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md\n"
            "If the USER explicitly authorized a new plan this turn, retry with PLAN_MINT_OK=1.",
            file=sys.stderr,
        )
        return 2
    except Exception:  # guardian: allow-broad-exception -- hook fail-soft contract
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
