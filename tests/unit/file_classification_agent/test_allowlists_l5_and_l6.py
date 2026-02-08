"""
Test L5 and L6 subprocess allowlists.

Validates:
- L5_SUBPROCESS_ALLOWLIST contains expected files
- L6_HYBRID_ALLOWLIST contains expected files
- Exact allowlist paths pass; near-miss paths fail
"""

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
)


class TestL5SubprocessAllowlist:
    """Tests for L5_SUBPROCESS_ALLOWLIST."""

    def test_allowlist_exists(self):
        """L5_SUBPROCESS_ALLOWLIST must be defined."""
        assert L5_SUBPROCESS_ALLOWLIST is not None
        assert isinstance(L5_SUBPROCESS_ALLOWLIST, frozenset)

    @pytest.mark.parametrize(
        "allowed_file",
        [
            "safe_subprocess_handler.py",
            "subprocess_security_util.py",
            "PreCommitSovereignAgent.py",
            "ArchitectureGovernorAgent.py",
            "AutonomyGuardianAgent.py",
            "SovereignActionPlaneAgent.py",
            "pre_deploy_check_util.py",
        ],
    )
    def test_expected_files_in_allowlist(self, allowed_file: str):
        """Expected L5 subprocess files must be in allowlist."""
        assert allowed_file in L5_SUBPROCESS_ALLOWLIST, f"Missing from allowlist: {allowed_file}"

    @pytest.mark.parametrize(
        "not_allowed",
        [
            "dashboard_e2_e_pipeline.py",
            "analysis_ops_validator.py",
            "deterministic_cleaner_validator.py",
            "GitAgent.py",
            "ReportLocationAgent.py",
            "random_subprocess_user.py",
        ],
    )
    def test_anomaly_files_not_in_allowlist(self, not_allowed: str):
        """Anomaly files must NOT be in L5 allowlist."""
        assert not_allowed not in L5_SUBPROCESS_ALLOWLIST, f"Should not be in allowlist: {not_allowed}"

    def test_allowlist_is_immutable(self):
        """L5_SUBPROCESS_ALLOWLIST must be immutable frozenset."""
        assert isinstance(L5_SUBPROCESS_ALLOWLIST, frozenset)

    def test_allowlist_minimum_size(self):
        """L5_SUBPROCESS_ALLOWLIST must have at least 7 entries."""
        assert len(L5_SUBPROCESS_ALLOWLIST) >= 7


class TestL6HybridAllowlist:
    """Tests for L6_HYBRID_ALLOWLIST."""

    def test_allowlist_exists(self):
        """L6_HYBRID_ALLOWLIST must be defined."""
        assert L6_HYBRID_ALLOWLIST is not None
        assert isinstance(L6_HYBRID_ALLOWLIST, frozenset)

    def test_playwright_util_in_allowlist(self):
        """verify_dashboard_e2e_playwright_util.py must be in L6 allowlist."""
        assert "verify_dashboard_e2e_playwright_util.py" in L6_HYBRID_ALLOWLIST

    @pytest.mark.parametrize(
        "not_allowed",
        [
            "random_subprocess_file.py",
            "dashboard_generator.py",
            "telemetry_agent.py",
        ],
    )
    def test_random_files_not_in_allowlist(self, not_allowed: str):
        """Random files must NOT be in L6 allowlist."""
        assert not_allowed not in L6_HYBRID_ALLOWLIST

    def test_allowlist_is_immutable(self):
        """L6_HYBRID_ALLOWLIST must be immutable frozenset."""
        assert isinstance(L6_HYBRID_ALLOWLIST, frozenset)


class TestAllowlistNearMisses:
    """Tests for near-miss paths that should NOT be allowed."""

    @pytest.mark.parametrize(
        "near_miss",
        [
            "Safe_subprocess_handler.py",  # Wrong case
            "safe_subprocess_handler",  # Missing .py
            "safe_subprocess_handlers.py",  # Plural
            "subprocess_handler.py",  # Missing prefix
        ],
    )
    def test_l5_near_misses_not_allowed(self, near_miss: str):
        """Near-miss filenames must NOT be in L5 allowlist."""
        assert near_miss not in L5_SUBPROCESS_ALLOWLIST

    @pytest.mark.parametrize(
        "near_miss",
        [
            "verify_dashboard_e2e_playwright.py",  # Missing _util
            "dashboard_e2e_playwright_util.py",  # Missing verify_
            "verify_dashboard_e2e_playwright_util",  # Missing .py
        ],
    )
    def test_l6_near_misses_not_allowed(self, near_miss: str):
        """Near-miss filenames must NOT be in L6 allowlist."""
        assert near_miss not in L6_HYBRID_ALLOWLIST
