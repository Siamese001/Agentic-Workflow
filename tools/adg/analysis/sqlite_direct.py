"""
Direct SQLite helper utilities for ADG graph analysis.

Provides low-level SQLite access for ad-hoc graph queries and
analysis when MCP tools are not available or for performance-critical operations.
"""

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json

logger = logging.getLogger(__name__)

_MAX_PATH_DEPTH = 20
_MAX_RESULT_ROWS = 100_000
_RELATION_TYPE_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")


def _validate_relation_types(relation_types: Optional[List[str]]) -> Optional[List[str]]:
    """Validate relation type identifiers to prevent injection via IN-clause builder."""
    if relation_types is None:
        return None
    if not isinstance(relation_types, list):
        raise TypeError("relation_types must be a list of strings")
    if not relation_types:
        return None
    cleaned: List[str] = []
    for rt in relation_types:
        if not isinstance(rt, str) or not _RELATION_TYPE_PATTERN.match(rt):
            raise ValueError(f"Invalid relation type identifier: {rt!r}")
        cleaned.append(rt)
    return cleaned


class GraphQueryHelper:
    """Helper class for direct SQLite graph queries."""

    def __init__(self, sqlite_path: str):
        """
        Initialize graph query helper.

        Args:
            sqlite_path: Path to ADG SQLite database
        """
        self.sqlite_path = Path(sqlite_path)
        if not self.sqlite_path.exists():
            raise ValueError(f"SQLite database not found: {sqlite_path}")

        self.conn = sqlite3.connect(str(self.sqlite_path))
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access

    def find_nodes_by_name(self, name: str, exact_match: bool = True) -> List[Dict[str, Any]]:
        """
        Find nodes by name.

        Args:
            name: Node name to search for
            exact_match: Whether to require exact match or allow partial

        Returns:
            List of matching nodes
        """
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name:
            return []
        try:
            if exact_match:
                query = "SELECT * FROM nodes WHERE adg_name = ? LIMIT ?"
                params: List[Any] = [name, _MAX_RESULT_ROWS]
            else:
                # Escape LIKE wildcards in user-supplied name
                escaped = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                query = "SELECT * FROM nodes WHERE adg_name LIKE ? ESCAPE '\\' LIMIT ?"
                params = [f"%{escaped}%", _MAX_RESULT_ROWS]
            cursor = self.conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Failed to find nodes by name %r: %s", name, e)
            return []

    def get_fan_in(self, node_id: int, relation_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get fan-in (incoming edges) for a node.

        Args:
            node_id: Node ID
            relation_types: Optional list of relation types to filter by

        Returns:
            List of incoming edges
        """
        if not isinstance(node_id, int):
            raise TypeError("node_id must be an int")
        validated = _validate_relation_types(relation_types)
        try:
            if validated:
                placeholders = ",".join(["?"] * len(validated))
                query = f"""
                    SELECT e.*, n.adg_name as source_adg_name, n.layer as source_layer
                    FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.tgt_id = ? AND e.relation_type IN ({placeholders})
                    LIMIT ?
                """
                params: List[Any] = [node_id, *validated, _MAX_RESULT_ROWS]
            else:
                query = """
                    SELECT e.*, n.adg_name as source_adg_name, n.layer as source_layer
                    FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.tgt_id = ?
                    LIMIT ?
                """
                params = [node_id, _MAX_RESULT_ROWS]
            cursor = self.conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Failed to get fan-in for node %s: %s", node_id, e)
            return []

    def get_fan_out(self, node_id: int, relation_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get fan-out (outgoing edges) for a node.

        Args:
            node_id: Node ID
            relation_types: Optional list of relation types to filter by

        Returns:
            List of outgoing edges
        """
        if not isinstance(node_id, int):
            raise TypeError("node_id must be an int")
        validated = _validate_relation_types(relation_types)
        try:
            if validated:
                placeholders = ",".join(["?"] * len(validated))
                query = f"""
                    SELECT e.*, n.adg_name as target_adg_name, n.layer as target_layer
                    FROM edges e
                    JOIN nodes n ON e.tgt_id = n.id
                    WHERE e.src_id = ? AND e.relation_type IN ({placeholders})
                    LIMIT ?
                """
                params: List[Any] = [node_id, *validated, _MAX_RESULT_ROWS]
            else:
                query = """
                    SELECT e.*, n.adg_name as target_adg_name, n.layer as target_layer
                    FROM edges e
                    JOIN nodes n ON e.tgt_id = n.id
                    WHERE e.src_id = ?
                    LIMIT ?
                """
                params = [node_id, _MAX_RESULT_ROWS]
            cursor = self.conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Failed to get fan-out for node %s: %s", node_id, e)
            return []

    def get_nodes_by_layer(self, layer: str) -> List[Dict[str, Any]]:
        """
        Get all nodes in a specific layer.

        Args:
            layer: Layer name

        Returns:
            List of nodes in the layer
        """
        try:
            query = "SELECT * FROM nodes WHERE layer = ?"
            cursor = self.conn.execute(query, [layer])
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get nodes by layer '{layer}': {e}")
            return []

    def get_nodes_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get all nodes in a specific file.

        Args:
            file_path: File path

        Returns:
            List of nodes in the file
        """
        try:
            query = "SELECT * FROM nodes WHERE file_path = ?"
            cursor = self.conn.execute(query, [file_path])
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get nodes by file '{file_path}': {e}")
            return []

    def execute_query(
        self, query: str, params: Optional[List[Union[str, int]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute custom SQL query (read-only).

        Args:
            query: SQL query (must be a single SELECT/WITH statement)
            params: Optional query parameters

        Returns:
            Query results (capped at _MAX_RESULT_ROWS)
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        stripped = query.lstrip().upper()
        if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
            raise ValueError("Only SELECT/WITH queries permitted via execute_query")
        if ";" in query.rstrip().rstrip(";"):
            raise ValueError("Multi-statement queries not permitted")
        try:
            cursor = self.conn.execute(query, params or [])
            rows = cursor.fetchmany(_MAX_RESULT_ROWS)
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error("Failed to execute query: %s", e)
            return []

    def get_node_details(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific node.

        Args:
            node_id: Node ID

        Returns:
            Node details or None if not found
        """
        try:
            query = "SELECT * FROM nodes WHERE id = ?"
            cursor = self.conn.execute(query, [node_id])
            row = cursor.fetchone()

            return dict(row) if row else None

        except Exception as e:
            logger.error(f"Failed to get node details for {node_id}: {e}")
            return None

    def find_shortest_path(
        self, src_id: int, tgt_id: int, relation_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find shortest path between two nodes (basic implementation).

        Args:
            src_id: Source node ID
            tgt_id: Target node ID
            relation_types: Optional relation types to consider

        Returns:
            List of nodes in the path
        """
        if not isinstance(src_id, int) or not isinstance(tgt_id, int):
            raise TypeError("src_id and tgt_id must be ints")
        validated_rt = _validate_relation_types(relation_types)
        try:
            if validated_rt:
                placeholders = ",".join(["?"] * len(validated_rt))
                query = f"""
                    WITH RECURSIVE path(id, adg_name, depth, path_str) AS (
                        SELECT n.id, n.adg_name, 0, CAST(n.id AS TEXT)
                        FROM nodes n
                        WHERE n.id = ?

                        UNION ALL

                        SELECT n.id, n.adg_name, p.depth + 1, p.path_str || '->' || CAST(n.id AS TEXT)
                        FROM edges e
                        JOIN nodes n ON e.tgt_id = n.id
                        JOIN path p ON e.src_id = p.id
                        WHERE e.relation_type IN ({placeholders})
                        AND p.depth < ?  -- Prevent infinite recursion
                    )
                    SELECT * FROM path WHERE id = ? AND depth <= ?
                    ORDER BY depth
                """
                params = [src_id, *validated_rt, _MAX_PATH_DEPTH, tgt_id, _MAX_PATH_DEPTH]
            else:
                query = """
                    WITH RECURSIVE path(id, adg_name, depth, path_str) AS (
                        SELECT n.id, n.adg_name, 0, CAST(n.id AS TEXT)
                        FROM nodes n
                        WHERE n.id = ?

                        UNION ALL

                        SELECT n.id, n.adg_name, p.depth + 1, p.path_str || '->' || CAST(n.id AS TEXT)
                        FROM edges e
                        JOIN nodes n ON e.tgt_id = n.id
                        JOIN path p ON e.src_id = p.id
                        WHERE p.depth < 10  -- Prevent infinite recursion
                    )
                    SELECT * FROM path WHERE id = ? AND depth <= 10
                    ORDER BY depth
                """
                params = [src_id, tgt_id]

            cursor = self.conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            logger.error(f"Failed to find shortest path from {src_id} to {tgt_id}: {e}")
            return []

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get basic graph statistics.

        Returns:
            Graph statistics
        """
        try:
            stats = {}

            # Node counts
            stats["total_nodes"] = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            stats["total_edges"] = self.conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

            # Layer distribution
            layers = self.conn.execute("""
                SELECT layer, COUNT(*) as count
                FROM nodes
                WHERE layer IS NOT NULL
                GROUP BY layer
            """).fetchall()
            stats["layer_distribution"] = {row[0]: row[1] for row in layers}

            # Node type distribution
            node_types = self.conn.execute("""
                SELECT node_type, COUNT(*) as count
                FROM nodes
                WHERE node_type IS NOT NULL
                GROUP BY node_type
            """).fetchall()
            stats["node_type_distribution"] = {row[0]: row[1] for row in node_types}

            # Relation type distribution
            relation_types = self.conn.execute("""
                SELECT relation_type, COUNT(*) as count
                FROM edges
                WHERE relation_type IS NOT NULL
                GROUP BY relation_type
            """).fetchall()
            stats["relation_type_distribution"] = {row[0]: row[1] for row in relation_types}

            return stats

        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return {}

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_graph_helper(snapshot_path: str) -> GraphQueryHelper:
    """
    Factory function to create graph helper from snapshot path.

    Args:
        snapshot_path: Path to ADG snapshot directory or file

    Returns:
        Configured GraphQueryHelper instance
    """
    snapshot_path = Path(snapshot_path)

    if snapshot_path.is_dir():
        # Find the latest SQLite file in the directory
        sqlite_files = list(snapshot_path.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise ValueError(f"No SQLite files found in {snapshot_path}")

        # Use the most recent file
        sqlite_file = max(sqlite_files, key=lambda p: p.stat().st_mtime)
    else:
        sqlite_file = snapshot_path

    if not sqlite_file.exists():
        raise ValueError(f"SQLite file not found: {sqlite_file}")

    return GraphQueryHelper(str(sqlite_file))


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sqlite_direct.py <snapshot_path> [query]")
        sys.exit(1)

    snapshot_path = sys.argv[1]

    try:
        helper = create_graph_helper(snapshot_path)

        if len(sys.argv) > 2:
            # Execute custom query
            query = sys.argv[2]
            results = helper.execute_query(query)
            print(json.dumps(results, indent=2))
        else:
            # Show graph statistics
            stats = helper.get_graph_statistics()
            print(json.dumps(stats, indent=2))

        helper.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
