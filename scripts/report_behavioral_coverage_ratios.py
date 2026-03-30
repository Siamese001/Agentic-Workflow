#!/usr/bin/env python3
"""Behavioral Coverage Ratios — Report runtime vs structural balance."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class BehavioralCoverageReporter:
    """Reporter for behavioral coverage ratio analysis."""

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.db_path = self._find_sqlite_db()
        self.metrics: dict[str, Any] = {}

    def _find_sqlite_db(self) -> Path | None:
        """Find the SQLite database file in the ADG directory."""
        if not self.adg_dir.exists():
            return None
        for pattern in ["*.sqlite", "*.db"]:
            files = list(self.adg_dir.glob(pattern))
            if files:
                return files[0]
        return None

    def _compute_balance_metrics(self) -> dict[str, Any]:
        """Compute runtime vs structural balance metrics."""
        if not self.db_path or not self.db_path.exists():
            return {"error": "No SQLite database found"}

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Count structural edges
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type IN ('imports', 'exports', 'defines', 'calls')
        """)
        structural = c.fetchone()[0]

        # Count runtime edges
        c.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type IN (
                'records_execution_trace', 'applies_guardrail',
                'emits_replay_key', 'snapshots_state'
            )
        """)
        runtime = c.fetchone()[0]

        # Count by layer
        c.execute("""
            SELECT layer, COUNT(*) FROM nodes
            WHERE entity_type = 'module'
            GROUP BY layer
        """)
        layer_counts = {row[0]: row[1] for row in c.fetchall()}

        conn.close()

        total = structural + runtime
        return {
            "structural_edges": structural,
            "runtime_edges": runtime,
            "total_edges": total,
            "structural_ratio": structural / total if total > 0 else 0,
            "runtime_ratio": runtime / total if total > 0 else 0,
            "layer_distribution": layer_counts,
        }

    def generate_report(self) -> dict[str, Any]:
        """Generate full coverage report."""
        self.metrics = self._compute_balance_metrics()
        return self.metrics


def report_behavioral_coverage_ratios(adg_dir: Path) -> dict[str, Any]:
    """Convenience function to generate coverage report."""
    reporter = BehavioralCoverageReporter(adg_dir)
    return reporter.generate_report()


# Alias for test compatibility
ADGRuntimeStructuralBalanceVerifier = BehavioralCoverageReporter
