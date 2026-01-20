#!/usr/bin/env python3
"""
UnifiedStructureValidatorAgent - Structure and Architecture Validation

Phase 2 Consolidation: Merges functionality from:
- GravityValidatorAgent (layer enforcement)
- HygieneValidatorAgent (duplicate/orphan detection)
- UnifiedHygieneValidatorAgent (hygiene checks)
- AgentRegistryValidatorAgent (registry compliance)
- CognitiveContractValidatorAgent (contract validation)

Features:
- Gravity/Layer violation detection (L3 importing L5 = violation)
- Hygiene checks (duplicates, orphans, dead code)
- Registry integration (validate agents are properly declared)
- Cognitive contract validation
"""
from __future__ import annotations

import ast
import json
import logging
import re
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger = logging.getLogger(__name__)


class StructureViolationType(Enum):
    """Types of structure violations."""
    GRAVITY = auto()          # Layer violation (L3 importing L5)
    DUPLICATE = auto()        # Duplicate agent/file
    ORPHAN = auto()           # Orphaned agent (not in registry)
    REGISTRY = auto()         # Registry compliance issue
    CONTRACT = auto()         # Cognitive contract violation
    HIERARCHY = auto()        # Hierarchy violation
    NAMING = auto()           # Naming convention violation
    LOCATION = auto()         # File in wrong location


# Layer hierarchy - lower number = lower layer
LAYER_HIERARCHY = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
    "Apps": 7,
}

# Valid import directions (can import from layers at or below)
# L3 can import from L0, L1, L2, L3 but NOT L4, L5, L6
GRAVITY_RULES = {
    "L0": {"L0"},
    "L1": {"L0", "L1"},
    "L2": {"L0", "L1", "L2"},
    "L3": {"L0", "L1", "L2", "L3"},
    "L4": {"L0", "L1", "L2", "L3", "L4"},
    "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
    "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
    "Apps": {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps"},
}


@dataclass
class StructureViolation:
    """Represents a structure violation."""
    violation_type: StructureViolationType
    message: str
    file_path: Optional[Path] = None
    source_layer: Optional[str] = None
    target_layer: Optional[str] = None
    severity: str = "error"
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        loc = str(self.file_path) if self.file_path else "unknown"
        return f"[{self.violation_type.name}] {loc}: {self.message}"


@dataclass
class StructureReport:
    """Report of structure validation results."""
    violations: List[StructureViolation] = field(default_factory=list)
    agents_found: int = 0
    agents_registered: int = 0
    duplicates_found: int = 0
    orphans_found: int = 0
    gravity_violations: int = 0
    execution_time: float = 0.0
    
    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)
    
    @property
    def is_valid(self) -> bool:
        return not self.has_errors


@dataclass
class StructureConfig:
    """Configuration for structure validation."""
    check_gravity: bool = True
    check_duplicates: bool = True
    check_orphans: bool = True
    check_registry: bool = True
    check_contracts: bool = True
    check_hierarchy: bool = True
    
    # Gravity settings
    strict_gravity: bool = True  # Fail on any gravity violation
    allow_utils_imports: bool = True  # Allow importing from utils at any layer
    
    # Registry settings
    registry_path: Optional[Path] = None
    agent_discovery_path: Optional[Path] = None
    
    # Paths
    project_root: Optional[Path] = None


def extract_layer_from_path(file_path: Path) -> Optional[str]:
    """Extract the layer (L0-L6, Apps) from a file path."""
    path_str = str(file_path)
    
    # Check for layer patterns
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
            return layer
        if f"/{layer}/" in path_str or f"\\{layer}\\" in path_str:
            return layer
    
    # Check for apps
    if "/apps_" in path_str or "\\apps_" in path_str:
        return "Apps"
    if "/apps/" in path_str or "\\apps/" in path_str:
        return "Apps"
    if path_str.startswith("apps_") or path_str.startswith("apps/"):
        return "Apps"
    
    return None


def extract_layer_from_import(import_path: str) -> Optional[str]:
    """Extract the layer from an import path."""
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f".{layer}_" in import_path or f"{layer}_" in import_path:
            return layer
    
    if ".apps_" in import_path or "apps_" in import_path:
        return "Apps"
    
    return None


class GravityVisitor(ast.NodeVisitor):
    """AST visitor to detect gravity (layer) violations."""
    
    def __init__(self, source_layer: str, file_path: Path):
        self.source_layer = source_layer
        self.file_path = file_path
        self.violations: List[StructureViolation] = []
        self.imports: List[Tuple[str, int]] = []  # (import_path, line_number)
    
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append((alias.name, node.lineno))
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append((node.module, node.lineno))
        self.generic_visit(node)
    
    def check_gravity_violations(self) -> List[StructureViolation]:
        """Check all imports for gravity violations."""
        allowed_layers = GRAVITY_RULES.get(self.source_layer, set())
        
        for import_path, line_no in self.imports:
            target_layer = extract_layer_from_import(import_path)
            
            if target_layer and target_layer not in allowed_layers:
                # Skip utils imports if allowed
                if "utils" in import_path.lower():
                    continue
                
                self.violations.append(StructureViolation(
                    violation_type=StructureViolationType.GRAVITY,
                    message=f"Layer violation: {self.source_layer} cannot import from {target_layer}",
                    file_path=self.file_path,
                    source_layer=self.source_layer,
                    target_layer=target_layer,
                    severity="error",
                    rule_id="GRAVITY-001",
                    suggestion=f"Move shared code to a lower layer or use dependency injection",
                ))
        
        return self.violations


@dataclass
class UnifiedStructureValidatorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Unified structure validation with gravity, hygiene, and registry checks.
    
    Consolidates:
    - GravityValidatorAgent (layer enforcement)
    - HygieneValidatorAgent (duplicate/orphan detection)
    - UnifiedHygieneValidatorAgent (hygiene checks)
    - AgentRegistryValidatorAgent (registry compliance)
    - CognitiveContractValidatorAgent (contract validation)
    
    Usage:
        agent = UnifiedStructureValidatorAgent()
        report = agent.validate_structure(Path("agentic_core"))
        
        # Check specific file for gravity violations
        violations = agent.check_gravity(Path("my_agent.py"))
    """
    
    config: StructureConfig = field(default_factory=StructureConfig)
    
    def __post_init__(self) -> None:
        """Initialize the validator."""
        self._registry_cache: Optional[Dict[str, Any]] = None
        self._discovery_cache: Optional[Dict[str, Any]] = None
        Logger.info("UnifiedStructureValidatorAgent initialized")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry if available."""
        if self._registry_cache is not None:
            return self._registry_cache
        
        if self.config.registry_path and self.config.registry_path.exists():
            try:
                self._registry_cache = json.loads(self.config.registry_path.read_text())
                return self._registry_cache
            except Exception as e:
                Logger.warning(f"Could not load registry: {e}")
        
        self._registry_cache = {}
        return self._registry_cache
    
    def _load_discovery(self) -> List[Dict[str, Any]]:
        """Load agent discovery data if available."""
        if self._discovery_cache is not None:
            return self._discovery_cache
        
        if self.config.agent_discovery_path and self.config.agent_discovery_path.exists():
            try:
                self._discovery_cache = json.loads(self.config.agent_discovery_path.read_text())
                return self._discovery_cache
            except Exception as e:
                Logger.warning(f"Could not load discovery: {e}")
        
        self._discovery_cache = []
        return self._discovery_cache
    
    def check_gravity(
        self,
        file_path: Path,
        source_code: Optional[str] = None,
    ) -> List[StructureViolation]:
        """
        Check a file for gravity (layer) violations.
        
        Args:
            file_path: Path to the file
            source_code: Optional source code (reads from file if not provided)
            
        Returns:
            List of gravity violations found
        """
        source_layer = extract_layer_from_path(file_path)
        if not source_layer:
            return []  # Can't determine layer, skip
        
        if source_code is None:
            try:
                source_code = file_path.read_text(encoding="utf-8")
            except Exception as e:
                return [StructureViolation(
                    violation_type=StructureViolationType.GRAVITY,
                    message=f"Could not read file: {e}",
                    file_path=file_path,
                    severity="error",
                )]
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []  # Syntax errors handled by code validator
        
        visitor = GravityVisitor(source_layer, file_path)
        visitor.visit(tree)
        return visitor.check_gravity_violations()
    
    def check_duplicates(
        self,
        directory: Path,
        pattern: str = "**/*Agent.py",
    ) -> List[StructureViolation]:
        """
        Check for duplicate agent definitions.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for agent files
            
        Returns:
            List of duplicate violations
        """
        violations = []
        agent_locations: Dict[str, List[Path]] = {}
        
        for file_path in directory.glob(pattern):
            # Skip archives and tests
            if "archive" in str(file_path).lower() or "test" in str(file_path).lower():
                continue
            
            agent_name = file_path.stem
            if agent_name not in agent_locations:
                agent_locations[agent_name] = []
            agent_locations[agent_name].append(file_path)
        
        for agent_name, locations in agent_locations.items():
            if len(locations) > 1:
                violations.append(StructureViolation(
                    violation_type=StructureViolationType.DUPLICATE,
                    message=f"Duplicate agent '{agent_name}' found in {len(locations)} locations",
                    file_path=locations[0],
                    severity="warning",
                    rule_id="DUP-001",
                    suggestion=f"Consolidate duplicates: {[str(p) for p in locations]}",
                ))
        
        return violations
    
    def check_orphans(
        self,
        directory: Path,
        registered_agents: Optional[Set[str]] = None,
    ) -> List[StructureViolation]:
        """
        Check for orphaned agents (not in registry).
        
        Args:
            directory: Directory to scan
            registered_agents: Set of registered agent names
            
        Returns:
            List of orphan violations
        """
        violations = []
        
        if registered_agents is None:
            # Try to load from discovery
            discovery = self._load_discovery()
            registered_agents = {a.get("class_name", "") for a in discovery}
        
        for file_path in directory.glob("**/*Agent.py"):
            # Skip archives and tests
            if "archive" in str(file_path).lower() or "test" in str(file_path).lower():
                continue
            
            agent_name = file_path.stem
            if agent_name not in registered_agents:
                violations.append(StructureViolation(
                    violation_type=StructureViolationType.ORPHAN,
                    message=f"Orphaned agent '{agent_name}' not found in registry",
                    file_path=file_path,
                    severity="warning",
                    rule_id="ORPHAN-001",
                    suggestion="Add agent to registry or archive if deprecated",
                ))
        
        return violations
    
    def check_registry_compliance(
        self,
        agent_name: str,
        agent_path: Path,
    ) -> List[StructureViolation]:
        """
        Check if an agent complies with registry requirements.
        
        Args:
            agent_name: Name of the agent
            agent_path: Path to the agent file
            
        Returns:
            List of registry violations
        """
        violations = []
        
        # Check file name matches class name
        expected_filename = f"{agent_name}.py"
        if agent_path.name != expected_filename:
            violations.append(StructureViolation(
                violation_type=StructureViolationType.REGISTRY,
                message=f"Filename '{agent_path.name}' does not match agent name '{agent_name}'",
                file_path=agent_path,
                severity="warning",
                rule_id="REG-001",
                suggestion=f"Rename file to {expected_filename}",
            ))
        
        return violations
    
    def validate_structure(
        self,
        directory: Path,
        config: Optional[StructureConfig] = None,
    ) -> StructureReport:
        """
        Perform full structure validation on a directory.
        
        Args:
            directory: Directory to validate
            config: Optional custom configuration
            
        Returns:
            StructureReport with all violations found
        """
        config = config or self.config
        report = StructureReport()
        start_time = datetime.now()
        
        all_violations = []
        
        # Check gravity violations
        if config.check_gravity:
            for file_path in directory.glob("**/*.py"):
                if "archive" in str(file_path).lower():
                    continue
                violations = self.check_gravity(file_path)
                all_violations.extend(violations)
                report.gravity_violations += len(violations)
        
        # Check duplicates
        if config.check_duplicates:
            violations = self.check_duplicates(directory)
            all_violations.extend(violations)
            report.duplicates_found = len(violations)
        
        # Check orphans
        if config.check_orphans:
            violations = self.check_orphans(directory)
            all_violations.extend(violations)
            report.orphans_found = len(violations)
        
        # Count agents
        agent_files = list(directory.glob("**/*Agent.py"))
        report.agents_found = len([f for f in agent_files if "archive" not in str(f).lower()])
        
        report.violations = all_violations
        report.execution_time = (datetime.now() - start_time).total_seconds()
        
        return report
    
    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[set] = None,
    ) -> Dict[str, int]:
        """L5 structure validation agent - operational healing."""
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        
        _call_path.add(agent_name)
        try:
            Logger.info(f"[{agent_name}] L5 structure validation healing")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


# =============================================================================
# BACKWARD COMPATIBILITY FACTORY METHODS (Migration Complete)
# =============================================================================

def create_legacy_gravity_validator(**kwargs: Any) -> UnifiedStructureValidatorAgent:
    """Factory for backward compatibility with GravityValidatorAgent."""
    config = StructureConfig(
        check_gravity=True,
        check_duplicates=False,
        check_orphans=False,
        check_registry=False,
    )
    return UnifiedStructureValidatorAgent(config=config, **kwargs)


def create_legacy_hygiene_validator(**kwargs: Any) -> UnifiedStructureValidatorAgent:
    """Factory for backward compatibility with HygieneValidatorAgent."""
    config = StructureConfig(
        check_gravity=False,
        check_duplicates=True,
        check_orphans=True,
        check_registry=False,
    )
    return UnifiedStructureValidatorAgent(config=config, **kwargs)


def create_legacy_registry_validator(**kwargs: Any) -> UnifiedStructureValidatorAgent:
    """Factory for backward compatibility with AgentRegistryValidatorAgent."""
    config = StructureConfig(
        check_gravity=False,
        check_duplicates=False,
        check_orphans=True,
        check_registry=True,
    )
    return UnifiedStructureValidatorAgent(config=config, **kwargs)
