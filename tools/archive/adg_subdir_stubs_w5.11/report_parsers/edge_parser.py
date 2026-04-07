"""Parser for edge density reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class EdgeReportParser(BaseReportParser):
    """Parser for edge_density_report_*.json files."""

    report_name = "Edge Density Report"
    report_filename_pattern = "edge_density_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"edge_density_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from edge density report.

        Returns missing critical edge types.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check for low coverage edge types
        coverage = self.report_data.get("coverage_by_type", {})
        critical_types = ["calls", "imports", "exports", "invokes_dynamic"]

        for edge_type in critical_types:
            type_coverage = coverage.get(edge_type, {})
            ratio = type_coverage.get("ratio", 1.0)

            if ratio < 0.8:
                deficiency = {
                    "id": f"edge_low_coverage_{edge_type}",
                    "category": FixCategory.SUGGEST_FIX,
                    "file_path": "ADG_METADATA",
                    "line_no": None,
                    "issue_type": f"low_edge_coverage_{edge_type}",
                    "description": f"Low coverage for critical edge type '{edge_type}': {ratio:.1%}",
                    "confidence": 0.7,
                    "metadata": {
                        "edge_type": edge_type,
                        "coverage_ratio": ratio,
                        "threshold": 0.8,
                    },
                }
                deficiencies.append(deficiency)

        return deficiencies
