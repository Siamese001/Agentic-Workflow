"""
Hygiene Guardian - Architectural Sanitation (Key 45)
Handles physical removal of empty folders, temporary artifacts, and ghost directories.
"""
import os
import shutil
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List
from typing import List, Tuple

from agentic_core.L2_execution.tool_registry.canon_base_agent import CanonBaseAgent

class HygieneGuardian(CanonBaseAgent):
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
                    print(f"      [!] Failed to remove artifact {path.name}: {e}")
        
        if count > 0:
            print(f"      [✓] Removed {count} temporary artifact(s).")

    def _prune_empty_folders(self, root: Path):
        """
        Recursively removes empty folders within Sovereign Roots. 
        Ensures 'orphaned' folders from moves are liquidated.
        """
        from agentic_core.runtime.shared.void_compliance import ALLOWED_ROOT_FOLDERS
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