"""Parser for replay determinism reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class DeterminismReportParser(BaseReportParser):
    """Parser for replay_determinism_report_*.json files."""

    report_name = "Replay Determinism Report"
    report_filename_pattern = "replay_determinism_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"replay_determinism_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from determinism report.

        Returns determinism failures and low scores.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check overall determinism score
        summary = self.report_data.get("summary", {})
        overall_score = summary.get("overall_determinism_score", 1.0)

        if overall_score < 0.95:
            deficiency = {
                "id": "determinism_low_overall_score",
                "category": FixCategory.BLOCK_FIX,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_determinism_score",
                "description": f"Low overall determinism score: {overall_score:.2f}",
                "confidence": 0.9,
                "metadata": {
                    "overall_score": overall_score,
                    "threshold": 0.95,
                },
            }
            deficiencies.append(deficiency)

        # Check individual test failures
        tests = self.report_data.get("tests", [])
        for test in tests:
            if not test.get("deterministic", True):
                test_name = test.get("name", "unknown")
                deficiency = {
                    "id": f"determinism_fail_{hash(test_name) & 0xFFFFFFFF}",
                    "category": FixCategory.BLOCK_FIX,
                    "file_path": test.get("file", "unknown"),
                    "line_no": test.get("line"),
                    "issue_type": "determinism_failure",
                    "description": f"Non-deterministic test: {test_name}",
                    "confidence": 0.95,
                    "metadata": {
                        "test_name": test_name,
                        "variations": test.get("variations", []),
                    },
                }
                deficiencies.append(deficiency)

        return deficiencies
