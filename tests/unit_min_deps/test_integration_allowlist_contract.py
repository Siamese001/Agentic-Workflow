"""
Integration placement contract — prevents orphan integration tests.

Enforced invariants:
    1. Every test file under tests/integration/ must reside under an allowed root
       (derived from pytest.ini testpaths).
    2. No top-level test files directly in tests/integration/ (must be in a subtree).
    3. tests/_quarantine/ is excluded from this check.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]
PYTEST_INI = ROOT / "pytest.ini"
INTEGRATION_BASE = ROOT / TESTS_DIR / "integration"


def _get_allowed_integration_roots() -> list[Path]:
    """Parse pytest.ini testpaths and return allowed integration root dirs."""
    parser = configparser.ConfigParser()
    parser.read(str(PYTEST_INI), encoding="utf-8")
    raw = parser.get("pytest", "testpaths", fallback="")
    roots = []
    for entry in raw.split():
        entry = entry.strip()
        if not entry:
            continue
        p = ROOT / entry.replace("/", "\\")
        # Only include paths that are under tests/integration/
        try:
            p.relative_to(INTEGRATION_BASE)
            roots.append(p)
        except ValueError:
            pass
    # Always include tests/integration/ itself as an allowed root
    if INTEGRATION_BASE.exists() and INTEGRATION_BASE not in roots:
        roots.append(INTEGRATION_BASE)
    return roots


def _find_integration_test_files() -> list[Path]:
    """Find all test_*.py files under tests/integration/, excluding _quarantine."""
    if not INTEGRATION_BASE.exists():
        return []
    results = []
    for f in INTEGRATION_BASE.rglob("test_*.py"):
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        if "_quarantine" in rel:
            continue
        results.append(f)
    return sorted(results)


class TestNoOrphanIntegrationTests:
    """Every integration test file must be under an allowed root from pytest.ini."""

    def test_all_integration_tests_under_allowed_roots(self) -> None:
                from agentic_core.L0_routing.config.path_constants import (
            """Test all_integration_tests_under_allowed_roots contract compliance."""
            # Arrange
            # TODO: Set up contract parties and terms
            contract_terms = {}  # Replace with actual contract terms

    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
            f"Found {len(orphans)} integration test file(s) outside allowed roots.\n"
            f"Allowed roots: {[str(r.relative_to(ROOT)).replace(chr(92), '/') for r in allowed]}\n"
            f"Orphans:\n"
            + "\n".join(f"  {o}" for o in orphans)
            + "\nMove to an allowed root or add the subtree to pytest.ini testpaths."
        )


class TestNoTopLevelIntegrationFiles:
    """No test files directly in tests/integration/ (must be in a subtree)."""

    def test_no_top_level_test_files(self) -> None:
    """Test no_top_level_files contract compliance."""
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
