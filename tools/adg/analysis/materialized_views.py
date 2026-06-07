"""
Materialized view manager for ADG SQLite.

Creates and maintains mv_* tables for high-value graph analyses:
centrality, chokepoints, blast radius, layer dependencies.
"""

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MaterializedViewManager:
    """Manage mv_* materialized view tables in ADG SQLite."""

    def __init__(self, sqlite_path: str):
        self.sqlite_path = Path(sqlite_path)
        if not self.sqlite_path.exists():
            raise ValueError(f"SQLite database not found: {sqlite_path}")
        self.conn = sqlite3.connect(str(self.sqlite_path))

    def _ensure_edge_indices(self):
        """Create indices on edges(src_id) and edges(tgt_id) if absent. Idempotent."""
        try:
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src_id)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_tgt ON edges(tgt_id)")
            self.conn.commit()
        except sqlite3.Error as e:
            logger.warning("Could not create edge indices: %s", e)

    def create_centrality_view(self):
        """Create mv_node_centrality with in/out degree and approximate betweenness.

        Uses single-pass GROUP BY aggregation (O(N+E)) instead of correlated
        subqueries (O(N*E)) — ~30x faster on large graphs.
        """
        try:
            self._ensure_edge_indices()
            self.conn.execute("DROP TABLE IF EXISTS mv_node_centrality")
            self.conn.execute("""
                CREATE TABLE mv_node_centrality AS
                WITH in_deg AS (
                    SELECT tgt_id AS node_id, COUNT(*) AS c FROM edges GROUP BY tgt_id
                ),
                out_deg AS (
                    SELECT src_id AS node_id, COUNT(*) AS c FROM edges GROUP BY src_id
                )
                SELECT
                    n.id AS node_id,
                    n.adg_name,
                    n.layer,
                    n.node_type,
                    COALESCE(i.c, 0) AS in_degree,
                    COALESCE(o.c, 0) AS out_degree,
                    COALESCE(i.c, 0) * COALESCE(o.c, 0) AS betweenness_centrality
                FROM nodes n
                LEFT JOIN in_deg i ON i.node_id = n.id
                LEFT JOIN out_deg o ON o.node_id = n.id
            """)
            self.conn.commit()
            logger.info("Created mv_node_centrality")
        except sqlite3.Error as e:
            logger.error("Failed to create centrality view: %s", e)
            raise

    def create_critical_path_view(self):
        """Create mv_critical_path_blast_radius for path criticality scoring.

        Single-pass aggregation (O(N+E)) instead of correlated subqueries.
        """
        try:
            self._ensure_edge_indices()
            self.conn.execute("DROP TABLE IF EXISTS mv_critical_path_blast_radius")
            self.conn.execute("""
                CREATE TABLE mv_critical_path_blast_radius AS
                WITH in_deg AS (
                    SELECT tgt_id AS node_id, COUNT(*) AS c FROM edges GROUP BY tgt_id
                ),
                out_deg AS (
                    SELECT src_id AS node_id, COUNT(*) AS c FROM edges GROUP BY src_id
                )
                SELECT
                    e.src_id,
                    e.tgt_id,
                    e.relation_type,
                    CAST(COALESCE(i.c, 0) + COALESCE(o.c, 0) AS REAL) / 100.0
                        AS path_criticality_score
                FROM edges e
                LEFT JOIN in_deg i ON i.node_id = e.tgt_id
                LEFT JOIN out_deg o ON o.node_id = e.src_id
            """)
            self.conn.commit()
            logger.info("Created mv_critical_path_blast_radius")
        except sqlite3.Error as e:
            logger.error("Failed to create critical path view: %s", e)
            raise

    def create_layer_dependency_view(self):
        """Create mv_layer_dependencies aggregating cross-layer edges."""
        try:
            self._ensure_edge_indices()
            self.conn.execute("DROP TABLE IF EXISTS mv_layer_dependencies")
            self.conn.execute("""
                CREATE TABLE mv_layer_dependencies AS
                SELECT
                    n1.layer AS source_layer,
                    n2.layer AS target_layer,
                    e.relation_type,
                    COUNT(*) AS dependency_count
                FROM edges e
                JOIN nodes n1 ON e.src_id = n1.id
                JOIN nodes n2 ON e.tgt_id = n2.id
                WHERE n1.layer IS NOT NULL AND n2.layer IS NOT NULL
                GROUP BY n1.layer, n2.layer, e.relation_type
            """)
            self.conn.commit()
            logger.info("Created mv_layer_dependencies")
        except sqlite3.Error as e:
            logger.error("Failed to create layer dependency view: %s", e)
            raise

    def create_chokepoint_view(self):
        """Create mv_chokepoints — nodes with high in*out product (bridges).

        Single-pass aggregation (O(N+E)) instead of correlated subqueries.
        """
        try:
            self._ensure_edge_indices()
            self.conn.execute("DROP TABLE IF EXISTS mv_chokepoints")
            self.conn.execute("""
                CREATE TABLE mv_chokepoints AS
                WITH in_deg AS (
                    SELECT tgt_id AS node_id, COUNT(*) AS c FROM edges GROUP BY tgt_id
                ),
                out_deg AS (
                    SELECT src_id AS node_id, COUNT(*) AS c FROM edges GROUP BY src_id
                )
                SELECT
                    n.id AS node_id,
                    n.adg_name,
                    n.layer,
                    i.c AS in_degree,
                    o.c AS out_degree,
                    i.c * o.c AS chokepoint_score
                FROM nodes n
                JOIN in_deg i ON i.node_id = n.id
                JOIN out_deg o ON o.node_id = n.id
                ORDER BY chokepoint_score DESC
            """)
            self.conn.commit()
            logger.info("Created mv_chokepoints")
        except sqlite3.Error as e:
            logger.error("Failed to create chokepoint view: %s", e)
            raise

    def create_all(self):
        """Create all materialized views."""
        self.create_centrality_view()
        self.create_critical_path_view()
        self.create_layer_dependency_view()
        self.create_chokepoint_view()

    def list_views(self) -> List[str]:
        """List existing mv_* tables."""
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mv_%'")
        return [row[0] for row in cursor.fetchall()]

    def get_view_stats(self) -> Dict[str, int]:
        """Return row counts per mv_* table."""
        stats = {}
        for view in self.list_views():
            try:
                count = self.conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
                stats[view] = count
            except sqlite3.Error as e:
                stats[view] = -1
                logger.warning(f"Could not count rows in {view}: {e}")
        return stats

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python materialized_views.py <sqlite_path> [create|stats]")
        sys.exit(1)

    path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "stats"

    mgr = MaterializedViewManager(path)
    try:
        if action == "create":
            mgr.create_all()
            print(json.dumps(mgr.get_view_stats(), indent=2))
        else:
            print(json.dumps(mgr.get_view_stats(), indent=2))
    finally:
        mgr.close()
