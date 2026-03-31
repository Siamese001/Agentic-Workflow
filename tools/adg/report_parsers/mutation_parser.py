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

    def _get_report_path(self) -> Path | None:
        """Get the path to the mutation report file."""
        return self.adg_dir / f"mutation_integrity_report_{self.timestamp}.json"

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from mutation integrity report.

        Extracts:
        - Low signature coverage
        - Missing mutation edges
        - Incomplete replay guarantees

        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check signature coverage
        signature_coverage = self.report_data.get("signature_coverage", {})
        coverage_pct = signature_coverage.get("coverage_percentage", 100.0)

        if coverage_pct < 90.0:
            total_modules = signature_coverage.get("total_modules", 0)
            modules_with_signatures = signature_coverage.get("modules_with_signatures", 0)

            deficiency = {
                "id": "mutation_low_signature_coverage",
                "category": FixCategory.AUTO_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_mutation_signature_coverage",
                "description": f"Mutation signature coverage is only {coverage_pct:.1f}% ({modules_with_signatures}/{total_modules} modules)",
                "confidence": 0.8,
                "metadata": {
                    "coverage_percentage": coverage_pct,
                    "modules_with_signatures": modules_with_signatures,
                    "total_modules": total_modules,
                },
            }
            deficiencies.append(deficiency)

        # Check mutation integrity metrics
        mutation_edges = self.report_data.get("mutation_integrity_metrics", {})

        if mutation_edges.get("mutation_signature", 0) == 0:
            deficiency = {
                "id": "missing_mutation_signatures",
                "category": FixCategory.AUTO_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "missing_mutation_signatures",
                "description": "No mutation signature edges found",
                "confidence": 0.85,
                "metadata": {"mutation_signature_count": 0},
            }
            deficiencies.append(deficiency)

        if mutation_edges.get("replay_key", 0) == 0:
            deficiency = {
                "id": "missing_replay_key_edges",
                "category": FixCategory.AUTO_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "missing_replay_keys",
                "description": "No replay key edges found",
                "confidence": 0.8,
                "metadata": {"replay_key_count": 0},
            }
            deficiencies.append(deficiency)

        # Check replay guarantees
        replay_guarantees = self.report_data.get("replay_guarantees", {})
        replay_completeness = replay_guarantees.get("replay_completeness", "complete")

        if replay_completeness != "closed":
            deficiency = {
                "id": f"replay_completeness_{replay_completeness}",
                "category": FixCategory.SUGGEST_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "incomplete_replay_guarantees",
                "description": f"Replay completeness is '{replay_completeness}', expected 'closed'",
                "confidence": 0.6,
                "metadata": {
                    "replay_completeness": replay_completeness,
                    "determinism_status": replay_guarantees.get("determinism_status"),
                },
            }
            deficiencies.append(deficiency)

        return deficiencies
