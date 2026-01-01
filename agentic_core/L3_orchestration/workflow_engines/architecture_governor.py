"""
ArchitectureGovernor - L3 Orchestration Framework Agent
Validates and enforces architectural patterns across the codebase.
[SSOT] Layer directories derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
logger: Any = logging.getLogger(__name__)
layer_dirs: Any = set(SOVEREIGN_REGISTRY['agentic_core']['subfolders'])

class architecture_governor:
    """
    L3 Orchestration: Architecture Pattern Enforcement
    Ensures code follows canonical architectural patterns and layer boundaries.
    """

    def __init__(self, project_root: Path=None):
        """
        Initialize the ArchitectureGovernor.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path.cwd()
        self.violations = []

    def validate_layer_boundaries(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate that file respects layer boundaries (L0-L5).
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            rel_path: Any = file_path.relative_to(self.project_root)
            parts: Any = rel_path.parts
            if len(parts) > 1 and parts[0] == 'agentic_core':
                if len(parts) > 2 and parts[1] in LAYER_DIRS:
                    return (True, f'Valid layer structure: {parts[1]}')
            return (False, 'File outside layer structure')
        except ValueError:
            return (False, 'File outside project root')

    def validate_architectural_patterns(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate architectural patterns in a file.
        
        Args:
            file_path: Path to file to validate
        
        Returns:
            Dictionary with validation results
        """
        is_valid, reason = self.validate_layer_boundaries(file_path)
        return {'file': str(file_path), 'valid': is_valid, 'reason': reason, 'violations': self.violations}

    def run_validation(self, files: List[Path]) -> Dict[str, Any]:
        """
        Run architecture validation on multiple files.
        
        Args:
            files: List of file paths to validate
            
        Returns:
            Summary of validation results
        """
        results: Any = []
        total_violations: Any = 0
        for file_path in files:
            result: Any = self.validate_architectural_patterns(file_path)
            results.append(result)
            if not result['valid']:
                total_violations += 1
        return {'total_files': len(files), 'total_violations': total_violations, 'results': results}