"""
Tests Configuration - Guardian Marker Registration
===================================================
This conftest.py registers the @pytest.mark.guardian marker for the Guardian Layer tests.

The Guardian Layer is a Zero-Trust architecture validation suite that ensures:
1. MRO & Inheritance Hardening (Phase 1)
2. Import Safety & Dependency Validation (Phase 2)
3. SSOT & Path Enforcement (Phase 3)

USAGE:
    pytest -m guardian              # Run only guardian tests
    pytest -m "not guardian"        # Run all tests except guardian
    pytest tests/guardian/ -v       # Run guardian tests with verbose output

MARKERS:
    @pytest.mark.guardian - Mark a test as part of the Guardian Layer
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Pytest sandbox isolation: redirect tmp_path to .pytest_tmp inside repo root
_BASETEMP = PROJECT_ROOT / ".pytest_tmp"


# =============================================================================
# MARKER REGISTRATION
# =============================================================================


def pytest_addoption(parser):
    """Register --import-strict CLI flag for controlled import strictness ramp."""
    parser.addoption(
        "--import-strict",
        action="store_true",
        default=False,
        help="Enable strict import mode: pytest.fail() instead of pytest.skip() on ImportError",
    )


def pytest_configure(config):
    """
    Register custom pytest markers for the Guardian Layer.

    This prevents warnings about unknown markers when running tests.
    Also sets basetemp early for tmp_path fixtures.
    """
    # Set basetemp early, before tmp_path fixtures are created
    if getattr(config, "option", None) and getattr(config.option, "basetemp", None) is None:
        config.option.basetemp = str(_BASETEMP)

    # Propagate --import-strict to environment for tests._config.import_strict_mode
    if getattr(config.option, "import_strict", False):
        os.environ["IMPORT_STRICT_MODE"] = "1"

    config.addinivalue_line(
        "markers",
        "guardian: marks tests as part of the Guardian Layer (Zero-Trust architecture validation)",
    )
    config.addinivalue_line(
        "markers",
        "constitutional: marks tests that enforce constitutional rules (cannot be overridden)",
    )
    config.addinivalue_line("markers", "ssot: marks tests that validate Single Source of Truth compliance")
    config.addinivalue_line("markers", "mro: marks tests that validate Method Resolution Order integrity")
    config.addinivalue_line(
        "markers",
        "import_safety: marks tests that validate import safety and dependencies",
    )


# =============================================================================
# SHARED FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def guardian_config() -> dict:
    """
    Return configuration for Guardian tests.

    This includes thresholds for technical debt tracking.
    """
    return {
        # Technical debt thresholds (tests pass if violations <= threshold)
        "thresholds": {
            "mro_violations": 10,
            "import_issues": 50,
            "circular_deps": 10,
            "forbidden_imports": 5,
            "missing_init": 20,
            "naming_violations": 50,
            "orphan_files": 30,
            "depth_violations": 20,
            "base_agent_violations": 5,
        },
        # Excluded directories for scanning
        "excluded_dirs": {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "archives",
            ".sovereign_healing_backup",
            ".backup",
            "node_modules",
            ".mypy_cache",
            ".ruff_cache",
            "temp_quiet_test",
            "temp_verbose_test",
        },
        # Source directories to scan
        "source_dirs": [
            "agentic_core",
            "apps_rg",
            "apps_lic",
            "apps_shared",
            "ops_scripts",
        ],
    }


# =============================================================================
# HOOKS FOR GUARDIAN REPORTING
# =============================================================================


def pytest_collection_modifyitems(config, items):
    """
    Default to integration tests only when no marker specified.
    Track guardian test counts for reporting.
    """
    # Get the marker expression from config
    marker_expr = config.getoption("-m", default="")

    # If no marker specified, default to integration_full_deps + governance + unit_min_deps
    if not marker_expr:
        default_markers = ("integration_full_deps", "governance", "unit_min_deps")
        deselected = []
        selected = []
        for item in items:
            if any(item.get_closest_marker(m) for m in default_markers):
                selected.append(item)
            else:
                deselected.append(item)

        # Replace items list with selected only
        items[:] = selected

        # Store deselected count for reporting
        config._deselected_count = len(deselected)

    # Track guardian test counts for reporting
    guardian_tests = [item for item in items if "guardian" in item.nodeid]
    if guardian_tests:
        config._guardian_test_count = len(guardian_tests)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add Guardian summary to pytest terminal output.

    This hook runs after all tests complete and provides
    a summary of Guardian test results.
    """
    # Check if we ran any guardian tests
    guardian_count = getattr(config, "_guardian_test_count", 0)

    if guardian_count == 0:
        return  # No guardian tests were run

    # Get test statistics
    stats = terminalreporter.stats
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    errors = len(stats.get("error", []))

    # Print Guardian summary
    terminalreporter.write_sep("=", "GUARDIAN LAYER SUMMARY")
    terminalreporter.write_line(f"Guardian tests run: {guardian_count}")
    terminalreporter.write_line(f"Passed: {passed}")
    terminalreporter.write_line(f"Failed: {failed}")
    terminalreporter.write_line(f"Errors: {errors}")

    if exitstatus == 0:
        terminalreporter.write_line("")
        terminalreporter.write_line("✅ GUARDIAN STATUS: PASS")
        terminalreporter.write_line("All architectural integrity checks passed.")
    else:
        terminalreporter.write_line("")
        terminalreporter.write_line("❌ GUARDIAN STATUS: FAIL")
        terminalreporter.write_line("Architectural violations detected. Review failed tests.")

    terminalreporter.write_sep("=", "")
