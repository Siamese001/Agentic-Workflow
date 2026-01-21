#!/usr/bin/env python3
"""
UnifiedCodeValidatorAgent - Single-Pass AST Code Validation

Phase 2 Consolidation: Merges functionality from:
- SyntaxValidatorAgent (syntax errors)
- CanonAstValidatorAgent (canon compliance)
- CanonValidatorAgent (canon rules)
- AsyncBlockingValidatorAgent (async/blocking patterns)
- PrintStatementValidatorAgent (forbidden print statements)

Features:
- Single-pass ast.NodeVisitor for efficiency
- Configurable RuleSet to toggle specific checks
- Aggregated ValidationReport with heterogeneous violations
- Backward compatible factory methods
"""
from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of code violations."""
    SYNTAX = auto()
    CANON = auto()
    ASYNC_BLOCKING = auto()
    PRINT_STATEMENT = auto()
    IMPORT = auto()
    NAMING = auto()
    TYPE_HINT = auto()
    DOCSTRING = auto()


@dataclass
class Violation:
    """Represents a single code violation."""
    violation_type: ViolationType
    message: str
    file_path: Path | None = None
    line_number: int = 0
    column: int = 0
    severity: str = "error"  # error, warning, info
    rule_id: str | None = None
    suggestion: str | None = None

    def __str__(self) -> str:
        loc = f"{self.file_path}:{self.line_number}:{self.column}" if self.file_path else f"line {self.line_number}"
        return f"[{self.violation_type.name}] {loc}: {self.message}"


@dataclass
class ValidationReport:
    """Aggregated report of all violations found."""
    file_path: Path | None = None
    violations: list[Violation] = field(default_factory=list)
    execution_time: float = 0.0
    checks_performed: set[str] = field(default_factory=set)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        return any(v.severity == "warning" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warning")

    def by_type(self, violation_type: ViolationType) -> list[Violation]:
        return [v for v in self.violations if v.violation_type == violation_type]

    def merge(self, other: ValidationReport) -> ValidationReport:
        """Merge another report into this one."""
        self.violations.extend(other.violations)
        self.checks_performed.update(other.checks_performed)
        self.execution_time += other.execution_time
        return self


@dataclass
class RuleSet:
    """Configuration for which validation rules to apply."""
    check_syntax: bool = True
    check_canon: bool = True
    check_async: bool = True
    check_print: bool = True
    check_imports: bool = True
    check_naming: bool = True
    check_type_hints: bool = False
    check_docstrings: bool = False

    # Canon-specific rules
    require_dataclass: bool = True
    require_healer_mixin: bool = True
    require_mcp_mixin: bool = False
    require_subatomic_mixin: bool = True

    # Async-specific rules
    forbid_sync_in_async: bool = True
    forbid_blocking_calls: bool = True

    # Print-specific rules
    allow_debug_prints: bool = False
    allow_logger_prints: bool = True

    # Naming rules
    agent_suffix_required: bool = True
    class_naming_pattern: str = r"^[A-Z][a-zA-Z0-9]*Agent$"

    @classmethod
    def strict(cls) -> RuleSet:
        """Create a strict rule set with all checks enabled."""
        return cls(
            check_type_hints=True,
            check_docstrings=True,
            require_mcp_mixin=True,
        )

    @classmethod
    def minimal(cls) -> RuleSet:
        """Create a minimal rule set for quick validation."""
        return cls(
            check_syntax=True,
            check_canon=False,
            check_async=False,
            check_print=False,
            check_imports=False,
            check_naming=False,
        )


class UnifiedASTVisitor(ast.NodeVisitor):
    """
    Single-pass AST visitor that performs all validation checks simultaneously.

    This is more efficient than running multiple separate visitors.
    """

    def __init__(
        self,
        rules: RuleSet,
        file_path: Path | None = None,
        source_code: str | None = None,
    ):
        self.rules = rules
        self.file_path = file_path
        self.source_code = source_code
        self.violations: list[Violation] = []

        # State tracking
        self._in_async_function = False
        self._current_class: str | None = None
        self._class_bases: dict[str, list[str]] = {}
        self._class_decorators: dict[str, list[str]] = {}
        self._imports: set[str] = set()
        self._from_imports: dict[str, set[str]] = {}

    def _add_violation(
        self,
        violation_type: ViolationType,
        message: str,
        node: ast.AST | None = None,
        severity: str = "error",
        rule_id: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Add a violation to the list."""
        line = getattr(node, "lineno", 0) if node else 0
        col = getattr(node, "col_offset", 0) if node else 0

        self.violations.append(Violation(
            violation_type=violation_type,
            message=message,
            file_path=self.file_path,
            line_number=line,
            column=col,
            severity=severity,
            rule_id=rule_id,
            suggestion=suggestion,
        ))

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports."""
        for alias in node.names:
            self._imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        module = node.module or ""
        if module not in self._from_imports:
            self._from_imports[module] = set()
        for alias in node.names:
            self._from_imports[module].add(alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Validate class definitions."""
        self._current_class = node.name

        # Track bases
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
        self._class_bases[node.name] = bases

        # Track decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
        self._class_decorators[node.name] = decorators

        # Canon checks
        if self.rules.check_canon and node.name.endswith("Agent"):
            self._check_canon_compliance(node, bases, decorators)

        # Naming checks
        if self.rules.check_naming and node.name.endswith("Agent"):
            self._check_naming_compliance(node)

        # Visit children
        self.generic_visit(node)
        self._current_class = None

    def _check_canon_compliance(
        self,
        node: ast.ClassDef,
        bases: list[str],
        decorators: list[str],
    ) -> None:
        """Check canon compliance for agent classes."""
        # Check for @dataclass decorator
        if self.rules.require_dataclass and "dataclass" not in decorators:
            self._add_violation(
                ViolationType.CANON,
                f"Agent class '{node.name}' missing @dataclass decorator",
                node,
                severity="warning",
                rule_id="CANON-001",
                suggestion="Add @dataclass decorator to agent class",
            )

        # Check for HealerMixin
        if self.rules.require_healer_mixin and "HealerMixin" not in bases:
            self._add_violation(
                ViolationType.CANON,
                f"Agent class '{node.name}' missing HealerMixin inheritance",
                node,
                severity="warning",
                rule_id="CANON-002",
                suggestion="Add HealerMixin to class inheritance",
            )

        # Check for SubatomicTestingMixin
        if self.rules.require_subatomic_mixin and "SubatomicTestingMixin" not in bases:
            self._add_violation(
                ViolationType.CANON,
                f"Agent class '{node.name}' missing SubatomicTestingMixin inheritance",
                node,
                severity="warning",
                rule_id="CANON-003",
                suggestion="Add SubatomicTestingMixin to class inheritance",
            )

        # Check for MCPHardenedMixin
        if self.rules.require_mcp_mixin and "MCPHardenedMixin" not in bases:
            self._add_violation(
                ViolationType.CANON,
                f"Agent class '{node.name}' missing MCPHardenedMixin inheritance",
                node,
                severity="warning",
                rule_id="CANON-004",
                suggestion="Add MCPHardenedMixin to class inheritance",
            )

    def _check_naming_compliance(self, node: ast.ClassDef) -> None:
        """Check naming compliance for agent classes."""
        if self.rules.agent_suffix_required and not node.name.endswith("Agent"):
            self._add_violation(
                ViolationType.NAMING,
                f"Agent class '{node.name}' should end with 'Agent' suffix",
                node,
                severity="warning",
                rule_id="NAME-001",
            )

        if self.rules.class_naming_pattern:
            pattern = re.compile(self.rules.class_naming_pattern)
            if not pattern.match(node.name):
                self._add_violation(
                    ViolationType.NAMING,
                    f"Class name '{node.name}' does not match pattern '{self.rules.class_naming_pattern}'",
                    node,
                    severity="warning",
                    rule_id="NAME-002",
                )

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function context."""
        self._in_async_function = True
        self.generic_visit(node)
        self._in_async_function = False

    def visit_Call(self, node: ast.Call) -> None:
        """Check for forbidden calls."""
        # Check for print statements
        if self.rules.check_print:
            self._check_print_call(node)

        # Check for blocking calls in async context
        if self.rules.check_async and self._in_async_function:
            self._check_blocking_call(node)

        self.generic_visit(node)

    def _check_print_call(self, node: ast.Call) -> None:
        """Check for forbidden print statements."""
        func = node.func

        is_print = False
        if isinstance(func, ast.Name) and func.id == "print":
            is_print = True
        elif isinstance(func, ast.Attribute) and func.attr == "print":
            is_print = True

        if is_print:
            # Check if it's a debug print (allowed if configured)
            if self.rules.allow_debug_prints:
                # Check for DEBUG or debug in arguments
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "DEBUG" in arg.value.upper() or "debug" in arg.value.lower():
                            return

            self._add_violation(
                ViolationType.PRINT_STATEMENT,
                "Forbidden print() statement found. Use logging instead.",
                node,
                severity="warning",
                rule_id="PRINT-001",
                suggestion="Replace print() with Logger.info() or Logger.debug()",
            )

    def _check_blocking_call(self, node: ast.Call) -> None:
        """Check for blocking calls in async context."""
        blocking_calls = {
            "time.sleep",
            "requests.get",
            "requests.post",
            "requests.put",
            "requests.delete",
            "open",
            "input",
        }

        func = node.func
        call_name = ""

        if isinstance(func, ast.Name):
            call_name = func.id
        elif isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name):
                call_name = f"{func.value.id}.{func.attr}"
            else:
                call_name = func.attr

        if call_name in blocking_calls or call_name.split(".")[-1] in ["sleep", "get", "post"]:
            self._add_violation(
                ViolationType.ASYNC_BLOCKING,
                f"Blocking call '{call_name}' in async function. Use async alternative.",
                node,
                severity="error",
                rule_id="ASYNC-001",
                suggestion=f"Use async version of {call_name}",
            )

    def visit_Expr(self, node: ast.Expr) -> None:
        """Check expression statements."""
        self.generic_visit(node)


@dataclass
class UnifiedCodeValidatorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Unified code validation with single-pass AST analysis.

    Consolidates:
    - SyntaxValidatorAgent (syntax)
    - CanonAstValidatorAgent (canon AST rules)
    - CanonValidatorAgent (canon compliance)
    - AsyncBlockingValidatorAgent (async patterns)
    - PrintStatementValidatorAgent (print detection)

    Usage:
        agent = UnifiedCodeValidatorAgent()
        report = agent.validate_file(Path("my_agent.py"))

        # Or with custom rules
        rules = RuleSet(check_async=False)
        report = agent.validate_file(path, rules=rules)
    """

    default_rules: RuleSet = field(default_factory=RuleSet)

    def __post_init__(self) -> None:
        """Initialize the validator."""
        Logger.info("UnifiedCodeValidatorAgent initialized")

    def validate_source(
        self,
        source_code: str,
        file_path: Path | None = None,
        rules: RuleSet | None = None,
    ) -> ValidationReport:
        """
        Validate source code string.

        Args:
            source_code: Python source code to validate
            file_path: Optional path for error reporting
            rules: Optional custom rule set

        Returns:
            ValidationReport with all violations found
        """
        rules = rules or self.default_rules
        report = ValidationReport(file_path=file_path)
        start_time = datetime.now()

        # Track which checks were performed
        if rules.check_syntax:
            report.checks_performed.add("syntax")
        if rules.check_canon:
            report.checks_performed.add("canon")
        if rules.check_async:
            report.checks_performed.add("async")
        if rules.check_print:
            report.checks_performed.add("print")
        if rules.check_naming:
            report.checks_performed.add("naming")

        # Step 1: Syntax check (parse the AST)
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            report.violations.append(Violation(
                violation_type=ViolationType.SYNTAX,
                message=f"Syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno or 0,
                column=e.offset or 0,
                severity="error",
                rule_id="SYNTAX-001",
            ))
            report.execution_time = (datetime.now() - start_time).total_seconds()
            return report

        # Step 2: Single-pass AST validation
        visitor = UnifiedASTVisitor(rules, file_path, source_code)
        visitor.visit(tree)
        report.violations.extend(visitor.violations)

        report.execution_time = (datetime.now() - start_time).total_seconds()
        return report

    def validate_file(
        self,
        file_path: Path,
        rules: RuleSet | None = None,
    ) -> ValidationReport:
        """
        Validate a Python file.

        Args:
            file_path: Path to Python file
            rules: Optional custom rule set

        Returns:
            ValidationReport with all violations found
        """
        try:
            source_code = file_path.read_text(encoding="utf-8")
        except Exception as e:
            report = ValidationReport(file_path=file_path)
            report.violations.append(Violation(
                violation_type=ViolationType.SYNTAX,
                message=f"Could not read file: {e}",
                file_path=file_path,
                severity="error",
            ))
            return report

        return self.validate_source(source_code, file_path, rules)

    def validate_files(
        self,
        file_paths: list[Path],
        rules: RuleSet | None = None,
    ) -> dict[Path, ValidationReport]:
        """
        Validate multiple files.

        Args:
            file_paths: List of paths to validate
            rules: Optional custom rule set

        Returns:
            Dictionary mapping file paths to their reports
        """
        results = {}
        for path in file_paths:
            results[path] = self.validate_file(path, rules)
        return results

    def validate_directory(
        self,
        directory: Path,
        rules: RuleSet | None = None,
        pattern: str = "**/*.py",
        exclude_patterns: list[str] | None = None,
    ) -> dict[Path, ValidationReport]:
        """
        Validate all Python files in a directory.

        Args:
            directory: Directory to scan
            rules: Optional custom rule set
            pattern: Glob pattern for files
            exclude_patterns: Patterns to exclude

        Returns:
            Dictionary mapping file paths to their reports
        """
        exclude_patterns = exclude_patterns or ["**/test_*", "**/__pycache__/*"]

        files = []
        for path in directory.glob(pattern):
            # Check exclusions
            excluded = False
            for exclude in exclude_patterns:
                if path.match(exclude):
                    excluded = True
                    break
            if not excluded:
                files.append(path)

        return self.validate_files(files, rules)

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L5 validation agent - operational healing."""
        if _call_path is None:
            _call_path = set()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}

        _call_path.add(agent_name)
        try:
            Logger.info(f"[{agent_name}] L5 code validation healing")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


# =============================================================================
# BACKWARD COMPATIBILITY FACTORY METHODS (Migration Complete)
# =============================================================================

def create_legacy_syntax_validator(**kwargs: Any) -> UnifiedCodeValidatorAgent:
    """Factory for backward compatibility with SyntaxValidatorAgent."""
    rules = RuleSet(
        check_syntax=True,
        check_canon=False,
        check_async=False,
        check_print=False,
    )
    return UnifiedCodeValidatorAgent(default_rules=rules, **kwargs)


def create_legacy_canon_validator(**kwargs: Any) -> UnifiedCodeValidatorAgent:
    """Factory for backward compatibility with CanonValidatorAgent."""
    rules = RuleSet(
        check_syntax=True,
        check_canon=True,
        check_async=False,
        check_print=False,
    )
    return UnifiedCodeValidatorAgent(default_rules=rules, **kwargs)


def create_legacy_async_validator(**kwargs: Any) -> UnifiedCodeValidatorAgent:
    """Factory for backward compatibility with AsyncBlockingValidatorAgent."""
    rules = RuleSet(
        check_syntax=True,
        check_canon=False,
        check_async=True,
        check_print=False,
    )
    return UnifiedCodeValidatorAgent(default_rules=rules, **kwargs)


def create_legacy_print_validator(**kwargs: Any) -> UnifiedCodeValidatorAgent:
    """Factory for backward compatibility with PrintStatementValidatorAgent."""
    rules = RuleSet(
        check_syntax=True,
        check_canon=False,
        check_async=False,
        check_print=True,
    )
    return UnifiedCodeValidatorAgent(default_rules=rules, **kwargs)
