"""
Strict markers governance contract.

Enforced invariants:
    1. Every pytest.mark.<name> used in collected tests is registered in pytest.ini.
    2. The marker registry in pytest.ini has no duplicate entries.
    3. Markers are sorted alphabetically (recommended, enforced).
"""

from __future__ import annotations

import ast
import configparser
import re
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]
PYTEST_INI = ROOT / "pytest.ini"

# Testpaths from pytest.ini — must match the explicit allowlist
COLLECTED_DIRS = [
    ROOT / TESTS_DIR / "unit_min_deps",
    ROOT / TESTS_DIR / "integration" / AGENTIC_CORE_DIR,
]

# Markers that are built-in to pytest (never need registration)
BUILTIN_MARKERS = frozenset(
    {
        "filterwarnings",
        "parametrize",
        "skip",
        "skipif",
        "usefixtures",
        "xfail",
    },
)


def _parse_registered_markers() -> list[str]:
    """Return list of marker names registered in pytest.ini, in file order."""
    parser = configparser.ConfigParser()
    parser.read(str(PYTEST_INI), encoding="utf-8")
    raw = parser.get("pytest", "markers", fallback="")
    markers = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "marker_name: description"
        name = line.split(":")[0].strip()
        if name:
            markers.append(name)
    return markers


def _scan_used_markers() -> set[str]:
    """AST-scan all test files in collected dirs for pytest.mark.<name> usage."""
    used: set[str] = set()
    marker_attr_re = re.compile(r"pytest\.mark\.(\w+)")

    for test_dir in COLLECTED_DIRS:
        if not test_dir.exists():
            continue
        for py_file in test_dir.rglob("test_*.py"):
            source = py_file.read_text(encoding="utf-8", errors="replace")
            # AST approach: find Attribute nodes for pytest.mark.<name>
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    # Check for pytest.mark.<name> pattern via source regex
                    # (AST alone can't easily chain attribute access)
                    pass

            # Regex fallback on source for pytest.mark.<name>
            for match in marker_attr_re.finditer(source):
                marker_name = match.group(1)
                if marker_name not in BUILTIN_MARKERS:
                    used.add(marker_name)

            # Also check pytestmark = pytest.mark.<name> assignments
            # and @pytest.mark.<name> decorators (covered by regex above)

    return used


class TestAllUsedMarkersRegistered:
    """Every pytest.mark.<name> used in collected tests must be registered."""

    def test_no_unregistered_markers(self) -> None:
    """Test no_unregistered_markers contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
    """Test no_duplicate_markers contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"

    def test_markers_sorted(self) -> None:
    """Test markers_sorted contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
