#!/usr/bin/env python3
"""
HierarchyEnforcerAgent - Ensures L4 structure compliance
"""

from pathlib import Path
from typing import List, Dict, Any

class HierarchyEnforcerAgent:
    """
    Enforces the canonical L4 hierarchy across agentic_core.
    Drills down from L2 -> L3 -> L4 to ensure all required directories exist.
    """
    
    def __init__(self, project_root: Path, ctx):
        from agentic_core.config.P1_core.structure_blueprint import (
            CANON_STRUCTURE, CORE_L3_SUBFOLDER_MAP, CORE_L4_SUBFOLDER_MAP
        )
        self.canon_structure = CANON_STRUCTURE
        self.l3_map = CORE_L3_SUBFOLDER_MAP
        self.l4_map = CORE_L4_SUBFOLDER_MAP
        self.project_root = project_root
        self.ctx = ctx
        
    def enforce_hierarchy(self) -> Dict[str, Any]:
        """
        Enforce L4 structure across all required directories.
        Returns dict of actions taken.
        """
        actions = []
        
        # Get L2 structure from CANON_STRUCTURE
        l2_structure = self.canon_structure["agentic_core"]["subfolders"]
        
        for l2_name in l2_structure:
            l2_path = self.project_root / "agentic_core" / l2_name
            if not l2_path.exists(): 
                continue
                
            # Check if this L2 has L3 requirements
            expected_l3 = set(self.l3_map.get(l2_name, []))
            
            for l3_name in expected_l3:
                l3_path = l2_path / l3_name
                if not l3_path.exists(): continue
                
                # [L4 DRILL DOWN]
                expected_l4 = set(self.l4_map.get(l3_name, []))
                actual_l4 = {p.name for p in l3_path.iterdir() if p.is_dir() and not p.name.startswith(".")}
                
                for missing_l4 in expected_l4 - actual_l4:
                    l4_path = l3_path / missing_l4
                    l4_path.mkdir(parents=True, exist_ok=True)
                    (l4_path / "__init__.py").touch()
                    actions.append(f"CREATED L4: {l2_name}/{l3_name}/{missing_l4}")
        
        return {
            "status": "success",
            "actions": actions,
            "l4_enforced": len(actions)
        }
    
    def validate_hierarchy(self) -> Dict[str, Any]:
        """
        Validate L4 structure compliance.
        Returns validation report.
        """
        violations = []
        
        # Get L2 structure from CANON_STRUCTURE
        l2_structure = self.canon_structure["agentic_core"]["subfolders"]
        
        for l2_name in l2_structure:
            l2_path = self.project_root / "agentic_core" / l2_name
            if not l2_path.exists(): 
                continue
                
            expected_l3 = set(self.l3_map.get(l2_name, []))
            
            for l3_name in expected_l3:
                l3_path = l2_path / l3_name
                if not l3_path.exists(): continue
                
                expected_l4 = set(self.l4_map.get(l3_name, []))
                actual_l4 = {p.name for p in l3_path.iterdir() if p.is_dir() and not p.name.startswith(".")}
                
                missing_l4 = expected_l4 - actual_l4
                if missing_l4:
                    violations.append({
                        "path": f"{l2_name}/{l3_name}",
                        "missing": list(missing_l4)
                    })
        
        return {
            "status": "validated",
            "violations": violations,
            "compliant": len(violations) == 0
        }
