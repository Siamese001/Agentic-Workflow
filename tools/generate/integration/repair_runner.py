"""P1/P2 auto-fix repair orchestrator integration for ADG generation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _run_p1_p2_auto_fix(adg_artifacts_dir: Path, ts: str) -> None:
    """Run P1/P2 auto-fix via repair orchestrator."""
    from tools.adg.repair import ADGRepairOrchestrator
    from tools.adg.repair.rule_engine import register_builtin_rules

    register_builtin_rules()

    sqlite_path = None
    sqlite_files = sorted(adg_artifacts_dir.glob("adg_indexed_*.sqlite"))
    if sqlite_files:
        sqlite_path = sqlite_files[-1]

    orchestrator = ADGRepairOrchestrator(
        adg_dir=adg_artifacts_dir,
        timestamp=ts,
        repo_root=ROOT,
        sqlite_path=sqlite_path,
    )

    try:
        result = orchestrator.run(dry_run=False)
        print(f"[ADG] Repair orchestrator completed: {result.deficiencies_found} deficiencies found")
        print(f"[ADG]   AUTO_FIX: {result.fixes_applied}")
        print(f"[ADG]   SUGGEST_FIX: {result.fixes_suggested}")
        print(f"[ADG]   BLOCK_FIX: {result.fixes_blocked}")
    except Exception as e:  # guardian: allow-broad-exception -- non-critical: repair orchestrator failure should not block ADG generation
        print(f"[WARNING] Repair orchestrator failed: {e}")
