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
    
    def _get_report_path(self) -> Path | None:
        """Get the path to the edge report file."""
        return self.adg_dir / f"edge_density_report_{self.timestamp}.json"
    
    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from edge density report.
        
        Extracts:
        - Missing critical edge types (0 instances)
        - Low edge density in critical areas
        
        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()
        
        if self.report_data is None:
            return []
        
        deficiencies = []
        
        # Check critical edge coverage
        critical_edges = [
            "determinism_seed",
            "emits_determinism_digest",
            "policy_verification",
            "authorize_and_execute",
            "dispatches_execution_plan",
            "enters_sandbox",
            "guardian_gate",
        ]
        
        critical_coverage = self.report_data.get("critical_edge_coverage", {})
        
        for edge_type in critical_edges:
            count = critical_coverage.get(edge_type, 0)
            if count == 0:
                deficiency = {
                    "id": f"missing_critical_edge_{edge_type}",
                    "category": FixCategory.BLOCK_FIX.value,
                    "file_path": "ADG_METADATA",
                    "line_no": None,
                    "issue_type": "missing_critical_edge",
                    "description": f"Critical edge type '{edge_type}' has 0 instances",
                    "confidence": 0.5,
                    "metadata": {
                        "edge_type": edge_type,
                        "count": count,
                    },
                }
                deficiencies.append(deficiency)
        
        # Check density metrics
        density_metrics = self.report_data.get("density_metrics", {})
        critical_percentage = density_metrics.get("critical_edge_percentage", 100.0)
        
        if critical_percentage < 50.0:
            deficiency = {
                "id": "low_critical_edge_coverage",
                "category": FixCategory.SUGGEST_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "low_critical_edge_coverage",
                "description": f"Only {critical_percentage:.1f}% of critical edge types present",
                "confidence": 0.7,
                "metadata": {
                    "critical_edge_percentage": critical_percentage,
                    "edges_found": density_metrics.get("critical_edges_found", 0),
                    "total_edge_types": len(critical_edges),
                },
            }
            deficiencies.append(deficiency)
        
        return deficiencies
