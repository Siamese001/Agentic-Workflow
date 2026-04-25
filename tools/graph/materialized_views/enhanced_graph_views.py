"""Enhanced graph materialized views for advanced analysis.

Adds high-value graph analyses:
1. Multi-hop dependency analysis (2-5 hop fan-in/out)
2. Layer transition matrices (cross-layer flow patterns)
3. Symbol-level centrality (functions/classes with high connectivity)
4. Risk-weighted impact scores (combines violations + centrality)
5. Architectural debt concentration hotspots
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


_ENHANCED_TABLES: tuple[str, ...] = (
    "mv_multi_hop_dependency_analysis",
    "mv_layer_transition_matrix",
    "mv_symbol_level_centrality",
    "mv_risk_weighted_impact_scores",
    "mv_architectural_debt_concentration",
)


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def materialize_enhanced_graph_views(sqlite_path: Path) -> dict[str, int]:
    """Create enhanced graph materialized views for advanced analysis.

    Returns:
        dict mapping table_name -> row_count for each enhanced view.
    """
    conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -128000")
    cur = conn.cursor()

    # Drop existing tables
    for tbl in reversed(_ENHANCED_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # 1. Multi-hop dependency analysis (2-5 hop fan-in/out)
    # -------------------------------------------------------------------------
    cur.execute("DROP TABLE IF EXISTS _t_hop_1")
    cur.execute("DROP TABLE IF EXISTS _t_hop_2")
    cur.execute("DROP TABLE IF EXISTS _t_hop_3")

    # 1-hop dependencies (direct)
    cur.execute("""
        CREATE TEMP TABLE _t_hop_1 AS
        SELECT DISTINCT
            src.resolved_path AS src_path,
            dst.resolved_path AS dst_path,
            src.layer AS src_layer,
            dst.layer AS dst_layer,
            1 AS hop_distance
        FROM edges e
        JOIN nodes src ON e.src_id = src.id
        JOIN nodes dst ON e.dst_id = dst.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND src.resolved_path IS NOT NULL
        AND dst.resolved_path IS NOT NULL
        AND src.resolved_path != dst.resolved_path
    """)

    # 2-hop dependencies
    cur.execute("""
        CREATE TEMP TABLE _t_hop_2 AS
        SELECT DISTINCT
            h1.src_path AS src_path,
            h2.dst_path AS dst_path,
            h1.src_layer AS src_layer,
            h2.dst_layer AS dst_layer,
            2 AS hop_distance
        FROM _t_hop_1 h1
        JOIN _t_hop_1 h2 ON h1.dst_path = h2.src_path
        WHERE h1.src_path != h2.dst_path
    """)

    # 3-hop dependencies
    cur.execute("""
        CREATE TEMP TABLE _t_hop_3 AS
        SELECT DISTINCT
            h2.src_path AS src_path,
            h3.dst_path AS dst_path,
            h2.src_layer AS src_layer,
            h3.dst_layer AS dst_layer,
            3 AS hop_distance
        FROM _t_hop_2 h2
        JOIN _t_hop_1 h3 ON h2.dst_path = h3.src_path
        WHERE h2.src_path != h3.dst_path
    """)

    # Combine all hops for analysis
    cur.execute(f"""
        CREATE TABLE mv_multi_hop_dependency_analysis AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id AS node_id,
            n.resolved_path AS file_path,
            n.layer AS layer,
            COALESCE(h1_1.count, 0) AS hop1_fan_in,
            COALESCE(h1_2.count, 0) AS hop1_fan_out,
            COALESCE(h2_1.count, 0) AS hop2_fan_in,
            COALESCE(h2_2.count, 0) AS hop2_fan_out,
            COALESCE(h3_1.count, 0) AS hop3_fan_in,
            COALESCE(h3_2.count, 0) AS hop3_fan_out,
            -- Multi-hop impact score (exponential decay)
            COALESCE(h1_1.count, 0) * 1.0 +
            COALESCE(h2_1.count, 0) * 0.5 +
            COALESCE(h3_1.count, 0) * 0.25 AS multi_hop_impact_score
        FROM nodes n
        LEFT JOIN (
            SELECT dst_path, COUNT(*) as count FROM _t_hop_1 GROUP BY dst_path
        ) h1_1 ON h1_1.dst_path = n.resolved_path
        LEFT JOIN (
            SELECT src_path, COUNT(*) as count FROM _t_hop_1 GROUP BY src_path
        ) h1_2 ON h1_2.src_path = n.resolved_path
        LEFT JOIN (
            SELECT dst_path, COUNT(*) as count FROM _t_hop_2 GROUP BY dst_path
        ) h2_1 ON h2_1.dst_path = n.resolved_path
        LEFT JOIN (
            SELECT src_path, COUNT(*) as count FROM _t_hop_2 GROUP BY src_path
        ) h2_2 ON h2_2.src_path = n.resolved_path
        LEFT JOIN (
            SELECT dst_path, COUNT(*) as count FROM _t_hop_3 GROUP BY dst_path
        ) h3_1 ON h3_1.dst_path = n.resolved_path
        LEFT JOIN (
            SELECT src_path, COUNT(*) as count FROM _t_hop_3 GROUP BY src_path
        ) h3_2 ON h3_2.src_path = n.resolved_path
        WHERE n.entity_type = 'module'
        AND n.resolved_path IS NOT NULL
    """)

    # -------------------------------------------------------------------------
    # 2. Layer transition matrix (cross-layer flow patterns)
    # -------------------------------------------------------------------------
    cur.execute(f"""
        CREATE TABLE mv_layer_transition_matrix AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src_layer,
            dst_layer,
            COUNT(*) AS transition_count,
            COUNT(DISTINCT src_path) AS unique_sources,
            COUNT(DISTINCT dst_path) AS unique_destinations,
            -- Transition risk based on layer gravity violations
            CASE
                WHEN src_layer = dst_layer THEN 0.5  -- Same layer: low risk
                WHEN src_layer < dst_layer THEN 1.0  -- Upward flow: normal
                ELSE 2.0  -- Downward flow: potential violation
            END AS transition_risk_weight
        FROM _t_hop_1
        GROUP BY src_layer, dst_layer
        ORDER BY transition_count DESC
    """)

    # -------------------------------------------------------------------------
    # 3. Symbol-level centrality (functions/classes with high connectivity)
    # -------------------------------------------------------------------------
    cur.execute("DROP TABLE IF EXISTS _t_symbol_centrality")
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_centrality AS
        SELECT
            n.id AS node_id,
            n.resolved_path AS file_path,
            n.symbol_name AS symbol_name,
            n.symbol_type AS symbol_type,
            n.layer AS layer,
            -- In-degree centrality (how many depend on this symbol)
            COUNT(DISTINCT e_in.src_id) AS in_degree,
            -- Out-degree centrality (how many this depends on)
            COUNT(DISTINCT e_out.dst_id) AS out_degree,
            -- Betweenness approximation (symbols that connect layers)
            COUNT(DISTINCT CASE WHEN src.layer != dst.layer THEN e_in.src_id END) AS cross_layer_connections
        FROM nodes n
        LEFT JOIN edges e_in ON n.id = e_in.dst_id AND e_in.relation_type IN ('calls', 'imports')
        LEFT JOIN nodes src ON e_in.src_id = src.id
        LEFT JOIN edges e_out ON n.id = e_out.src_id AND e_out.relation_type IN ('calls', 'imports')
        LEFT JOIN nodes dst ON e_out.dst_id = dst.id
        WHERE n.entity_type = 'symbol'
        AND n.symbol_name IS NOT NULL
        GROUP BY n.id, n.resolved_path, n.symbol_name, n.symbol_type, n.layer
    """)

    cur.execute(f"""
        CREATE TABLE mv_symbol_level_centrality AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            node_id,
            file_path,
            symbol_name,
            symbol_type,
            layer,
            in_degree,
            out_degree,
            cross_layer_connections,
            -- Combined centrality score
            (in_degree * 1.0 + out_degree * 0.8 + cross_layer_connections * 1.5) AS centrality_score,
            -- High-risk symbols (high centrality in critical layers)
            CASE
                WHEN layer IN ('L0', 'L5') AND (in_degree + out_degree) > 10 THEN 1.0
                WHEN layer IN ('L3', 'L4') AND (in_degree + out_degree) > 20 THEN 0.8
                ELSE 0.5
            END AS risk_factor
        FROM _t_symbol_centrality
        WHERE in_degree > 0 OR out_degree > 0
        ORDER BY centrality_score DESC
    """)

    # -------------------------------------------------------------------------
    # 4. Risk-weighted impact scores (violations + centrality)
    # -------------------------------------------------------------------------
    cur.execute(f"""
        CREATE TABLE mv_risk_weighted_impact_scores AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id AS node_id,
            n.resolved_path AS file_path,
            n.layer AS layer,
            COALESCE(mh.multi_hop_impact_score, 0) AS dependency_impact,
            COALESCE(viol.violation_count, 0) AS violation_count,
            COALESCE(viol.severity_score, 0) AS severity_score,
            -- Combined risk score
            (COALESCE(mh.multi_hop_impact_score, 0) * 1.0 +
             COALESCE(viol.severity_score, 0) * 2.0) AS combined_risk_score,
            -- Risk tier
            CASE
                WHEN COALESCE(viol.severity_score, 0) > 50 THEN 'CRITICAL'
                WHEN COALESCE(mh.multi_hop_impact_score, 0) > 100 THEN 'HIGH_IMPACT'
                WHEN COALESCE(viol.violation_count, 0) > 5 THEN 'VIOLATION_PRONE'
                ELSE 'NORMAL'
            END AS risk_tier
        FROM nodes n
        LEFT JOIN mv_multi_hop_dependency_analysis mh ON n.id = mh.node_id
        LEFT JOIN (
            SELECT
                node_id,
                COUNT(*) AS violation_count,
                SUM(
                    CASE violation_type
                        WHEN 'P0' THEN 100
                        WHEN 'P1' THEN 50
                        WHEN 'P2' THEN 10
                        WHEN 'P3' THEN 5
                        ELSE 1
                    END
                ) AS severity_score
            FROM violations
            GROUP BY node_id
        ) viol ON n.id = viol.node_id
        WHERE n.entity_type = 'module'
        AND n.resolved_path IS NOT NULL
    """)

    # -------------------------------------------------------------------------
    # 5. Architectural debt concentration hotspots
    # -------------------------------------------------------------------------
    cur.execute(f"""
        CREATE TABLE mv_architectural_debt_concentration AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            layer,
            COUNT(*) AS module_count,
            SUM(CASE WHEN risk_tier = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_modules,
            SUM(CASE WHEN risk_tier = 'HIGH_IMPACT' THEN 1 ELSE 0 END) AS high_impact_modules,
            SUM(CASE WHEN risk_tier = 'VIOLATION_PRONE' THEN 1 ELSE 0 END) AS violation_prone_modules,
            AVG(combined_risk_score) AS avg_risk_score,
            MAX(combined_risk_score) AS max_risk_score,
            -- Debt concentration ratio
            (SUM(CASE WHEN risk_tier IN ('CRITICAL', 'HIGH_IMPACT') THEN 1 ELSE 0 END) * 1.0 /
             NULLIF(COUNT(*), 0)) AS debt_concentration_ratio
        FROM mv_risk_weighted_impact_scores
        GROUP BY layer
        ORDER BY debt_concentration_ratio DESC
    """)

    # Get row counts
    row_counts = {}
    for tbl in _ENHANCED_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        row_counts[tbl] = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return row_counts


if __name__ == "__main__":
    # Test run with current snapshot
    from tools.generate.core import _get_latest_adg_path

    sqlite_path = _get_latest_adg_path()
    if sqlite_path:
        counts = materialize_enhanced_graph_views(sqlite_path)
        print("Enhanced graph views created:")
        for table, count in counts.items():
            print(f"  {table}: {count} rows")
    else:
        print("No ADG snapshot found")
