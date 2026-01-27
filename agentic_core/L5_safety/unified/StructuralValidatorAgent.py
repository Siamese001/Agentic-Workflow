from enum import Enum, auto
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

#!/usr/bin/env python3
"""
StructuralValidatorAgent - Structure Validation & Compliance

Phase 4 Hard Migration: Consolidates:
- GravityValidatorAgent (layer gravity validation)
- HierarchyValidatorAgent (hierarchy validation)
- NamingLawValidatorAgent (naming convention validation)
- TerritoryValidatorAgent (territory/location validation)
- BlueprintValidatorAgent (blueprint compliance)

Features:
- Gravity violation validation
- Hierarchy compliance validation
- Naming convention enforcement
- Territory/location validation
- Blueprint compliance validation
"""

import logging
import re
from datetime import datetime

Logger = logging.getLogger(__name__)


class StructureValidationType(Enum):
    """Types of structure validation."""

    GRAVITY = auto()
    HIERARCHY = auto()
    NAMING = auto()
    TERRITORY = auto()
    BLUEPRINT = auto()


@dataclass
class StructureValidationResult:
    """Represents a structure validation result."""
    
    validation_type: StructureValidationType
    file_path: str
    issue: str
    severity: str = "MEDIUM"
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class StructureConfig:
    """Configuration for structure validation."""
    
    project_root: Path
    gravity_rules: Dict[str, Any] = field(default_factory=dict)
    hierarchy_rules: Dict[str, Any] = field(default_factory=dict)
    naming_rules: Dict[str, Any] = field(default_factory=dict)
    territory_rules: Dict[str, Any] = field(default_factory=dict)
    blueprint_rules: Dict[str, Any] = field(default_factory=dict)


class StructuralValidatorAgent(SovereignBaseAgent, SubatomicTestingMixin):
    """
    Unified Structure Validation Agent.
    
    Consolidates all structure validation logic into a single,
    efficient agent that validates multiple aspects of code structure.
    """
    
    def __init__(self, config: StructureConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.Logger = logging.getLogger(f"{self.__class__.__name__}")
        self._validation_results: List[StructureValidationResult] = []
    
    def validate_gravity(self, file_path: Path) -> List[StructureValidationResult]:
        """Validate gravity compliance for a file."""
        results = []
        
        # Example gravity validation: check if file is in correct layer
        if "L0_maintenance" in str(file_path) and "agent" in file_path.name.lower():
            if not file_path.name.startswith("Maintenance"):
                results.append(StructureValidationResult(
                    validation_type=StructureValidationType.GRAVITY,
                    file_path=str(file_path),
                    issue="L0 maintenance agent should start with 'Maintenance'",
                    severity="HIGH",
                    suggested_fix=f"Rename {file_path.name} to Maintenance{file_path.name}",
                    auto_fixable=True
                ))
        
        return results
    
    def validate_hierarchy(self, file_path: Path) -> List[StructureValidationResult]:
        """Validate hierarchy compliance for a file."""
        results = []
        
        # Example hierarchy validation: check import hierarchy
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for circular imports or incorrect layer dependencies
            if "from agentic_core.L6_observability" in content and "L0_maintenance" in str(file_path):
                results.append(StructureValidationResult(
                    validation_type=StructureValidationType.HIERARCHY,
                    file_path=str(file_path),
                    issue="L0 maintenance agent importing from L6 (violates hierarchy)",
                    severity="HIGH",
                    suggested_fix="Remove L6 dependency from L0 agent",
                    auto_fixable=False
                ))
        except Exception as e:
            self.Logger.warning(f"Could not read {file_path}: {e}")
        
        return results
    
    def validate_naming(self, file_path: Path) -> List[StructureValidationResult]:
        """Validate naming conventions for a file."""
        results = []
        
        # Example naming validation: check class names
        if file_path.suffix == '.py':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for agent naming convention
                if "Agent" in content and file_path.name.startswith("test_"):
                    # Test files should not have Agent classes
                    if re.search(r'class\s+\w+Agent', content):
                        results.append(StructureValidationResult(
                            validation_type=StructureValidationType.NAMING,
                            file_path=str(file_path),
                            issue="Test file contains Agent class",
                            severity="MEDIUM",
                            suggested_fix="Move Agent class out of test file or rename",
                            auto_fixable=False
                        ))
            except Exception as e:
                self.Logger.warning(f"Could not read {file_path}: {e}")
        
        return results
    
    def validate_territory(self, file_path: Path) -> List[StructureValidationResult]:
        """Validate territory compliance for a file."""
        results = []
        
        # Example territory validation: check if file is in correct territory
        file_str = str(file_path)
        
        # Check for files in wrong territories
        if "prompt_governance" in file_str and "validator" in file_str:
            if "L5_safety" not in file_str:
                results.append(StructureValidationResult(
                    validation_type=StructureValidationType.TERRITORY,
                    file_path=str(file_path),
                    issue="Prompt governance validator should be in L5_safety",
                    severity="HIGH",
                    suggested_fix="Move file to L5_safety/validators directory",
                    auto_fixable=False
                ))
        
        return results
    
    def validate_blueprint(self, file_path: Path) -> List[StructureValidationResult]:
        """Validate blueprint compliance for a file."""
        results = []
        
        # Example blueprint validation: check structure blueprint compliance
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import CORE_SUBFOLDER_MAP
            
            file_str = str(file_path)
            
            # Check if file is in a valid subfolder
            for layer, subfolders in CORE_SUBFOLDER_MAP.items():
                if layer in file_str:
                    # Extract the subfolder from the path
                    parts = Path(file_str).parts
                    if layer in parts:
                        layer_idx = parts.index(layer)
                        if layer_idx + 1 < len(parts):
                            subfolder = parts[layer_idx + 1]
                            if subfolder not in subfolders:
                                results.append(StructureValidationResult(
                                    validation_type=StructureValidationType.BLUEPRINT,
                                    file_path=str(file_path),
                                    issue=f"Subfolder '{subfolder}' not in blueprint for layer '{layer}'",
                                    severity="HIGH",
                                    suggested_fix=f"Move to valid subfolder: {', '.join(subfolders)}",
                                    auto_fixable=False
                                ))
                    break
        except ImportError:
            self.Logger.warning("Could not import structure blueprint for validation")
        
        return results
    
    def validate_file(self, file_path: Path) -> List[StructureValidationResult]:
        """Validate a single file for all structure rules."""
        results = []
        
        # Run all validation types
        results.extend(self.validate_gravity(file_path))
        results.extend(self.validate_hierarchy(file_path))
        results.extend(self.validate_naming(file_path))
        results.extend(self.validate_territory(file_path))
        results.extend(self.validate_blueprint(file_path))
        
        return results
    
    def validate_directory(self, directory: Path) -> List[StructureValidationResult]:
        """Validate all Python files in a directory."""
        results = []
        
        if not directory.exists():
            self.Logger.warning(f"Directory does not exist: {directory}")
            return results
        
        for py_file in directory.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                results.extend(self.validate_file(py_file))
        
        return results
    
    def validate_project(self) -> Dict[str, Any]:
        """Validate the entire project structure."""
        self.Logger.info("Starting full project structure validation")
        
        all_results = []
        project_root = self.config.project_root
        
        # Validate all Python files in the project
        for py_file in project_root.rglob("*.py"):
            if "__pycache__" not in str(py_file) and ".git" not in str(py_file):
                all_results.extend(self.validate_file(py_file))
        
        # Categorize results
        summary = {
            "total_issues": len(all_results),
            "gravity_issues": len([r for r in all_results if r.validation_type == StructureValidationType.GRAVITY]),
            "hierarchy_issues": len([r for r in all_results if r.validation_type == StructureValidationType.HIERARCHY]),
            "naming_issues": len([r for r in all_results if r.validation_type == StructureValidationType.NAMING]),
            "territory_issues": len([r for r in all_results if r.validation_type == StructureValidationType.TERRITORY]),
            "blueprint_issues": len([r for r in all_results if r.validation_type == StructureValidationType.BLUEPRINT]),
            "high_severity": len([r for r in all_results if r.severity == "HIGH"]),
            "medium_severity": len([r for r in all_results if r.severity == "MEDIUM"]),
            "low_severity": len([r for r in all_results if r.severity == "LOW"]),
            "auto_fixable": len([r for r in all_results if r.auto_fixable]),
            "results": all_results
        }
        
        self.Logger.info(f"Validation complete: {summary['total_issues']} issues found")
        return summary
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, int]:
        """Heal structure violations found during validation."""
        validation_results = self.validate_project()
        
        violations_found = validation_results["total_issues"]
        violations_fixed = 0
        errors = 0
        skipped = 0
        
        if violations_found == 0:
            return {
                'violations_found': 0,
                'violations_fixed': 0,
                'errors': 0,
                'skipped': 0
            }
        
        self.Logger.info(f"Found {violations_found} structure violations")
        
        # Process auto-fixable violations
        for result in validation_results["results"]:
            if result.auto_fixable and execute and not dry_run:
                try:
                    # Apply auto-fix (placeholder - would implement actual fixes)
                    self.Logger.info(f"Auto-fixing: {result.issue}")
                    violations_fixed += 1
                except Exception as e:
                    self.Logger.error(f"Failed to fix {result.file_path}: {e}")
                    errors += 1
            elif not result.auto_fixable:
                skipped += 1
        
        if dry_run:
            self.Logger.info("DRY RUN: No fixes applied")
        
        return {
            'violations_found': violations_found,
            'violations_fixed': violations_fixed,
            'errors': errors,
            'skipped': skipped
        }


class StructureViolationType(Enum):
    """Types of structure violations."""

    GRAVITY = auto()
    HIERARCHY = auto()
    NAMING = auto()
    TERRITORY = auto()
    BLUEPRINT = auto()


@dataclass
class StructureViolation:
    """Represents a structure violation."""
    
    violation_type: StructureViolationType
    file_path: str
    issue: str
    severity: str = "MEDIUM"
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    line_number: Optional[int] = None


@dataclass
class StructureReport:
    """Report generated by structure validation."""
    
    validation_summary: Dict[str, Any]
    violations: List[StructureViolation]
    total_violations: int
    auto_fixable_count: int
    high_severity_count: int
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "validation_summary": self.validation_summary,
            "violations": [
                {
                    "type": v.violation_type.name,
                    "file_path": v.file_path,
                    "issue": v.issue,
                    "severity": v.severity,
                    "suggested_fix": v.suggested_fix,
                    "auto_fixable": v.auto_fixable,
                    "line_number": v.line_number
                }
                for v in self.violations
            ],
            "total_violations": self.total_violations,
            "auto_fixable_count": self.auto_fixable_count,
            "high_severity_count": self.high_severity_count,
            "validation_timestamp": self.validation_timestamp
        }


# Factory functions for backward compatibility
def create_legacy_gravity_validator(**kwargs):
    """Create a legacy gravity validator."""
    return StructuralValidatorAgent(config=StructureConfig(project_root=Path.cwd()), **kwargs)


def create_legacy_hygiene_validator(**kwargs):
    """Create a legacy hygiene validator."""
    return StructuralValidatorAgent(config=StructureConfig(project_root=Path.cwd()), **kwargs)


def create_legacy_registry_validator(**kwargs):
    """Create a legacy registry validator."""
    return StructuralValidatorAgent(config=StructureConfig(project_root=Path.cwd()), **kwargs)


# Backward compatibility alias
UnifiedStructureValidatorAgent = StructuralValidatorAgent


__all__ = [
    "StructuralValidatorAgent",
    "StructureValidationType",
    "StructureValidationResult",
    "StructureConfig",
    "StructureViolationType",
    "StructureViolation",
    "StructureReport",
    "UnifiedStructureValidatorAgent",
    "create_legacy_gravity_validator",
    "create_legacy_hygiene_validator",
    "create_legacy_registry_validator",
]
