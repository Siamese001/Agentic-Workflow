"""
File: agentic_core/L5_safety/policy_engine/ComplexityAnalyzerAgent.py
Rationale:
    L5 Sovereign Guardian for Cognitive Complexity.
    - Enforces McCabe Cyclomatic Complexity limits.
    - Detects "God Functions" (too many lines/branches).
    - Hardened with Atomic Reporting and SovereignBase integration.
"""

import ast
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.validators.decorators import standard_heal

Logger = logging.getLogger(__name__)


@dataclass
class ComplexityViolation:
    file_path: Path
    function_name: str
    line_number: int
    complexity: int
    max_allowed: int
    type: str  # 'CYCLOMATIC', 'LENGTH', 'ARGUMENTS'
    severity: str


@dataclass
class ComplexityConfig:
    max_cyclomatic_complexity: int = 10  # Standard strict limit
    max_function_length: int = 50  # Lines of code
    max_arguments: int = 6  # Function arguments
    ignore_tests: bool = True
    project_root: Path | None = None


class ComplexityAnalyzerAgent(SovereignBaseAgent):
    """
    [L5 VALIDATOR] static analysis for code complexity.
    Prevents cognitive overload and unverifiable logic.
    """

    def __init__(self, config: ComplexityConfig | None = None):
        self._complexity_config = config or ComplexityConfig()
        self.project_root = self._complexity_config.project_root or Path.cwd()
        self._lock = threading.RLock()
        self._violations: list[ComplexityViolation] = []

    def analyze_repository(self, target_path: Path = None) -> dict[str, Any]:
        """Entry point for full scan."""
        target = target_path or self.project_root
        self._violations = []

        files = list(target.rglob("*.py"))
        for file_path in files:
            if self._complexity_config.ignore_tests and (
                "test" in file_path.name or "tests" in file_path.parts
            ):
                continue
            self.analyze_file(file_path)

        return {
            "total_files": len(files),
            "violations": [v.__dict__ for v in self._violations],
            "status": "FAIL" if self._violations else "PASS",
        }

    def analyze_file(self, file_path: Path) -> list[ComplexityViolation]:
        """Analyze a single file for complexity metrics."""
        if not file_path.exists():
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            Logger.error(f"Failed to parse {file_path}: {e}")
            return []

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 1. Cyclomatic Complexity
                complexity = self._calculate_complexity(node)
                if complexity > self._complexity_config.max_cyclomatic_complexity:
                    v = ComplexityViolation(
                        file_path=file_path,
                        function_name=node.name,
                        line_number=node.lineno,
                        complexity=complexity,
                        max_allowed=self._complexity_config.max_cyclomatic_complexity,
                        type="CYCLOMATIC",
                        severity="CRITICAL" if complexity > 20 else "WARNING",
                    )
                    violations.append(v)

                # 2. Function Length
                length = node.end_lineno - node.lineno
                if length > self._complexity_config.max_function_length:
                    violations.append(
                        ComplexityViolation(
                            file_path=file_path,
                            function_name=node.name,
                            line_number=node.lineno,
                            complexity=length,
                            max_allowed=self._complexity_config.max_function_length,
                            type="LENGTH",
                            severity="WARNING",
                        )
                    )

                # 3. Argument Count
                arg_count = len(node.args.args)
                if arg_count > self._complexity_config.max_arguments:
                    violations.append(
                        ComplexityViolation(
                            file_path=file_path,
                            function_name=node.name,
                            line_number=node.lineno,
                            complexity=arg_count,
                            max_allowed=self._complexity_config.max_arguments,
                            type="ARGUMENTS",
                            severity="INFO",
                        )
                    )

        with self._lock:
            self._violations.extend(violations)
        return violations

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Computes McCabe Cyclomatic Complexity."""
        complexity = 1
        for child in ast.walk(node):
            # Branching nodes
            if isinstance(
                child,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.AsyncFor,
                    ast.ExceptHandler,
                    ast.With,
                    ast.AsyncWith,
                    ast.Assert,
                ),
            ):
                complexity += 1
            # Boolean operators (and/or counts as branches)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    @standard_heal
    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """
        Sovereign Interface.
        Note: Complexity cannot be auto-healed safely, only reported.
        """
        report = self.analyze_repository(self.project_root)
        Logger.info(f"[Complexity] Found {len(report['violations'])} violations.")
        return {
            "violations_found": len(report["violations"]),
            "violations_fixed": 0,  # Cannot auto-fix complexity
            "report": report,
        }

    def heal(self, violation: dict) -> dict:
        """Heal complexity violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cyclomatic, length, arguments)
                - path: Path to the violating file
                - function_name: Name of the complex function

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        Logger.info("[COMPLEXITY_ANALYZER] Complexity violations require manual refactoring")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Complexity violations require manual refactoring",
        }
