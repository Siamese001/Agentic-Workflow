"""Parser for mutation integrity reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class MutationReportParser(BaseReportParser):
    """Parser for mutation_integrity_report_*.json files."""

    report_name = "Mutation Integrity Report"
    report_filename_pattern = "mutation_integrity_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser."""
        super().__init__(adg_dir, timestamp)

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file."""
        path = self.adg_dir / f"mutation_integrity_report_{self.timestamp}.json"
        return path if path.exists() else None

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from mutation integrity report.

        Returns low signature coverage and missing mutation edges.
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check signature coverage
        coverage = self.report_data.get("signature_coverage", {})
        overall = coverage.get("overall", 1.0)

        if overall < 0.8:
            deficiency = {
                "id": "mutation_low_signature_coverage",
                "category": FixCategory.SUGGEST_FIX,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_signature_coverage",
                "description": f"Low mutation signature coverage: {overall:.1%}",
                "confidence": 0.75,
                "metadata": coverage,
            }
            deficiencies.append(deficiency)

        # Check for modules with missing mutation edges
        modules = self.report_data.get("modules", {})
        for module_path, module_data in list(modules.items())[:50]:
            if module_data.get("missing_mutations", 0) > 0:
                deficiency = {
                    "id": f"mutation_missing_{hash(module_path) & 0xFFFFFFFF}",
                    "category": FixCategory.AUTO_FIX,
                    "file_path": module_path,
                    "line_no": None,
                    "issue_type": "missing_mutation_edges",
                    "description": f"Module missing {module_data['missing_mutations']} mutation edges",
                    "confidence": 0.8,
                    "metadata": module_data,
                }
                deficiencies.append(deficiency)

        # Check replay key coverage
        replay = self.report_data.get("replay_key_coverage", {})
        if replay.get("ratio", 1.0) < 0.9:
            deficiency = {
                "id": "mutation_low_replay_coverage",
                "category": FixCategory.SUGGEST_FIX,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_replay_key_coverage",
                "description": f"Low replay key coverage: {replay.get('ratio', 0):.1%}",
                "confidence": 0.75,
                "metadata": replay,
            }
            deficiencies.append(deficiency)

        return deficiencies
