"""Phase F materialized views — Hotspot × Coverage risk join.

Plan: `docs/archive/windsurf/legacy-tree/plans/hotspot-coverage-pipeline-c4e8d2.md` (W2)

Family 9 — Risk × Coverage prioritization
    `mv_hotspot_coverage_risk` — per-node join of:
        * `mv_path_criticality_rollup` (criticality_score ← fan_in × fan_out
                                        × violation_count × cross_layer_edges)
        * `mv_high_fan_in_out_with_defects` (combined_risk_score)
        * `mv_debt_concentration_hotspots` (total_debt_score, hotspot_rank)
        * `coverage_by_path` (line + branch coverage_pct)
        * `test_stubs` (Mock-instantiation density — negative coverage signal)

    Adds three derived bands per node:
        * `risk_band` — P75-percentile-driven bucket of criticality_score:
              CRITICAL  ≥ P95
              HIGH      ≥ P75 and < P95
              MEDIUM    ≥ P50 and < P75
              LOW       < P50
        * `coverage_band` — absolute thresholds on coverage_pct:
              FULL       ≥ 90.0
              GOOD       70.0 ≤ x < 90.0
              PARTIAL    30.0 ≤ x < 70.0
              MINIMAL    > 0.0 and < 30.0
              ABSENT     coverage_pct = -1 (no row in coverage_by_path)
        * `priority_band` — derived from (risk_band, coverage_band):
              P1_URGENT  CRITICAL/HIGH risk & coverage ABSENT/MINIMAL
              P2_GAP     CRITICAL/HIGH risk & coverage PARTIAL
              P3_OK      CRITICAL/HIGH risk & coverage GOOD/FULL
              P4_LOW     MEDIUM risk regardless
              P5_NOOP    LOW risk
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.materialized_views.phase_c_trace_drift_debt import _snapshot_id_expr
from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv as _connect_sqlite

_PHASE_F_TABLES: tuple[str, ...] = ("mv_hotspot_coverage_risk",)


def materialize_phase_f(sqlite_path: Path, *, conn: sqlite3.Connection | None = None) -> dict[str, int]:
    """Create Phase F materialized tables. Idempotent — safe to call repeatedly.

    Depends on:
        * Phase E (must run first — produces `mv_path_criticality_rollup`,
          `mv_high_fan_in_out_with_defects`)
        * Phase C (`mv_debt_concentration_hotspots`)
        * `coverage_by_path` table populated by `tools/adg/ingest_coverage_py.py`
          (or empty / missing — handled via LEFT JOIN)
        * `test_stubs` table (best-effort LEFT JOIN; may be empty)

    Returns:
        dict mapping table_name -> row_count.
    """
    _owns_conn = conn is None
    if conn is None:
        conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -64000")
    conn.execute("PRAGMA temp_store = MEMORY")
    cur = conn.cursor()

    for tbl in reversed(_PHASE_F_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # Defensive: if `coverage_by_path` doesn't exist (ingester never ran),
    # create empty so the LEFT JOIN doesn't crash.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS coverage_by_path (
            resolved_path TEXT PRIMARY KEY,
            lines_hit     INTEGER NOT NULL DEFAULT 0,
            arcs_hit      INTEGER NOT NULL DEFAULT 0,
            context_count INTEGER NOT NULL DEFAULT 0,
            lines_total   INTEGER NOT NULL DEFAULT -1,
            coverage_pct  REAL    NOT NULL DEFAULT -1.0,
            mode          TEXT    NOT NULL DEFAULT 'empty',
            ingested_at   TEXT    NOT NULL DEFAULT ''
        )
        """
    )

    # Same defensive pattern for `test_stubs` (populated by ADG static analysis;
    # may be absent on minimal snapshots / unit-test fixtures).
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test_stubs (
            id INTEGER PRIMARY KEY,
            file_path TEXT,
            line_no INTEGER,
            mock_class TEXT,
            has_failure_config INTEGER
        )
        """
    )

    # Compute risk percentiles up-front so we have stable thresholds for the
    # CASE expression below. Using NTILE-equivalent logic.
    p50, p75, p95 = _compute_percentiles(cur, "mv_path_criticality_rollup", "criticality_score")

    # The big join. Each row is one production module ('module' entity_type)
    # joined to its coverage data (LEFT) and its test-stub density (LEFT).
    cur.execute(
        f"""
        CREATE TABLE mv_hotspot_coverage_risk AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                              AS node_id,
            n.resolved_path                   AS file,
            n.layer                           AS layer,
            COALESCE(cr.fan_in, 0)            AS fan_in,
            COALESCE(cr.fan_out, 0)           AS fan_out,
            COALESCE(cr.violation_count, 0)   AS violation_count,
            COALESCE(cr.cross_layer_edges, 0) AS cross_layer_edges,
            COALESCE(cr.criticality_score, 0.0)            AS criticality_score,
            COALESCE(hd.combined_risk_score, 0.0)          AS combined_risk_score,
            COALESCE(dc.total_debt_score, 0.0)             AS total_debt_score,
            COALESCE(dc.hotspot_rank, 0)                   AS hotspot_rank,
            COALESCE(cov.lines_hit, 0)                     AS lines_hit,
            COALESCE(cov.lines_total, -1)                  AS lines_total,
            COALESCE(cov.coverage_pct, -1.0)               AS coverage_pct,
            COALESCE(cov.arcs_hit, 0)                      AS arcs_hit,
            COALESCE(cov.context_count, 0)                 AS context_count,
            COALESCE(cov.mode, 'absent')                   AS coverage_mode,
            COALESCE(ts.mock_count, 0)                     AS mock_count,
            CASE
                WHEN COALESCE(cr.criticality_score, 0.0) <= 0.0 THEN 'LOW'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p95} THEN 'CRITICAL'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p75} THEN 'HIGH'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p50} THEN 'MEDIUM'
                ELSE 'LOW'
            END AS risk_band,
            CASE
                WHEN COALESCE(cov.coverage_pct, -1.0) < 0.0  THEN 'ABSENT'
                WHEN COALESCE(cov.coverage_pct, -1.0) >= 90.0 THEN 'FULL'
                WHEN COALESCE(cov.coverage_pct, -1.0) >= 70.0 THEN 'GOOD'
                WHEN COALESCE(cov.coverage_pct, -1.0) >= 30.0 THEN 'PARTIAL'
                WHEN COALESCE(cov.coverage_pct, -1.0) > 0.0   THEN 'MINIMAL'
                ELSE 'ABSENT'
            END AS coverage_band,
            CASE
                WHEN COALESCE(cr.criticality_score, 0.0) <= 0.0 THEN 'P5_NOOP'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p75}
                  AND (COALESCE(cov.coverage_pct, -1.0) < 30.0)
                THEN 'P1_URGENT'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p75}
                  AND COALESCE(cov.coverage_pct, -1.0) < 70.0
                THEN 'P2_GAP'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p75}
                THEN 'P3_OK'
                WHEN COALESCE(cr.criticality_score, 0.0) >= {p50}
                THEN 'P4_LOW'
                ELSE 'P5_NOOP'
            END AS priority_band
        FROM nodes n
        LEFT JOIN mv_path_criticality_rollup       cr  ON cr.node_id = n.id
        LEFT JOIN mv_high_fan_in_out_with_defects  hd  ON hd.node_id = n.id
        LEFT JOIN mv_debt_concentration_hotspots   dc  ON dc.file    = n.resolved_path
        LEFT JOIN coverage_by_path                 cov ON cov.resolved_path = n.resolved_path
        LEFT JOIN (
            SELECT file_path, COUNT(*) AS mock_count
            FROM test_stubs
            GROUP BY file_path
        ) ts ON ts.file_path = n.resolved_path
        WHERE n.entity_type = 'module'
          AND n.resolved_path != ''
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
          AND n.resolved_path NOT LIKE 'ops_scripts/%'
          AND n.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/%'
        ORDER BY criticality_score DESC, n.resolved_path
        """
    )

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_hotspot_coverage_risk_priority "
        "ON mv_hotspot_coverage_risk(priority_band, criticality_score DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_hotspot_coverage_risk_layer "
        "ON mv_hotspot_coverage_risk(layer, priority_band)"
    )

    counts = {tbl: cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0] for tbl in _PHASE_F_TABLES}
    conn.commit()
    if _owns_conn:
        conn.close()
    return counts


def _compute_percentiles(cur: sqlite3.Cursor, table: str, column: str) -> tuple[float, float, float]:
    """Compute (P50, P75, P95) for `column` in `table`.

    Returns (0.0, 0.0, 0.0) if the table is empty or doesn't exist — banding
    falls back to LOW for everyone, which is the safe default.
    """
    try:
        rows = cur.execute(
            f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}"
        ).fetchall()
    except sqlite3.OperationalError:
        return (0.0, 0.0, 0.0)
    if not rows:
        return (0.0, 0.0, 0.0)
    n = len(rows)

    # Index for percentile p (0..1): floor((n-1) * p) gives a stable, no-interpolation choice.
    def _at(p: float) -> float:
        idx = int((n - 1) * p)
        return float(rows[idx][0])

    return (_at(0.50), _at(0.75), _at(0.95))
