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
        registered = set(_parse_registered_markers())
        used = _scan_used_markers()
        unregistered = used - registered - BUILTIN_MARKERS
        assert not unregistered, (
            f"Found {len(unregistered)} marker(s) used in tests but NOT registered in pytest.ini:\n"
            + "\n".join(f"  {m}" for m in sorted(unregistered))
            + "\nAdd these to the markers section in pytest.ini or remove usage."
        )


class TestNoDuplicateMarkers:
    """Marker registry must not contain duplicate entries."""

    def test_no_duplicate_markers(self) -> None:
        markers = _parse_registered_markers()
        seen: dict[str, int] = {}
        duplicates: list[str] = []
        for m in markers:
            if m in seen:
                duplicates.append(m)
            seen[m] = seen.get(m, 0) + 1
        assert not duplicates, "Duplicate marker registrations found:\n" + "\n".join(
            f"  {d} (appears {seen[d]} times)" for d in duplicates
        )


class TestMarkersSorted:
    """Marker registry should be sorted alphabetically for maintainability."""

    def test_markers_sorted(self) -> None:
        markers = _parse_registered_markers()
        sorted_markers = sorted(markers, key=str.lower)
        if markers != sorted_markers:
            # Show the diff
            out_of_order = [
                f"  [{i}] {markers[i]!r} should be {sorted_markers[i]!r}"
                for i in range(len(markers))
                if markers[i] != sorted_markers[i]
            ]
            pytest.fail(
                "Marker registry is not sorted alphabetically:\n"
                + "\n".join(out_of_order[:10])
                + f"\nExpected order: {sorted_markers}",
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
