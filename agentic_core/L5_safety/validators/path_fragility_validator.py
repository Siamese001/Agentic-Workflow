"""
Path Fragility Anti-Pattern Detector

Detects string-based path manipulation instead of pathlib.Path usage.

Pattern Detection:
- os.path.join() calls
- os.getcwd() usage
- String concatenation for paths (+ "/" +)
- os.path.exists(), os.path.isfile(), etc.
"""

import ast
from pathlib import Path

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)


class PathFragilityDetector(AntiPatternDetector):
    """
    Detects string-based path manipulation.

    String paths cause cross-platform incompatibility between
    Windows and Unix systems.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-path-string"

    # os.path functions to detect
    OS_PATH_FUNCTIONS = {
        "join",
        "exists",
        "isfile",
        "isdir",
        "basename",
        "dirname",
        "abspath",
        "realpath",
        "normpath",
        "expanduser",
        "splitext",
    }

    # os functions to detect
    OS_FUNCTIONS = {
        "getcwd",
        "chdir",
    }

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "setup.py",
            "setup.cfg",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.PATH_FRAGILITY

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect path fragility patterns in the AST."""
        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        # guardian: allow-silent-swallow
        except Exception:
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                violation = self._check_call(node, file_path, source_lines)
                if violation:
                    violations.append(violation)
            elif isinstance(node, ast.BinOp):
                violation = self._check_string_concat(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_call(
        self,
        node: ast.Call,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if a call uses os.path functions."""

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check for os.path.* calls
        if isinstance(node.func, ast.Attribute):
            # Check os.path.join, os.path.exists, etc.
            if isinstance(node.func.value, ast.Attribute):
                if (
                    isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.value.attr == "path"
                    and node.func.attr in self.OS_PATH_FUNCTIONS
                ):
                    return self._create_violation(node, file_path, f"os.path.{node.func.attr}()")

            # Check os.getcwd(), os.chdir()
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr in self.OS_FUNCTIONS
            ):
                return self._create_violation(node, file_path, f"os.{node.func.attr}()")

        return None

    def _check_string_concat(
        self,
        node: ast.BinOp,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check for string concatenation patterns that look like path building."""

        # Check for whitelist comment
        if hasattr(node, "lineno") and node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check for string addition with path separators
        if not isinstance(node.op, ast.Add):
            return None

        # Look for patterns like: path + "/" + filename
        def contains_path_separator(n: ast.expr) -> bool:
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                return "/" in n.value or "\\" in n.value
            if isinstance(n, ast.BinOp):
                return contains_path_separator(n.left) or contains_path_separator(n.right)
            return False

        if contains_path_separator(node):
            return self._create_violation(node, file_path, "String concatenation for path building")

        return None

    def _create_violation(
        self,
        node: ast.expr,
        file_path: Path,
        pattern: str,
    ) -> AntiPatternViolation:
        """Create a violation for detected pattern."""
        evidence = self._get_source_line(file_path, node.lineno)

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=f"Path fragility: {pattern} - use pathlib.Path instead",
            evidence=evidence,
            severity="warning",
            suggested_fix=self._generate_fix_suggestion(pattern),
            metadata={
                "pattern": pattern,
            },
        )

    def _generate_fix_suggestion(self, pattern: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "os.path.join" in pattern:
            return """Replace os.path.join with pathlib.Path:
    # Before
    path = os.path.join(base, "subdir", "file.txt")

    # After
    from pathlib import Path
    path = Path(base) / "subdir" / "file.txt" """

        if "os.getcwd" in pattern:
            return """Replace os.getcwd with Path.cwd():
    # Before
    cwd = os.getcwd()

    # After
    from pathlib import Path
    cwd = Path.cwd()"""

        if "os.path.exists" in pattern:
            return """Replace os.path.exists with Path.exists():
    # Before
    if os.path.exists(path):

    # After
    from pathlib import Path
    if Path(path).exists():"""

        return """Use pathlib.Path for all path operations:
    from pathlib import Path

    # Path construction
    path = Path(base) / "subdir" / "file.txt"

    # Path operations
    path.exists()
    path.is_file()
    path.is_dir()
    path.parent
    path.name"""


__all__ = ["PathFragilityDetector"]
