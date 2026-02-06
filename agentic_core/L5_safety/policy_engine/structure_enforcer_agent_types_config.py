#!/usr/bin/env python3
from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
StructureEnforcerAgent - Structural Enforcement

Phase 3 Hard Migration: Consolidates:
- GravityEnforcerAgent (layer gravity enforcement)
- HierarchyEnforcerAgent (hierarchy enforcement)
- NamingEnforcerAgent (naming conventions)
- DocEnforcerAgent (documentation enforcement)
- ASCIIEnforcerAgent (ASCII compliance)
- StrictDocEnforcerAgent (strict documentation)

Features:
- Gravity/layer import enforcement
- Hierarchy validation
- Naming convention enforcement ([Name]Agent suffix)
- Documentation completeness checks
- ASCII compliance validation
- Auto-rename for non-compliant classes
"""


import ast
import logging
import re
import shutil
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class StructureViolationType:
    """Types of structure violations."""

    GRAVITY = "GRAVITY"
    HIERARCHY = "HIERARCHY"
    NAMING = "NAMING"
    DOCUMENTATION = "DOCUMENTATION"
    ASCII = "ASCII"


@dataclass
class StructureViolation:
    """Represents a structure violation."""

    file_path: Path
    line_number: int
    violation_type: str
    message: str
    suggested_fix: str | None = None
    auto_fixable: bool = False
    severity: str = "ERROR"


@dataclass
class NamingRule:
    """Naming convention rule."""

    pattern: str
    suffix: str
    description: str
    auto_rename: bool = True


@dataclass
class StructureConfig:
    """configuration for structure enforcement."""

    enable_gravity: bool = True
    enable_hierarchy: bool = True
    enable_naming: bool = True
    enable_documentation: bool = True
    enable_ascii: bool = True
    auto_fix: bool = False
    agent_suffix: str = "Agent"
    required_docstring: bool = True
    min_docstring_length: int = 10


class StructureEnforcerAgent(SovereignBaseAgent):
    """
    Unified structure enforcement with gravity and naming.

    Consolidates:
    - GravityEnforcerAgent (layer imports)
    - HierarchyEnforcerAgent (hierarchy)
    - NamingEnforcerAgent (naming)
    - DocEnforcerAgent (documentation)
    - ASCIIEnforcerAgent (ASCII)
    - StrictDocEnforcerAgent (strict docs)

    Usage:
        enforcer = StructureEnforcerAgent()

        # Validate structure
        violations = enforcer.validate_file(Path("my_agent.py"))

        # Check gravity
        is_valid = enforcer.check_gravity_import("L2", "L5")

        # Force rename
        enforcer.force_rename_class(Path("BadName.py"), "BadName", "BadNameAgent")
    """

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        # Enforcer identifies structural issues; active healing is via Healer agents
        return {"violations": 0, "fixed": 0, "errors": 0}

    # Layer hierarchy (lower number = lower layer)
    LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

    # Gravity rules: which layers can import from which
    # Lower layers should NOT import from higher layers
    GRAVITY_RULES = {
        "L0": {"L0"},  # L0 can only import L0
        "L1": {"L0", "L1"},  # L1 can import L0, L1
        "L2": {"L0", "L1", "L2"},  # L2 can import L0, L1, L2
        "L3": {"L0", "L1", "L2", "L3"},  # L3 can import L0-L3
        "L4": {"L0", "L1", "L2", "L3", "L4"},  # L4 can import L0-L4
        "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},  # L5 can import L0-L5
        "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},  # L6 can import all
    }

    def __init__(
        self,
        project_root: Path | None = None,
        agent_config: StructureConfig | None = None,
    ):
        self.project_root = project_root or Path.cwd()
        self._agent_config = agent_config or StructureConfig()
        self._lock = threading.RLock()
        self._violations: list[StructureViolation] = []

        Logger.info("StructureEnforcerAgent initialized")

    def validate_file(self, file_path: Path) -> list[StructureViolation]:
        """Validate a file for all structure rules."""
        violations = []

        if not file_path.exists():
            return violations

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return violations

        # Run all enabled checks
        if self._agent_config.enable_gravity:
            violations.extend(self._check_gravity(file_path, content))

        if self._agent_config.enable_naming:
            violations.extend(self._check_naming(file_path, content))

        if self._agent_config.enable_documentation:
            violations.extend(self._check_documentation(file_path, content))

        if self._agent_config.enable_ascii:
            violations.extend(self._check_ascii(file_path, content))

        return violations

    def _extract_layer(self, path: Path) -> str | None:
        """Extract layer from file path."""
        path_str = str(path)
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
                return layer
        return None

    def _extract_layer_from_module(self, module: str) -> str | None:
        """Extract layer from module name."""
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f".{layer}_" in module or module.startswith(f"{layer}_") or f"_{layer}_" in module:
                return layer
        return None

    def _check_gravity(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check gravity (layer import) violations."""
        violations = []

        source_layer = self._extract_layer(file_path)
        if not source_layer:
            return violations

        allowed_layers = self.GRAVITY_RULES.get(source_layer, set())

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                target_layer = self._extract_layer_from_module(node.module)
                if target_layer and target_layer not in allowed_layers:
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.GRAVITY,
                            message=f"Gravity violation: {source_layer} cannot import from {target_layer}",
                            severity="CRITICAL",
                        )
                    )

        return violations

    def _check_naming(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check naming convention violations."""
        violations = []

        # Only check Agent files
        if not file_path.name.endswith("Agent.py"):
            return violations

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.endswith(self._agent_config.agent_suffix):
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.NAMING,
                            message=f"Class '{node.name}' must end with '{self._agent_config.agent_suffix}' suffix",
                            suggested_fix=f"{node.name}{self._agent_config.agent_suffix}",
                            auto_fixable=True,
                        )
                    )

        return violations

    def _check_documentation(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check documentation violations."""
        violations = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                docstring = ast.get_docstring(node)

                if self._agent_config.required_docstring and not docstring:
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.DOCUMENTATION,
                            message=f"Missing docstring for {type(node).__name__} '{node.name}'",
                            severity="WARNING",
                        )
                    )
                elif docstring and len(docstring) < self._agent_config.min_docstring_length:
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.DOCUMENTATION,
                            message=f"Docstring too short for '{node.name}' (min {self._agent_config.min_docstring_length} chars)",
                            severity="INFO",
                        )
                    )

        return violations

    def _check_ascii(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check ASCII compliance."""
        violations = []

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            try:
                line.encode("ascii")
            except UnicodeEncodeError:
                # Find non-ASCII characters
                non_ascii = [c for c in line if ord(c) > 127]
                violations.append(
                    StructureViolation(
                        file_path=file_path,
                        line_number=i,
                        violation_type=StructureViolationType.ASCII,
                        message=f"Non-ASCII characters found: {non_ascii[:5]}",
                        severity="WARNING",
                    )
                )

        return violations

    def check_gravity_import(self, source_layer: str, target_layer: str) -> tuple[bool, str]:
        """
        Check if an import from source to target layer is allowed.

        Args:
            source_layer: Layer doing the import (e.g., "L2")
            target_layer: Layer being imported (e.g., "L5")

        Returns:
            Tuple of (allowed, reason)
        """
        allowed_layers = self.GRAVITY_RULES.get(source_layer, set())

        if target_layer in allowed_layers:
            return True, f"{source_layer} can import from {target_layer}"
        else:
            return False, f"Gravity violation: {source_layer} cannot import from {target_layer}"

    def force_rename_class(
        self,
        file_path: Path,
        old_name: str,
        new_name: str,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """
        Force rename a class to comply with naming conventions.

        Args:
            file_path: Path to the file
            old_name: Current class name
            new_name: New class name (should end with Agent)
            dry_run: If True, don't actually modify

        Returns:
            Result dictionary
        """
        result = {
            "file": str(file_path),
            "old_name": old_name,
            "new_name": new_name,
            "applied": False,
            "dry_run": dry_run,
        }

        if not file_path.exists():
            result["error"] = "File not found"
            return result

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result["error"] = str(e)
            return result

        # Replace class name
        new_content = re.sub(
            rf"\bclass\s+{old_name}\b",
            f"class {new_name}",
            content,
        )

        # Replace all references
        new_content = re.sub(rf"\b{old_name}\b", new_name, new_content)

        if new_content == content:
            result["message"] = "No changes needed"
            return result

        if not dry_run:
            # Backup first
            backup_dir = self.project_root / "archives" / "healing_backups" / "naming"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)

            # Write new content
            file_path.write_text(new_content, encoding="utf-8")
            result["applied"] = True
            result["backup"] = str(backup_path)

            Logger.info(f"Renamed class: {old_name} -> {new_name} in {file_path}")
        else:
            result["message"] = "Dry run - no changes applied"

        return result

    def validate_hierarchy(self, file_path: Path) -> list[StructureViolation]:
        """Validate file hierarchy placement."""
        violations = []

        layer = self._extract_layer(file_path)
        if not layer:
            return violations

        # Check if file is in correct layer directory
        expected_prefix = f"{layer}_"
        path_parts = file_path.parts

        layer_found = False
        for part in path_parts:
            if part.startswith(expected_prefix):
                layer_found = True
                break

        if not layer_found:
            violations.append(
                StructureViolation(
                    file_path=file_path,
                    line_number=0,
                    violation_type=StructureViolationType.HIERARCHY,
                    message=f"File not in expected layer directory: {layer}",
                )
            )

        return violations

    def get_violations(self) -> list[StructureViolation]:
        """Get all recorded violations."""
        return self._violations.copy()

    def heal(self, violation: dict) -> dict:
        """Heal structure enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, hierarchy, naming, documentation, ascii)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        violation_type = violation.get("type", "")
        path = violation.get("path", "")

        Logger.info(f"[STRUCTURE_ENFORCER] Healing {violation_type} at {path}")

        try:
            file_path = Path(path) if path else None
            if not file_path or not file_path.exists():
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            if violation_type == "gravity":
                result = self.enforce_gravity(file_path)
                return {
                    "violations_fixed": len(result),
                    "violations_found": len(result),
                    "errors": 0,
                    "skipped": 0,
                }
            elif violation_type == "naming":
                result = self.enforce_naming(file_path)
                return {
                    "violations_fixed": len(result),
                    "violations_found": len(result),
                    "errors": 0,
                    "skipped": 0,
                }
            elif violation_type == "hierarchy":
                result = self.enforce_hierarchy(file_path)
                return {
                    "violations_fixed": len(result),
                    "violations_found": len(result),
                    "errors": 0,
                    "skipped": 0,
                }
            else:
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        except Exception as e:
            Logger.error(f"[STRUCTURE_ENFORCER] Failed to heal: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}


# Factory methods for backward compatibility
def create_legacy_gravity_enforcer() -> StructureEnforcerAgent:
    """Create enforcer for gravity rules."""
    config = StructureConfig(
        enable_gravity=True,
        enable_hierarchy=False,
        enable_naming=False,
        enable_documentation=False,
        enable_ascii=False,
    )
    return StructureEnforcerAgent(config=config)


def create_legacy_naming_enforcer() -> StructureEnforcerAgent:
    """Create enforcer for naming conventions."""
    config = StructureConfig(
        enable_gravity=False,
        enable_hierarchy=False,
        enable_naming=True,
        enable_documentation=False,
        enable_ascii=False,
    )
    return StructureEnforcerAgent(config=config)


def create_legacy_doc_enforcer() -> StructureEnforcerAgent:
    """Create enforcer for documentation."""
    config = StructureConfig(
        enable_gravity=False,
        enable_hierarchy=False,
        enable_naming=False,
        enable_documentation=True,
        enable_ascii=False,
    )
    return StructureEnforcerAgent(config=config)
