# Core pytest configuration
import pytest

# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"

# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")

# Core pytest configuration
import pytest

# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"

# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")

"""Root conftest — suppress lifecycle trace logging during test collection and execution."""
import logging
from pathlib import Path

import pytest  # noqa: E402

from .conftest_factories import *

# Suppress lifecycle trace loggers that emit ~100K lines during import/execution.
# These overwhelm pytest's capture system causing OSError: Bad file descriptor.
for _name in ["adg", "lifecycle"]:
    _lg = logging.getLogger(_name)
    _lg.setLevel(logging.CRITICAL)
    _lg.propagate = False

# Phase 0.2: Session-scoped ADG fixture to eliminate redundant scans
@pytest.fixture(scope="session")
def cached_adg_scan():
    """Pre-computed ADG scan shared across all test modules.

    Eliminates redundant 3-5 minute scans per test session.
    Cache file: tests/.adg_cache.json
    """
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    cache_path = Path("tests/.adg_cache.json")
    scanner = ADGStaticScanner(
        repo_root=Path("."),
        cache_path=cache_path,
        include_tests=True
    )

    # Use a consistent commit SHA for cache hits across sessions
    result = scanner.scan(commit_sha="phase0-session-scan")

    print(f"\n=== ADG Session Cache ===")
    print(f"Cache file: {cache_path}")
    print(f"Nodes: {len(result.nodes)}")
    print(f"Edges: {len(result.edges)}")
    print(f"Digest: {result.digest[:16]}...")

    return result
