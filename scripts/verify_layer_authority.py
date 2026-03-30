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

    def _verify_layer_authority_compliance(self) -> dict[str, Any]:
        """Verify L4 entities have proper authority constraints."""
        result = {"compliant": True, "violation_count": 0, "issues": []}
        
        if not self.db_path or not self.db_path.exists():
            result["issues"].append("No SQLite database found")
            return result

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
            result["compliant"] = False
            result["violation_count"] = incomplete
            result["issues"].append(f"{incomplete} L4 entities with incomplete authority")
        
        return result

    def _verify_uwg_termination_for_writes(self) -> dict[str, Any]:
        """Verify all write operations terminate at Universal Write Gateway."""
        result = {"uwg_violations": []}

        if not self.db_path or not self.db_path.exists():
            return result

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find write operations not terminating at UWG
        # Also check if source has execution_terminates_at_uwg edge (properly guarded)
        c.execute("""
            SELECT e.src_id, n.adg_name
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'writes_to'
            AND e.dst_id NOT IN (
                SELECT id FROM nodes
                WHERE adg_name LIKE '%UniversalWriteGateway%'
                OR adg_name LIKE '%UWG%'
            )
            AND e.src_id NOT IN (
                SELECT src_id FROM edges
                WHERE relation_type = 'execution_terminates_at_uwg'
            )
        """)
        violations = c.fetchall()
        conn.close()

        for src_id, adg_name in violations:
            result["uwg_violations"].append({"module_name": adg_name})

        return result

    def _verify_l4_identity_completeness(self) -> dict[str, Any]:
        """Verify L4 nodes have complete identity."""
        result = {"identity_issues": 0}

        if not self.db_path or not self.db_path.exists():
            return result

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

        result["identity_issues"] = incomplete
        return result

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all layer authority checks."""
        all_issues: list[str] = []

        # Check 1: returns dict with compliance info
        result = self._verify_layer_authority_compliance()
        all_issues.extend(result.get("issues", []))

        # Check 2: returns dict with 'uwg_violations' key
        result = self._verify_uwg_termination_for_writes()
        all_issues.extend([f"UWG violation: {v['module_name']}" for v in result.get('uwg_violations', [])])

        # Check 3: returns dict with 'identity_issues' key
        result = self._verify_l4_identity_completeness()
        if result.get('identity_issues', 0) > 0:
            all_issues.append(f"{result['identity_issues']} L4 nodes with incomplete identity")
        if result.get('issues', []):
            all_issues.extend(result['issues'])

        return len(all_issues) == 0, all_issues
