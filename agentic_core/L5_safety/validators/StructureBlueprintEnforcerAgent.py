"""
StructureBlueprintEnforcerAgent — ETERNAL SSOT GUARDIAN

Resurrected from SSOT enforcement audit logic — 2025-12-30
Ensures structure_blueprint.py remains the SINGLE SOURCE OF TRUTH for all folder structure.

Canon Enforcement:
- No hard-coded paths duplicating SSOT definitions
- All folder references must import from structure_blueprint.py
- Detects drift and reports violations for healing
"""
import ast
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    sovereign_registry,
    core_subfolder_map,
    apps_rg_subfolder_map,
    apps_lic_subfolder_map,
    apps_shared_subfolder_map,
    tests_subfolder_map,
)


class StructureBlueprintEnforcerAgent:
    """
    L5 sovereign agent that enforces structure_blueprint.py as SSOT.
    Runs during validation/healing cycles.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.ssot_file = self.project_root / "agentic_core" / "config" / "blueprint_sovereign" / "structure_blueprint.py"
        
        # Build complete set of all SSOT path segments
        self.ssot_paths = self._build_ssot_paths()

    def _build_ssot_paths(self) -> set:
        """Extract all unique path segments from SSOT"""
        paths = set()
        
        # Root folders
        paths.update(sovereign_registry.keys())
        
        # All subfolders
        for mapping in [core_subfolder_map, apps_rg_subfolder_map, apps_lic_subfolder_map,
                        apps_shared_subfolder_map, tests_subfolder_map]:
            for parent, subs in mapping.items():
                paths.add(parent)
                for sub in subs:
                    paths.add(sub)
                    paths.add(f"{parent}/{sub}")
        
        return paths

    def validate_ssot_compliance(self) -> List[Dict[str, Any]]:
        """
        Scan entire repo for hard-coded paths that violate SSOT.
        Returns structured violations for healer integration.
        """
        violations = []
        
        if not self.ssot_paths:
            violations.append({
                "type": "ssot_empty",
                "severity": "critical",
                "message": "SSOT path set is empty — failed to load structure_blueprint.py"
            })
            return violations
        
        # ULTRA pattern: matches any string containing SSOT path segments
        escaped = [re.escape(p) for p in sorted(self.ssot_paths, key=len, reverse=True)]
        pattern = re.compile(
            r'(?:[\'\"f].*?)(' + '|'.join(escaped) + r')',
            re.IGNORECASE
        )
        
        for py_file in self.project_root.rglob("*.py"):
            if py_file == self.ssot_file:
                continue
            if any(ex in str(py_file) for ex in {"__pycache__", ".git", "archives"}):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
            except:
                continue
            
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                # Allow imports from SSOT
                if "structure_blueprint" in line:
                    continue
                
                matches = pattern.findall(line)
                for match in matches:
                    violations.append({
                        "type": "ssot_duplication",
                        "severity": "high",
                        "file": str(py_file.relative_to(self.project_root)),
                        "line": i,
                        "duplicate_path": match,
                        "context": line.strip(),
                        "suggestion": "Replace with import from structure_blueprint.py"
                    })
        
        return violations

    def execute(self) -> Dict[str, Any]:
        """Primary execution entrypoint for orchestrator"""
        violations = self.validate_ssot_compliance()
        
        return {
            "violation_count": len(violations),
            "violations": violations[:50],  # Cap for reporting
            "status": "compliant" if not violations else "violations_detected",
            "summary": f"SSOT compliance check complete — {len(violations)} duplication(s) found"
        }


# Ensure discovery
__all__ = ["StructureBlueprintEnforcerAgent"]
