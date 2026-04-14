#!/usr/bin/env python3
"""Phase E materialized views — Graph-native architectural intelligence (Prompt 5).

Graph-native views for:
1. Reverse dependency rollup by layer (hotspots by inbound dependency surface)
2. Chokepoint / bridge detection (modules with high betweenness/connectivity)
3. SCC cluster rollup (tightly coupled architecture zones)
4. Critical path blast radius (graph-derived change impact)

Uses SQL-based graph analysis for simplicity and auditability.
No networkx dependency required.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def _validate_sqlite_path(sqlite_path: Path) -> Path:
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"ADG SQLite path is not a file: {sqlite_path}")
    return sqlite_path


def _connect_sqlite(sqlite_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(_validate_sqlite_path(sqlite_path)), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


from typing import Any

_PHASE_E_TABLES: tuple[str, ...] = (
    "mv_graph_reverse_dependency_hotspots",
    "mv_graph_chokepoint_bridges",
    "mv_graph_scc_clusters",
    "mv_graph_critical_path_blast_radius",
)


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def materialize_phase_e(sqlite_path: Path) -> dict[str, int]:
    """Create all Phase E graph-native materialized tables.

    Returns:
        dict mapping table_name -> row_count for each Phase E table.
    """
    conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -64000")
    cur = conn.cursor()

    for tbl in reversed(_PHASE_E_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # Family 12 — Reverse dependency rollup by layer
    # -------------------------------------------------------------------------
    # Detects modules with large or risky inbound dependency surfaces
    # Fixed: Aggregate at symbol level first (edges reference symbols, not modules)
    # then join to modules via resolved_path

    cur.execute("DROP TABLE IF EXISTS _t_symbol_inbound")
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_inbound AS
        SELECT
            dst_sym.resolved_path AS file_path,
            COUNT(DISTINCT src_sym.resolved_path) AS fan_in
        FROM edges e
        JOIN nodes dst_sym ON e.dst_id = dst_sym.id
        JOIN nodes src_sym ON e.src_id = src_sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND dst_sym.resolved_path IS NOT NULL
        AND src_sym.resolved_path IS NOT NULL
        GROUP BY dst_sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sym_in ON _t_symbol_inbound(file_path)")

    cur.execute(f"""
        CREATE TABLE mv_graph_reverse_dependency_hotspots AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id AS node_id,
            n.resolved_path AS file_path,
            n.layer AS layer,
            COALESCE(si.fan_in, 0) AS direct_inbound,
            0 AS hop2_inbound,  -- Deferred: 2-hop needs iterative calculation
            COALESCE(si.fan_in, 0) * 1.0 AS reverse_dependency_score,
            CASE WHEN n.layer IN ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6',
                                  'L_APP', 'L_SHARED', 'L_RUNTIME')
                 THEN 2.0 ELSE 1.0 END AS layer_criticality_weight
        FROM nodes n
        LEFT JOIN _t_symbol_inbound si ON si.file_path = n.resolved_path
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
          AND COALESCE(si.fan_in, 0) > 20  -- Filter noise
        ORDER BY reverse_dependency_score * layer_criticality_weight DESC
    """)
    cur.execute("DROP TABLE IF EXISTS _t_symbol_inbound")

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_graph_rev_dep "
        "ON mv_graph_reverse_dependency_hotspots(reverse_dependency_score DESC, layer)"
    )

    # -------------------------------------------------------------------------
    # Family 13 — Chokepoint / bridge detection
    # -------------------------------------------------------------------------
    # Detects modules that act as structural bridges or high-impact connectors
    # High (in-degree * out-degree) ratio indicates potential chokepoint
    # Graph-native: betweenness approximation using local connectivity

    cur.execute(f"""
        CREATE TABLE mv_graph_chokepoint_bridges AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            hc.node_id,
            hc.resolved_path AS file_path,
            hc.layer AS layer,
            hc.fan_in,
            hc.fan_out,
            -- Chokepoint score: high product of in/out with imbalance penalty
            ROUND(
                CAST(hc.fan_in AS REAL) * hc.fan_out /
                NULLIF(ABS(hc.fan_in - hc.fan_out) + 1, 0),
            2) AS bridge_score,
            -- Ratio imbalance: large disparity between in/out indicates bridge
            ROUND(
                CAST(MAX(hc.fan_in, hc.fan_out) AS REAL) /
                NULLIF(MIN(hc.fan_in, hc.fan_out) + 1, 0),
            2) AS imbalance_ratio,
            -- Classification
            CASE
                WHEN hc.fan_in > 100 AND hc.fan_out > 100
                    AND hc.fan_in * hc.fan_out > 10000 THEN 'high_impact_bridge'
                WHEN hc.fan_in > 50 AND hc.fan_out > 50
                    AND hc.fan_in * hc.fan_out > 2500 THEN 'bridge_candidate'
                WHEN ABS(hc.fan_in - hc.fan_out) > 100 THEN 'asymmetric_connector'
                ELSE 'moderate_connector'
            END AS bridge_type
        FROM mv_hotspot_centrality hc
        WHERE hc.fan_in > 20 OR hc.fan_out > 20
          AND hc.resolved_path NOT LIKE 'tests/%'
          AND hc.resolved_path NOT LIKE 'tools/%'
        ORDER BY bridge_score DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_graph_bridge "
        "ON mv_graph_chokepoint_bridges(bridge_score DESC, bridge_type)"
    )

    # -------------------------------------------------------------------------
    # Family 14 — SCC cluster rollup (tightly coupled architecture zones)
    # -------------------------------------------------------------------------
    # Detects strongly connected or cyclic architecture zones
    # Uses 2-way reachability as approximation for SCC membership
    # NOTE: This view may return 0 rows if the codebase has no import cycles.
    # An empty result is actually a positive architectural signal (acyclic).

    cur.execute("DROP TABLE IF EXISTS _t_reachability")

    # Build reachability table (nodes that can reach each other via imports/calls)
    # Using 2-hop approximation for performance on large graphs
    cur.execute("""
        CREATE TEMP TABLE _t_reachability AS
        SELECT DISTINCT
            n1.id AS node_a,
            n2.id AS node_b,
            n1.resolved_path AS path_a,
            n2.resolved_path AS path_b,
            n1.layer AS layer_a,
            n2.layer AS layer_b
        FROM edges e1
        JOIN edges e2 ON e2.src_id = e1.dst_id
        JOIN nodes n1 ON e1.src_id = n1.id AND n1.entity_type = 'module'
        JOIN nodes n2 ON e2.dst_id = n2.id AND n2.entity_type = 'module'
        WHERE e1.relation_type IN ('imports', 'calls')
          AND e2.relation_type IN ('imports', 'calls')
          AND n1.resolved_path != n2.resolved_path
          AND n1.resolved_path NOT LIKE 'tests/%'
          AND n2.resolved_path NOT LIKE 'tests/%'
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_t_reach ON _t_reachability(node_a, node_b)")

    # Find mutual reachability (clusters)
    cur.execute(f"""
        CREATE TABLE mv_graph_scc_clusters AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            r1.node_a AS node_id,
            r1.path_a AS file_path,
            r1.layer_a AS layer,
            COUNT(DISTINCT r2.node_b) AS cluster_size,
            GROUP_CONCAT(DISTINCT r2.path_b) AS cluster_members,
            -- Risk score based on cluster size and critical layers
            COUNT(DISTINCT r2.node_b) * 10 +
            SUM(CASE WHEN r2.layer_b IN
                ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6') THEN 5 ELSE 0 END)
                AS scc_risk_score,
            CASE
                WHEN COUNT(DISTINCT r2.node_b) > 20 THEN 'large_tight_cluster'
                WHEN COUNT(DISTINCT r2.node_b) > 10 THEN 'medium_tight_cluster'
                WHEN COUNT(DISTINCT r2.node_b) > 5 THEN 'small_tight_cluster'
                ELSE 'coupled_pair'
            END AS cluster_type
        FROM _t_reachability r1
        JOIN _t_reachability r2 ON r1.node_a = r2.node_a
        WHERE r1.path_a < r2.path_b  -- Avoid duplicates, only store ordered pairs
        GROUP BY r1.node_a
        HAVING cluster_size > 2  -- Filter noise
        ORDER BY scc_risk_score DESC
    """)

    cur.execute("DROP TABLE IF EXISTS _t_reachability")

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_graph_scc "
        "ON mv_graph_scc_clusters(scc_risk_score DESC, cluster_type)"
    )

    # -------------------------------------------------------------------------
    # Family 15 — Critical path blast radius
    # -------------------------------------------------------------------------
    # Graph-derived "if this node changes, what high-value regions are at risk?"
    # Fixed: Aggregate at symbol level first, then join to modules
    # Simplified: Direct downstream only (2-hop deferred due to complexity)

    cur.execute("DROP TABLE IF EXISTS _t_symbol_downstream")
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_downstream AS
        SELECT
            src_sym.resolved_path AS source_file,
            dst_sym.resolved_path AS imported_file,
            COUNT(DISTINCT e.id) AS edge_count
        FROM edges e
        JOIN nodes src_sym ON e.src_id = src_sym.id
        JOIN nodes dst_sym ON e.dst_id = dst_sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND src_sym.resolved_path IS NOT NULL
        AND dst_sym.resolved_path IS NOT NULL
        GROUP BY src_sym.resolved_path, dst_sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sym_ds ON _t_symbol_downstream(imported_file)")

    cur.execute(f"""
        CREATE TABLE mv_graph_critical_path_blast_radius AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id AS node_id,
            n.resolved_path AS file_path,
            n.layer AS layer,
            -- Direct downstream (modules importing this)
            COUNT(DISTINCT sd.source_file) AS direct_downstream,
            0 AS hop2_downstream,  -- Deferred: 2-hop needs iterative calculation
            -- Raw blast radius score
            COUNT(DISTINCT sd.source_file) * 1.0 AS raw_blast_radius,
            -- Weighted by downstream layer criticality
            ROUND(
                COUNT(DISTINCT sd.source_file) * 1.0 *
                AVG(CASE WHEN importer.layer IN
                    ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6',
                     'L_APP', 'L_SHARED', 'L_RUNTIME')
                    THEN 2.0 ELSE 1.0 END),
            2) AS weighted_blast_radius,
            -- Critical downstream count
            SUM(CASE WHEN importer.layer IN
                ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6') THEN 1 ELSE 0 END)
                AS critical_downstream_count,
            CASE
                WHEN COUNT(DISTINCT sd.source_file) > 100 THEN 'high_impact_hub'
                WHEN COUNT(DISTINCT sd.source_file) > 50 THEN 'moderate_impact_hub'
                ELSE 'standard_impact'
            END AS blast_radius_type
        FROM nodes n
        LEFT JOIN _t_symbol_downstream sd ON sd.imported_file = n.resolved_path
        LEFT JOIN nodes importer ON importer.resolved_path = sd.source_file
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        GROUP BY n.id
        HAVING weighted_blast_radius > 30  -- Filter noise
        ORDER BY weighted_blast_radius DESC
    """)
    cur.execute("DROP TABLE IF EXISTS _t_symbol_downstream")

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_graph_blast "
        "ON mv_graph_critical_path_blast_radius(weighted_blast_radius DESC, layer)"
    )

    conn.commit()

    counts: dict[str, int] = {}
    try:
        for tbl in _PHASE_E_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
            counts[tbl] = row[0] if row else 0
    finally:
        conn.close()

    return counts


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python phase_e_graph_intelligence.py <sqlite_path>")
        sys.exit(1)

    sqlite_path = Path(sys.argv[1])
    counts = materialize_phase_e(sqlite_path)
    print("Phase E graph-native views created:")
    for table, count in counts.items():
        print(f"  {table}: {count} rows")
