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

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        allowed = _get_allowed_integration_roots()
        assert allowed, (
            "No integration roots found in pytest.ini testpaths. "
            "Expected at least one path under tests/integration/."
        )

        orphans: list[str] = []
        for test_file in _find_integration_test_files():
            under_allowed = any(test_file == root or root in test_file.parents for root in allowed)
            if not under_allowed:
                rel = str(test_file.relative_to(ROOT)).replace("\\", "/")
                orphans.append(rel)

        assert not orphans, (
            f"Found {len(orphans)} integration test file(s) outside allowed roots.\n"
            f"Allowed roots: {[str(r.relative_to(ROOT)).replace(chr(92), '/') for r in allowed]}\n"
            f"Orphans:\n"
            + "\n".join(f"  {o}" for o in orphans)
            + "\nMove to an allowed root or add the subtree to pytest.ini testpaths."
        )


class TestNoTopLevelIntegrationFiles:
    """No test files directly in tests/integration/ (must be in a subtree)."""

    def test_no_top_level_test_files(self) -> None:
        if not INTEGRATION_BASE.exists():
            return
        top_level = [
            f
            for f in INTEGRATION_BASE.iterdir()
            if f.is_file() and f.name.startswith("test_") and f.suffix == ".py"
        ]
        violations = [str(f.relative_to(ROOT)).replace("\\", "/") for f in top_level]
        assert not violations, (
            f"Found {len(violations)} top-level test file(s) in tests/integration/:\n"
            + "\n".join(f"  {v}" for v in violations)
            + "\nIntegration tests must live in an explicit subtree (e.g., tests/integration/agentic_core/)."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
