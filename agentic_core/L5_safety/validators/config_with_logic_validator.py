"""
Config-With-Logic Anti-Pattern Detector

Detects business logic embedded inside config-typed objects or files.
Config should be pure data; callable logic in config creates hidden
runtime behaviour and makes enforcement blurry.

Pattern Detection:
- lambda expressions in module-level assignments
- if/match branches inside functions whose name ends with _config/_spec/_policy
- callable values (lambda/function refs) in dict literals assigned to *_config,
  *_spec, or *_policy variables
"""

from __future__ import annotations

import ast
from pathlib import Path

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

_CONFIG_SUFFIXES = ("_config", "_spec", "_policy", "_settings", "_options")
_WHITELIST_COMMENT = "# guardian: allow-config-with-logic"


class ConfigWithLogicDetector(AntiPatternDetector):
    """
    Detects logic (lambdas, conditionals) embedded in config-typed objects.

    Config-with-logic makes governance enforcement blurry because business
    rules buried in data structures are invisible to policy scanners and
    cannot be independently tested or versioned.
    """

    WHITELIST_COMMENT = _WHITELIST_COMMENT

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.CONFIG_WITH_LOGIC

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect config-with-logic patterns in the AST."""
        violations: list[AntiPatternViolation] = []

        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            source_lines = []

        for node in ast.walk(tree):
            # 1. Module-level assignment: x_config = {...lambda...}
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if self._is_config_name(target):
                        v = self._check_value_for_logic(node.value, file_path, source_lines, node.lineno)
                        violations.extend(v)

            # 2. Annotated assignment: x_config: T = {...lambda...}
            elif isinstance(node, ast.AnnAssign):
                if node.value and self._is_config_name(node.target):
                    v = self._check_value_for_logic(node.value, file_path, source_lines, node.lineno)
                    violations.extend(v)

            # 3. Function named *_config/*_spec/*_policy contains if/match
            elif isinstance(node, ast.FunctionDef):
                if any(node.name.endswith(s) for s in _CONFIG_SUFFIXES):
                    for child in ast.walk(node):
                        if isinstance(child, ast.If):
                            if not self._is_whitelisted_line(source_lines, child.lineno):
                                evidence = self._get_source_line(file_path, child.lineno)
                                violations.append(
                                    AntiPatternViolation(
                                        file_path=file_path,
                                        line_number=child.lineno,
                                        category=self.category,
                                        message=(
                                            f"Config-with-logic: 'if' branch inside "
                                            f"config-factory function '{node.name}'"
                                        ),
                                        evidence=evidence,
                                        severity="warning",
                                        suggested_fix=(
                                            "Extract conditional logic to a separate "
                                            "factory or builder; keep config functions "
                                            "as pure data constructors."
                                        ),
                                    )
                                )

        return violations

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _is_config_name(self, node: ast.expr) -> bool:
        """Return True if the AST name node looks like a config variable."""
        if isinstance(node, ast.Name):
            return any(node.id.endswith(s) for s in _CONFIG_SUFFIXES)
        if isinstance(node, ast.Attribute):
            return any(node.attr.endswith(s) for s in _CONFIG_SUFFIXES)
        return False

    def _check_value_for_logic(
        self,
        value: ast.expr,
        file_path: Path,
        source_lines: list[str],
        lineno: int,
    ) -> list[AntiPatternViolation]:
        """Walk a value node and flag any lambda expressions found."""
        violations: list[AntiPatternViolation] = []
        for child in ast.walk(value):
            if isinstance(child, ast.Lambda):
                line = getattr(child, "lineno", lineno)
                if self._is_whitelisted_line(source_lines, line):
                    continue
                evidence = self._get_source_line(file_path, line)
                violations.append(
                    AntiPatternViolation(
                        file_path=file_path,
                        line_number=line,
                        category=self.category,
                        message=("Config-with-logic: lambda expression embedded in config-typed variable"),
                        evidence=evidence,
                        severity="error",
                        suggested_fix=(
                            "Replace the lambda with a named function defined "
                            "outside the config dict, or move the logic to the "
                            "caller that reads the config."
                        ),
                    )
                )
        return violations

    def _is_whitelisted_line(self, source_lines: list[str], lineno: int) -> bool:
        """Return True if the line or its predecessor contains the whitelist comment."""
        for check_line in (lineno - 1, lineno - 2):
            if 0 <= check_line < len(source_lines):
                if _WHITELIST_COMMENT in source_lines[check_line]:
                    return True
        return False


__all__ = ["ConfigWithLogicDetector"]
