"""conftest.py for tests/unit/

Under --import-mode=importlib pytest registers tests/agentic_core as the
AGENTIC_CORE_DIR package in sys.modules, shadowing the production package at
the project root. The pytest_configure hook fires before any test module is
imported, purging all agentic_core.* entries from sys.modules and re-inserting
the project root so subsequent imports resolve to the real production package.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path IMMEDIATELY at module load time
_PROJECT_ROOT = str(Path(__file__).parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Hardcoded fallback values to avoid collection-time imports
_AGENTIC_CORE_DIR = "agentic_core"
_TESTS_DIR = "tests"


def pytest_configure(config):
    """Purge shadowed agentic_core from sys.modules before any test imports."""
    # Try to get actual values from config, fallback to hardcoded
    try:
        from agentic_core.L0_routing.config.path_constants import (
            AGENTIC_CORE_DIR,
            TESTS_DIR,
        )
    except ImportError:
        # Use hardcoded values during collection when imports may fail
        AGENTIC_CORE_DIR = _AGENTIC_CORE_DIR
        TESTS_DIR = _TESTS_DIR

    # Remove all agentic_core.* entries that point into tests/ so the next
    # import resolves from the project root production package.
    _tests_agentic_core = str(Path(_PROJECT_ROOT) / TESTS_DIR / AGENTIC_CORE_DIR)
    to_delete = []
    for key, mod in sys.modules.items():
        if not key.startswith(AGENTIC_CORE_DIR):
            continue
        pkg_path = getattr(mod, "__path__", None)
        pkg_file = getattr(mod, "__file__", "") or ""
        if pkg_path and any(_tests_agentic_core in str(p) for p in pkg_path):
            to_delete.append(key)
        elif _tests_agentic_core in pkg_file:
            to_delete.append(key)
    for key in to_delete:
        del sys.modules[key]

    # Add markers
    config.addinivalue_line("markers", "data: marks tests as data-dependent")


# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"
