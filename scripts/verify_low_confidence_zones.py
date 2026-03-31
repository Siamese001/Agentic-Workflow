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

    def _verify_dead_import_detection(self) -> dict[str, Any]:
        """Verify dead imports are detected and tagged."""
        if not self.db_path or not self.db_path.exists():
            return {"total_dead_imports": 0, "unresolved_symbols": []}

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count dead import edges
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'dead_imports'
        """)
        dead_imports = c.fetchone()[0]

        # Get unresolved symbols
        c.execute("""
            SELECT DISTINCT symbol FROM edges
            WHERE relation_type = 'unresolved_import'
        """)
        unresolved = [row[0] for row in c.fetchall()]
        conn.close()

        return {"total_dead_imports": dead_imports, "unresolved_symbols": unresolved}

    def _verify_low_confidence_zone_analysis(self) -> dict[str, Any]:
        """Verify low confidence nodes are analyzed."""
        if not self.db_path or not self.db_path.exists():
            return {"total_low_confidence": 0, "inferred_symbol_ratio": 0.0}

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

        # Total nodes for ratio calculation
        c.execute("SELECT COUNT(*) FROM nodes")
        total = c.fetchone()[0]
        conn.close()

        inferred_ratio = inferred / total if total > 0 else 0.0

        return {"total_low_confidence": low_confidence, "inferred_symbol_ratio": inferred_ratio}

    def _verify_unresolved_import_analysis(self) -> dict[str, Any]:
        """Verify unresolved imports are tracked."""
        if not self.db_path or not self.db_path.exists():
            return {"total_unresolved_imports": 0, "high_unresolved_count": False}

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count unresolved imports
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'unresolved_import'
        """)
        unresolved = c.fetchone()[0]
        conn.close()

        return {"total_unresolved_imports": unresolved, "high_unresolved_count": unresolved > 1000}

    def _verify_inferred_symbol_ratio(self) -> dict[str, Any]:
        """Verify ratio of inferred symbols is bounded."""
        if not self.db_path or not self.db_path.exists():
            return {"inferred_symbol_ratio": 0.0, "high_ratio": False}

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM nodes")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'inferred'")
        inferred = c.fetchone()[0]

        conn.close()

        ratio = inferred / total if total > 0 else 0.0
        return {"inferred_symbol_ratio": ratio, "high_ratio": ratio > 0.5}

    # Alias for test compatibility
    _verify_inferred_symbol_analysis = _verify_inferred_symbol_ratio

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all dead code zone checks."""
        # Run checks that return dicts and extract issues
        dead_import_result = self._verify_dead_import_detection()
        low_conf_result = self._verify_low_confidence_zone_analysis()
        unresolved_result = self._verify_unresolved_import_analysis()
        inferred_result = self._verify_inferred_symbol_ratio()

        all_issues: list[str] = []

        # Check for issues in results
        if dead_import_result.get("total_dead_imports", 0) > 1000:
            all_issues.append(f"{dead_import_result['total_dead_imports']} dead imports detected")
        if low_conf_result.get("total_low_confidence", 0) > 1000:
            all_issues.append(f"{low_conf_result['total_low_confidence']} low confidence nodes")
        if unresolved_result.get("high_unresolved_count", False):
            all_issues.append(f"{unresolved_result['total_unresolved_imports']} unresolved imports")
        if inferred_result.get("high_ratio", False):
            all_issues.append(f"Inferred symbol ratio {inferred_result['inferred_symbol_ratio']:.1%} is high")

        return len(all_issues) == 0, all_issues
