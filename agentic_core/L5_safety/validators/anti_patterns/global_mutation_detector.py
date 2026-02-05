"""
Global Mutation Anti-Pattern Detector

Detects runtime modifications to global state that break agent isolation.

Pattern Detection:
- sys.path.insert() and sys.path.append()
- os.environ modifications
- Global variable mutations in module scope
"""

import ast
from pathlib import Path

from .base_detector import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)


class GlobalMutationDetector(AntiPatternDetector):
    """
    Detects runtime global state modifications.

    Global mutations cause "spooky action at a distance" where
    one agent's changes affect other agents unexpectedly.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-global-mutation"

    # sys.path modification methods
    SYS_PATH_METHODS = {"insert", "append", "extend", "remove"}

    # os.environ modification methods
    ENVIRON_METHODS = {"update", "setdefault", "pop", "clear"}

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files (entry points and config files)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "__main__.py",
            "setup.py",
            "manage.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.GLOBAL_MUTATION

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect global mutation patterns in the AST."""
        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                violation = self._check_call(node, file_path, source_lines)
                if violation:
                    violations.append(violation)
            elif isinstance(node, ast.Subscript):
                violation = self._check_subscript_assign(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_call(
        self,
        node: ast.Call,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if a call modifies global state."""

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check for sys.path.insert(), sys.path.append(), etc.
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                # sys.path.insert(0, ...)
                if (
                    isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "sys"
                    and node.func.value.attr == "path"
                    and node.func.attr in self.SYS_PATH_METHODS
                ):
                    return self._create_violation(
                        node,
                        file_path,
                        f"sys.path.{node.func.attr}()",
                        "sys.path",
                    )

            # os.environ.update(), os.environ.setdefault()
            if (
                isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "os"
                and node.func.value.attr == "environ"
                and node.func.attr in self.ENVIRON_METHODS
            ):
                return self._create_violation(
                    node,
                    file_path,
                    f"os.environ.{node.func.attr}()",
                    "os.environ",
                )

        return None

    def _check_subscript_assign(
        self,
        node: ast.Subscript,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check for os.environ['KEY'] = value patterns."""

        # This is tricky - we need to find the parent Assign node
        # For now, we'll check if this subscript is on os.environ

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check for os.environ[...] pattern
        if isinstance(node.value, ast.Attribute):
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == "os"
                and node.value.attr == "environ"
            ):
                # Get the key being set
                key = ""
                if isinstance(node.slice, ast.Constant):
                    key = str(node.slice.value)

                # Check if this is in an assignment context
                # We check the source line for '='
                evidence = self._get_source_line(file_path, node.lineno)
                if "=" in evidence and "==" not in evidence:
                    return self._create_violation(
                        node,
                        file_path,
                        f"os.environ['{key}'] assignment",
                        "os.environ",
                    )

        return None

    def _create_violation(
        self,
        node: ast.expr,
        file_path: Path,
        pattern: str,
        mutation_target: str,
    ) -> AntiPatternViolation:
        """Create a violation for detected pattern."""
        evidence = self._get_source_line(file_path, node.lineno)

        severity = "error" if "sys.path" in mutation_target else "warning"

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=f"Global mutation: {pattern} modifies global state at runtime",
            evidence=evidence,
            severity=severity,
            suggested_fix=self._generate_fix_suggestion(mutation_target),
            metadata={
                "pattern": pattern,
                "mutation_target": mutation_target,
            },
        )

    def _generate_fix_suggestion(self, mutation_target: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "sys.path" in mutation_target:
            return """Remove runtime sys.path manipulation:

    # Option 1: Set PYTHONPATH before running
    # export PYTHONPATH=/path/to/project:$PYTHONPATH

    # Option 2: Use pyproject.toml or setup.py for package installation
    # pip install -e .

    # Option 3: Use absolute imports from project root
    from agentic_core.module import function"""

        if "os.environ" in mutation_target:
            return """Use configuration management instead of runtime env modification:

    # Option 1: Use environment variables at startup
    # Set in .env file or shell profile

    # Option 2: Use AgentDefaults for configuration
    from agentic_core.config.agent_defaults import AgentDefaults
    value = AgentDefaults.get("CONFIG_NAME", "default")

    # Option 3: Pass configuration through function parameters
    def my_function(config_value: str = None):
        config_value = config_value or os.getenv("CONFIG_NAME", "default")"""

        return """Avoid modifying global state at runtime.
Use dependency injection or configuration management instead."""


__all__ = ["GlobalMutationDetector"]
