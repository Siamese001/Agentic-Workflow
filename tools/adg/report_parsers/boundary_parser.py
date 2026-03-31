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

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"boundary_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from boundary report.

        Returns unresolved imports and incomplete boundaries.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check for unresolved imports (handle both list and dict formats)
        unresolved = self.report_data.get("unresolved_imports", [])
        if isinstance(unresolved, dict):
            # Convert dict format to list of deficiency dicts
            for module, count in list(unresolved.items())[:50]:
                if count > 0:
                    deficiency = {
                        "id": f"boundary_unresolved_{hash(module) & 0xFFFFFFFF}",
                        "category": FixCategory.SUGGEST_FIX,
                        "file_path": module,
                        "line_no": None,
                        "issue_type": "unresolved_import",
                        "description": f"Unresolved imports in module: {module} ({count} occurrences)",
                        "confidence": 0.8,
                        "metadata": {"module": module, "count": count},
                    }
                    deficiencies.append(deficiency)
        elif isinstance(unresolved, list):
            # Original list format handling
            for imp in unresolved[:50]:  # Limit to first 50
                if isinstance(imp, dict):
                    module = imp.get("module", "unknown")
                    name = imp.get("name", "unknown")

                    deficiency = {
                        "id": f"boundary_unresolved_{hash(module + name) & 0xFFFFFFFF}",
                        "category": FixCategory.SUGGEST_FIX,
                        "file_path": imp.get("source_file", "unknown"),
                        "line_no": imp.get("line"),
                        "issue_type": "unresolved_import",
                        "description": f"Unresolved import: {module}.{name}",
                        "confidence": 0.8,
                        "metadata": imp,
                    }
                    deficiencies.append(deficiency)

        # Check boundary completeness
        completeness = self.report_data.get("completeness", {})
        if completeness.get("ratio", 1.0) < 0.9:
            deficiency = {
                "id": "boundary_low_completeness",
                "category": FixCategory.AUTO_FIX,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "boundary_incomplete",
                "description": f"Low boundary completeness: {completeness.get('ratio', 0):.1%}",
                "confidence": 0.7,
                "metadata": completeness,
            }
            deficiencies.append(deficiency)

        return deficiencies
