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

    def _verify_trace_replay_completeness(self) -> tuple[bool, list[str]]:
        """Verify modules with writes have trace/replay coverage."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Find modules that write but lack trace/replay
        c.execute("""
            SELECT DISTINCT src_id FROM edges
            WHERE relation_type = 'writes_to'
            AND src_id NOT IN (
                SELECT DISTINCT src_id FROM edges
                WHERE relation_type = 'records_execution_trace'
            )
        """)
        modules_without_trace = len(c.fetchall())
        conn.close()

        if modules_without_trace > 0:
            return False, [f"{modules_without_trace} writing modules lack trace coverage"]
        return True, []

    def _verify_critical_execution_surfaces(self) -> tuple[bool, list[str]]:
        """Verify critical execution surfaces have coverage."""
        if not self.db_path or not self.db_path.exists():
            return False, ["No SQLite database found"]

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check for modules with both trace and replay keys
        c.execute("""
            SELECT COUNT(DISTINCT src_id) FROM edges
            WHERE relation_type = 'records_execution_trace'
        """)
        with_trace = c.fetchone()[0]

        c.execute("""
            SELECT COUNT(DISTINCT src_id) FROM edges
            WHERE relation_type = 'emits_replay_key'
        """)
        with_replay = c.fetchone()[0]

        conn.close()

        issues = []
        if with_trace == 0:
            issues.append("No modules with execution trace found")
        if with_replay == 0:
            issues.append("No modules with replay key found")

        return len(issues) == 0, issues

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
