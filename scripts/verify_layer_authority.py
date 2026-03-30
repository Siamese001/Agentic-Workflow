#!/usr/bin/env python3
"""ADG Layer Authority Verification — Validate governance boundaries."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ADGLayerAuthorityVerifier:
    """Verifier for L4 governance layer authority."""

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

    def _verify_layer_authority_compliance(self) -> tuple[bool, list[str]]:
        """Verify L4 entities have proper authority constraints."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for L4 entities without proper authority
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE layer = 'L4'
            AND (identity_kind IS NULL OR identity_kind = '')
        """)
        incomplete = c.fetchone()[0]
        conn.close()

        if incomplete > 0:
            return False, [f"{incomplete} L4 entities with incomplete authority"]
        return True, []

    def _verify_uwg_termination_for_writes(self) -> tuple[bool, list[str]]:
        """Verify all write operations terminate at UniversalWriteGateway."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find write operations not terminating at UWG
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'writes_to'
            AND dst_id NOT IN (
                SELECT id FROM nodes
                WHERE adg_name LIKE '%UniversalWriteGateway%'
                OR adg_name LIKE '%UWG%'
            )
        """)
        invalid = c.fetchone()[0]
        conn.close()

        if invalid > 0:
            return False, [f"{invalid} writes not terminating at UWG"]
        return True, []

    def _verify_l4_identity_completeness(self) -> tuple[bool, list[str]]:
        """Verify L4 nodes have complete identity."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check L4 nodes with incomplete identity
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE layer = 'L4'
            AND (resolved_path IS NULL OR resolved_path = '')
        """)
        incomplete = c.fetchone()[0]
        conn.close()

        if incomplete > 0:
            return False, [f"{incomplete} L4 nodes with incomplete identity"]
        return True, []

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all layer authority checks."""
        checks = [
            self._verify_layer_authority_compliance,
            self._verify_uwg_termination_for_writes,
            self._verify_l4_identity_completeness,
        ]

        all_issues = []
        for check in checks:
            passed, issues = check()
            all_issues.extend(issues)

        return len(all_issues) == 0, all_issues
