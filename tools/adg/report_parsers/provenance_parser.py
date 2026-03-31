"""Parser for provenance reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class ProvenanceReportParser(BaseReportParser):
    """Parser for provenance_report_*.json files."""

    report_name = "Provenance Report"
    report_filename_pattern = "provenance_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"provenance_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from provenance report.

        Returns missing validation fields and count mismatches.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check for validation failures
        validation = self.report_data.get("validation", {})

        if not validation.get("node_count_match", True):
            deficiency = {
                "id": "provenance_node_count_mismatch",
                "category": FixCategory.BLOCK_FIX,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "provenance_node_count_mismatch",
                "description": "Node count mismatch between ADG sources and provenance record",
                "confidence": 0.95,
                "metadata": {
                    "sqlite_count": validation.get("sqlite_node_count"),
                    "report_count": validation.get("report_node_count"),
                },
            }
            deficiencies.append(deficiency)

        if not validation.get("edge_count_match", True):
            deficiency = {
                "id": "provenance_edge_count_mismatch",
                "category": FixCategory.BLOCK_FIX,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "provenance_edge_count_mismatch",
                "description": "Edge count mismatch between ADG sources and provenance record",
                "confidence": 0.95,
                "metadata": {
                    "sqlite_count": validation.get("sqlite_edge_count"),
                    "report_count": validation.get("report_edge_count"),
                },
            }
            deficiencies.append(deficiency)

        return deficiencies
