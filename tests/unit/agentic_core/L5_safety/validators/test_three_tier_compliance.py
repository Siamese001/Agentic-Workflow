"""
Unit Tests for Phase 2: Three-Tier Compliance Assessment
=========================================================
Tests the three-tier compliance checker for Contract, Blueprint, and Soul coverage.

USAGE:
    pytest tests/unit/agentic_core/L5_safety/validators/test_three_tier_compliance.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.enforcement.registry_verification_script import AgentInfo
from agentic_core.L5_safety.enforcement.three_tier_compliance_script import (
    AgentCompliance,
    ComplianceResult,
    ThreeTierComplianceChecker,
    TierStatus,
    run_compliance_check,
)


class TestTierStatus:
    """Tests for TierStatus dataclass."""

    def test_tier_status_creation(self):
        """Test basic TierStatus creation."""
        status = TierStatus(tier_name="Contract", is_covered=True)
        assert status.tier_name == "Contract"
        assert status.is_covered is True

    def test_tier_status_defaults(self):
        """Test TierStatus default values."""
        status = TierStatus(tier_name="Blueprint", is_covered=False)
        assert status.coverage_type == ""
        assert status.details == []
        assert status.gaps == []

    def test_tier_status_with_details(self):
        """Test TierStatus with details."""
        status = TierStatus(
            tier_name="Soul",
            is_covered=True,
            coverage_type="Unit tests",
            details=["test_agent.py"],
        )
        assert status.coverage_type == "Unit tests"
        assert len(status.details) == 1


class TestAgentCompliance:
    """Tests for AgentCompliance dataclass."""

    def test_agent_compliance_creation(self):
        """Test basic AgentCompliance creation."""
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        compliance = AgentCompliance(agent=agent)
        assert compliance.agent.class_name == "TestAgent"

    def test_is_fully_compliant_false_by_default(self):
        """Test is_fully_compliant is False by default."""
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        compliance = AgentCompliance(agent=agent)
        assert compliance.is_fully_compliant is False

    def test_is_fully_compliant_true_when_all_covered(self):
        """Test is_fully_compliant is True when all tiers covered."""
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        compliance = AgentCompliance(agent=agent)
        compliance.contract_tier = TierStatus("Contract", True)
        compliance.blueprint_tier = TierStatus("Blueprint", True)
        compliance.soul_tier = TierStatus("Soul", True)
        assert compliance.is_fully_compliant is True

    def test_compliance_score_zero(self):
        """Test compliance score is 0 when no tiers covered."""
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        compliance = AgentCompliance(agent=agent)
        assert compliance.compliance_score == 0

    def test_compliance_score_three(self):
        """Test compliance score is 3 when all tiers covered."""
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        compliance = AgentCompliance(agent=agent)
        compliance.contract_tier = TierStatus("Contract", True)
        compliance.blueprint_tier = TierStatus("Blueprint", True)
        compliance.soul_tier = TierStatus("Soul", True)
        assert compliance.compliance_score == 3

    def test_compliance_score_partial(self):
        """Test compliance score with partial coverage."""
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="test/TestAgent.py",
        )
        compliance = AgentCompliance(agent=agent)
        compliance.contract_tier = TierStatus("Contract", True)
        compliance.blueprint_tier = TierStatus("Blueprint", False)
        compliance.soul_tier = TierStatus("Soul", True)
        assert compliance.compliance_score == 2


class TestComplianceResult:
    """Tests for ComplianceResult dataclass."""

    def test_compliance_result_defaults(self):
        """Test ComplianceResult default values."""
        result = ComplianceResult()
        assert result.total_agents == 0
        assert result.fully_compliant == 0
        assert result.contract_covered == 0
        assert result.blueprint_covered == 0
        assert result.soul_covered == 0

    def test_contract_coverage_pct_zero_agents(self):
        """Test contract coverage percentage with zero agents."""
        result = ComplianceResult()
        assert result.contract_coverage_pct == 0

    def test_contract_coverage_pct_calculation(self):
        """Test contract coverage percentage calculation."""
        result = ComplianceResult()
        result.total_agents = 10
        result.contract_covered = 8
        assert result.contract_coverage_pct == 80.0

    def test_blueprint_coverage_pct_calculation(self):
        """Test blueprint coverage percentage calculation."""
        result = ComplianceResult()
        result.total_agents = 10
        result.blueprint_covered = 5
        assert result.blueprint_coverage_pct == 50.0

    def test_soul_coverage_pct_calculation(self):
        """Test soul coverage percentage calculation."""
        result = ComplianceResult()
        result.total_agents = 10
        result.soul_covered = 3
        assert result.soul_coverage_pct == 30.0

    def test_overall_compliance_pct_calculation(self):
        """Test overall compliance percentage calculation."""
        result = ComplianceResult()
        result.total_agents = 10
        result.fully_compliant = 2
        assert result.overall_compliance_pct == 20.0


class TestThreeTierComplianceChecker:
    """Tests for ThreeTierComplianceChecker class."""

    def test_checker_initialization(self):
        """Test checker initialization."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        assert checker.project_root == PROJECT_ROOT

    def test_scan_guardian_tests(self):
        """Test scanning for Guardian tests."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        tests = checker._scan_guardian_tests()
        assert isinstance(tests, list)
        # Guardian tests should exist
        assert len(tests) > 0

    def test_scan_unit_tests(self):
        """Test scanning for unit tests."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        tests = checker._scan_unit_tests()
        assert isinstance(tests, list)
        assert len(tests) > 0

    def test_build_unit_test_map(self):
        """Test building unit test map."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        checker._unit_tests = checker._scan_unit_tests()
        agent_map = checker._build_unit_test_map()
        assert isinstance(agent_map, dict)
        # Should have entries for various agents
        assert len(agent_map) > 0

    def test_normalize_agent_name(self):
        """Test agent name normalization."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        assert checker._normalize_agent_name("LocationAgent") == "locationagent"
        expected = "hop1profileanalysisagent"
        assert checker._normalize_agent_name("HOP1ProfileAnalysisAgent") == expected
        assert checker._normalize_agent_name("Test_Agent") == "testagent"

    def test_check_contract_tier_covered(self):
        """Test contract tier check for covered agent."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="agentic_core/L5_safety/validators/TestAgent.py",
        )
        status = checker._check_contract_tier(agent)
        assert status.is_covered is True
        assert "ruff" in status.details

    def test_check_contract_tier_excluded(self):
        """Test contract tier check for excluded agent."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="archives/old/TestAgent.py",
        )
        status = checker._check_contract_tier(agent)
        assert status.is_covered is False
        assert len(status.gaps) > 0

    def test_check_blueprint_tier(self):
        """Test blueprint tier check."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        checker._guardian_tests = checker._scan_guardian_tests()
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="agentic_core/L5_safety/validators/TestAgent.py",
            layer="L5",
            inheritance=["SovereignBaseAgent"],
        )
        status = checker._check_blueprint_tier(agent)
        # Should be covered by guardian tests
        assert status.is_covered is True

    def test_check_soul_tier_with_test(self):
        """Test soul tier check for agent with unit test."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        checker._unit_tests = checker._scan_unit_tests()
        checker._unit_test_agent_map = checker._build_unit_test_map()

        # LocationAgent should have a unit test
        agent = AgentInfo(
            class_name="LocationAgent",
            file_path=PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py",
            relative_path="agentic_core/L5_safety/validators/LocationAgent.py",
            layer="L5",
        )
        status = checker._check_soul_tier(agent)
        assert status.is_covered is True

    def test_check_soul_tier_without_test(self):
        """Test soul tier check for agent without unit test."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        checker._unit_tests = checker._scan_unit_tests()
        checker._unit_test_agent_map = checker._build_unit_test_map()

        # Use a fake agent that definitely has no test
        agent = AgentInfo(
            class_name="NonExistentFakeAgent",
            file_path=Path("/fake/NonExistentFakeAgent.py"),
            relative_path="fake/NonExistentFakeAgent.py",
            layer="Unknown",
        )
        status = checker._check_soul_tier(agent)
        assert status.is_covered is False
        assert len(status.gaps) > 0

    def test_suggest_test_path(self):
        """Test test path suggestion."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="LocationAgent",
            file_path=Path("/test/LocationAgent.py"),
            relative_path="agentic_core/L5_safety/validators/LocationAgent.py",
        )
        suggested = checker._suggest_test_path(agent)
        assert "tests/unit" in suggested
        assert "test_location_agent.py" in suggested

    def test_check_compliance_returns_result(self):
        """Test check_compliance returns ComplianceResult."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()
        assert isinstance(result, ComplianceResult)
        assert result.total_agents > 0

    def test_check_compliance_finds_guardian_tests(self):
        """Test check_compliance finds Guardian tests."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()
        assert len(result.guardian_tests) > 0

    def test_check_compliance_finds_unit_tests(self):
        """Test check_compliance finds unit tests."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()
        assert len(result.unit_tests) > 0

    def test_generate_report_format(self):
        """Test report generation format."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()
        report = checker.generate_report(result)
        assert "# Phase 2: Three-Tier Compliance Assessment Report" in report
        assert "## Summary" in report
        assert "Tier Coverage" in report


class TestRunComplianceCheck:
    """Tests for run_compliance_check function."""

    def test_run_compliance_check_returns_result(self):
        """Test run_compliance_check convenience function."""
        result = run_compliance_check()
        assert isinstance(result, ComplianceResult)


class TestContractTierCoverage:
    """Tests for Contract tier coverage logic."""

    def test_all_non_excluded_agents_covered(self):
        """Test that all non-excluded agents are covered by Contract tier."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()

        # All agents should be covered by Contract tier (pre-commit)
        # unless they are in excluded directories
        for compliance in result.agent_compliance:
            path = compliance.agent.relative_path.replace("\\", "/")
            if "archives/" not in path and ".sovereign_healing_backup/" not in path:
                assert compliance.contract_tier.is_covered is True


class TestBlueprintTierCoverage:
    """Tests for Blueprint tier coverage logic."""

    def test_guardian_tests_provide_coverage(self):
        """Test that Guardian tests provide Blueprint coverage."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()

        # Most agents should have Blueprint coverage from Guardian tests
        covered_count = sum(1 for c in result.agent_compliance if c.blueprint_tier.is_covered)
        assert covered_count > 0


class TestSoulTierCoverage:
    """Tests for Soul tier coverage logic."""

    def test_agents_with_unit_tests_covered(self):
        """Test that agents with unit tests have Soul coverage."""
        checker = ThreeTierComplianceChecker(project_root=PROJECT_ROOT)
        result = checker.check_compliance()

        # Some agents should have Soul coverage
        covered_count = sum(1 for c in result.agent_compliance if c.soul_tier.is_covered)
        assert covered_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
