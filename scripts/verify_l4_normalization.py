#!/usr/bin/env python3
"""ADG L4 Normalization Verification — Validate layer 4 classification."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ADGL4NormalizationVerifier:
    """Verifier for L4 layer normalization and identity resolution."""

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.db_path = self._find_sqlite_db()
        self.issues: list[str] = []

    def _find_sqlite_db(self) -> Path | None:
        """Find the SQLite database file in the ADG directory."""
        if not self.adg_dir.exists():
            return None
        for pattern in ["*.sqlite", "*.db"]:
            files = list(self.adg_dir.glob(pattern))
            if files:
                return files[0]
        return None

    def _verify_l4_layer_classification(self) -> tuple[bool, list[str]]:
        """Verify L4 entities are correctly classified."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count L_UNKNOWN in L4 paths
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE resolved_path LIKE '%L4%'
            AND layer = 'L_UNKNOWN'
        """)
        unknown_in_l4 = c.fetchone()[0]
        conn.close()

        if unknown_in_l4 > 0:
            return False, [f"{unknown_in_l4} L4 path nodes have L_UNKNOWN layer"]
        return True, []

    def _verify_l4_identity_resolution(self) -> tuple[bool, list[str]]:
        """Verify L4 identities are properly resolved."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for unresolved L4 entities
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE layer = 'L4'
            AND (adg_name IS NULL OR adg_name = '' OR adg_name LIKE '%UNRESOLVED%')
        """)
        unresolved = c.fetchone()[0]
        conn.close()

        if unresolved > 0:
            return False, [f"{unresolved} L4 entities with unresolved identity"]
        return True, []

    def _verify_l4_path_integrity(self) -> dict[str, Any]:
        """Verify L4 path integrity - check for L_UNKNOWN in L4 paths."""
        result = {"l4_nodes": [], "unknown_layer_nodes": []}
        
        if not self.db_path or not self.db_path.exists():
            return result

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Get all L4 path nodes
        c.execute("""
            SELECT adg_name, layer, resolved_path FROM nodes
            WHERE resolved_path LIKE '%L4%'
        """)
        for row in c.fetchall():
            adg_name, layer, resolved_path = row
            node_info = {"name": adg_name, "layer": layer, "path": resolved_path}
            result["l4_nodes"].append(node_info)
            if layer == 'L_UNKNOWN':
                result["unknown_layer_nodes"].append(node_info)

        conn.close()
        return result

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all L4 normalization checks."""
        checks = [
            self._verify_l4_layer_classification,
            self._verify_l4_identity_resolution,
        ]

        all_issues = []
        for check in checks:
            passed, issues = check()
            all_issues.extend(issues)

        return len(all_issues) == 0, all_issues
