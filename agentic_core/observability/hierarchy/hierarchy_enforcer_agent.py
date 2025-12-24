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
        Apps depth enforcement. If it's not depth 3, it gets archived.
        """
        from agentic_core.config.P1_core.structure_blueprint import APPS_EXACT_DEPTH
        actions = []

        # [APPS DEPTH 3] Target all files under apps_* (Universal enforcement)
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            rel = file_path.relative_to(self.project_root)
            if not rel.parts[0].startswith("apps_"):
                continue

            depth = len(rel.parts)
            if depth != APPS_EXACT_DEPTH:
                # ARCHIVE THE DRIFT
                archive_path = self.archive_root / "apps_depth" / rel
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                explanation = f"# APPS DEPTH VIOLATION ARCHIVED — {__import__('datetime').datetime.now().isoformat()}\n"
                explanation += f"# {rel} was depth {depth}, but apps_* MUST be exactly {APPS_EXACT_DEPTH}.\n\n"

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    archive_path.write_text(explanation + content, encoding="utf-8")
                    file_path.unlink()
                    actions.append(f"ARCHIVED apps_* drift: {rel}")
                    self.ctx.report("DepthEnforcer", 1, True, f"Archived {rel} (apps depth {depth})")
                except Exception as e:
                    actions.append(f"APPS ARCHIVE FAILED: {rel} — {e}")

        return actions

    def enforce_universal_depth(self) -> List[str]:
        """
        Universal depth enforcement for all file types under agentic_core.
        Archives non-Python files that violate depth 4 rule.
        """
        from agentic_core.config.P1_core.structure_blueprint import AGENTIC_CORE_EXACT_DEPTH
        actions = []

        # [UNIVERSAL ENFORCEMENT] Target common data/doc extensions
        target_exts = {".json", ".md", ".yaml", ".yml", ".toml", ".txt"}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            if file_path.suffix.lower() not in target_exts:
                continue

            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] == "agentic_core":
                depth = len(rel.parts)
                if depth != AGENTIC_CORE_EXACT_DEPTH:
                    # [ARCHIVE UNIVERSAL DRIFT]
                    archive_path = self.archive_root / "non_python" / rel
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    header = f"# UNIVERSAL DEPTH VIOLATION — {__import__('datetime').datetime.now().isoformat()}\n"
                    header += f"# File {rel} was at depth {depth}, but MUST be {AGENTIC_CORE_EXACT_DEPTH}.\n\n"

                    try:
                        # We handle text files directly; binaries might need different logic
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        archive_path.write_text(header + content, encoding="utf-8")
                        file_path.unlink()
                        actions.append(f"ARCHIVED non-python drift: {rel}")
                    except Exception as e:
                        actions.append(f"FAILED to archive non-python {rel}: {e}")

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
        issues.extend(self.enforce_universal_depth())
        if issues:
            print(f"   [HEALING] HierarchyEnforcerAgent: {len(issues)} actions taken")
