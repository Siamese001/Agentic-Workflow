"""Parser for closure validation reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser


class ClosureReportParser(BaseReportParser):
    """Parser for closure_validation_report_*.json files."""
    
    report_name = "Closure Validation Report"
    report_filename_pattern = "closure_validation_report_*.json"
    
    def _get_report_path(self) -> Path | None:
        """Get the path to the closure report file."""
        return self.adg_dir / f"closure_validation_report_{self.timestamp}.json"
    
    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from closure report.
        
        Extracts failed closure rows with appropriate categorization:
        - AUTO_FIX: Edge semantic precision, node granularity
        - SUGGEST_FIX: Structural coverage, data lineage
        - BLOCK_FIX: Critical edge missing, determinism failures
        
        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()
        
        if self.report_data is None:
            return []
        
        deficiencies = []
        rows = self.report_data.get("closure_rows", [])
        
        for row in rows:
            if row.get("passed", True):
                continue
            
            capability = row.get("capability", "UNKNOWN")
            ratio = row.get("ratio", 0.0)
            threshold = row.get("threshold", 0.95)
            
            # Determine category and confidence based on capability
            category = FixCategory.BLOCK_FIX
            confidence = 0.7
            
            if capability in ("EDGE SEMANTIC PRECISION", "NODE GRANULARITY (BLOCK / EXPRESSION)"):
                category = FixCategory.AUTO_FIX
                confidence = 0.9
            elif capability in ("STRUCTURAL COVERAGE", "DATA LINEAGE", "CONTROL FLOW"):
                category = FixCategory.SUGGEST_FIX
                confidence = 0.75
            elif capability == "DETERMINISM (ARTIFACT LEVEL)":
                category = FixCategory.BLOCK_FIX
                confidence = 0.3
            elif capability == "SIDE EFFECT MODELING":
                category = FixCategory.SUGGEST_FIX
                confidence = 0.7
            elif capability == "TEMPORAL ORDERING":
                category = FixCategory.AUTO_FIX
                confidence = 0.85
            
            deficiency = {
                "id": f"closure_{capability.lower().replace(' ', '_').replace('/', '_')}",
                "category": category.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": f"closure_fail_{capability.lower().replace(' ', '_').replace('/', '_')}",
                "description": f"Closure validation failed for {capability}: {ratio:.2%} (threshold: {threshold:.0%})",
                "confidence": confidence,
                "metadata": {
                    "capability": capability,
                    "ratio": ratio,
                    "threshold": threshold,
                    "numerator": row.get("numerator"),
                    "denominator": row.get("denominator"),
                    "evidence": row.get("evidence"),
                },
            }
            deficiencies.append(deficiency)
        
        return deficiencies
