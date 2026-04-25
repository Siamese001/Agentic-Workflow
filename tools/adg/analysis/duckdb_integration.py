"""
DuckDB integration for columnar aggregations over ADG SQLite snapshots.

Provides high-performance analytical queries for large-scale graph analysis
while maintaining SQLite as the canonical source of truth.
"""

import duckdb
import sqlite3
import tempfile
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

_MAX_CUSTOM_ROWS = 10_000
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|COPY|EXPORT|IMPORT|CALL|INSTALL|LOAD)\b",
    re.IGNORECASE,
)


class DuckDBGraphAnalyzer:
    """Columnar graph analysis using DuckDB over ADG SQLite snapshots."""

    def __init__(self, sqlite_path: str, temp_dir: Optional[str] = None):
        """
        Initialize DuckDB analyzer with ADG SQLite snapshot.

        Args:
            sqlite_path: Path to ADG SQLite snapshot
            temp_dir: Optional temp directory for DuckDB operations
        """
        self.sqlite_path = Path(sqlite_path)
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.duckdb_conn = None
        self._setup_duckdb()

    def _setup_duckdb(self):
        """Setup DuckDB connection with SQLite extensions."""
        try:
            self.duckdb_conn = duckdb.connect(":memory:")
            self.duckdb_conn.execute("INSTALL sqlite;")
            self.duckdb_conn.execute("LOAD sqlite;")
            # Quote-escape path for ATTACH (DuckDB ATTACH doesn't accept bound params)
            safe_path = str(self.sqlite_path).replace("'", "''")
            self.duckdb_conn.execute(f"ATTACH '{safe_path}' AS adg (TYPE sqlite);")
            logger.info("DuckDB connected to ADG snapshot: %s", self.sqlite_path)
        except (duckdb.Error, OSError) as e:
            logger.error("Failed to setup DuckDB: %s", e)
            raise

    def get_layer_distribution(self) -> Dict[str, Any]:
        """Get node distribution by layer with performance metrics."""
        query = """
        SELECT
            layer,
            COUNT(*) as node_count,
            COUNT(DISTINCT file_path) as file_count,
            AVG(CASE WHEN node_type = 'function' THEN 1 ELSE 0 END) as function_ratio,
            AVG(CASE WHEN node_type = 'class' THEN 1 ELSE 0 END) as class_ratio
        FROM adg.nodes
        WHERE layer IS NOT NULL
        GROUP BY layer
        ORDER BY node_count DESC
        """

        result = self.duckdb_conn.execute(query).fetchall()

        return {
            "layer_distribution": [
                {
                    "layer": row[0],
                    "node_count": row[1],
                    "file_count": row[2],
                    "function_ratio": row[3],
                    "class_ratio": row[4],
                }
                for row in result
            ],
            "total_layers": len(result),
        }

    def analyze_import_patterns(self) -> Dict[str, Any]:
        """Analyze import patterns across layers with columnar performance."""
        query = """
        WITH import_flows AS (
            SELECT
                n1.layer as source_layer,
                n2.layer as target_layer,
                COUNT(*) as import_count,
                COUNT(DISTINCT n1.file_path) as source_files,
                COUNT(DISTINCT n2.file_path) as target_files
            FROM adg.edges e
            JOIN adg.nodes n1 ON e.src_id = n1.id
            JOIN adg.nodes n2 ON e.tgt_id = n2.id
            WHERE e.relation_type = 'imports'
            AND n1.layer IS NOT NULL
            AND n2.layer IS NOT NULL
            GROUP BY n1.layer, n2.layer
        )
        SELECT
            source_layer,
            target_layer,
            import_count,
            source_files,
            target_files,
            import_count * 1.0 / source_files as imports_per_source_file,
            import_count * 1.0 / target_files as imports_per_target_file
        FROM import_flows
        ORDER BY import_count DESC
        """

        result = self.duckdb_conn.execute(query).fetchall()

        return {
            "import_patterns": [
                {
                    "source_layer": row[0],
                    "target_layer": row[1],
                    "import_count": row[2],
                    "source_files": row[3],
                    "target_files": row[4],
                    "imports_per_source_file": row[5],
                    "imports_per_target_file": row[6],
                }
                for row in result
            ]
        }

    def get_hotspot_candidates(self, min_fan_in: int = 10) -> Dict[str, Any]:
        """Identify hotspot candidates using columnar aggregation."""
        query = """
        WITH node_stats AS (
            SELECT
                n.id,
                n.adg_name,
                n.layer,
                n.node_type,
                n.file_path,
                COUNT(DISTINCT CASE WHEN e.relation_type = 'imports' THEN e.tgt_id END) as fan_in_imports,
                COUNT(DISTINCT CASE WHEN e.relation_type = 'imports' THEN e.src_id END) as fan_out_imports,
                COUNT(DISTINCT CASE WHEN e.relation_type = 'calls' THEN e.tgt_id END) as fan_in_calls,
                COUNT(DISTINCT CASE WHEN e.relation_type = 'calls' THEN e.src_id END) as fan_out_calls,
                COUNT(DISTINCT e.tgt_id) as total_fan_in,
                COUNT(DISTINCT e.src_id) as total_fan_out
            FROM adg.nodes n
            LEFT JOIN adg.edges e ON n.id = e.src_id OR n.id = e.tgt_id
            GROUP BY n.id, n.adg_name, n.layer, n.node_type, n.file_path
        )
        SELECT
            id,
            adg_name,
            layer,
            node_type,
            file_path,
            fan_in_imports,
            fan_out_imports,
            fan_in_calls,
            fan_out_calls,
            total_fan_in,
            total_fan_out,
            (total_fan_in * total_fan_out) as centrality_score
        FROM node_stats
        WHERE total_fan_in >= ?
        ORDER BY centrality_score DESC
        LIMIT 100
        """

        result = self.duckdb_conn.execute(query, [min_fan_in]).fetchall()

        return {
            "hotspot_candidates": [
                {
                    "id": row[0],
                    "adg_name": row[1],
                    "layer": row[2],
                    "node_type": row[3],
                    "file_path": row[4],
                    "fan_in_imports": row[5],
                    "fan_out_imports": row[6],
                    "fan_in_calls": row[7],
                    "fan_out_calls": row[8],
                    "total_fan_in": row[9],
                    "total_fan_out": row[10],
                    "centrality_score": row[11],
                }
                for row in result
            ]
        }

    def analyze_violation_distribution(self) -> Dict[str, Any]:
        """Analyze violation distribution across layers and files."""
        query = """
        SELECT
            v.violation_type,
            v.severity,
            n.layer,
            COUNT(*) as violation_count,
            COUNT(DISTINCT n.file_path) as affected_files,
            COUNT(DISTINCT n.id) as affected_nodes
        FROM adg.violations v
        JOIN adg.nodes n ON v.node_id = n.id
        GROUP BY v.violation_type, v.severity, n.layer
        ORDER BY violation_count DESC
        """

        result = self.duckdb_conn.execute(query).fetchall()

        return {
            "violation_distribution": [
                {
                    "violation_type": row[0],
                    "severity": row[1],
                    "layer": row[2],
                    "violation_count": row[3],
                    "affected_files": row[4],
                    "affected_nodes": row[5],
                }
                for row in result
            ]
        }

    def get_materialized_view_stats(self) -> Dict[str, Any]:
        """Get statistics about existing materialized views."""
        # Check which materialized views exist
        views_query = """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE 'mv_%'
        """

        try:
            result = self.duckdb_conn.execute(views_query).fetchall()
            existing_views = [row[0] for row in result]

            view_stats = {}
            for view in existing_views:
                try:
                    count_query = f"SELECT COUNT(*) FROM adg.{view}"
                    count = self.duckdb_conn.execute(count_query).fetchone()[0]
                    view_stats[view] = {"row_count": count}
                except Exception as e:
                    view_stats[view] = {"error": str(e)}

            return {
                "existing_views": existing_views,
                "view_stats": view_stats,
                "total_views": len(existing_views),
            }

        except Exception as e:
            logger.error(f"Failed to get materialized view stats: {e}")
            return {"error": str(e)}

    def execute_custom_query(self, query: str) -> Dict[str, Any]:
        """Execute custom analytical query safely (read-only, single statement)."""
        if not isinstance(query, str) or not query.strip():
            return {"error": "query must be a non-empty string"}
        stripped_upper = query.lstrip().upper()
        if not (stripped_upper.startswith("SELECT") or stripped_upper.startswith("WITH")):
            return {"error": "Only SELECT/WITH queries are allowed"}
        if _FORBIDDEN_KEYWORDS.search(query):
            return {"error": "Query contains forbidden keyword"}
        # Reject multi-statement
        if ";" in query.rstrip().rstrip(";"):
            return {"error": "Multi-statement queries not permitted"}
        try:
            cursor = self.duckdb_conn.execute(query)
            rows = cursor.fetchmany(_MAX_CUSTOM_ROWS)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return {
                "columns": columns,
                "rows": [list(row) for row in rows],
                "row_count": len(rows),
                "truncated": len(rows) >= _MAX_CUSTOM_ROWS,
            }
        except duckdb.Error as e:
            logger.error("Failed to execute custom query: %s", e)
            return {"error": str(e)}

    def close(self):
        """Close DuckDB connection."""
        if self.duckdb_conn:
            self.duckdb_conn.close()
            logger.info("DuckDB connection closed")


def create_duckdb_analyzer(snapshot_path: str) -> DuckDBGraphAnalyzer:
    """
    Factory function to create DuckDB analyzer from snapshot path.

    Args:
        snapshot_path: Path to ADG snapshot directory or file

    Returns:
        Configured DuckDBGraphAnalyzer instance
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

    return DuckDBGraphAnalyzer(str(sqlite_file))


# CLI interface for testing
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python duckdb_integration.py <snapshot_path> [analysis_type]")
        sys.exit(1)

    snapshot_path = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "overview"

    try:
        analyzer = create_duckdb_analyzer(snapshot_path)

        if analysis_type == "overview":
            result = analyzer.get_layer_distribution()
        elif analysis_type == "imports":
            result = analyzer.analyze_import_patterns()
        elif analysis_type == "hotspots":
            result = analyzer.get_hotspot_candidates()
        elif analysis_type == "violations":
            result = analyzer.analyze_violation_distribution()
        elif analysis_type == "views":
            result = analyzer.get_materialized_view_stats()
        else:
            print(f"Unknown analysis type: {analysis_type}")
            print("Available: overview, imports, hotspots, violations, views")
            sys.exit(1)

        print(json.dumps(result, indent=2))
        analyzer.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
