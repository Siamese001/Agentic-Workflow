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
    
    def _get_report_path(self) -> Path | None:
        """Get the path to the layer report file."""
        return self.adg_dir / f"layer_coverage_report_{self.timestamp}.json"
    
    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from layer coverage report.
        
        Extracts:
        - Low layer coverage (< 50%)
        - Unknown layer modules (potentially auto-fixable)
        
        Returns:
            List of deficiency dictionaries
        """
        if self.report_data is None:
            self.load()
        
        if self.report_data is None:
            return []
        
        deficiencies = []
        
        # Check overall coverage
        coverage_pct = self.report_data.get("coverage_metrics", {}).get("coverage_percentage", 100.0)
        if coverage_pct < 50.0:
            deficiency = {
                "id": "layer_low_coverage",
                "category": FixCategory.SUGGEST_FIX.value,
                "file_path": "ADG_METADATA",
                "line_no": None,
                "issue_type": "layer_low_coverage",
                "description": f"Layer coverage is only {coverage_pct:.1f}%",
                "confidence": 0.8,
                "metadata": {
                    "coverage_percentage": coverage_pct,
                    "total_modules": self.report_data.get("total_modules", 0),
                    "unknown_count": self.report_data.get("coverage_metrics", {}).get("unknown_modules", 0),
                },
            }
            deficiencies.append(deficiency)
        
        # Extract unknown modules
        unknown_modules = self.report_data.get("unknown_modules", [])
        for module in unknown_modules[:100]:  # Limit to first 100
            module_path = module.get("resolved_path", "")
            if not module_path:
                continue
            
            # Try to infer layer from path
            inferred_layer = self._infer_layer_from_path(module_path)
            
            if inferred_layer:
                # High confidence auto-fix
                deficiency = {
                    "id": f"unknown_layer_{self._sanitize_id(module_path)}",
                    "category": FixCategory.AUTO_FIX.value,
                    "file_path": module_path,
                    "line_no": 1,
                    "issue_type": "unknown_layer_inferrable",
                    "description": f"Module has unknown layer (inferred: {inferred_layer})",
                    "suggested_fix": f"# ADG Layer: {inferred_layer}",
                    "confidence": 0.85,
                    "metadata": {
                        "adg_name": module.get("adg_name"),
                        "inferred_layer": inferred_layer,
                        "identity_kind": module.get("identity_kind"),
                    },
                }
            else:
                # Needs human review
                deficiency = {
                    "id": f"unknown_layer_{self._sanitize_id(module_path)}",
                    "category": FixCategory.SUGGEST_FIX.value,
                    "file_path": module_path,
                    "line_no": 1,
                    "issue_type": "unknown_layer_not_inferrable",
                    "description": "Module has unknown layer (cannot infer from path)",
                    "confidence": 0.6,
                    "metadata": {
                        "adg_name": module.get("adg_name"),
                        "identity_kind": module.get("identity_kind"),
                    },
                }
            
            deficiencies.append(deficiency)
        
        return deficiencies
    
    def _infer_layer_from_path(self, path: str) -> str | None:
        """Infer layer from file path.
        
        Args:
            path: File path
            
        Returns:
            Inferred layer (L0-L6, L_APP) or None
        """
        path_lower = path.lower()
        
        # Check for layer prefixes
        for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
            if f"/{layer}_" in path_lower or f"\\{layer}_" in path_lower:
                return layer
            if f"/{layer}/" in path_lower or f"\\{layer}\\" in path_lower:
                return layer
        
        # Check for apps
        for app_prefix in ("apps_eval", "apps_exec", "apps_lic", "apps_research",
                          "apps_rfp", "apps_rg", "apps_shared"):
            if path_lower.startswith(app_prefix) or f"/{app_prefix}" in path_lower:
                return "L_APP"
        
        # Check for tests
        if path_lower.startswith("tests/") or path_lower.startswith("tests\\"):
            return "L_TEST"
        
        return None
    
    def _sanitize_id(self, path: str) -> str:
        """Sanitize path for use as ID.
        
        Args:
            path: File path
            
        Returns:
            Sanitized ID string
        """
        return path.replace("/", "_").replace("\\", "_").replace(".", "_")[:100]
