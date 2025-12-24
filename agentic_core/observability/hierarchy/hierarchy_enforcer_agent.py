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
        
        # [DEPTH ARCHIVAL] Where depth-drift goes to die
        from agentic_core.config.P1_core.structure_blueprint import DEPRECATION_ARCHIVE
        self.archive_root = project_root / DEPRECATION_ARCHIVE / "depth_violations"
        self.archive_root.mkdir(parents=True, exist_ok=True)
        
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
    
    def enforce_depth_precision(self) -> List[str]:
        """
        Sovereign depth enforcement. If it's at the wrong level, it gets archived.
        """
        from agentic_core.config.P1_core.structure_blueprint import (
            CANONICAL_PRECISION_DEPTH, AGENTIC_CORE_EXACT_DEPTH
        )
        actions = []

        for py_file in self.project_root.rglob("*.py"):
            # Skip hidden files or the archive itself
            if any(part.startswith(".") for part in py_file.parts) or "archives" in str(py_file):
                continue
            
            rel = py_file.relative_to(self.project_root)
            parts = rel.parts
            depth = len(parts)
            root_folder = parts[0]

            # Find what the depth SHOULD be
            required_depth = None
            if root_folder == "agentic_core":
                required_depth = AGENTIC_CORE_EXACT_DEPTH
            elif root_folder in CANONICAL_PRECISION_DEPTH:
                required_depth = CANONICAL_PRECISION_DEPTH[root_folder]

            # If it's wrong, we purge it
            if required_depth and depth != required_depth:
                archive_path = self.archive_root / rel
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                # Build the "obituary" for the file
                explanation = f"# DEPTH VIOLATION ARCHIVED — {__import__('datetime').datetime.now().isoformat()}\n"
                explanation += f"# REASON: Required depth for '{root_folder}' is {required_depth}, but found {depth}.\n"
                explanation += f"# To restore: Move this file to a valid depth-4 territory in agentic_core.\n\n"

                try:
                    content = py_file.read_text(encoding="utf-8")
                    with open(archive_path, "w") as f:
                        f.write(explanation + content)
                    
                    py_file.unlink()  # Sovereign purge
                    actions.append(f"ARCHIVED depth violation: {rel}")
                    self.ctx.report("DepthEnforcer", 1, True, f"Archived {rel} (Invalid Depth)")
                except Exception as e:
                    actions.append(f"FAILED to archive {rel}: {str(e)}")

        return actions

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
    
    async def execute(self, ctx):
        issues = self.enforce_hierarchy()
        issues.extend(self.enforce_depth_precision())
        if issues:
            print(f"   [HEALING] HierarchyEnforcerAgent: {len(issues)} actions taken")
