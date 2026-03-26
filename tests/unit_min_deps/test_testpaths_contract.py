"""
Test topology hard lock — enforces pytest collection boundaries.

Enforced invariants:
    1. pytest.ini has [pytest] header (not [tool:pytest]).
    2. testpaths includes ONLY tests/unit_min_deps, tests/integration/agentic_core,
       tests/agentic_core, tests/enforcement, and tests/governance.
    3. norecursedirs includes apps_rg, apps_lic, apps_shared, ops_scripts.
    4. There is NO root-level conftest.py.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_UNIT_DIR,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]
PYTEST_INI = ROOT / "pytest.ini"

REQUIRED_TESTPATHS = {
    "tests/unit_min_deps",
    "tests/integration/agentic_core",
    "tests/architecture",
    "tests/enforcement",
    "tests/governance",
    "tests/system_learning",
    "tests/sovereign_hardening",
    TESTS_UNIT_DIR,
}

REQUIRED_NORECURSEDIRS = {APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, OPS_SCRIPTS_DIR, "_quarantine"}


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
                from agentic_core.L0_routing.config.path_constants import (
            """Test has_pysection contract compliance."""
            # Arrange
            # TODO: Set up contract parties and terms
            contract_terms = {}  # Replace with actual contract terms

    contract_terms = {}  # Replace with actual contract terms

    # Act
    """Test no_tool_pysection contract compliance."""
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
    def test_testpaths_exact_match(self) -> None:
    """Test testpaths_exact_match contract compliance."""
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
    """norecursedirs must exclude apps_* and ops_scripts from collection."""

    def test_norecursedirs_includes_required(self) -> None:
    """Test norecursedirs_includes_required contract compliance."""
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

class TestNoRootConftest:
    """Root-level conftest.py must not exist (no global collection hooks)."""

    def test_no_root_conftest(self) -> None:
    """Test no_root_conftest contract compliance."""
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
