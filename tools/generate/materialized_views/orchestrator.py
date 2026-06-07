"""Orchestrator for ADG SQLite materialized view refresh.

Calls Phase A → B → C → D → E in dependency order.
Returns combined row-count dict and logs a summary table.
"""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm  # §16 progress-bar compliance for the multi-phase MV refresh

try:
    from tools.generate.materialized_views.sqlite_helpers import (
        connect_sqlite_for_mv,
        validate_sqlite_path,
    )
except ImportError:  # pragma: no cover — standalone ``python -m materialized_views`` layout
    from materialized_views.sqlite_helpers import (
        connect_sqlite_for_mv,
        validate_sqlite_path,
    )

try:
    from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
    from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b
    from tools.generate.materialized_views.phase_c_trace_drift_debt import materialize_phase_c
    from tools.generate.materialized_views.phase_d_snapshot_regression import materialize_phase_d
    from tools.generate.materialized_views.phase_e_graph_intelligence import materialize_phase_e
    from tools.generate.materialized_views.phase_f_hotspot_coverage import materialize_phase_f
except ImportError:
    from materialized_views.phase_a_path_authority import materialize_phase_a
    from materialized_views.phase_b_capability_tool_task import materialize_phase_b
    from materialized_views.phase_c_trace_drift_debt import materialize_phase_c
    from materialized_views.phase_d_snapshot_regression import materialize_phase_d
    from materialized_views.phase_e_graph_intelligence import materialize_phase_e
    from materialized_views.phase_f_hotspot_coverage import materialize_phase_f


def materialize_all_views(sqlite_path: Path) -> dict[str, int]:
    """Refresh all 42 ADG materialized view tables. Idempotent.

    Runs Phase A, then B (depends on A), then C (depends on A), then D
    (depends on A+B+C), then E (graph-native, depends on A+B). Logs a compact
    summary table to stdout.

    Args:
        sqlite_path: Path to the live ADG SQLite database.

    Returns:
        dict mapping every materialized table name to its post-refresh row count.
    """
    sqlite_path = validate_sqlite_path(sqlite_path)
    all_counts: dict[str, int] = {}

    # W1.3 (plan adg-gate-pipeline-efficiency-e4b1c7): phases run sequentially in
    # dependency order — A → B,C (depend on A) → D (A+B+C) → E (A+B) → F. Phase F
    # (Hotspot × Coverage, plan hotspot-coverage-pipeline-c4e8d2) also depends on
    # the `coverage_by_path` table written by tools/adg/ingest_coverage_py.py
    # ahead of this call; its LEFT JOINs make missing data fail-soft. The order
    # below is load-bearing — do not reorder. Surface a progress bar (§16): MV
    # refresh is a >5 s step that was previously silent until the summary table.
    _phases = (
        ("A path/authority", materialize_phase_a),
        ("B capability/tool/task", materialize_phase_b),
        ("C trace/drift/debt", materialize_phase_c),
        ("D snapshot/regression", materialize_phase_d),
        ("E graph-intelligence", materialize_phase_e),
        ("F hotspot×coverage", materialize_phase_f),
    )
    # W2.1 (plan adg-gate-pipeline-efficiency-e4b1c7): open ONE WAL connection for
    # the whole refresh instead of one per phase. Phases run sequentially in
    # dependency order, so a shared connection keeps the 64MB page cache warm
    # across phases, makes each phase's tables visible to the next without a
    # close/reopen, and avoids up-to-6 intermediate WAL checkpoints. Each phase
    # still commits and only closes the connection when it opened it (standalone).
    _shared_conn = connect_sqlite_for_mv(sqlite_path)
    try:
        for _label, _phase_fn in tqdm(
            _phases, desc="ADG-MV phases", unit="phase", total=len(_phases)
        ):
            all_counts.update(_phase_fn(sqlite_path, conn=_shared_conn))
    finally:
        _shared_conn.close()

    _log_summary(all_counts)
    return all_counts


def _log_summary(counts: dict[str, int]) -> None:
    """Print a compact summary of materialized view row counts."""
    total = len(counts)
    zero_rows = [n for n, c in counts.items() if c == 0]
    non_zero = total - len(zero_rows)

    print(f"[ADG-MV] Materialized view refresh complete: {total} tables")
    print(f"[ADG-MV]   Non-empty: {non_zero}  |  Empty (0-row): {len(zero_rows)}")

    col_w = max((len(n) for n in counts), default=0) + 2
    for name, count in sorted(counts.items()):
        flag = "  (empty)" if count == 0 else ""
        print(f"[ADG-MV]   {name:<{col_w}} {count:>6}{flag}")

    if zero_rows:
        print(f"[ADG-MV] NOTE: {len(zero_rows)} empty table(s) — normal if corpus has no matching patterns.")
