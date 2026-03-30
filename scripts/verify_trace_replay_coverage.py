#!/usr/bin/env python3
"""ADG Trace Replay Coverage Verification — Validate execution traceability."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ADGTraceReplayCoverageVerifier:
    """Verifier for trace and replay coverage across execution surfaces."""

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

    def _verify_trace_replay_completeness(self) -> dict[str, Any]:
        """Verify modules with writes have trace/replay coverage."""
        result = {"modules_without_trace": []}
        
        if not self.db_path or not self.db_path.exists():
            return result

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find modules that write but lack trace/replay
        c.execute("""
            SELECT DISTINCT n.adg_name FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'writes_to'
            AND e.src_id NOT IN (
                SELECT DISTINCT src_id FROM edges
                WHERE relation_type = 'records_execution_trace'
            )
        """)
        modules_without_trace = [row[0] for row in c.fetchall()]
        conn.close()

        result["modules_without_trace"] = modules_without_trace
        return result

    def _analyze_execution_surface_coverage(self) -> dict[str, Any]:
        """Analyze execution surface coverage metrics."""
        result = {
            "execution_surfaces": {},
            "total_modules": 0,
        }
        
        if not self.db_path or not self.db_path.exists():
            return result

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count total modules
        c.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'")
        result["total_modules"] = c.fetchone()[0]

        # Get execution surface coverage
        c.execute("""
            SELECT relation_type, COUNT(*) FROM edges
            WHERE relation_type IN ('records_execution_trace', 'emits_replay_key', 'signs_execution_trace')
            GROUP BY relation_type
        """)
        for row in c.fetchall():
            result["execution_surfaces"][row[0]] = row[1]

        conn.close()
        return result

    def _verify_critical_execution_surfaces(self) -> dict[str, Any]:
        """Verify critical execution surfaces have coverage."""
        result = {"total_modules": 0, "with_trace": 0, "with_replay": 0}
        
        if not self.db_path or not self.db_path.exists():
            return result

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count modules with both trace and replay keys
        c.execute("SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type = 'records_execution_trace'")
        result["with_trace"] = c.fetchone()[0]

        c.execute("SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type = 'emits_replay_key'")
        result["with_replay"] = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'")
        result["total_modules"] = c.fetchone()[0]

        conn.close()
        return result

    def verify_all(self) -> tuple[bool, list[str]]:
        """Run all trace replay coverage checks."""
        checks = [
            self._verify_trace_replay_completeness,
            self._verify_critical_execution_surfaces,
        ]

        all_issues = []
        for check in checks:
            passed, issues = check()
            all_issues.extend(issues)

        return len(all_issues) == 0, all_issues
