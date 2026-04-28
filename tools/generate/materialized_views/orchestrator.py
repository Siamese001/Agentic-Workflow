"""Orchestrator for ADG SQLite materialized view refresh.

Calls Phase A → B → C → D → E in dependency order.
Returns combined row-count dict and logs a summary table.
"""

from __future__ import annotations

from pathlib import Path

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


def _validate_sqlite_path(sqlite_path: Path) -> Path:
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"ADG SQLite path is not a file: {sqlite_path}")
    return sqlite_path


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
    sqlite_path = _validate_sqlite_path(sqlite_path)
    all_counts: dict[str, int] = {}

    counts_a = materialize_phase_a(sqlite_path)
    all_counts.update(counts_a)

    counts_b = materialize_phase_b(sqlite_path)
    all_counts.update(counts_b)

    counts_c = materialize_phase_c(sqlite_path)
    all_counts.update(counts_c)

    counts_d = materialize_phase_d(sqlite_path)
    all_counts.update(counts_d)

    # Phase E: Graph-native intelligence (Prompt 5)
    counts_e = materialize_phase_e(sqlite_path)
    all_counts.update(counts_e)

    # Phase F: Hotspot × Coverage risk join (plan hotspot-coverage-pipeline-c4e8d2)
    # Depends on Phase C (debt) + Phase E (criticality, fan-in/out with defects)
    # + the `coverage_by_path` table written by `tools/adg/ingest_coverage_py.py`
    # ahead of this call. LEFT JOINs make missing data fail-soft.
    counts_f = materialize_phase_f(sqlite_path)
    all_counts.update(counts_f)

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
