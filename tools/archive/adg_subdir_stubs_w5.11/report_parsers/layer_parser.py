"""Parser for layer coverage reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class LayerReportParser(BaseReportParser):
    """Parser for layer_coverage_report_*.json files."""

    report_name = "Layer Coverage Report"
    report_filename_pattern = "layer_coverage_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"layer_coverage_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from layer coverage report.

        Returns modules with unknown layer assignments.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []
        modules = self.report_data.get("modules", {})

        for module_path, module_info in modules.items():
            layer = module_info.get("layer", "L_UNKNOWN")

            if layer == "L_UNKNOWN":
                deficiency = {
                    "id": f"layer_unknown_{hash(module_path) & 0xFFFFFFFF}",
                    "category": FixCategory.AUTO_FIX,
                    "file_path": module_path,
                    "line_no": 1,
                    "issue_type": "unknown_layer_inferrable",
                    "description": f"Module has unknown layer assignment: {module_path}",
                    "suggested_fix": self._infer_layer_from_path(module_path),
                    "confidence": 0.85,
                    "metadata": {
                        "current_layer": layer,
                        "inferred_layer": self._infer_layer_from_path(module_path),
                    },
                }
                deficiencies.append(deficiency)

        return deficiencies

    def _infer_layer_from_path(self, path: str) -> str | None:
        """Infer layer from file path."""
        path_lower = path.lower()

        if "l0_routing" in path_lower:
            return "L0"
        elif "l1_cognition" in path_lower:
            return "L1"
        elif "l2_execution" in path_lower:
            return "L2"
        elif "l3_orchestration" in path_lower:
            return "L3"
        elif "l4_memory" in path_lower:
            return "L4"
        elif "l5_safety" in path_lower:
            return "L5"
        elif "l6_governance" in path_lower:
            return "L6"

        return None
