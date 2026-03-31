"""Parser for boundary reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class BoundaryReportParser(BaseReportParser):
    """Parser for boundary_report_*.json files."""

    report_name = "Boundary Report"
    report_filename_pattern = "boundary_report_*.json"

    def _get_report_path(self) -> Path | None:
        """Get the path to the boundary report file."""
        return self.adg_dir / f"boundary_report_{self.timestamp}.json"

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from boundary report.

        Extracts:
        - Unresolved boundary imports
        - Incomplete boundary completeness

        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check boundary metrics
        boundary_metrics = self.report_data.get("boundary_metrics", {})
        total_unresolved = boundary_metrics.get("total_unresolved", 0)
        boundary_completeness = boundary_metrics.get("boundary_completeness", "complete")

        if total_unresolved > 0:
            # This might be auto-fixable with import analysis
            deficiency = {
                "id": f"boundary_unresolved_{total_unresolved}",
                "category": FixCategory.SUGGEST_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "unresolved_boundary_imports",
                "description": f"{total_unresolved} unresolved boundary imports detected",
                "confidence": 0.7,
                "metadata": {
                    "unresolved_count": total_unresolved,
                    "critical_path_unresolved": boundary_metrics.get("critical_path_unresolved", 0),
                },
            }
            deficiencies.append(deficiency)

        if boundary_completeness == "incomplete":
            boundary_counts = self.report_data.get("boundary_edge_counts", {})
            unresolved_count = boundary_counts.get("unresolved_boundary", 0)

            deficiency = {
                "id": "boundary_incomplete",
                "category": FixCategory.SUGGEST_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "boundary_completeness_incomplete",
                "description": f"Boundary analysis incomplete ({unresolved_count} unresolved)",
                "confidence": 0.6,
                "metadata": {
                    "boundary_completeness": boundary_completeness,
                    "boundary_edge_counts": boundary_counts,
                },
            }
            deficiencies.append(deficiency)

        return deficiencies
