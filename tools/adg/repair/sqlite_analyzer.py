"""SQLite analyzer for deep ADG deficiency detection.

Provides direct SQL queries against ADG SQLite database for
edge-level deficiency detection when reports are insufficient.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory


class SQLiteAnalyzer:
    """Analyzes ADG SQLite database for deficiencies.

    This class provides direct SQL queries against the ADG SQLite
    database to detect deficiencies that may not be visible in
    the high-level reports.

    Usage:
        analyzer = SQLiteAnalyzer(
            sqlite_path=Path("artifacts/adg/adg_indexed_03122026_0512.sqlite")
        )

        # Get modules missing governance edges
        missing = analyzer.get_modules_missing_governance_edges()

        # Get unresolved imports
        unresolved = analyzer.get_unresolved_imports()
    """

    def __init__(self, sqlite_path: Path):
        """Initialize the SQLite analyzer.

        Args:
            sqlite_path: Path to ADG SQLite database
        """
        self.sqlite_path = Path(sqlite_path)
        self._conn: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection.

        Returns:
            SQLite connection
        """
        if self._conn is None:
            self._conn = sqlite3.connect(self.sqlite_path)
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> SQLiteAnalyzer:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def get_table_counts(self) -> dict[str, int]:
        """Get row counts for main tables.

        Returns:
            Dictionary mapping table name to row count
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        tables = ["nodes", "edges", "meta", "violations"]
        counts = {}

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = 0

        return counts

    def get_edge_counts_by_type(self) -> dict[str, int]:
        """Get counts of edges by relation type.

        Returns:
            Dictionary mapping relation type to count
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
        return dict(cursor.fetchall())

    def get_modules_missing_governance_edges(self) -> list[dict[str, Any]]:
        """Find modules missing key governance edges.

        Returns:
            List of module dictionaries with missing edge info
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get all modules
        cursor.execute("""
            SELECT id, adg_name, resolved_path
            FROM nodes
            WHERE entity_type = 'module'
        """)
        modules = cursor.fetchall()

        # Governance edge types to check
        governance_edges = [
            "applies_guardrail",
            "records_execution_trace",
            "reads_policy_state",
            "emits_replay_key",
            "emits_determinism_digest",
            "snapshots_state",
            "signs_execution_trace",
        ]

        results = []

        for module_id, adg_name, resolved_path in modules:
            missing_edges = []

            for edge_type in governance_edges:
                cursor.execute("""
                    SELECT COUNT(*) FROM edges
                    WHERE src_id = ? AND relation_type = ?
                """, (module_id, edge_type))

                count = cursor.fetchone()[0]
                if count == 0:
                    missing_edges.append(edge_type)

            if missing_edges:
                results.append({
                    "module_id": module_id,
                    "adg_name": adg_name,
                    "resolved_path": resolved_path,
                    "missing_governance_edges": missing_edges,
                    "missing_count": len(missing_edges),
                })

        return results

    def get_unresolved_imports(self) -> list[dict[str, Any]]:
        """Find unresolved imports.

        Returns:
            List of unresolved import dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                src.adg_name as source_module,
                src.resolved_path as source_path,
                dst.adg_name as target_module,
                e.relation_type,
                e.symbol
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'unresolved_boundary'
               OR (e.relation_type = 'imports' AND dst.entity_type = 'unresolved')
            LIMIT 100
        """)

        results = []
        for row in cursor.fetchall():
            results.append({
                "source_module": row[0],
                "source_path": row[1],
                "target_module": row[2],
                "relation_type": row[3],
                "symbol": row[4],
            })

        return results

    def get_semantic_precision_gaps(self) -> dict[str, Any]:
        """Analyze semantic precision gaps.

        Returns:
            Dictionary with semantic precision analysis
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total edges
        cursor.execute("SELECT COUNT(*) FROM edges")
        total_edges = cursor.fetchone()[0]

        # Semantic edges
        cursor.execute("SELECT COUNT(*) FROM edges WHERE semantic_type != ''")
        semantic_edges = cursor.fetchone()[0]

        # Execution edges
        cursor.execute("SELECT COUNT(*) FROM edges WHERE edge_kind = 'execution'")
        execution_edges = cursor.fetchone()[0]

        # Ordered execution edges
        cursor.execute("""
            SELECT COUNT(*) FROM edges
            WHERE edge_kind = 'execution' AND dynamic_resolution LIKE 'seq=%'
        """)
        ordered_edges = cursor.fetchone()[0]

        # Specific semantic types
        semantic_types = [
            "controls_flow",
            "flows_to",
            "emits_side_effect",
            "resolves_callsite",
        ]

        type_counts = {}
        for st in semantic_types:
            cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (st,))
            type_counts[st] = cursor.fetchone()[0]

        return {
            "total_edges": total_edges,
            "semantic_edges": semantic_edges,
            "semantic_edge_ratio": semantic_edges / total_edges if total_edges > 0 else 0,
            "execution_edges": execution_edges,
            "ordered_execution_edges": ordered_edges,
            "temporal_ordering_ratio": ordered_edges / execution_edges if execution_edges > 0 else 0,
            "semantic_type_counts": type_counts,
        }

    def get_layer_violations(self) -> list[dict[str, Any]]:
        """Get layer violation details.

        Returns:
            List of layer violation dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                src.adg_name as source_module,
                src.resolved_path as source_path,
                src.layer as source_layer,
                dst.adg_name as target_module,
                dst.resolved_path as target_path,
                dst.layer as target_layer,
                e.symbol as violation_type
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'violates'
            LIMIT 100
        """)

        results = []
        for row in cursor.fetchall():
            results.append({
                "source_module": row[0],
                "source_path": row[1],
                "source_layer": row[2],
                "target_module": row[3],
                "target_path": row[4],
                "target_layer": row[5],
                "violation_type": row[6],
            })

        return results

    def get_deficiencies_as_dicts(self) -> list[dict[str, Any]]:
        """Get all SQLite-derived deficiencies as standardized dictionaries.

        Returns:
            List of deficiency dictionaries
        """
        deficiencies = []

        # Check governance gaps
        gov_gaps = self.get_modules_missing_governance_edges()
        for gap in gov_gaps:
            if gap["missing_count"] > 0:
                deficiency = {
                    "id": f"sqlite_gov_gap_{gap['module_id']}",
                    "category": FixCategory.SUGGEST_FIX.value,
                    "file_path": gap["resolved_path"] or "UNKNOWN",
                    "line_no": None,
                    "issue_type": "missing_governance_edges",
                    "description": f"Module missing {gap['missing_count']} governance edges: {', '.join(gap['missing_governance_edges'][:3])}",
                    "confidence": 0.75,
                    "metadata": {
                        "module_id": gap["module_id"],
                        "adg_name": gap["adg_name"],
                        "missing_edges": gap["missing_governance_edges"],
                    },
                }
                deficiencies.append(deficiency)

        # Check unresolved imports
        unresolved = self.get_unresolved_imports()
        for unres in unresolved:
            deficiency = {
                "id": f"sqlite_unresolved_{unres['source_module']}_{unres['target_module']}",
                "category": FixCategory.SUGGEST_FIX.value,
                "file_path": unres["source_path"] or "UNKNOWN",
                "line_no": None,
                "issue_type": "unresolved_import",
                "description": f"Unresolved import: {unres['target_module']}",
                "confidence": 0.7,
                "metadata": {
                    "source_module": unres["source_module"],
                    "target_module": unres["target_module"],
                    "symbol": unres["symbol"],
                },
            }
            deficiencies.append(deficiency)

        # Check semantic precision
        semantic_gaps = self.get_semantic_precision_gaps()
        if semantic_gaps["semantic_edge_ratio"] < 0.95:
            deficiency = {
                "id": "sqlite_low_semantic_ratio",
                "category": FixCategory.AUTO_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_semantic_edge_ratio",
                "description": f"Semantic edge ratio is {semantic_gaps['semantic_edge_ratio']:.2%}",
                "confidence": 0.8,
                "metadata": semantic_gaps,
            }
            deficiencies.append(deficiency)

        return deficiencies
