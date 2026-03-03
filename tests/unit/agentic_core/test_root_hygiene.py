"""
File: tests/L0/test_root_hygiene.py
Rationale:
    Verifies that the RootHygieneEnforcer correctly cleans the environment.
"""

import pytest

from agentic_core.L0_routing.scripts.root_hygiene_util import enforce_root_hygiene


@pytest.fixture
def dirty_repo(tmp_path):
    """Creates a dirty mock repo with illegal root folders."""
    # Setup Markers
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "pyproject.toml").touch()

    # Create Illegal Root Scripts
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "standalone_tool.py").write_text("print('hello')")
    (scripts / "core_tool.py").write_text("import agentic_core\nprint('core')")

    # Create Illegal Coverage
    cov = tmp_path / "coverage_html"
    cov.mkdir()
    (cov / "index.html").touch()

    return tmp_path


def test_hygiene_enforcement(dirty_repo, monkeypatch):
    """Test that scripts are moved to correct locations and root is cleaned."""
    monkeypatch.chdir(dirty_repo)

    # Run Enforcer
    enforce_root_hygiene()

    # Assertions
    # 1. Illegal dirs gone
    assert not (dirty_repo / "scripts").exists()
    assert not (dirty_repo / "coverage_html").exists()

    # 2. Standalone script -> ops_scripts
    assert (dirty_repo / "ops_scripts" / "standalone_tool.py").exists()

    # 3. Core script -> agentic_core/L0_routing/scripts
    assert (dirty_repo / "agentic_core" / "L0_routing" / "scripts" / "core_tool.py").exists()

    # 4. Coverage -> reports
    assert (dirty_repo / "reports" / "coverage_html" / "index.html").exists()


def test_purge_cache_refiling(dirty_repo, monkeypatch):
    """Test the specific rule for purge_cache.py reorganization."""
    monkeypatch.chdir(dirty_repo)

    # Setup purge_cache in illegal scripts folder
    (dirty_repo / "scripts" / "purge_cache.py").write_text("print('clean')")

    enforce_root_hygiene()

    # Should end up nested in maintenance
    assert (dirty_repo / "ops_scripts" / "maintenance" / "purge_cache.py").exists()
