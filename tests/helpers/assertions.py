"""
Custom assertions for blueprint and FCA testing.

Provides assertion helpers for validating classification results,
violations, and remediation recommendations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)


class ViolationAssertion:
    """Assertion helper for violation checking."""

    def __init__(self, violations: Sequence[Mapping[str, Any]]):
        self.violations = list(violations)

    def has_violation(self, code: str) -> bool:
        """Check if a violation with the given code exists."""
        return any(v.get("code") == code for v in self.violations)

    def has_violation_for_path(self, path: str | Path) -> bool:
        """Check if a violation exists for the given path."""
        path_str = str(path)
        return any(path_str in str(v.get("path", "")) for v in self.violations)

    def assert_violation_code(self, code: str, msg: str = "") -> None:
        """Assert that a violation with the given code exists."""
        assert self.has_violation(code), (
            f"Expected violation code '{code}' not found. {msg}\nViolations: {self.violations}"
        )

    def assert_no_violation_code(self, code: str, msg: str = "") -> None:
        """Assert that no violation with the given code exists."""
        assert not self.has_violation(code), (
            f"Unexpected violation code '{code}' found. {msg}\nViolations: {self.violations}"
        )

    def assert_violation_count(self, expected: int, msg: str = "") -> None:
        """Assert the number of violations."""
        actual = len(self.violations)
        assert actual == expected, (
            f"Expected {expected} violations, got {actual}. {msg}\nViolations: {self.violations}"
        )

    def assert_no_violations(self, msg: str = "") -> None:
        """Assert that no violations exist."""
        self.assert_violation_count(0, msg)


class ClassificationAssertion:
    """Assertion helper for FCA classification results."""

    def __init__(self, result: Mapping[str, Any]):
        self.result = dict(result)

    @property
    def file_type(self) -> str:
        """Get the classified file type."""
        return self.result.get("type", "UNKNOWN")

    @property
    def target_layer(self) -> str | None:
        """Get the suggested target layer."""
        return self.result.get("target_layer")

    @property
    def target_subfolder(self) -> str | None:
        """Get the suggested target subfolder."""
        return self.result.get("target_subfolder")

    @property
    def violations(self) -> ViolationAssertion:
        """Get violations as assertion helper."""
        return ViolationAssertion(self.result.get("violations", []))

    def assert_type(self, expected: str, msg: str = "") -> None:
        """Assert the classified file type."""
        assert self.file_type == expected, f"Expected type '{expected}', got '{self.file_type}'. {msg}"

    def assert_target_layer(self, expected: str, msg: str = "") -> None:
        """Assert the target layer."""
        assert self.target_layer == expected, f"Expected layer '{expected}', got '{self.target_layer}'. {msg}"

    def assert_target_subfolder(self, expected: str, msg: str = "") -> None:
        """Assert the target subfolder."""
        assert self.target_subfolder == expected, (
            f"Expected subfolder '{expected}', got '{self.target_subfolder}'. {msg}"
        )

    def assert_is_agent(self, msg: str = "") -> None:
        """Assert that the file is classified as AGENT."""
        self.assert_type("AGENT", msg)

    def assert_is_validator(self, msg: str = "") -> None:
        """Assert that the file is classified as VALIDATOR."""
        self.assert_type("VALIDATOR", msg)

    def assert_is_script(self, msg: str = "") -> None:
        """Assert that the file is classified as SCRIPT."""
        self.assert_type("SCRIPT", msg)

    def assert_needs_move(self, to_subfolder: str, msg: str = "") -> None:
        """Assert that the file needs to be moved to a specific subfolder."""
        self.assert_target_subfolder(to_subfolder, msg)


def assert_path_exists(path: Path, msg: str = "") -> None:
    """Assert that a path exists."""
    assert path.exists(), f"Path does not exist: {path}. {msg}"


def assert_path_not_exists(path: Path, msg: str = "") -> None:
    """Assert that a path does not exist."""
    assert not path.exists(), f"Path should not exist: {path}. {msg}"


def assert_file_contains(path: Path, substring: str, msg: str = "") -> None:
    """Assert that a file contains a substring."""
    content = path.read_text(encoding="utf-8")
    assert substring in content, f"File {path} does not contain '{substring}'. {msg}"


def assert_file_not_contains(path: Path, substring: str, msg: str = "") -> None:
    """Assert that a file does not contain a substring."""
    content = path.read_text(encoding="utf-8")
    assert substring not in content, f"File {path} should not contain '{substring}'. {msg}"


def assert_import_resolves(module_path: str) -> None:
    """Assert that a module can be imported."""
    import importlib

    try:
        importlib.import_module(module_path)
    except ImportError as e:
        raise AssertionError(f"Module '{module_path}' cannot be imported: {e}") from e


def assert_no_agents_outside_reasoning(root: Path) -> list[str]:
    """
    Scan a directory tree and return paths of Agent classes outside reasoning/.

    Returns empty list if all agents are in reasoning/.
    """
    import ast

    violations = []

    for py_file in root.rglob("*.py"):
        # Skip reasoning/ folders
        if "/reasoning/" in str(py_file) or "\\reasoning\\" in str(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.endswith("Agent") and not node.name.startswith("I"):
                        # Check if it's a Protocol
                        is_protocol = any(
                            (isinstance(base, ast.Name) and base.id == "Protocol")
                            or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                            for base in node.bases
                        )
                        if not is_protocol:
                            violations.append(str(py_file))
                            break
        except SyntaxError:  # review: Syntax errors should be caught at parser level, not runtime
            continue

    return violations


def assert_no_nested_lcd(root: Path, leaf_domains: set[str]) -> list[str]:
    """
    Scan for nested LCD subtrees under leaf domains.

    Returns list of violation paths.
    """
    lcd_subfolders = {"reasoning", "enforcement", "config", "types", "validators", "utils"}
    violations = []

    for domain in leaf_domains:
        domain_path = root / AGENTIC_CORE_DIR / domain
        if not domain_path.exists():
            continue

        for subfolder in lcd_subfolders:
            nested_path = domain_path / subfolder
            if nested_path.exists() and nested_path.is_dir():
                violations.append(str(nested_path))

    return violations
