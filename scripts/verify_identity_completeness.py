#!/usr/bin/env python3
"""ADG Identity Completeness Verification — Validate node/edge schema coverage."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ADGIdentityCompletenessVerifier:
    """Verifier for identity completeness across ADG nodes."""

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.db_path = self._find_sqlite_db()
        self.issues: list[str] = []
        self.errors: list[str] = []  # Required by tests
        self.warnings: list[str] = []  # Required by tests

    def _find_sqlite_db(self) -> Path | None:
        """Find the SQLite database file in the ADG directory."""
        if not self.adg_dir.exists():
            return None
        for pattern in ["*.sqlite", "*.db"]:
            files = list(self.adg_dir.glob(pattern))
            if files:
                return files[0]
        return None

    def _get_table_columns(self, table_name: str) -> list[str]:
        """Get column names for a table."""
        if not self.db_path or not self.db_path.exists():
            return []

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in c.fetchall()]
        conn.close()
        return columns

    def _verify_node_schema_completeness(self) -> None:
        """Verify nodes have all required fields."""
        if not self.db_path or not self.db_path.exists():
            self.errors.append("No SQLite database found")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for nodes with NULL identity fields
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE identity_kind IS NULL OR identity_kind = ''
        """)
        incomplete = c.fetchone()[0]
        
        # Check for enhanced fields missing
        c.execute("PRAGMA table_info(nodes)")
        columns = [row[1] for row in c.fetchall()]
        
        conn.close()

        if incomplete > 0:
            self.errors.append(f"{incomplete} nodes with incomplete identity")
        
        # Warn about missing enhanced fields
        enhanced_fields = ['identity_origin', 'domain', 'owner_surface']
        missing = [f for f in enhanced_fields if f not in columns]
        if missing:
            self.warnings.append(f"Missing enhanced fields: {missing}")

    def _verify_first_party_module_completeness(self) -> None:
        """Verify first-party modules have required fields."""
        if not self.db_path or not self.db_path.exists():
            self.errors.append("No SQLite database found")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for first-party modules (not site-packages) missing layer
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE entity_type = 'module'
            AND (layer IS NULL OR layer = '' OR layer = 'L_UNKNOWN' OR layer = 'UNKNOWN')
            AND resolved_path NOT LIKE '%site-packages%'
        """)
        incomplete = c.fetchone()[0]
        conn.close()

        if incomplete > 0:
            self.errors.append(f"{incomplete} first-party modules with UNKNOWN layer")

    def _verify_low_confidence_node_traceability(self) -> None:
        """Verify LOW confidence nodes have traceability info."""
        if not self.db_path or not self.db_path.exists():
            self.errors.append("No SQLite database found")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count LOW confidence nodes
        c.execute("SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'")
        low_confidence = c.fetchone()[0]

        # Count unresolved imports
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'unresolved_import'
        """)
        unresolved = c.fetchone()[0]

        conn.close()

        if low_confidence > 0:
            self.warnings.append(f"{low_confidence} LOW confidence nodes found")
        if unresolved > 0:
            self.warnings.append(f"{unresolved} unresolved imports found")

    def _verify_enum_value_constraints(self) -> tuple[bool, list[str]]:
        """Verify enum fields have valid values."""
        valid_confidence = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}
        valid_layers = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_UNKNOWN"}

        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for invalid confidence values
        c.execute("SELECT DISTINCT confidence FROM nodes")
        invalid_confidence = [row[0] for row in c.fetchall()
                           if row[0] and row[0] not in valid_confidence]

        # Check for invalid layer values
        c.execute("SELECT DISTINCT layer FROM nodes")
        invalid_layers = [row[0] for row in c.fetchall()
                         if row[0] and row[0] not in valid_layers]

        conn.close()

        issues = []
        if invalid_confidence:
            issues.append(f"Invalid confidence values: {invalid_confidence}")
        if invalid_layers:
            issues.append(f"Invalid layer values: {invalid_layers}")

        return len(issues) == 0, issues

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all identity completeness checks."""
        # Run checks that populate errors/warnings directly
        self._verify_node_schema_completeness()
        self._verify_first_party_module_completeness()
        self._verify_low_confidence_node_traceability()
        
        # Run check that returns tuple
        passed, issues = self._verify_enum_value_constraints()
        
        all_issues = list(self.errors) + list(self.warnings) + list(issues)

        return len(all_issues) == 0, all_issues
