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
    
    def _get_report_path(self) -> Path | None:
        """Get the path to the provenance report file."""
        return self.adg_dir / f"provenance_report_{self.timestamp}.json"
    
    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from provenance report.
        
        Extracts:
        - Missing validation fields (commit_sha, scanner_digest, etc.)
        - Node/edge count mismatches
        
        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()
        
        if self.report_data is None:
            return []
        
        deficiencies = []
        
        # Check validation fields
        validation = self.report_data.get("validation", {})
        reconciliation = self.report_data.get("reconciliation", {})
        
        required_fields = [
            ("has_commit_sha", "commit_sha", "Commit SHA missing"),
            ("has_repo_state_hash", "repo_state_hash", "Repo state hash missing"),
            ("has_scanner_digest", "scanner_digest", "Scanner digest missing"),
            ("has_artifact_digest", "artifact_digest", "Artifact digest missing"),
        ]
        
        for field_key, field_name, description in required_fields:
            if not validation.get(field_key, False):
                deficiency = {
                    "id": f"provenance_missing_{field_name}",
                    "category": FixCategory.SUGGEST_FIX.value,
                    "file_path": "ADG_METADATA",
                    "line_no": None,
                    "issue_type": "provenance_missing_field",
                    "description": description,
                    "confidence": 0.8,
                    "metadata": {
                        "missing_field": field_name,
                        "validation_key": field_key,
                    },
                }
                deficiencies.append(deficiency)
        
        # Check reconciliation mismatches
        if reconciliation.get("nodes_match") is False:
            report_nodes = reconciliation.get("report_nodes", 0)
            db_nodes = reconciliation.get("db_nodes", 0)
            
            deficiency = {
                "id": "provenance_node_mismatch",
                "category": FixCategory.BLOCK_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "provenance_reconciliation_fail",
                "description": f"Node count mismatch: report={report_nodes}, db={db_nodes}",
                "confidence": 0.4,
                "metadata": {
                    "report_nodes": report_nodes,
                    "db_nodes": db_nodes,
                    "difference": abs(report_nodes - db_nodes),
                },
            }
            deficiencies.append(deficiency)
        
        if reconciliation.get("edges_match") is False:
            report_edges = reconciliation.get("report_edges", 0)
            db_edges = reconciliation.get("db_edges", 0)
            
            deficiency = {
                "id": "provenance_edge_mismatch",
                "category": FixCategory.BLOCK_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "provenance_reconciliation_fail",
                "description": f"Edge count mismatch: report={report_edges}, db={db_edges}",
                "confidence": 0.4,
                "metadata": {
                    "report_edges": report_edges,
                    "db_edges": db_edges,
                    "difference": abs(report_edges - db_edges),
                },
            }
            deficiencies.append(deficiency)
        
        return deficiencies
