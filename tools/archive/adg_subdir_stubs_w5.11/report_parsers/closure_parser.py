"""Parser for closure validation reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class ClosureReportParser(BaseReportParser):
    """Parser for closure_validation_report_*.json files."""

    report_name = "Closure Validation Report"
    report_filename_pattern = "closure_validation_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"closure_validation_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from closure validation report.

        Returns closure capability failures as deficiencies.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []
        closure_rows = self.report_data.get("closure_rows", [])

        for row in closure_rows:
            if not row.get("passed", True):
                deficiency = {
                    "id": f"closure_{row.get('id', 'unknown')}",
                    "category": FixCategory.AUTO_FIX,
                    "file_path": "ADG_METADATA",
                    "line_no": None,
                    "issue_type": f"closure_failure_{row.get('capability', 'unknown').lower().replace(' ', '_')}",
                    "description": f"Closure validation failed for {row.get('capability', 'unknown')}: "
                    f"ratio={row.get('ratio', 0):.2f}, threshold={row.get('threshold', 0):.2f}",
                    "confidence": 0.95,
                    "metadata": {
                        "capability": row.get("capability"),
                        "ratio": row.get("ratio"),
                        "threshold": row.get("threshold"),
                        "numerator": row.get("numerator"),
                        "denominator": row.get("denominator"),
                    },
                }
                deficiencies.append(deficiency)

        return deficiencies
