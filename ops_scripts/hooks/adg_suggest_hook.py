#!/usr/bin/env python3
"""T10.7: ADG Suggest-Fix Report Hook — surfaces ADG:HIGH issues for HITL review.

This hook NEVER modifies files. It reports SUGGEST_FIX deficiencies so the
developer is aware of HIGH-severity issues that need human decisions before
the RepairOrchestrator can be authorised to fix them.

SEVERITY MODEL:
    ADG:CRITICAL → BLOCK_FIX    (handled by T10.6 / T13.6 — blocks commit)
    ADG:HIGH     → SUGGEST_FIX  ← THIS HOOK (warn only, never blocks)
    ADG:MEDIUM   → AUTO_FIX     (handled by T4.5)
    ADG:LOW      → AUTO_FIX     (handled by T4.5)

Output: JSON report written to $PRE_COMMIT_ISSUES_DIR/adg_suggest_hook.jsonl
        for aggregation by T21 pre-commit summary reporter.

Always exits 0 (reporter, never a blocker).

Usage (pre-commit):
    entry: py ops_scripts/hooks/adg_suggest_hook.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_ISSUES_DIR = Path(os.environ.get("PRE_COMMIT_ISSUES_DIR", Path(os.environ.get("TEMP", "/tmp")) / "pre-commit-issues"))


def _write_jsonl(issues: list[dict]) -> None:
    """Write issues to the pre-commit issues dir for T21 aggregation."""
    try:
        _ISSUES_DIR.mkdir(parents=True, exist_ok=True)
        out_path = _ISSUES_DIR / "adg_suggest_hook.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for issue in issues:
                f.write(json.dumps(issue) + "\n")
    except OSError:
        pass


def main() -> int:
    try:
        from tools.adg.repair import ADGRepairOrchestrator
        from tools.adg.repair.types import FixCategory

        artifacts_dir = ROOT / "artifacts" / "adg"
        sqlite_files = sorted(artifacts_dir.glob("adg_indexed_*.sqlite"), reverse=True)
        if not sqlite_files:
            print("[ADG-SUGGEST] No ADG SQLite found — skipping.")
            return 0

        sqlite_path = sqlite_files[0]
        ts_stem = sqlite_path.stem.replace("adg_indexed_", "")

        orchestrator = ADGRepairOrchestrator(
            adg_dir=artifacts_dir,
            timestamp=ts_stem,
            repo_root=ROOT,
            sqlite_path=sqlite_path,
        )

        deficiencies = orchestrator.detect_deficiencies()
        suggest = [d for d in deficiencies if d.category == FixCategory.SUGGEST_FIX]

        if not suggest:
            print("[ADG-SUGGEST] No ADG:HIGH (SUGGEST_FIX) issues found.")
            return 0

        print(f"[ADG-SUGGEST] {len(suggest)} ADG:HIGH issue(s) require HITL review before auto-fix:")
        issues_out = []
        for d in suggest:
            msg = f"  {d.file_path}:{d.line_no or '?'}  [{d.issue_type}]  {d.description}"
            print(msg)
            issues_out.append({
                "hook": "adg-suggest-fix",
                "severity": "HIGH",
                "fix_category": "SUGGEST_FIX",
                "file": str(d.file_path),
                "line": d.line_no,
                "issue_type": d.issue_type,
                "description": d.description,
                "suggested_fix": d.suggested_fix,
            })

        _write_jsonl(issues_out)
        print("[ADG-SUGGEST] To apply: run `python tools/adg/adg_repair.py --latest --apply` after HITL approval.")

    except Exception as e:  # guardian: allow-broad-exception -- pre-commit reporter must never block commits on orchestrator errors
        print(f"[ADG-SUGGEST] Warning: orchestrator error ({e}) — skipping suggest report.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
