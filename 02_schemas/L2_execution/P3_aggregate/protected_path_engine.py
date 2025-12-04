#!/usr/bin/env python3
"""
Protected-Path Loader and Expansion Engine for Agentic-Workflow

Implements G6: Protected-path loader + expansion engine

Provides runtime pattern loading, expansion logic, and cross-phase shared
protected-path definitions that all phases can reference for enforcement.
"""

import re
import fnmatch
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ProtectionLevel(Enum):
    READ_ONLY = "read_only"
    NO_DELETE = "no_delete"
    NO_RENAME = "no_rename"
    NO_MOVE = "no_move"
    IMMUTABLE = "immutable"


@dataclass
class ProtectedPath:
    pattern: str
    level: ProtectionLevel
    description: str
    phase_scope: List[str]  # Which phases this applies to
    expanded_paths: List[str] = None  # Resolved concrete paths


class ProtectedPathEngine:
    """
    Protected-path loader and expansion engine
    
    Loads protected path patterns from META, expands them to concrete paths,
    and provides enforcement APIs for all phases to use.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.meta_yaml_path = self.workspace_root / "unified_structure_subatomic_meta.yaml"
        
        # Add path for imports
        sys.path.insert(0, str(self.workspace_root / "02_schemas"))
        
        # Load SSoT merger for canonical structure
        from ssot_merger import SSoTMerger
        self.ssot_merger = SSoTMerger(workspace_root)
        self.canonical_ssot = self.ssot_merger.merge()
        
        self.protected_paths: List[ProtectedPath] = []
        self.expanded_cache: Dict[str, List[str]] = {}
        
    def load_protected_paths_from_meta(self) -> List[ProtectedPath]:
        """
        Load protected path patterns from META YAML
        
        Returns:
            List of ProtectedPath objects
        """
        try:
            with open(self.meta_yaml_path, 'r', encoding='utf-8') as f:
                meta = yaml.safe_load(f)
            
            protected_patterns = meta.get('protected_paths', [])
            paths = []
            
            for pattern in protected_patterns:
                # Determine protection level based on pattern characteristics
                level = self._determine_protection_level(pattern)
                
                # Apply to all phases by default
                phase_scope = ['0.5', '1', '2', '3', '4']
                
                protected_path = ProtectedPath(
                    pattern=pattern,
                    level=level,
                    description=f"Protected pattern: {pattern}",
                    phase_scope=phase_scope,
                    expanded_paths=[]
                )
                
                paths.append(protected_path)
            
            self.protected_paths = paths
            return paths
            
        except Exception as e:
            raise ValueError(f"Failed to load protected paths from META: {e}")
    
    def _determine_protection_level(self, pattern: str) -> ProtectionLevel:
        """
        Determine protection level based on pattern characteristics
        
        Args:
            pattern: Glob pattern string
            
        Returns:
            ProtectionLevel enum value
        """
        if pattern == "**/__init__.py":
            return ProtectionLevel.IMMUTABLE
        elif pattern.endswith("*.md"):
            return ProtectionLevel.NO_DELETE
        elif pattern.startswith("**/"):
            return ProtectionLevel.NO_MOVE
        else:
            return ProtectionLevel.READ_ONLY
    
    def expand_pattern_to_paths(self, pattern: str) -> List[str]:
        """
        Expand a glob pattern to concrete paths in the workspace
        
        Args:
            pattern: Glob pattern to expand
            
        Returns:
            List of matching concrete paths
        """
        if pattern in self.expanded_cache:
            return self.expanded_cache[pattern]
        
        expanded = []
        
        # Convert glob pattern to regex for more flexible matching
        regex_pattern = self._glob_to_regex(pattern)
        
        # Walk the workspace and find matches
        for path in self.workspace_root.rglob("*"):
            if path.is_file():
                relative_path = path.relative_to(self.workspace_root)
                path_str = str(relative_path).replace("\\", "/")
                
                # Check if path matches pattern
                if fnmatch.fnmatch(path_str, pattern) or re.match(regex_pattern, path_str):
                    expanded.append(path_str)
        
        # Cache the result
        self.expanded_cache[pattern] = expanded
        return expanded
    
    def _glob_to_regex(self, pattern: str) -> str:
        """
        Convert glob pattern to regex for enhanced matching
        
        Args:
            pattern: Glob pattern
            
        Returns:
            Regex pattern string
        """
        # Convert glob wildcards to regex
        regex = pattern.replace("**", ".*").replace("*", "[^/]*").replace("?", "[^/]")
        regex = f"^{regex}$"
        return regex
    
    def expand_all_protected_paths(self) -> Dict[str, List[str]]:
        """
        Expand all protected path patterns to concrete paths
        
        Returns:
            Dict mapping patterns to expanded path lists
        """
        if not self.protected_paths:
            self.load_protected_paths_from_meta()
        
        expansion_results = {}
        
        for protected_path in self.protected_paths:
            expanded = self.expand_pattern_to_paths(protected_path.pattern)
            protected_path.expanded_paths = expanded
            expansion_results[protected_path.pattern] = expanded
        
        return expansion_results
    
    def check_path_protection(self, path: str, operation: str = "read", 
                             phase: str = "all") -> Optional[ProtectedPath]:
        """
        Check if a path is protected for a given operation and phase
        
        Args:
            path: Path to check (relative to workspace root)
            operation: Operation type (read, write, delete, rename, move)
            phase: Phase identifier (0.5, 1, 2, 3, 4, or all)
            
        Returns:
            ProtectedPath if protected, None if not protected
        """
        if not self.protected_paths:
            self.load_protected_paths_from_meta()
        
        # Normalize path
        normalized_path = path.replace("\\", "/")
        
        for protected_path in self.protected_paths:
            # Check if this applies to the current phase
            if phase != "all" and phase not in protected_path.phase_scope:
                continue
            
            # Check if path matches the pattern
            if fnmatch.fnmatch(normalized_path, protected_path.pattern):
                # Check if operation is allowed based on protection level
                if self._is_operation_blocked(operation, protected_path.level):
                    return protected_path
        
        return None
    
    def _is_operation_blocked(self, operation: str, level: ProtectionLevel) -> bool:
        """
        Check if an operation is blocked by protection level
        
        Args:
            operation: Operation to check
            level: Protection level
            
        Returns:
            True if operation is blocked
        """
        blocked_ops = {
            ProtectionLevel.IMMUTABLE: ["write", "delete", "rename", "move"],
            ProtectionLevel.NO_DELETE: ["delete"],
            ProtectionLevel.NO_RENAME: ["rename"],
            ProtectionLevel.NO_MOVE: ["move"],
            ProtectionLevel.READ_ONLY: ["write", "delete", "rename", "move"]
        }
        
        return operation in blocked_ops.get(level, [])
    
    def get_phase_protected_paths(self, phase: str) -> List[ProtectedPath]:
        """
        Get all protected paths that apply to a specific phase
        
        Args:
            phase: Phase identifier
            
        Returns:
            List of ProtectedPath objects for the phase
        """
        if not self.protected_paths:
            self.load_protected_paths_from_meta()
        
        return [p for p in self.protected_paths if phase in p.phase_scope]
    
    def validate_phase_operations(self, phase: str, operations: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Validate a list of operations for a phase against protected paths
        
        Args:
            phase: Phase identifier
            operations: List of operation dicts with 'path' and 'operation' keys
            
        Returns:
            List of validation results
        """
        results = []
        
        for op in operations:
            path = op.get('path', '')
            operation = op.get('operation', 'read')
            
            protection = self.check_path_protection(path, operation, phase)
            
            result = {
                'path': path,
                'operation': operation,
                'allowed': protection is None,
                'protected_path': protection.pattern if protection else None,
                'protection_level': protection.level.value if protection else None,
                'phase': phase
            }
            
            results.append(result)
        
        return results
    
    def generate_protection_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive protection report
        
        Returns:
            Dict with protection analysis
        """
        # Load and expand all protected paths
        self.load_protected_paths_from_meta()
        expansion_results = self.expand_all_protected_paths()
        
        report = {
            "workspace_root": str(self.workspace_root),
            "total_patterns": len(self.protected_paths),
            "total_protected_paths": sum(len(paths) for paths in expansion_results.values()),
            "patterns_by_level": {},
            "expansion_results": expansion_results,
            "phase_coverage": {}
        }
        
        # Group by protection level
        for protected_path in self.protected_paths:
            level = protected_path.level.value
            if level not in report["patterns_by_level"]:
                report["patterns_by_level"][level] = []
            report["patterns_by_level"][level].append({
                "pattern": protected_path.pattern,
                "description": protected_path.description,
                "phase_scope": protected_path.phase_scope
            })
        
        # Analyze phase coverage
        for phase in ["0.5", "1", "2", "3", "4"]:
            phase_paths = self.get_phase_protected_paths(phase)
            report["phase_coverage"][phase] = {
                "pattern_count": len(phase_paths),
                "total_paths": sum(len(p.expanded_paths or []) for p in phase_paths)
            }
        
        return report
    
    def save_protection_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Save protection report to file
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Path where report was saved
        """
        if output_path is None:
            output_path = self.workspace_root / "02_schemas" / "protected_path_report.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_protection_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """
    CLI entry point for protected path engine
    
    Usage:
    python protected_path_engine.py [--workspace /path/to/workspace] [--report /path/to/report.json]
    """
    import argparse
    import yaml
    import json
    
    parser = argparse.ArgumentParser(description="Protected path loader and expansion engine")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--report", type=Path,
                       help="Output path for protection report")
    parser.add_argument("--check-path", type=str,
                       help="Check if a specific path is protected")
    parser.add_argument("--operation", type=str, default="read",
                       choices=["read", "write", "delete", "rename", "move"],
                       help="Operation to check for protected path")
    parser.add_argument("--phase", type=str, default="all",
                       help="Phase to check protection for")
    
    args = parser.parse_args()
    
    engine = ProtectedPathEngine(args.workspace)
    
    try:
        if args.check_path:
            # Check specific path protection
            protection = engine.check_path_protection(args.check_path, args.operation, args.phase)
            
            if protection:
                print(f"✗ Path '{args.check_path}' is PROTECTED")
                print(f"  Pattern: {protection.pattern}")
                print(f"  Level: {protection.level.value}")
                print(f"  Operation '{args.operation}' blocked: {engine._is_operation_blocked(args.operation, protection.level)}")
            else:
                print(f"✓ Path '{args.check_path}' is not protected for operation '{args.operation}'")
        
        else:
            # Generate full protection report
            report_path = engine.save_protection_report(args.report)
            report = engine.generate_protection_report()
            
            print("=== PROTECTED PATH ANALYSIS ===")
            print(f"Total patterns: {report['total_patterns']}")
            print(f"Total protected paths: {report['total_protected_paths']}")
            print(f"Report saved: {report_path}")
            
            # Show patterns by level
            for level, patterns in report['patterns_by_level'].items():
                print(f"\n{level.upper()} patterns: {len(patterns)}")
                for pattern in patterns:
                    print(f"  - {pattern['pattern']}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Protected path engine error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
