#!/usr/bin/env python3
"""
ArchitectureGovernor - L3 Orchestration Framework Agent
Validates and enforces architectural patterns across the codebase.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

logger = logging.getLogger(__name__)


class ArchitectureGovernor:
    """
    L3 Orchestration: Architecture Pattern Enforcement
    Ensures code follows canonical architectural patterns and layer boundaries.
    """
    
    def __init__(self, project_root: Path = None):
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
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            
            # Check if file is in a layer directory
            layer_dirs = {'L0_maintenance', 'L1_cognition', 'L2_execution', 
                         'L3_orchestration', 'L4_state', 'L5_safety'}
            
            if len(parts) > 1 and parts[0] == 'agentic_core':
                if len(parts) > 2 and parts[1] in layer_dirs:
                    return True, f"Valid layer structure: {parts[1]}"
                    
            return False, "File outside layer structure"
            
        except ValueError:
            return False, "File outside project root"
    
    def validate_architectural_patterns(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate architectural patterns in a file.
        
        Args:
            file_path: Path to file to validate
        
        Returns:
            Dictionary with validation results
        """
        is_valid, reason = self.validate_layer_boundaries(file_path)
        
        return {
            'file': str(file_path),
            'valid': is_valid,
            'reason': reason,
            'violations': self.violations
        }
    
    def run_validation(self, files: List[Path]) -> Dict[str, Any]:
        """
        Run architecture validation on multiple files.
        
        Args:
            files: List of file paths to validate
            
        Returns:
            Summary of validation results
        """
        results = []
        total_violations = 0
        
        for file_path in files:
            result = self.validate_architectural_patterns(file_path)
            results.append(result)
            if not result['valid']:
                total_violations += 1
        
        return {
            'total_files': len(files),
            'total_violations': total_violations,
            'results': results
        }