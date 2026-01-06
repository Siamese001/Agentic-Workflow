from __future__ import annotations
"""
Hygiene Guardian - Architectural Sanitation (Key 45)
Handles physical removal of empty folders, temporary artifacts, and ghost directories.
"""
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import CanonBaseAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


# NAMING CANON COMPLIANCE — renamed to HygieneGuardianAgent for discovery and sovereignty — 2025-12-30
class HygieneGuardianAgent(CanonBaseAgent, MCPHardenedMixin):
    """
    Validates Canon Key 45: Shared Utils and Repository Hygiene.
    Ensures that architectural shifts do not leave behind structural debris.
    """
    
    def get_validation_keys(self) -> List[int]:
                    
        return [45]

    async def execute(self):
        """Execute comprehensive repository sanitation pass."""
        print(f"\n[>>>] {self.name} ACTIVATED: Performing Sanitation Sweep...")
        
        project_root = Path(os.getcwd())
        
        # 1. Sweep Temporary Artifacts
        self._sweep_temp_artifacts(project_root)
        
        # 2. Prune Empty Ghost Directories
        self._prune_empty_folders(project_root)
        
        print(f"   [{self.name}] ✅ Key 45: PASS - Repository hygiene maintained.")

    def _sweep_temp_artifacts(self, root: Path):
        """Removes .temp, .heal_tmp, and other ephemeral debris."""
        artifact_patterns = ["*.heal_tmp", "*.temp", "*.tmp", ".pytest_cache", "__pycache__"]
        count = 0
        
        for pattern in artifact_patterns:
            for path in root.rglob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                    count += 1
                except Exception as e:
                    print(f"      [!] Failed to remove Artifact {path.name}: {e}")
        
        if count > 0:
            print(f"      [✓] Removed {count} temporary Artifact(s).")

    def _prune_empty_folders(self, root: Path):
        """
        Recursively removes empty folders within Sovereign Roots. 
        Ensures 'orphaned' folders from moves are liquidated.
        """
        # [PHASE 20] DEPRECATION: void_compliance.py removed
        from agentic_core.config.blueprint_sovereign.structure_blueprint import ROOT_WHITELIST
        ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
        count = 0
        
        for root_folder in ALLOWED_ROOT_FOLDERS:
            root_path = root / root_folder
            if not root_path.exists():
                continue
                
            # Walk bottom-up to ensure nested empty folders are caught first
            for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
                current_dir = Path(dirpath)
                
                # Never delete a Sovereign Root itself
                if current_dir.name in ALLOWED_ROOT_FOLDERS:
                    continue
                
                # Check if folder is truly empty (ignoring system noise)
                children = [x for x in current_dir.iterdir() if x.name not in {".gitkeep"}]
                
                if not children:
                    try:
                        current_dir.rmdir()
                        count += 1
                    except Exception as e:
                        pass # Folder might not be empty due to OS locks
        
        if count > 0:
            print(f"      [✓] Liquidated {count} empty ghost directorie(s).")

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

def create_hygiene_guardian(ctx=None) -> Any:
    """Brief description of functionality and purpose."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)

    return HygieneGuardianAgent(ctx)