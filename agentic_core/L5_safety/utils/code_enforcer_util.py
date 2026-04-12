"""Code Enforcer Utility - Deterministic code enforcement.

This module provides deterministic code enforcement functionality previously
implemented in CodeEnforcerAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 8 Micro-Wave 4).

Usage:
    from agentic_core.L5_safety.utils.code_enforcer_util import (
        CodeEnforcer, EnforcementType, ViolationSeverity, CodeViolation
    )

    # Enforce code standards
    enforcer = CodeEnforcer()
    violations = enforcer.validate_file(Path("my_file.py"))
"""

from __future__ import annotations

import ast
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class EnforcementType(Enum):
    """Types of code enforcement."""

    SSOT_SYNC = "SSOT_SYNC"
    CODE_STANDARDS = "CODE_STANDARDS"
    PATTERN = "PATTERN"
    TYPE_HINTS = "TYPE_HINTS"
    SOVEREIGNTY = "SOVEREIGNTY"


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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "enforcement_type": self.enforcement_type.value,
            "severity": self.severity.name,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
            "auto_fixable": self.auto_fixable,
        }


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
    """Configuration for code enforcement."""

    enable_ssot_sync: bool = True
    enable_standards: bool = True
    enable_patterns: bool = True
    enable_type_hints: bool = True
    enable_sovereignty: bool = True
    auto_fix: bool = False
    ssot_registry_path: Path | None = None
    protected_layers: set[str] = field(default_factory=lambda: {"L5", "L6"})


class CodeEnforcer:
    """Deterministic code enforcement without agent overhead."""

    LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

    def __init__(
        self,
        project_root: Path | None = None,
        config: EnforcementConfig | None = None,
    ) -> None:
        """Initialize the code enforcer.

        Args:
            project_root: Root directory of the project
            config: Optional enforcement configuration
        """
        self.project_root = project_root or Path.cwd()
        self.config = config or EnforcementConfig()
        self._lock = threading.RLock()
        self._signed_exceptions: dict[str, SignedException] = {}
        self._violations: list[CodeViolation] = []

        # Compile patterns
        self._forbidden_patterns = {
            "mutable_default": re.compile(r"def\s+\w+\([^)]*=\s*(\[\]|\{\}|\(\))"),
            "bare_except": re.compile(r"except\s*:"),
            "eval_exec": re.compile(r"\b(eval|exec)\s*\("),
            "print_statement": re.compile(r"^\s*print\s*\("),
        }
        self._agent_suffix_pattern = re.compile(r"class\s+(\w+)(?:\(|:)")

    def validate_file(self, file_path: Path) -> list[CodeViolation]:
        """Validate a file for all enabled enforcement types.

        Args:
            file_path: Path to the file to validate

        Returns:
            List of code violations found
        """
        violations: list[CodeViolation] = []

        if not file_path.exists():
            return violations

        try:
            content = file_path.read_text(encoding="utf-8")
        except (ValueError, TypeError, OSError):
            return violations

        if self.config.enable_standards:
            violations.extend(self._check_standards(file_path, content))

        if self.config.enable_patterns:
            violations.extend(self._check_patterns(file_path, content))

        if self.config.enable_type_hints:
            violations.extend(self._check_type_hints(file_path, content))

        if self.config.enable_sovereignty:
            violations.extend(self._check_sovereignty_violations(file_path, content))

        with self._lock:
            self._violations.extend(violations)

        return violations

    def _check_standards(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check code standards compliance."""
        violations = []
        lines = content.split("\n")

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
                        ),
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
                        ),
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
                if node.returns is None and not node.name.startswith("_"):
                    violations.append(
                        CodeViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            enforcement_type=EnforcementType.TYPE_HINTS,
                            severity=ViolationSeverity.INFO,
                            message=f"Function '{node.name}' missing return type hint",
                        ),
                    )

        return violations

    def _check_sovereignty_violations(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for sovereignty violations (cross-layer access)."""
        violations = []
        file_layer = self._extract_layer(file_path)

        if not file_layer:
            return violations

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
                        ),
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
        source_level = self.LAYER_ORDER.get(source_layer, -1)
        target_level = self.LAYER_ORDER.get(target_layer, -1)

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
        """Check if a layer can modify a target file.

        Args:
            source_layer: Layer attempting modification
            target_file: File being modified
            agent_id: Optional agent ID for exception checking

        Returns:
            Tuple of (allowed, reason)
        """
        target_layer = self._extract_layer(target_file)

        if not target_layer:
            return (True, "No layer restriction")

        if target_layer not in self.config.protected_layers:
            return (True, "Target layer not protected")

        source_level = self.LAYER_ORDER.get(source_layer, -1)
        target_level = self.LAYER_ORDER.get(target_layer, -1)

        if source_level >= target_level:
            return (True, "Same or higher layer")

        if agent_id:
            exception_key = f"{source_layer}:{target_file}"
            if exception_key in self._signed_exceptions:
                exc = self._signed_exceptions[exception_key]
                if exc.expires_at is None or datetime.utcnow() < exc.expires_at:
                    return (True, f"Signed exception: {exc.reason}")

        return (False, f"Sovereignty violation: {source_layer} cannot modify {target_layer} file")

    def grant_exception(
        self,
        source_layer: str,
        target_file: Path,
        granted_by: str,
        reason: str,
        expires_at: datetime | None = None,
    ) -> SignedException:
        """Grant a signed exception for cross-layer access.

        Args:
            source_layer: Source layer
            target_file: Target file
            granted_by: Who granted the exception
            reason: Reason for exception
            expires_at: Optional expiration datetime

        Returns:
            The created SignedException
        """
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

        return exception

    def get_violations(self) -> list[CodeViolation]:
        """Get all recorded violations."""
        return self._violations.copy()

    def clear_violations(self) -> None:
        """Clear all recorded violations."""
        self._violations = []


def validate_file(file_path: str | Path, config: EnforcementConfig | None = None) -> list[CodeViolation]:
    """Standalone function to validate a file.

    Args:
        file_path: Path to the file
        config: Optional enforcement configuration

    Returns:
        List of violations
    """
    enforcer = CodeEnforcer(config=config)
    return enforcer.validate_file(Path(file_path))


def check_sovereignty(
    source_layer: str,
    target_file: str | Path,
    protected_layers: set[str] | None = None,
) -> tuple[bool, str]:
    """Standalone function to check sovereignty.

    Args:
        source_layer: Source layer
        target_file: Target file path
        protected_layers: Optional set of protected layers

    Returns:
        Tuple of (allowed, reason)
    """
    config = EnforcementConfig(
        protected_layers=protected_layers or {"L5", "L6"},
    )
    enforcer = CodeEnforcer(config=config)
    return enforcer.check_sovereignty(source_layer, Path(target_file))


def heal_repository(**kwargs: Any) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance).

    Enforcement violations require manual review.
    """
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 0,
    }


def heal(violation: dict[str, Any]) -> dict[str, Any]:
    """Heal code enforcement violations.

    Args:
        violation: Violation dict

    Returns:
        Healing result dict
    """
    violation_type = violation.get("type", "unknown")

    return {
        "status": "skipped",
        "details": f"Enforcement violations require manual review: {violation_type}",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for Code Enforcer Utility."""
    import argparse
    import logging

    parser = argparse.ArgumentParser(description="Code Enforcer Utility")
    parser.add_argument("file", help="Python file to validate")
    parser.add_argument(
        "--checks",
        nargs="+",
        choices=["standards", "patterns", "types", "sovereignty", "all"],
        default=["all"],
        help="Validation checks to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config = EnforcementConfig(
        enable_standards="all" in args.checks or "standards" in args.checks,
        enable_patterns="all" in args.checks or "patterns" in args.checks,
        enable_type_hints="all" in args.checks or "types" in args.checks,
        enable_sovereignty="all" in args.checks or "sovereignty" in args.checks,
    )

    enforcer = CodeEnforcer(config=config)
    violations = enforcer.validate_file(Path(args.file))

    print(f"Violations found: {len(violations)}")
    for v in violations:
        print(f"  [{v.severity.name}] {v.enforcement_type.value}:{v.line_number} - {v.message}")


if __name__ == "__main__":
    main()
