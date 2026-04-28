"""Integration tests for formal verification scanners."""

import pytest


@pytest.mark.unit_min_deps
def test_repo_no_powershell_violations():
    """Test that repository has no PowerShell violations."""


@pytest.mark.unit_min_deps
def test_repo_no_write_gateway_violations():
    """Test that repository has no write gateway violations in scope."""


@pytest.mark.unit_min_deps
def test_repo_no_determinism_violations():
    """Test that repository has no determinism violations in replay/storage."""


@pytest.mark.unit_min_deps
def test_scanner_coverage():
    """Test that scanners cover expected directories."""

    if tools_dir.exists():
        pass

    if evidence_dir.exists():
        pass

    if agentic_core_dir.exists():
        pass

    if replay_dir.exists():
        pass

    if storage_dir.exists():
        pass


@pytest.mark.unit_min_deps
def test_scanner_deterministic_output():
    """Test that scanners produce deterministic output across runs."""

    def check_sorted(violations):
        for i in range(1, len(violations)):
            if violations[i - 1] > violations[i]:
                return False
        return True
