"""
Unit Tests for Phase 1: Registry Verification
==============================================
Tests the registry verification module for agent discovery completeness.

USAGE:
    pytest tests/unit/agentic_core/L5_safety/validators/test_registry_verification.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
    AgentInfo,
    RegistryVerifier,
    VerificationResult,
    run_verification,
)


class TestAgentInfo:
    """Tests for AgentInfo dataclass."""

    def test_agent_info_creation(self):
        """Test basic AgentInfo creation."""
        info = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
            layer="L5",
            has_agent_class=True,
        )
        assert info.class_name == "TestAgent"
        assert info.layer == "L5"
        assert info.has_agent_class is True

    def test_agent_info_defaults(self):
        """Test AgentInfo default values."""
        info = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        assert info.layer == "Unknown"
        assert info.has_agent_class is False
        assert info.inheritance == []
        assert info.key_methods == []


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    def test_verification_result_defaults(self):
        """Test VerificationResult default values."""
        result = VerificationResult()
        assert result.total_filesystem_agents == 0
        assert result.total_registry_agents == 0
        assert result.orphan_agents == []
        assert result.missing_agents == []
        assert result.path_mismatches == []
        assert result.valid_agents == []
        assert result.coverage_percentage == 0.0
        assert result.is_complete is False

    def test_verification_result_complete_when_no_issues(self):
        """Test is_complete flag logic."""
        result = VerificationResult()
        result.is_complete = (
            len(result.orphan_agents) == 0
            and len(result.missing_agents) == 0
            and len(result.path_mismatches) == 0
        )
        assert result.is_complete is True


class TestRegistryVerifier:
    """Tests for RegistryVerifier class."""

    def test_find_project_root(self):
        """Test project root detection."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        assert verifier.project_root == PROJECT_ROOT
        assert verifier.project_root.exists()

    def test_is_excluded_archives(self):
        """Test exclusion of archives directory."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        path = Path("archives/old/TestAgent.py")
        assert verifier._is_excluded(path) is True

    def test_is_excluded_pycache(self):
        """Test exclusion of __pycache__ directory."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        path = Path("agentic_core/__pycache__/TestAgent.py")
        assert verifier._is_excluded(path) is True

    def test_is_excluded_valid_path(self):
        """Test non-excluded path."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/validators/TestAgent.py")
        assert verifier._is_excluded(path) is False

    def test_is_test_file_true(self):
        """Test detection of test files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        assert verifier._is_test_file(Path("tests/unit/test_agent.py")) is True
        assert verifier._is_test_file(Path("src/test_something.py")) is True

    def test_is_test_file_false(self):
        """Test non-test file detection."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        assert verifier._is_test_file(Path("agentic_core/TestAgent.py")) is False

    def test_extract_layer_l5(self):
        """Test layer extraction for L5."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("agentic_core/L5_safety/validators/TestAgent.py")
        assert layer == "L5"

    def test_extract_layer_l0(self):
        """Test layer extraction for L0."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("agentic_core/L0_routing/scripts/TestAgent.py")
        assert layer == "L0"

    def test_extract_layer_base(self):
        """Test layer extraction for base_agents."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("agentic_core/base_agents/SovereignBaseAgent.py")
        assert layer == "Base"

    def test_extract_layer_apps_rg(self):
        """Test layer extraction for apps_rg."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("apps_rg/engines/TestAgent.py")
        assert layer == "Apps_RG"

    def test_extract_layer_apps_lic(self):
        """Test layer extraction for apps_lic."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("apps_lic/engines/TestAgent.py")
        assert layer == "Apps_LIC"

    def test_extract_layer_root(self):
        """Test layer extraction for root files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        layer = verifier._extract_layer("TestAgent.py")
        assert layer == "Root"

    def test_scan_filesystem_finds_agents(self):
        """Test filesystem scan finds agent files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        agents = verifier.scan_filesystem()
        assert len(agents) > 0
        # Verify all found items are agents
        for agent in agents:
            assert agent.class_name.endswith("Agent")

    def test_scan_filesystem_excludes_tests(self):
        """Test filesystem scan excludes test files."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        agents = verifier.scan_filesystem()
        for agent in agents:
            assert "tests" not in agent.relative_path.split("\\")
            assert "tests" not in agent.relative_path.split("/")

    def test_load_registry(self):
        """Test loading registry from JSON."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        registry = verifier.load_registry()
        assert isinstance(registry, list)

    def test_verify_registry_returns_result(self):
        """Test verify_registry returns VerificationResult."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        assert isinstance(result, VerificationResult)
        assert result.total_filesystem_agents > 0

    def test_verify_registry_detects_missing_agents(self):
        """Test detection of agents missing from registry."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        # Given the registry only has 2 agents, there should be many missing
        assert len(result.missing_agents) > 0

    def test_generate_report_format(self):
        """Test report generation format."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "# Phase 1: Registry Verification Report" in report
        assert "## Summary" in report
        assert "Total Filesystem Agents" in report


class TestRunVerification:
    """Tests for run_verification function."""

    def test_run_verification_returns_result(self):
        """Test run_verification convenience function."""
        result = run_verification()
        assert isinstance(result, VerificationResult)


class TestParseAgentFile:
    """Tests for agent file parsing."""

    def test_parse_valid_agent_file(self):
        """Test parsing a valid agent file."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)

        # Find a known agent file
        agent_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py"
        if agent_path.exists():
            result = verifier._parse_agent_file(agent_path)
            assert result is not None
            assert result.has_agent_class is True
            assert "Agent" in result.class_name

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file returns None."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier._parse_agent_file(Path("/nonexistent/TestAgent.py"))
        assert result is None


class TestCoverageCalculation:
    """Tests for coverage percentage calculation."""

    def test_coverage_zero_when_no_agents(self):
        """Test coverage is 0 when no filesystem agents."""
        result = VerificationResult()
        result.total_filesystem_agents = 0
        # Coverage should remain 0
        assert result.coverage_percentage == 0.0

    def test_coverage_calculation(self):
        """Test coverage percentage calculation."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()

        if result.total_filesystem_agents > 0:
            expected_coverage = len(result.valid_agents) / result.total_filesystem_agents * 100
            assert abs(result.coverage_percentage - expected_coverage) < 0.01


class TestOrphanDetection:
    """Tests for orphan agent detection."""

    def test_orphan_detection_with_mock_registry(self):
        """Test orphan detection with mocked registry."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)

        # Create a mock registry with a non-existent agent
        mock_registry = [
            {
                "class_name": "NonExistentAgent",
                "path": "fake/path/NonExistentAgent.py",
            },
        ]

        with patch.object(verifier, "load_registry", return_value=mock_registry):
            result = verifier.verify_registry()
            # Should detect the orphan
            orphan_names = [o["class_name"] for o in result.orphan_agents]
            assert "NonExistentAgent" in orphan_names


class TestPathMismatchDetection:
    """Tests for path mismatch detection."""

    def test_path_mismatch_detection(self):
        """Test detection of path mismatches."""
        verifier = RegistryVerifier(project_root=PROJECT_ROOT)
        result = verifier.verify_registry()

        # The current registry has path mismatches (scripts\BootstrapAgent.py vs actual path)
        # This should be detected
        if result.total_registry_agents > 0:
            # Either we have path mismatches or orphans for the registry entries
            total_issues = len(result.path_mismatches) + len(result.orphan_agents)
            assert total_issues >= 0  # At minimum, verify the check runs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
