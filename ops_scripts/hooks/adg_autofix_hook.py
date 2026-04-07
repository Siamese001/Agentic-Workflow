#!/usr/bin/env python3
"""T4.5: ADG Auto-Fix Hook — runs RepairOrchestrator AUTO_FIX rules on staged files.

This hook applies safe, deterministic repairs at commit time:
    - fix_guardian_format    (ADG:MEDIUM → AUTO_FIX)
    - fix_import_order       (ADG:MEDIUM → AUTO_FIX)
    - fix_unused_imports     (ADG:MEDIUM → AUTO_FIX)
    - fix_missing_all        (ADG:MEDIUM → AUTO_FIX)
    - fix_missing_typing     (ADG:LOW    → AUTO_FIX)

SEVERITY MODEL:
    ADG:CRITICAL → BLOCK_FIX    (never run here — handled by T10.6 + T13.6)
    ADG:HIGH     → SUGGEST_FIX  (never run here — handled by T10.7)
    ADG:MEDIUM   → AUTO_FIX     ← THIS HOOK
    ADG:LOW      → AUTO_FIX     ← THIS HOOK

Always exits 0 (auto-fixer, never blocks commits).
Files fixed are re-staged automatically.

Usage (pre-commit):
    entry: py ops_scripts/hooks/adg_autofix_hook.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _get_staged_python_files() -> list[Path]:
    """Return list of staged Python files that exist on disk."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return [
        ROOT / f
        for f in result.stdout.strip().splitlines()
        if f.endswith(".py") and (ROOT / f).exists()
    ]


def _restage_files(files: list[Path]) -> None:
    """Re-stage files that were modified by auto-fix rules."""
    if not files:
        return
    subprocess.run(
        ["git", "add"] + [str(f) for f in files],
        cwd=ROOT,
        check=False,
    )


def main() -> int:
    staged = _get_staged_python_files()
    if not staged:
        print("[ADG-AUTO-FIX] No staged Python files — skipping.")
        return 0

    print(f"[ADG-AUTO-FIX] Scanning {len(staged)} staged Python file(s) for AUTO_FIX issues...")

    try:
        from tools.adg.repair import ADGRepairOrchestrator
        from tools.adg.repair.types import FixCategory

        artifacts_dir = ROOT / "artifacts" / "adg"
        sqlite_files = sorted(artifacts_dir.glob("adg_indexed_*.sqlite"), reverse=True)
        sqlite_path = sqlite_files[0] if sqlite_files else None

        if sqlite_path is None:
            print("[ADG-AUTO-FIX] No ADG SQLite found — skipping (run generate_full_adg.py first).")
            return 0

        ts_stem = sqlite_path.stem.replace("adg_indexed_", "")
        orchestrator = ADGRepairOrchestrator(
            adg_dir=artifacts_dir,
            timestamp=ts_stem,
            repo_root=ROOT,
            sqlite_path=sqlite_path,
        )

        deficiencies = orchestrator.detect_deficiencies()
        auto_fix = [d for d in deficiencies if d.category == FixCategory.AUTO_FIX]

        if not auto_fix:
            print("[ADG-AUTO-FIX] No AUTO_FIX deficiencies found — nothing to do.")
            return 0

        staged_paths = {str(f.relative_to(ROOT)) for f in staged}
        scoped = [d for d in auto_fix if str(d.file_path) in staged_paths]

        if not scoped:
            print(f"[ADG-AUTO-FIX] {len(auto_fix)} AUTO_FIX issue(s) found but none in staged files.")
            return 0

        print(f"[ADG-AUTO-FIX] Applying {len(scoped)} AUTO_FIX repair(s)...")
        result = orchestrator.run(dry_run=False)

        fixed_files = [
            ROOT / fr.deficiency_id.split(":")[0]
            for fr in (result.fix_results if result else [])
            if fr.success
        ]
        _restage_files([f for f in fixed_files if f.exists()])

        applied = result.fixes_applied if result else 0
        failed = result.failed_fixes if result else 0
        print(f"[ADG-AUTO-FIX] Done: {applied} applied, {failed} failed.")

    except Exception as e:  # guardian: allow-broad-exception -- pre-commit hook must not block commits on orchestrator errors; auto-fix is best-effort
        print(f"[ADG-AUTO-FIX] Warning: orchestrator error ({e}) — skipping auto-fix.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
