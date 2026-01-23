#!/usr/bin/env python3
from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
UnifiedCodeEnforcerAgent - Code Sovereignty Enforcement

Phase 3 Hard Migration: Consolidates:
- CodeSSOTEnforcerAgent (SSOT registry sync)
- CodeStandardsEnforcerAgent (code standards)
- PatternEnforcerAgent (pattern enforcement)
- TypeEnforcerAgent (type hint enforcement)
- PythonFileSovereigntyEnforcerAgent (file sovereignty)

Features:
- SSOT registry synchronization
- Code standards enforcement
- Pattern detection and enforcement
- Type hint validation
- Layer sovereignty protection (L5 files protected from L3/L4 modification)
- Signed exception support for cross-layer access
"""


import ast
import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class EnforcementType(Enum):
    """Types of code enforcement."""

    SSOT_SYNC = auto()
    CODE_STANDARDS = auto()
    PATTERN = auto()
    TYPE_HINTS = auto()
    SOVEREIGNTY = auto()


class ViolationSeverity(Enum):
    """Severity levels for violations."""

    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


@dataclass
class CodeViolation:
    """Represents a code violation."""

    file_path: Path
    line_number: int
    enforcement_type: EnforcementType
    severity: ViolationSeverity
    message: str
    suggested_fix: str | None = None
    auto_fixable: bool = False


@dataclass
class SignedException:
    """Signed exception for cross-layer access."""

    exception_id: str
    source_layer: str
    target_layer: str
    target_file: str
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    reason: str = ""


@dataclass
class EnforcementConfig:
    """configuration for code enforcement."""

    enable_ssot_sync: bool = True
    enable_standards: bool = True
    enable_patterns: bool = True
    enable_type_hints: bool = True
    enable_sovereignty: bool = True
    auto_fix: bool = False
    ssot_registry_path: Path | None = None
    protected_layers: set[str] = field(default_factory=lambda: {"L5", "L6"})


class UnifiedCodeEnforcerAgent(SovereignBaseAgent):
    """
    Unified code enforcement with sovereignty protection.

    Consolidates:
    - CodeSSOTEnforcerAgent (SSOT sync)
    - CodeStandardsEnforcerAgent (standards)
    - PatternEnforcerAgent (patterns)
    - TypeEnforcerAgent (type hints)
    - PythonFileSovereigntyEnforcerAgent (sovereignty)

    Usage:
        enforcer = UnifiedCodeEnforcerAgent()

        # Validate a file
        violations = enforcer.validate_file(Path("my_agent.py"))

        # Check sovereignty
        can_modify = enforcer.check_sovereignty("L3", Path("L5/agent.py"))

        # Sync SSOT
        enforcer.sync_ssot_registry()
    """

    def __init__(
        self,
        project_root: Path | None = None,
        config: EnforcementConfig | None = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.config = config or EnforcementConfig()
        self._lock = threading.RLock()
        self._ssot_registry: dict[str, Any] = {}
        self._signed_exceptions: dict[str, SignedException] = {}
        self._violations: list[CodeViolation] = []

        # Pattern definitions
        self._forbidden_patterns = {
            "mutable_default": re.compile(r"def\s+\w+\([^)]*=\s*(\[\]|\{\}|\(\))"),
            "bare_except": re.compile(r"except\s*:"),
            "eval_exec": re.compile(r"\b(eval|exec)\s*\("),
            "print_statement": re.compile(r"^\s*print\s*\("),
        }

        # Standard patterns
        self._agent_suffix_pattern = re.compile(r"class\s+(\w+)(?:\(|:)")
        self._type_hint_pattern = re.compile(r"def\s+\w+\([^)]*\)\s*(?:->|:)")

        Logger.info("UnifiedCodeEnforcerAgent initialized")

    def validate_file(self, file_path: Path) -> list[CodeViolation]:
        """Validate a file for all enforcement types."""
        violations = []

        if not file_path.exists():
            return violations

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return violations

        # Run all enabled checks
        if self.config.enable_standards:
            violations.extend(self._check_standards(file_path, content))

        if self.config.enable_patterns:
            violations.extend(self._check_patterns(file_path, content))

        if self.config.enable_type_hints:
            violations.extend(self._check_type_hints(file_path, content))

        if self.config.enable_sovereignty:
            violations.extend(self._check_sovereignty_violations(file_path, content))

        return violations

    def _check_standards(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check code standards compliance."""
        violations = []
        lines = content.split("\n")

        # Check for Agent suffix in class names
        for i, line in enumerate(lines, 1):
            match = self._agent_suffix_pattern.search(line)
            if match:
                class_name = match.group(1)
                if file_path.name.endswith("Agent.py") and not class_name.endswith("Agent"):
                    violations.append(
                        CodeViolation(
                            file_path=file_path,
                            line_number=i,
                            enforcement_type=EnforcementType.CODE_STANDARDS,
                            severity=ViolationSeverity.ERROR,
                            message=f"Class '{class_name}' must end with 'Agent' suffix",
                            suggested_fix=f"class {class_name}Agent",
                            auto_fixable=True,
                        )
                    )

        return violations

    def _check_patterns(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for forbidden patterns."""
        violations = []
        lines = content.split("\n")

        for pattern_name, pattern in self._forbidden_patterns.items():
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    violations.append(
                        CodeViolation(
                            file_path=file_path,
                            line_number=i,
                            enforcement_type=EnforcementType.PATTERN,
                            severity=ViolationSeverity.WARNING,
                            message=f"Forbidden pattern '{pattern_name}' detected",
                        )
                    )

        return violations

    def _check_type_hints(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for type hint compliance."""
        violations = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check return type hint
                if node.returns is None and not node.name.startswith("_"):
                    violations.append(
                        CodeViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            enforcement_type=EnforcementType.TYPE_HINTS,
                            severity=ViolationSeverity.INFO,
                            message=f"Function '{node.name}' missing return type hint",
                        )
                    )

        return violations

    def _check_sovereignty_violations(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for sovereignty violations (cross-layer access)."""
        violations = []

        # Determine file's layer
        file_layer = self._extract_layer(file_path)
        if not file_layer:
            return violations

        # Check imports for layer violations
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                import_layer = self._extract_layer_from_import(node)
                if import_layer and self._is_sovereignty_violation(file_layer, import_layer):
                    violations.append(
                        CodeViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            enforcement_type=EnforcementType.SOVEREIGNTY,
                            severity=ViolationSeverity.CRITICAL,
                            message=f"Sovereignty violation: {file_layer} importing from {import_layer}",
                        )
                    )

        return violations

    def _extract_layer(self, path: Path) -> str | None:
        """Extract layer from file path."""
        path_str = str(path)
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
                return layer
        return None

    def _extract_layer_from_import(self, node: ast.AST) -> str | None:
        """Extract layer from import statement."""
        if isinstance(node, ast.ImportFrom) and node.module:
            for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
                if f".{layer}_" in node.module or node.module.startswith(f"{layer}_"):
                    return layer
        return None

    def _is_sovereignty_violation(self, source_layer: str, target_layer: str) -> bool:
        """Check if import violates sovereignty rules."""
        layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

        source_level = layer_order.get(source_layer, -1)
        target_level = layer_order.get(target_layer, -1)

        # Lower layers cannot import from higher protected layers
        if target_layer in self.config.protected_layers:
            if source_level < target_level:
                return True

        return False

    def check_sovereignty(
        self,
        source_layer: str,
        target_file: Path,
        agent_id: str | None = None,
    ) -> tuple[bool, str]:
        """
        Check if a layer can modify a target file.

        Args:
            source_layer: Layer attempting modification (e.g., "L3")
            target_file: File being modified
            agent_id: Optional agent ID for exception checking

        Returns:
            Tuple of (allowed, reason)
        """
        target_layer = self._extract_layer(target_file)

        if not target_layer:
            return True, "No layer restriction"

        # Check if target is protected
        if target_layer not in self.config.protected_layers:
            return True, "Target layer not protected"

        # Check layer hierarchy
        layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
        source_level = layer_order.get(source_layer, -1)
        target_level = layer_order.get(target_layer, -1)

        if source_level >= target_level:
            return True, "Same or higher layer"

        # Check for signed exception
        if agent_id:
            exception_key = f"{source_layer}:{target_file}"
            if exception_key in self._signed_exceptions:
                exc = self._signed_exceptions[exception_key]
                if exc.expires_at is None or datetime.utcnow() < exc.expires_at:
                    return True, f"Signed exception: {exc.reason}"

        return False, f"Sovereignty violation: {source_layer} cannot modify {target_layer} file"

    def grant_exception(
        self,
        source_layer: str,
        target_file: Path,
        granted_by: str,
        reason: str,
        expires_at: datetime | None = None,
    ) -> SignedException:
        """Grant a signed exception for cross-layer access."""
        import secrets

        exception = SignedException(
            exception_id=secrets.token_hex(8),
            source_layer=source_layer,
            target_layer=self._extract_layer(target_file) or "unknown",
            target_file=str(target_file),
            granted_by=granted_by,
            expires_at=expires_at,
            reason=reason,
        )

        exception_key = f"{source_layer}:{target_file}"
        self._signed_exceptions[exception_key] = exception

        Logger.info(f"Granted exception: {source_layer} -> {target_file} by {granted_by}")
        return exception

    def sync_ssot_registry(self) -> dict[str, Any]:
        """Synchronize with SSOT registry."""
        with self._lock:
            if not self.config.ssot_registry_path:
                self.config.ssot_registry_path = self.project_root / "agent_discovery_full.json"

            if self.config.ssot_registry_path.exists():
                import json

                try:
                    self._ssot_registry = json.loads(
                        self.config.ssot_registry_path.read_text(encoding="utf-8")
                    )
                    Logger.info(
                        f"SSOT registry synced: {len(self._ssot_registry.get('agents', []))} agents"
                    )
                except Exception as e:
                    Logger.error(f"Failed to sync SSOT registry: {e}")

            return self._ssot_registry

    def update_ssot_registry(self, updates: dict[str, Any]) -> bool:
        """Update SSOT registry with changes."""
        with self._lock:
            if not self.config.ssot_registry_path:
                return False

            self._ssot_registry.update(updates)

            import json

            try:
                self.config.ssot_registry_path.write_text(
                    json.dumps(self._ssot_registry, indent=2),
                    encoding="utf-8",
                )
                Logger.info("SSOT registry updated")
                return True
            except Exception as e:
                Logger.error(f"Failed to update SSOT registry: {e}")
                return False

    def get_violations(self) -> list[CodeViolation]:
        """Get all recorded violations."""
        return self._violations.copy()


# Factory methods for backward compatibility
def create_legacy_ssot_enforcer() -> UnifiedCodeEnforcerAgent:
    """Create enforcer for SSOT sync."""
    config = EnforcementConfig(
        enable_ssot_sync=True,
        enable_standards=False,
        enable_patterns=False,
        enable_type_hints=False,
        enable_sovereignty=False,
    )
    return UnifiedCodeEnforcerAgent(config=config)


def create_legacy_standards_enforcer() -> UnifiedCodeEnforcerAgent:
    """Create enforcer for code standards."""
    config = EnforcementConfig(
        enable_ssot_sync=False,
        enable_standards=True,
        enable_patterns=True,
        enable_type_hints=True,
        enable_sovereignty=False,
    )
    return UnifiedCodeEnforcerAgent(config=config)


def create_legacy_sovereignty_enforcer() -> UnifiedCodeEnforcerAgent:
    """Create enforcer for file sovereignty."""
    config = EnforcementConfig(
        enable_ssot_sync=False,
        enable_standards=False,
        enable_patterns=False,
        enable_type_hints=False,
        enable_sovereignty=True,
    )
    return UnifiedCodeEnforcerAgent(config=config)
