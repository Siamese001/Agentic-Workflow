#!/usr/bin/env python3
"""
L6 Watchdog: Drift Detector Agent
Scans for files that exist outside the CANON_KEY_TO_FOLDER_MAP.
Exempts root protected files and __init__.py glue files.
"""
from pathlib import Path
from typing import List, Set

from agentic_core.config.P1_core.structure_blueprint import (
    CANON_KEY_TO_FOLDER_MAP,
    ROOT_PROTECTED_FILES,
)


class DriftDetectorAgent:
    """Detects files that have drifted outside mapped canon territories."""
    
    def __init__(self, project_root: Path):
        """
        Initialize DriftDetectorAgent.
        
        Args:
            project_root: Absolute path to project root
        """
        self.root = project_root
        # Build set of all mapped paths from SSOT
        self.mapped_paths: Set[str] = set()
        for paths in CANON_KEY_TO_FOLDER_MAP.values():
            self.mapped_paths.update(paths)
    
    async def execute(self) -> List[str]:
        """
        Scan for unmapped files (drift violations).
        
        Returns:
            List of violation messages
        """
        violations = []
        
        for py_file in self.root.rglob("*.py"):
            # Skip hidden/system directories
            if any(part.startswith(".") or part == "__pycache__" for part in py_file.parts):
                continue
            
            rel = str(py_file.relative_to(self.root)).replace("\\", "/")
            
            # Exemption: Root protected files and __init__.py are allowed drift
            if py_file.name in ROOT_PROTECTED_FILES:
                continue
            if py_file.name == "__init__.py":
                continue
            
            # Check if file is within any mapped territory
            if not any(rel.startswith(m + "/") or rel == m for m in self.mapped_paths):
                violations.append(f"DRIFT VIOLATION: Unmapped file '{rel}'")
        
        return violations
