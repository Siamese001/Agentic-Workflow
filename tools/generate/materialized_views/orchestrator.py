"""Orchestrator for ADG SQLite materialized-view refresh.

Calls Phase A → B → C → D → E → F, hardens the canonical SQLite file,
materializes Phase G repository health, refreshes planner statistics, and
checkpoint-seals the portable main database.
"""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm  # §16 progress-bar compliance for the multi-phase MV refresh

try:
    from tools.generate.materialized_views.sqlite_helpers import (
        connect_sqlite_for_mv,
        validate_sqlite_path,
    )
    from tools.generate.sqlite_hardening import harden_sqlite_connection, seal_sqlite_connection
except ImportError:  # pragma: no cover — standalone ``python -m materialized_views`` layout
    from materialized_views.sqlite_helpers import (
        connect_sqlite_for_mv,
        validate_sqlite_path,
    )
    from sqlite_hardening import harden_sqlite_connection, seal_sqlite_connection

try:
    from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
    from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b
    from tools.generate.materialized_views.phase_c_trace_drift_debt import materialize_phase_c
    from tools.generate.materialized_views.phase_d_snapshot_regression import materialize_phase_d
    from tools.generate.materialized_views.phase_e_graph_intelligence import materialize_phase_e
    from tools.generate.materialized_views.phase_f_hotspot_coverage import materialize_phase_f
    from tools.generate.materialized_views.phase_g_repo_health import materialize_phase_g
except ImportError:
    from materialized_views.phase_a_path_authority import materialize_phase_a
    from materialized_views.phase_b_capability_tool_task import materialize_phase_b
    from materialized_views.phase_c_trace_drift_debt import materialize_phase_c
    from materialized_views.phase_d_snapshot_regression import materialize_phase_d
    from materialized_views.phase_e_graph_intelligence import materialize_phase_e
    from materialized_views.phase_f_hotspot_coverage import materialize_phase_f
    from materialized_views.phase_g_repo_health import materialize_phase_g


def materialize_all_views(sqlite_path: Path) -> dict[str, int]:
    """Refresh all configured ADG materialized tables. Idempotent.

    Phase G runs only after A–F and SQLite hardening, because its graph-truth
    dimension consumes the recorded quick-check and foreign-key evidence.
    A shared WAL connection keeps upstream tables and planner pages warm.

    Args:
        sqlite_path: Path to the live ADG SQLite database.

    Returns:
        Mapping from every materialized table name to its post-refresh row count.
    """

    sqlite_path = validate_sqlite_path(sqlite_path)
    all_counts: dict[str, int] = {}

    # Dependency order is load-bearing:
    # A → B,C (depend on A) → D (A+B+C) → E (A+B) → F (A/B/C + coverage)
    # → SQLite hardening → G (all prior evidence + hardening receipt).
    base_phases = (
        ("A path/authority", materialize_phase_a),
        ("B capability/tool/task", materialize_phase_b),
        ("C trace/drift/debt", materialize_phase_c),
        ("D snapshot/regression", materialize_phase_d),
        ("E graph-intelligence", materialize_phase_e),
        ("F hotspot×coverage", materialize_phase_f),
    )

    shared_conn = connect_sqlite_for_mv(sqlite_path)
    try:
        with tqdm(total=len(base_phases) + 3, desc="ADG-MV phases", unit="phase") as progress:
            for label, phase_fn in base_phases:
                progress.set_postfix_str(label, refresh=False)
                all_counts.update(phase_fn(sqlite_path, conn=shared_conn))
                progress.update(1)

            progress.set_postfix_str("SQLite hardening", refresh=False)
            hardening = harden_sqlite_connection(shared_conn)
            progress.update(1)

            progress.set_postfix_str("G repository health", refresh=False)
            all_counts.update(materialize_phase_g(sqlite_path, conn=shared_conn))
            # Phase G adds indexes after the hardening pass; refresh planner
            # statistics once more before publishing the read artifact.
            shared_conn.execute("PRAGMA optimize")
            shared_conn.commit()
            progress.update(1)

            progress.set_postfix_str("SQLite portable seal", refresh=False)
            seal = seal_sqlite_connection(shared_conn)
            progress.update(1)
    finally:
        shared_conn.close()

    print(
        "[ADG-MV] SQLite hardening: "
        f"quick_check={hardening.quick_check} "
        f"foreign_keys={hardening.foreign_key_violation_count} "
        f"indexes={hardening.index_count} (+{hardening.indexes_created}) "
        f"user_version={hardening.user_version} "
        f"journal={seal.journal_mode} wal_busy={seal.wal_busy}"
    )
    _log_summary(all_counts)
    return all_counts


def _log_summary(counts: dict[str, int]) -> None:
    """Print a compact summary of materialized-view row counts."""

    total = len(counts)
    zero_rows = [name for name, count in counts.items() if count == 0]
    non_zero = total - len(zero_rows)

    print(f"[ADG-MV] Materialized view refresh complete: {total} tables")
    print(f"[ADG-MV]   Non-empty: {non_zero}  |  Empty (0-row): {len(zero_rows)}")

    col_w = max((len(name) for name in counts), default=0) + 2
    for name, count in sorted(counts.items()):
        flag = "  (empty)" if count == 0 else ""
        print(f"[ADG-MV]   {name:<{col_w}} {count:>6}{flag}")

    if zero_rows:
        print(
            f"[ADG-MV] NOTE: {len(zero_rows)} empty table(s) — " "normal if corpus has no matching patterns."
        )
