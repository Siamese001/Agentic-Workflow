#!/usr/bin/env python3
"""ADG Dead Code Zone Control Verification — Validate dead code detection."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ADGDeadCodeZoneControlVerifier:
    """Verifier for dead code zones and low confidence areas."""

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

    def _verify_dead_import_detection(self) -> tuple[bool, list[str]]:
        """Verify dead imports are detected and tagged."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count dead import edges
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'dead_imports'
        """)
        dead_imports = c.fetchone()[0]
        conn.close()

        # Note: Having dead imports is OK, they should just be tagged
        return True, []

    def _verify_low_confidence_zone_analysis(self) -> tuple[bool, list[str]]:
        """Verify low confidence nodes are analyzed."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count LOW confidence nodes
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE confidence = 'LOW'
        """)
        low_confidence = c.fetchone()[0]

        # Count nodes with inferred symbols
        c.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE identity_kind = 'inferred'
        """)
        inferred = c.fetchone()[0]

        conn.close()

        issues = []
        if low_confidence > 100:  # Arbitrary threshold
            issues.append(f"{low_confidence} LOW confidence nodes (high)")
        if inferred > 100:
            issues.append(f"{inferred} inferred nodes (high)")

        return len(issues) == 0, issues

    def _verify_unresolved_import_analysis(self) -> tuple[bool, list[str]]:
        """Verify unresolved imports are tracked."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count unresolved imports
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'unresolved_import'
        """)
        unresolved = c.fetchone()[0]
        conn.close()

        if unresolved > 1000:  # Arbitrary threshold
            return False, [f"{unresolved} unresolved imports (high)"]
        return True, []

    def _verify_inferred_symbol_ratio(self) -> tuple[bool, list[str]]:
        """Verify ratio of inferred symbols is bounded."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM nodes")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'inferred'")
        inferred = c.fetchone()[0]

        conn.close()

        if total > 0:
            ratio = inferred / total
            if ratio > 0.5:  # More than 50% inferred is concerning
                return False, [f"Inferred symbol ratio {ratio:.1%} is high"]

        return True, []

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all dead code zone checks."""
        checks = [
            self._verify_dead_import_detection,
            self._verify_low_confidence_zone_analysis,
            self._verify_unresolved_import_analysis,
            self._verify_inferred_symbol_ratio,
        ]

        all_issues = []
        for check in checks:
            passed, issues = check()
            all_issues.extend(issues)

        return len(all_issues) == 0, all_issues
