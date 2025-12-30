"""
L6 Watchdog: Drift Detector Agent
Scans for files that exist outside the CANON_KEY_TO_FOLDER_MAP.
Exempts root protected files and __init__.py glue files.
"""
from pathlib import Path
from typing import Any, List, Set
from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_KEY_TO_FOLDER_MAP, ROOT_PROTECTED_FILES

class drift_detector_agent:
    """Detects files that have drifted outside mapped canon territories."""

    def __init__(self, project_root: Path):
        """
        Initialize DriftDetectorAgent.
        
        Args:
            project_root: Absolute path to project root
        """
        self.root = project_root
        self.mapped_paths: Set[str] = set()
        for paths in CANON_KEY_TO_FOLDER_MAP.values():
            self.mapped_paths.update((p for p in paths if p != '*'))

    async def execute(self) -> List[str]:
        """
        Scan for unmapped files (drift violations).
        
        Returns:
            List of violation messages
        """
        violations: Any = []
        for py_file in self.root.rglob('*.py'):
            if any((part.startswith('.') or part == '__pycache__' for part in py_file.parts)):
                continue
            rel: Any = str(py_file.relative_to(self.root)).replace('\\', '/')
            if py_file.name in ROOT_PROTECTED_FILES:
                continue
            if py_file.name == '__init__.py':
                continue
            if not any((rel.startswith(m + '/') or rel == m for m in self.mapped_paths)):
                violations.append(f"DRIFT VIOLATION: Unmapped file '{rel}'")
        return violations
