"""Tests for MigrationHelper."""

import pytest

# from agentic_core.utils.feature_flags import FeatureFlagManager
# from agentic_core.utils.migration_helper import (
#     ComplianceResult,
#     MigrationHelper,
#     MigrationStatus,
#     check_agent_compliance,
#     get_migration_status,
# )

# from agentic_core.mixins.feature_flagged_agent_mixin import FeatureFlaggedAgentMixin


class NonCompliantAgent:
    """Agent without FeatureFlaggedAgentMixin."""

    def some_method(self):
        pass


class CompliantAgent:  # TODO: Fix FeatureFlaggedAgentMixin import
    """Agent with FeatureFlaggedAgentMixin."""

    def some_method(self):
        pass

    def verify_action(self, *args, **kwargs):
        pass

    def submit_for_review(self, *args, **kwargs):
        pass


class TestComplianceResult:
    """Tests for ComplianceResult dataclass."""

    def test_create_result(self):
        """Test creating a compliance result."""
        result = ComplianceResult(
            agent_name="TestAgent",
            compliant=True,
            has_feature_flag_mixin=True,
            has_verification_gate=True,
            has_human_review=True,
            has_meta_learning=True,
            has_audit_trail=True,
        )
        assert result.agent_name == "TestAgent"
        assert result.compliant is True
        assert result.missing_components == []
        assert result.recommendations == []

    def test_create_result_with_missing(self):
        """Test creating result with missing components."""
        result = ComplianceResult(
            agent_name="TestAgent",
            compliant=False,
            has_feature_flag_mixin=False,
            has_verification_gate=False,
            has_human_review=False,
            has_meta_learning=False,
            has_audit_trail=False,
            missing_components=["FeatureFlaggedAgentMixin"],
            recommendations=["Add mixin"],
        )
        assert result.compliant is False
        assert len(result.missing_components) == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ComplianceResult(
            agent_name="TestAgent",
            compliant=True,
            has_feature_flag_mixin=True,
            has_verification_gate=True,
            has_human_review=True,
            has_meta_learning=True,
            has_audit_trail=True,
        )
        d = result.to_dict()
        assert d["agent_name"] == "TestAgent"
        assert d["compliant"] is True
        assert "missing_components" in d


class TestMigrationStatus:
    """Tests for MigrationStatus dataclass."""

    def test_create_status(self):
        """Test creating migration status."""
        status = MigrationStatus(
            total_agents=10,
            compliant_agents=8,
            non_compliant_agents=2,
            compliance_percentage=80.0,
        )
        assert status.total_agents == 10
        assert status.compliant_agents == 8
        assert status.compliance_percentage == 80.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        status = MigrationStatus(
            total_agents=10,
            compliant_agents=8,
            non_compliant_agents=2,
            compliance_percentage=80.0,
            agents_by_status={"compliant": ["A", "B"], "non_compliant": ["C"]},
        )
        d = status.to_dict()
        assert d["total_agents"] == 10
        assert "agents_by_status" in d


class TestMigrationHelper:
    """Tests for MigrationHelper."""

    def setup_method(self):
        """Clear state before each test."""
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        """Clear state after each test."""
        FeatureFlagManager.clear_all_overrides()

    def test_check_agent_compliance_non_compliant(self):
        """Test checking non-compliant agent."""
        result = MigrationHelper.check_agent_compliance(NonCompliantAgent)

        assert result.agent_name == "NonCompliantAgent"
        assert result.compliant is False
        assert result.has_feature_flag_mixin is False
        assert "FeatureFlaggedAgentMixin" in result.missing_components

    def test_check_agent_compliance_compliant(self):
        """Test checking compliant agent."""
        result = MigrationHelper.check_agent_compliance(CompliantAgent)

        assert result.agent_name == "CompliantAgent"
        assert result.compliant is True
        assert result.has_feature_flag_mixin is True

    def test_check_agent_compliance_strict_mode(self):
        """Test strict mode requires all components."""
        result = MigrationHelper.check_agent_compliance(CompliantAgent, strict=True)

        # Compliant agent has mixin but may not have all method implementations
        # in the base class definition - they come from the mixin
        assert result.has_feature_flag_mixin is True

    def test_check_agent_compliance_partial(self):
        """Test checking partial agent (some methods, no mixin)."""
        result = MigrationHelper.check_agent_compliance(PartialAgent)

        assert result.has_feature_flag_mixin is False
        assert result.has_verification_gate is True
        assert result.has_human_review is True
        assert result.compliant is False  # No mixin

    def test_check_agent_compliance_partial_strict(self):
        """Test strict mode for partial agent."""
        result = MigrationHelper.check_agent_compliance(PartialAgent, strict=True)

        assert result.compliant is False
        assert len(result.missing_components) > 0

    def test_has_feature_flag_mixin(self):
        """Test checking for mixin in MRO."""
        assert MigrationHelper._has_feature_flag_mixin(CompliantAgent) is True
        assert MigrationHelper._has_feature_flag_mixin(NonCompliantAgent) is False

    def test_has_method(self):
        """Test checking for method existence."""
        assert MigrationHelper._has_method(PartialAgent, "verify_action") is True
        assert MigrationHelper._has_method(PartialAgent, "nonexistent") is False

    def test_get_migration_status_empty(self):
        """Test migration status with no agents."""
        status = MigrationHelper.get_migration_status([])

        assert status.total_agents == 0
        assert status.compliance_percentage == 0.0

    def test_get_migration_status_mixed(self):
        """Test migration status with mixed compliance."""
        agents = [CompliantAgent, NonCompliantAgent, PartialAgent]
        status = MigrationHelper.get_migration_status(agents)

        assert status.total_agents == 3
        assert status.compliant_agents == 1
        assert status.non_compliant_agents == 2
        assert status.compliance_percentage == pytest.approx(33.33, rel=0.1)

    def test_get_migration_status_all_compliant(self):
        """Test migration status when all agents compliant."""
        agents = [CompliantAgent]
        status = MigrationHelper.get_migration_status(agents)

        assert status.total_agents == 1
        assert status.compliant_agents == 1
        assert status.compliance_percentage == 100.0

    def test_get_migration_status_includes_flag_status(self):
        """Test that status includes feature flag status."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        status = MigrationHelper.get_migration_status([CompliantAgent])

        assert "feature_flag_status" in status.to_dict()
        assert status.feature_flag_status["ENABLE_META_LEARNING"] is True

    def test_generate_migration_report(self):
        """Test generating migration report."""
        agents = [CompliantAgent, NonCompliantAgent]
        report = MigrationHelper.generate_migration_report(agents)

        assert "AGENT MIGRATION STATUS REPORT" in report
        assert "Total Agents: 2" in report
        assert "Compliant: 1" in report
        assert "Non-Compliant: 1" in report

    def test_generate_migration_report_lists_non_compliant(self):
        """Test that report lists non-compliant agents."""
        agents = [CompliantAgent, NonCompliantAgent]
        report = MigrationHelper.generate_migration_report(agents)

        assert "Non-Compliant Agents:" in report
        assert "NonCompliantAgent" in report


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_check_agent_compliance_function(self):
        """Test convenience function."""
        result = check_agent_compliance(CompliantAgent)
        assert result.compliant is True

    def test_get_migration_status_function(self):
        """Test convenience function."""
        status = get_migration_status([CompliantAgent, NonCompliantAgent])
        assert status.total_agents == 2
