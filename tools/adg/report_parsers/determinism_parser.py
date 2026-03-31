"""Parser for determinism reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class DeterminismReportParser(BaseReportParser):
    """Parser for replay_determinism_report_*.json files."""

    report_name = "Determinism Report"
    report_filename_pattern = "replay_determinism_report_*.json"

    def _get_report_path(self) -> Path | None:
        """Get the path to the determinism report file."""
        return self.adg_dir / f"replay_determinism_report_{self.timestamp}.json"

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from determinism report.

        Extracts:
        - Failed determinism checks
        - Low determinism scores
        - Missing determinism edges

        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return []

        deficiencies = []

        # Check determinism status
        validation = self.report_data.get("validation", {})
        determinism_status = validation.get("determinism_status", "unknown")

        if determinism_status != "closed":
            proof = self.report_data.get("proof", {})

            # Check which digests failed
            failed_checks = []
            check_mapping = [
                ("scanner_digest_match", "Scanner digest mismatch"),
                ("artifact_digest_match", "Artifact digest mismatch"),
                ("node_row_digest_match", "Node row digest mismatch"),
                ("edge_row_digest_match", "Edge row digest mismatch"),
            ]

            for key, description in check_mapping:
                if not proof.get(key, False):
                    failed_checks.append((key, description))

            if failed_checks:
                deficiency = {
                    "id": f"determinism_fail_{determinism_status}",
                    "category": FixCategory.BLOCK_FIX.value,
                    "file_path": "ADG_METADATA",
                    "line_no": None,
                    "issue_type": "determinism_failure",
                    "description": f"Determinism check failed ({len(failed_checks)} checks): {', '.join(d[1] for d in failed_checks)}",
                    "confidence": 0.3,
                    "metadata": {
                        "determinism_status": determinism_status,
                        "failed_checks": [d[0] for d in failed_checks],
                        "proof": proof,
                    },
                }
                deficiencies.append(deficiency)

        # Check determinism coverage
        coverage = self.report_data.get("determinism_coverage", {})
        determinism_score = coverage.get("determinism_score", 1.0)

        if determinism_score < 0.8:
            deficiency = {
                "id": "low_determinism_score",
                "category": FixCategory.BLOCK_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_determinism_score",
                "description": f"Determinism score is only {determinism_score:.2f}",
                "confidence": 0.4,
                "metadata": {
                    "determinism_score": determinism_score,
                    "modules_with_determinism_digest": coverage.get("modules_with_determinism_digest", 0),
                    "modules_with_replay_keys": coverage.get("modules_with_replay_keys", 0),
                },
            }
            deficiencies.append(deficiency)

        # Check for missing determinism edges
        metrics = self.report_data.get("determinism_metrics", {})

        if metrics.get("determinism_digest_edges", 0) == 0:
            deficiency = {
                "id": "missing_determinism_digest_edges",
                "category": FixCategory.AUTO_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "missing_determinism_edges",
                "description": "No determinism digest edges found in ADG",
                "confidence": 0.8,
                "metadata": {"metric": "determinism_digest_edges"},
            }
            deficiencies.append(deficiency)

        return deficiencies
