"""
Test topology hard lock — enforces pytest collection boundaries.

Enforced invariants:
    1. pytest.ini has [pytest] header (not [tool:pytest]).
    2. testpaths includes ONLY tests/unit_min_deps and tests/integration.
    3. norecursedirs includes apps_rg, apps_lic, apps_shared, ops_scripts.
    4. There is NO root-level conftest.py.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]
PYTEST_INI = ROOT / "pytest.ini"

REQUIRED_TESTPATHS = {"tests/unit_min_deps", "tests/integration/agentic_core"}

REQUIRED_NORECURSEDIRS = {"apps_rg", "apps_lic", "apps_shared", "ops_scripts", "_quarantine"}


def _read_pytest_ini() -> configparser.ConfigParser:
    """Parse pytest.ini and return the config parser."""
    parser = configparser.ConfigParser()
    parser.read(str(PYTEST_INI), encoding="utf-8")
    return parser


# ---------------------------------------------------------------------------
# 1. pytest.ini has [pytest] header
# ---------------------------------------------------------------------------


class TestPytestIniHeader:
    """pytest.ini must use [pytest] section header, not [tool:pytest]."""

    def test_has_pytest_section(self) -> None:
        parser = _read_pytest_ini()
        assert "pytest" in parser.sections(), (
            f"pytest.ini must have [pytest] section header.\nFound sections: {parser.sections()}"
        )

    def test_no_tool_pytest_section(self) -> None:
        parser = _read_pytest_ini()
        assert "tool:pytest" not in parser.sections(), (
            "pytest.ini must NOT use [tool:pytest] (that's for setup.cfg).\nUse [pytest] instead."
        )


# ---------------------------------------------------------------------------
# 2. testpaths includes ONLY the allowed directories
# ---------------------------------------------------------------------------


class TestTestpathsContract:
    """testpaths must be locked to tests/unit_min_deps and tests/integration only."""

    def test_testpaths_exact_match(self) -> None:
        parser = _read_pytest_ini()
        raw = parser.get("pytest", "testpaths", fallback="")
        actual = {p.strip() for p in raw.split() if p.strip()}
        assert actual == REQUIRED_TESTPATHS, (
            f"testpaths must be exactly {sorted(REQUIRED_TESTPATHS)}.\nGot: {sorted(actual)}"
        )


# ---------------------------------------------------------------------------
# 3. norecursedirs includes required directories
# ---------------------------------------------------------------------------


class TestNorecursedirsContract:
    """norecursedirs must exclude apps_* and ops_scripts from collection."""

    def test_norecursedirs_includes_required(self) -> None:
        parser = _read_pytest_ini()
        raw = parser.get("pytest", "norecursedirs", fallback="")
        actual = {p.strip() for p in raw.split() if p.strip()}
        missing = REQUIRED_NORECURSEDIRS - actual
        assert not missing, (
            f"norecursedirs is missing required entries: {sorted(missing)}.\n"
            f"Current norecursedirs: {sorted(actual)}"
        )


# ---------------------------------------------------------------------------
# 4. No root-level conftest.py
# ---------------------------------------------------------------------------


class TestNoRootConftest:
    """Root-level conftest.py must not exist (no global collection hooks)."""

    def test_no_root_conftest(self) -> None:
        root_conftest = ROOT / "conftest.py"
        assert not root_conftest.exists(), (
            "Root-level conftest.py must not exist.\n"
            "Global collection error suppression hooks are forbidden.\n"
            "Use directory-based isolation (tests/unit_min_deps/, tests/integration/) instead."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
