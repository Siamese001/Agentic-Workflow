"""P1/P2 auto-fix repair orchestrator integration for ADG generation."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)


def _resolve_repair_sqlite(adg_artifacts_dir: Path, ts: str, sqlite_path: Path | None) -> Path | None:
    """Resolve a deterministic, schema-valid sqlite source for repair orchestration."""
    candidate: Path | None = None

    if sqlite_path is not None and Path(sqlite_path).exists():
        candidate = Path(sqlite_path).resolve()
    else:
        ts_candidate = (adg_artifacts_dir / f"adg_indexed_{ts}.sqlite").resolve()
        if ts_candidate.exists():
            candidate = ts_candidate
        else:
            sqlite_files = sorted(
                adg_artifacts_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime
            )
            if sqlite_files:
                candidate = sqlite_files[-1].resolve()

    if candidate is None:
        return None

    required_tables = {"nodes", "edges", "violations", "meta"}
    try:
        with sqlite3.connect(str(candidate), timeout=10) as conn:
            existing_tables = {
                row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
    except (
        sqlite3.Error
    ):  # guardian: allow-silent-swallow -- invalid sqlite candidate should be skipped, not crash generation
        return None

    if required_tables - existing_tables:
        return None

    return candidate


def _run_p1_p2_auto_fix(
    adg_artifacts_dir: Path,
    ts: str,
    sqlite_path: Path | None = None,
    *,
    dry_run: bool = False,
) -> None:
    """Run P1/P2 repair analysis via repair orchestrator."""
    try:
        from tools.adg.repair import ADGRepairOrchestrator as _orchestrator_cls
        from tools.adg.repair.rule_engine import register_builtin_rules as _register_rules
    except ImportError:
        from adg.repair import ADGRepairOrchestrator as _orchestrator_cls  # type: ignore[no-redef]
        from adg.repair.rule_engine import register_builtin_rules as _register_rules  # type: ignore[no-redef]

    _register_rules()

    resolved_sqlite = _resolve_repair_sqlite(adg_artifacts_dir, ts, sqlite_path)
    if resolved_sqlite is not None:
        print(f"[ADG] Repair orchestrator sqlite source: {resolved_sqlite}")
    else:
        print(
            "[ADG] WARNING: Repair orchestrator sqlite source unavailable or invalid; continuing without sqlite-backed repair analysis"
        )

    orchestrator = _orchestrator_cls(
        adg_dir=adg_artifacts_dir,
        timestamp=ts,
        repo_root=ROOT,
        sqlite_path=resolved_sqlite,
    )

    try:
        result = orchestrator.run(dry_run=dry_run)
        mode = "DRY RUN" if dry_run else "APPLY"
        print(f"[ADG] Repair orchestrator completed ({mode}): {result.deficiencies_found} deficiencies found")
        print(f"[ADG]   AUTO_FIX: {result.fixes_applied}")
        print(f"[ADG]   SUGGEST_FIX: {result.fixes_suggested}")
        print(f"[ADG]   BLOCK_FIX: {result.fixes_blocked}")
    except (
        ImportError,
        AttributeError,
        OSError,
        RuntimeError,
        ValueError,
    ) as e:  # guardian: allow-broad-exception -- non-critical: repair orchestrator failure should not block ADG generation
        print(f"[WARNING] Repair orchestrator failed: {e}")
