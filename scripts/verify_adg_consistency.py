#!/usr/bin/env python3
"""ADG Consistency Verification — Validate SQLite integrity and metrics."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ConsistencyVerificationError(Exception):
    """Error raised when consistency verification fails."""
    pass


class ADGConsistencyVerifier:
    """Verifier for ADG SQLite database consistency."""

    REQUIRED_METRICS = {
        "total_nodes": "SELECT COUNT(*) FROM nodes",
        "total_edges": "SELECT COUNT(*) FROM edges",
        "node_types": "SELECT COUNT(DISTINCT entity_type) FROM nodes",
        "edge_types": "SELECT COUNT(DISTINCT relation_type) FROM edges",
    }

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.db_path = self._find_sqlite_db()
        self.sqlite_path = self.db_path  # Alias for test compatibility
        self.issues: list[str] = []
        self.errors: list[str] = []  # Required by tests

    def _execute_sql_query(self, sql_query: str) -> int:
        """Execute a SQL query and return the integer result."""
        if not self.db_path or not self.db_path.exists():
            return 0
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(sql_query)
        result = c.fetchone()
        conn.close()
        
        if result and result[0] is not None:
            return int(result[0])
        return 0

    def _find_sqlite_db(self) -> Path | None:
        """Find the SQLite database file in the ADG directory."""
        if not self.adg_dir.exists():
            return None
        for pattern in ["*.sqlite", "*.db"]:
            files = list(self.adg_dir.glob(pattern))
            if files:
                return files[0]
        return None

    def _verify_foreign_key_integrity(self) -> None:
        """Verify foreign key relationships between nodes and edges."""
        if not self.db_path or not self.db_path.exists():
            self.errors.append("No SQLite database found")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for orphaned edges (src_id or dst_id not in nodes)
        c.execute("""
            SELECT COUNT(*) FROM edges e
            LEFT JOIN nodes n1 ON e.src_id = n1.id
            LEFT JOIN nodes n2 ON e.dst_id = n2.id
            WHERE n1.id IS NULL OR n2.id IS NULL
        """)
        orphaned = c.fetchone()[0]
        conn.close()

        if orphaned > 0:
            self.errors.append(f"{orphaned} orphaned edges found")

    def _verify_relation_type_consistency(self) -> None:
        """Verify all edges have valid relation types."""
        if not self.db_path or not self.db_path.exists():
            self.errors.append("No SQLite database found")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for edges with NULL or empty relation_type
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type IS NULL OR relation_type = ''
        """)
        invalid = c.fetchone()[0]
        conn.close()

        if invalid > 0:
            self.errors.append(f"{invalid} edges with invalid relation_type")

    def _verify_count_integrity(self) -> tuple[bool, list[str]]:
        """Verify counts in meta table match actual counts."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Get actual counts
        c.execute("SELECT COUNT(*) FROM nodes")
        actual_nodes = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM edges")
        actual_edges = c.fetchone()[0]

        # Get meta counts
        c.execute("SELECT value FROM meta WHERE key = 'total_nodes'")
        meta_nodes_row = c.fetchone()
        c.execute("SELECT value FROM meta WHERE key = 'total_edges'")
        meta_edges_row = c.fetchone()

        conn.close()

        issues = []
        if meta_nodes_row and int(meta_nodes_row[0]) != actual_nodes:
            issues.append(f"Node count mismatch: meta={meta_nodes_row[0]}, actual={actual_nodes}")
        if meta_edges_row and int(meta_edges_row[0]) != actual_edges:
            issues.append(f"Edge count mismatch: meta={meta_edges_row[0]}, actual={actual_edges}")

        return len(issues) == 0, issues

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all consistency checks."""
        # Run checks that populate errors directly
        self._verify_foreign_key_integrity()
        self._verify_relation_type_consistency()
        
        # Run check that returns tuple
        passed, issues = self._verify_count_integrity()
        
        all_issues = list(self.errors) + list(issues)

        return len(all_issues) == 0, all_issues
