"""Direct SQLite helper utilities for ad-hoc graph queries.

Provides convenient functions for common graph analysis patterns:
1. K-hop dependency queries
2. Layer transition analysis
3. Symbol centrality queries
4. Risk-weighted impact calculations
5. Blast radius analysis

All functions work directly with sqlite3 for maximum performance
and can be used by agents without MCP overhead.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add repo root for imports
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.generate.core import _get_latest_adg_path


class ADGSQLiteHelper:
    """Helper class for direct ADG SQLite queries with common graph patterns."""

    def __init__(self, sqlite_path: Optional[Path] = None):
        """Initialize helper with ADG SQLite path.

        Args:
            sqlite_path: Path to ADG SQLite file (auto-detected if None)
        """
        if sqlite_path is None:
            sqlite_path = _get_latest_adg_path()

        if not sqlite_path:
            raise ValueError("No ADG SQLite file found")

        self.sqlite_path = sqlite_path
        self._conn = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create SQLite connection with optimal settings."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.sqlite_path), timeout=30)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA cache_size = -128000")
            self._conn.execute("PRAGMA temp_store = MEMORY")
        return self._conn

    def close(self) -> None:
        """Close SQLite connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_k_hop_dependencies(
        self,
        node_id: Union[str, int],
        direction: str = "outbound",
        max_hops: int = 3,
        relation_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get k-hop dependencies for a node.

        Args:
            node_id: Starting node ID
            direction: "outbound" (what this depends on) or "inbound" (what depends on this)
            max_hops: Maximum number of hops to explore
            relation_types: List of relation types to include (default: ['imports', 'calls'])

        Returns:
            List of dependency paths with hop distance and node details
        """
        if relation_types is None:
            relation_types = ["imports", "calls"]

        conn = self._get_connection()
        cur = conn.cursor()

        # Build recursive CTE for k-hop analysis
        rel_type_placeholders = ",".join(["?" for _ in relation_types])

        if direction == "outbound":
            cte = f"""
            WITH RECURSIVE hop_analysis AS (
                -- Base case: direct dependencies
                SELECT
                    e.dst_id as target_id,
                    n.resolved_path as target_path,
                    n.layer as target_layer,
                    n.entity_type as target_type,
                    n.symbol_name as target_symbol,
                    e.relation_type,
                    1 as hop_distance,
                    CAST(e.dst_id || '|' || e.relation_type AS TEXT) as path_trace
                FROM edges e
                JOIN nodes n ON e.dst_id = n.id
                WHERE e.src_id = ?
                AND e.relation_type IN ({rel_type_placeholders})
                AND n.resolved_path IS NOT NULL

                UNION ALL

                -- Recursive case: extend paths
                SELECT
                    e.dst_id as target_id,
                    n.resolved_path as target_path,
                    n.layer as target_layer,
                    n.entity_type as target_type,
                    n.symbol_name as target_symbol,
                    e.relation_type,
                    ha.hop_distance + 1 as hop_distance,
                    ha.path_trace || '->' || e.dst_id || '|' || e.relation_type as path_trace
                FROM edges e
                JOIN nodes n ON e.dst_id = n.id
                JOIN hop_analysis ha ON e.src_id = ha.target_id
                WHERE ha.hop_distance < ?
                AND e.relation_type IN ({rel_type_placeholders})
                AND n.resolved_path IS NOT NULL
                -- Prevent cycles
                AND INSTR(ha.path_trace, e.dst_id || '|' || e.relation_type) = 0
            )
            SELECT * FROM hop_analysis ORDER BY hop_distance, target_path
            """
        else:  # inbound
            cte = f"""
            WITH RECURSIVE hop_analysis AS (
                -- Base case: direct dependents
                SELECT
                    e.src_id as target_id,
                    n.resolved_path as target_path,
                    n.layer as target_layer,
                    n.entity_type as target_type,
                    n.symbol_name as target_symbol,
                    e.relation_type,
                    1 as hop_distance,
                    CAST(e.src_id || '|' || e.relation_type AS TEXT) as path_trace
                FROM edges e
                JOIN nodes n ON e.src_id = n.id
                WHERE e.dst_id = ?
                AND e.relation_type IN ({rel_type_placeholders})
                AND n.resolved_path IS NOT NULL

                UNION ALL

                -- Recursive case: extend paths
                SELECT
                    e.src_id as target_id,
                    n.resolved_path as target_path,
                    n.layer as target_layer,
                    n.entity_type as target_type,
                    n.symbol_name as target_symbol,
                    e.relation_type,
                    ha.hop_distance + 1 as hop_distance,
                    ha.path_trace || '->' || e.src_id || '|' || e.relation_type as path_trace
                FROM edges e
                JOIN nodes n ON e.src_id = n.id
                JOIN hop_analysis ha ON e.dst_id = ha.target_id
                WHERE ha.hop_distance < ?
                AND e.relation_type IN ({rel_type_placeholders})
                AND n.resolved_path IS NOT NULL
                -- Prevent cycles
                AND INSTR(ha.path_trace, e.src_id || '|' || e.relation_type) = 0
            )
            SELECT * FROM hop_analysis ORDER BY hop_distance, target_path
            """

        params = [node_id, max_hops] + relation_types + [max_hops] + relation_types
        cur.execute(cte, params)

        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_layer_transition_matrix(self, relation_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get layer transition matrix showing cross-layer dependencies.

        Args:
            relation_types: List of relation types to include

        Returns:
            List of layer transitions with counts and risk scores
        """
        if relation_types is None:
            relation_types = ["imports", "calls"]

        conn = self._get_connection()
        cur = conn.cursor()

        rel_type_placeholders = ",".join(["?" for _ in relation_types])
        cur.execute(
            f"""
            SELECT
                src.layer as source_layer,
                dst.layer as target_layer,
                COUNT(*) as transition_count,
                COUNT(DISTINCT src.resolved_path) as unique_sources,
                COUNT(DISTINCT dst.resolved_path) as unique_targets,
                -- Risk assessment based on layer gravity
                CASE
                    WHEN src.layer = dst.layer THEN 0.5  -- Same layer
                    WHEN src.layer < dst.layer THEN 1.0  -- Upward flow (normal)
                    ELSE 2.0  -- Downward flow (potential violation)
                END as risk_weight,
                -- Most common transition type
                (
                    SELECT e.relation_type
                    FROM edges e2
                    JOIN nodes n2 ON e2.src_id = n2.id
                    WHERE e2.dst_id = dst.id
                    AND n2.layer = src.layer
                    AND e2.relation_type IN ({rel_type_placeholders})
                    GROUP BY e2.relation_type
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ) as dominant_relation_type
            FROM edges e
            JOIN nodes src ON e.src_id = src.id
            JOIN nodes dst ON e.dst_id = dst.id
            WHERE e.relation_type IN ({rel_type_placeholders})
            AND src.layer IS NOT NULL
            AND dst.layer IS NOT NULL
            AND src.layer != dst.layer  -- Only cross-layer transitions
            GROUP BY src.layer, dst.layer
            ORDER BY transition_count DESC, risk_weight DESC
        """,
            relation_types + relation_types,
        )

        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_symbol_centrality(
        self, min_connections: int = 1, symbol_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get symbol-level centrality metrics.

        Args:
            min_connections: Minimum total connections to include
            symbol_types: Filter by symbol types (function, class, etc.)

        Returns:
            List of symbols with centrality metrics
        """
        conn = self._get_connection()
        cur = conn.cursor()

        symbol_type_filter = ""
        params = [min_connections]
        if symbol_types:
            placeholders = ",".join(["?" for _ in symbol_types])
            symbol_type_filter = f"AND n.symbol_type IN ({placeholders})"
            params.extend(symbol_types)

        cur.execute(
            f"""
            SELECT
                n.id as symbol_id,
                n.resolved_path as file_path,
                n.layer as layer,
                n.symbol_name as symbol_name,
                n.symbol_type as symbol_type,
                -- In-degree (how many depend on this symbol)
                (
                    SELECT COUNT(DISTINCT e_in.src_id)
                    FROM edges e_in
                    WHERE e_in.dst_id = n.id
                    AND e_in.relation_type IN ('calls', 'imports')
                ) as in_degree,
                -- Out-degree (how many this symbol depends on)
                (
                    SELECT COUNT(DISTINCT e_out.dst_id)
                    FROM edges e_out
                    WHERE e_out.src_id = n.id
                    AND e_out.relation_type IN ('calls', 'imports')
                ) as out_degree,
                -- Cross-layer connections
                (
                    SELECT COUNT(DISTINCT CASE
                        WHEN src.layer != dst.layer THEN e_in.src_id
                        WHEN src.layer != dst.layer THEN e_out.dst_id
                    END)
                    FROM edges e_cross
                    JOIN nodes src ON e_cross.src_id = src.id
                    JOIN nodes dst ON e_cross.dst_id = dst.id
                    WHERE (e_cross.src_id = n.id OR e_cross.dst_id = n.id)
                    AND e_cross.relation_type IN ('calls', 'imports')
                    AND src.layer != dst.layer
                ) as cross_layer_connections,
                -- Combined centrality score
                (
                    (SELECT COUNT(DISTINCT e_in.src_id) FROM edges e_in WHERE e_in.dst_id = n.id AND e_in.relation_type IN ('calls', 'imports')) * 1.0 +
                    (SELECT COUNT(DISTINCT e_out.dst_id) FROM edges e_out WHERE e_out.src_id = n.id AND e_out.relation_type IN ('calls', 'imports')) * 0.8 +
                    COALESCE((
                        SELECT COUNT(DISTINCT CASE
                            WHEN src.layer != dst.layer THEN e_in.src_id
                            WHEN src.layer != dst.layer THEN e_out.dst_id
                        END)
                        FROM edges e_cross
                        JOIN nodes src ON e_cross.src_id = src.id
                        JOIN nodes dst ON e_cross.dst_id = dst.id
                        WHERE (e_cross.src_id = n.id OR e_cross.dst_id = n.id)
                        AND e_cross.relation_type IN ('calls', 'imports')
                        AND src.layer != dst.layer
                    ), 0) * 1.5
                ) as centrality_score
            FROM nodes n
            WHERE n.entity_type = 'symbol'
            AND n.symbol_name IS NOT NULL
            {symbol_type_filter}
            HAVING (
                (SELECT COUNT(DISTINCT e_in.src_id) FROM edges e_in WHERE e_in.dst_id = n.id AND e_in.relation_type IN ('calls', 'imports')) +
                (SELECT COUNT(DISTINCT e_out.dst_id) FROM edges e_out WHERE e_out.src_id = n.id AND e_out.relation_type IN ('calls', 'imports'))
            ) >= ?
            ORDER BY centrality_score DESC
        """,
            params,
        )

        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_blast_radius(
        self, node_ids: List[Union[str, int]], max_hops: int = 3, include_violations: bool = True
    ) -> Dict[str, Any]:
        """Calculate blast radius for multiple nodes.

        Args:
            node_ids: List of starting node IDs
            max_hops: Maximum hops to analyze
            include_violations: Whether to include violation counts

        Returns:
            Dict with blast radius analysis
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # Get all reachable nodes within max_hops
        node_placeholders = ",".join(["?" for _ in node_ids])
        cur.execute(
            f"""
            WITH RECURSIVE blast_radius AS (
                -- Base case: starting nodes
                SELECT
                    id as node_id,
                    resolved_path as file_path,
                    layer,
                    entity_type,
                    0 as hop_distance,
                    CAST(id AS TEXT) as path_trace
                FROM nodes
                WHERE id IN ({node_placeholders})

                UNION ALL

                -- Recursive case: expand outward
                SELECT
                    CASE
                        WHEN e.src_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) THEN e.dst_id
                        WHEN e.dst_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) THEN e.src_id
                    END as node_id,
                    n.resolved_path as file_path,
                    n.layer,
                    n.entity_type,
                    br.hop_distance + 1 as hop_distance,
                    br.path_trace || '->' ||
                    CASE
                        WHEN e.src_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) THEN e.dst_id
                        WHEN e.dst_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) THEN e.src_id
                    END as path_trace
                FROM edges e
                JOIN nodes n ON (
                    (e.src_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) AND e.dst_id = n.id) OR
                    (e.dst_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) AND e.src_id = n.id)
                )
                JOIN blast_radius br ON (
                    (e.src_id = br.node_id AND br.hop_distance < ?) OR
                    (e.dst_id = br.node_id AND br.hop_distance < ?)
                )
                WHERE br.hop_distance < ?
                AND e.relation_type IN ('imports', 'calls')
                AND n.resolved_path IS NOT NULL
                AND INSTR(br.path_trace,
                    CASE
                        WHEN e.src_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) THEN e.dst_id
                        WHEN e.dst_id IN (SELECT node_id FROM blast_radius WHERE hop_distance < ?) THEN e.src_id
                    END
                ) = 0  -- Prevent cycles
            )
            SELECT
                node_id,
                file_path,
                layer,
                entity_type,
                MIN(hop_distance) as min_hop_distance,
                COUNT(*) as reach_paths,
                GROUP_CONCAT(DISTINCT path_trace) as all_paths
            FROM blast_radius
            GROUP BY node_id, file_path, layer, entity_type
            ORDER BY min_hop_distance, file_path
        """,
            [max_hops] * 9 + node_ids,
        )

        columns = [desc[0] for desc in cur.description]
        reachable_nodes = []
        for row in cur.fetchall():
            reachable_nodes.append(dict(zip(columns, row)))

        # Add violation counts if requested
        if include_violations:
            reachable_node_ids = [r["node_id"] for r in reachable_nodes]
            if reachable_node_ids:
                placeholders = ",".join(["?" for _ in reachable_node_ids])
                cur.execute(
                    f"""
                    SELECT
                        node_id,
                        COUNT(*) as violation_count,
                        SUM(
                            CASE violation_type
                                WHEN 'P0' THEN 100
                                WHEN 'P1' THEN 50
                                WHEN 'P2' THEN 10
                                WHEN 'P3' THEN 5
                                ELSE 1
                            END
                        ) as severity_score
                    FROM violations
                    WHERE node_id IN ({placeholders})
                    GROUP BY node_id
                """,
                    reachable_node_ids,
                )

                violation_map = {row[0]: {"count": row[1], "severity": row[2]} for row in cur.fetchall()}

                # Add violation data to reachable nodes
                for node in reachable_nodes:
                    if node["node_id"] in violation_map:
                        node["violation_count"] = violation_map[node["node_id"]]["count"]
                        node["severity_score"] = violation_map[node["node_id"]]["severity"]
                    else:
                        node["violation_count"] = 0
                        node["severity_score"] = 0

        # Calculate summary statistics
        summary = {
            "starting_nodes": len(node_ids),
            "total_reachable": len(reachable_nodes),
            "max_hops_analyzed": max_hops,
            "nodes_by_hop": {},
            "layers_affected": set(),
            "violation_summary": {},
        }

        for node in reachable_nodes:
            hop = node["min_hop_distance"]
            if hop not in summary["nodes_by_hop"]:
                summary["nodes_by_hop"][hop] = 0
            summary["nodes_by_hop"][hop] += 1
            summary["layers_affected"].add(node["layer"])

            if include_violations:
                if "violation_count" in node:
                    summary["violation_summary"]["total_violations"] = (
                        summary["violation_summary"].get("total_violations", 0) + node["violation_count"]
                    )
                    summary["violation_summary"]["total_severity"] = (
                        summary["violation_summary"].get("total_severity", 0) + node["severity_score"]
                    )

        summary["layers_affected"] = list(summary["layers_affected"])

        return {"reachable_nodes": reachable_nodes, "summary": summary}

    def execute_custom_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute a custom SQL query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(query, params or ())
        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        return results


# Convenience functions for common patterns
def get_node_impact_analysis(node_id: Union[str, int], max_hops: int = 3) -> Dict[str, Any]:
    """Get comprehensive impact analysis for a node.

    Args:
        node_id: Node ID to analyze
        max_hops: Maximum hops for dependency analysis

    Returns:
        Dict with inbound/outbound dependencies and impact metrics
    """
    helper = ADGSQLiteHelper()
    try:
        outbound = helper.get_k_hop_dependencies(node_id, "outbound", max_hops)
        inbound = helper.get_k_hop_dependencies(node_id, "inbound", max_hops)
        blast = helper.get_blast_radius([node_id], max_hops)

        return {
            "node_id": node_id,
            "outbound_dependencies": outbound,
            "inbound_dependencies": inbound,
            "blast_radius": blast,
            "impact_metrics": {
                "total_outbound": len(outbound),
                "total_inbound": len(inbound),
                "total_reachable": len(blast["reachable_nodes"]),
                "max_outbound_hop": max([d["hop_distance"] for d in outbound], default=0),
                "max_inbound_hop": max([d["hop_distance"] for d in inbound], default=0),
            },
        }
    finally:
        helper.close()


def get_layer_risk_analysis() -> List[Dict[str, Any]]:
    """Get risk analysis for all layer transitions.

    Returns:
        List of layer transitions with risk assessments
    """
    helper = ADGSQLiteHelper()
    try:
        transitions = helper.get_layer_transition_matrix()

        # Add risk categorization
        for transition in transitions:
            risk_score = transition["transition_count"] * transition["risk_weight"]
            transition["calculated_risk_score"] = risk_score

            if risk_score > 100:
                transition["risk_category"] = "CRITICAL"
            elif risk_score > 50:
                transition["risk_category"] = "HIGH"
            elif risk_score > 20:
                transition["risk_category"] = "MEDIUM"
            else:
                transition["risk_category"] = "LOW"

        return transitions
    finally:
        helper.close()


if __name__ == "__main__":
    # Example usage
    helper = ADGSQLiteHelper()

    print("ADG SQLite Helper Examples:")
    print(f"SQLite path: {helper.sqlite_path}")

    # Get layer transitions
    transitions = helper.get_layer_transition_matrix()
    print(f"\nLayer transitions found: {len(transitions)}")
    for t in transitions[:5]:  # Show first 5
        print(
            f"  {t['source_layer']} -> {t['target_layer']}: {t['transition_count']} (risk: {t['risk_weight']})"
        )

    helper.close()
