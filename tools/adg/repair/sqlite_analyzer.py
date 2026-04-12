"""SQLite analyzer for ADG Repair Orchestrator.

Provides direct SQL queries against the ADG SQLite database
to detect deficiencies that aren't visible in JSON reports.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteAnalyzer:
    """Analyzer for ADG SQLite database.

    Performs deep analysis of the ADG SQLite database to detect:
    - Missing governance edges
    - Unresolved imports
    - Semantic precision gaps
    - Layer violations

    Usage:
        analyzer = SQLiteAnalyzer(sqlite_path)
        deficiencies = analyzer.get_deficiencies_as_dicts()
    """

    def __init__(self, sqlite_path: Path):
        """Initialize the analyzer.

        Args:
            sqlite_path: Path to ADG SQLite database
        """
        self.sqlite_path = Path(sqlite_path)
        self._connection: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.sqlite_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Close database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> SQLiteAnalyzer:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def get_table_counts(self) -> dict[str, int]:
        """Get row counts for all tables.

        Returns:
            Dictionary mapping table names to row counts
        """
        conn = self._get_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        counts = {}
        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]

        return counts

    def get_edge_counts_by_type(self) -> dict[str, int]:
        """Get edge counts grouped by relation type.

        Returns:
            Dictionary mapping relation types to counts
        """
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type",
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_modules_missing_governance_edges(self) -> list[dict[str, Any]]:
        """Find modules missing critical governance edges.

        Returns:
            List of module dictionaries
        """
        conn = self._get_connection()

        # Find modules without applies_guardrail edges
        cursor = conn.execute(
            """
            SELECT DISTINCT n.id, n.resolved_path, n.layer
            FROM nodes n
            WHERE n.entity_type = 'module'
            AND n.id NOT IN (
                SELECT DISTINCT src_id FROM edges WHERE relation_type = 'applies_guardrail'
            )
            LIMIT 100
            """,
        )

        modules = []
        for row in cursor.fetchall():
            modules.append(
                {
                    "id": row[0],
                    "resolved_path": row[1],
                    "layer": row[2],
                    "missing_edge": "applies_guardrail",
                }
            )

        return modules

    def get_unresolved_imports(self) -> list[dict[str, Any]]:
        """Find unresolved imports in the ADG.

        Returns:
            List of unresolved import dictionaries
        """
        conn = self._get_connection()

        # Find imports that don't resolve to known modules
        cursor = conn.execute(
            """
            SELECT e.id, e.src_id, e.dst_id, e.relation_type, n.label
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'imports'
            AND e.dst_id NOT IN (SELECT id FROM nodes WHERE entity_type = 'module')
            LIMIT 100
            """,
        )

        imports = []
        for row in cursor.fetchall():
            imports.append(
                {
                    "edge_id": row[0],
                    "src_id": row[1],
                    "dst_id": row[2],
                    "relation_type": row[3],
                    "src_label": row[4],
                }
            )

        return imports

    def get_semantic_precision_gaps(self) -> dict[str, Any]:
        """Find semantic precision gaps.

        Returns:
            Dictionary with precision statistics
        """
        conn = self._get_connection()

        # Count nodes with vs without semantic annotations
        cursor = conn.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN json_extract(metadata, '$.precision') IS NOT NULL THEN 1 ELSE 0 END) as with_precision
            FROM nodes
            """,
        )

        row = cursor.fetchone()
        total = row[0] if row else 0
        with_precision = row[1] if row else 0

        return {
            "total_nodes": total,
            "nodes_with_precision": with_precision,
            "nodes_without_precision": total - with_precision,
            "precision_ratio": with_precision / total if total > 0 else 0,
        }

    def get_layer_violations(self) -> list[dict[str, Any]]:
        """Find layer boundary violations.

        Returns:
            List of violation dictionaries
        """
        conn = self._get_connection()

        # Find edges that violate layer boundaries (relation_type='violates')
        cursor = conn.execute(
            """
            SELECT
                e.id,
                e.src_id,
                e.dst_id,
                e.relation_type,
                e.source_file,
                e.line_no,
                src.layer as src_layer,
                dst.layer as dst_layer
            FROM edges e
            JOIN nodes src ON e.src_id = src.id
            JOIN nodes dst ON e.dst_id = dst.id
            WHERE e.relation_type = 'violates'
            LIMIT 100
            """,
        )

        violations = []
        for row in cursor.fetchall():
            violations.append(
                {
                    "edge_id": row[0],
                    "src_id": row[1],
                    "dst_id": row[2],
                    "relation_type": row[3],
                    "source_file": row[4],
                    "line_no": row[5],
                    "src_layer": row[6],
                    "dst_layer": row[7],
                }
            )

        return violations

    def get_p2_antipatterns(self) -> list[dict[str, Any]]:
        """Find HIGH-severity P2 antipattern edges across all source files.

        Covers all four HIGH-severity categories: silent_exception_swallow,
        broad_exception_catch, log_and_swallow, return_none_swallow.
        No LIMIT — returns complete inventory for ratchet enforcement.

        Returns:
            List of antipattern dictionaries with edge_id, source_file, line_no, edge_kind, symbol
        """
        conn = self._get_connection()

        cursor = conn.execute(
            """
            SELECT
                e.id,
                e.source_file,
                e.line_no,
                e.edge_kind,
                e.symbol
            FROM edges e
            WHERE e.edge_kind IN (
                'silent_exception_swallow',
                'broad_exception_catch',
                'log_and_swallow',
                'return_none_swallow'
            )
            ORDER BY e.edge_kind, e.source_file, e.line_no
            """,
        )

        antipatterns = []
        for row in cursor.fetchall():
            antipatterns.append(
                {
                    "edge_id": row[0],
                    "source_file": row[1] or "",
                    "line_no": row[2],
                    "edge_kind": row[3],
                    "symbol": row[4] or "",
                }
            )

        return antipatterns

    def get_deficiencies_as_dicts(self) -> list[dict[str, Any]]:
        """Get all deficiencies as standardized dictionaries.

        Returns:
            List of deficiency dictionaries
        """
        from tools.adg.repair.types import FixCategory

        deficiencies = []

        # Add governance edge deficiencies
        for module in self.get_modules_missing_governance_edges():
            deficiencies.append(
                {
                    "id": f"sqlite_gov_{module['id']}",
                    "category": FixCategory.SUGGEST_FIX,
                    "file_path": module["resolved_path"],
                    "line_no": None,
                    "issue_type": "missing_governance_edges",
                    "description": f"Module missing governance edges: {module['missing_edge']}",
                    "confidence": 0.8,
                    "metadata": module,
                }
            )

        # Add layer violations
        for violation in self.get_layer_violations():
            deficiencies.append(
                {
                    "id": f"sqlite_layer_{violation['edge_id']}",
                    "category": FixCategory.BLOCK_FIX,
                    "file_path": violation["source_file"],
                    "line_no": violation["line_no"],
                    "issue_type": "layer_violation",
                    "description": f"Layer violation: {violation['src_layer']} -> {violation['dst_layer']}",
                    "confidence": 0.9,
                    "metadata": violation,
                }
            )

        # Add P2 antipatterns (classify only, no auto-fix)
        for antipattern in self.get_p2_antipatterns():
            deficiencies.append(
                {
                    "id": f"sqlite_p2_{antipattern['edge_id']}",
                    "category": FixCategory.BLOCK_FIX,
                    "file_path": antipattern["source_file"],
                    "line_no": antipattern["line_no"],
                    "issue_type": antipattern["edge_kind"],
                    "description": (
                        f"P2 antipattern: {antipattern['edge_kind']} "
                        f"in {antipattern['source_file']}:{antipattern['line_no']}"
                        + (f" ({antipattern['symbol']})" if antipattern.get("symbol") else "")
                    ),
                    "confidence": 0.95,
                    "metadata": antipattern,
                }
            )

        return deficiencies
