"""
End-to-End Integration Tests for Agent Migration.

Tests the complete integration of all migration components:
- Interfaces and Protocols
- Feature Flags and Dynamic Loading
- L5 Safety Adapters
- Component Factory
- Domain Integration
"""

import os
import tempfile

import pytest

from agentic_core.mixins.feature_flagged_agent_mixin import (
    FeatureFlaggedAgentMixin,
)
from agentic_core.integration.component_factory import ComponentFactory
from agentic_core.integration.migration_helper import (
    MigrationHelper,
    check_agent_compliance,
)
from agentic_core.interfaces.review_protocol import (
    ReviewRequest,
    ReviewStatus,
)
from agentic_core.interfaces.verification_types import (
    VerificationRequest,
)
from agentic_core.L5_safety.reasoning.human_review_adapter import HumanReviewAdapter
from agentic_core.L5_safety.reasoning.verification_gate_adapter import (
    VerificationGateAdapter,
)
from agentic_core.utils.dependency_resolver import DynamicLoader
from agentic_core.primitives.feature_flags import FeatureFlagManager
from apps_shared.integration.domain_agent_mixin import (
    DomainAgentMixin,
    LICDomainMixin,
    RGDomainMixin,
)
from apps_shared.integration.integration_config import get_domain_config


class TestE2EFeatureFlagIntegration:
    """E2E tests for feature flag integration across all layers."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()
        DynamicLoader.clear_cache()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()
        DynamicLoader.clear_cache()

    def test_flags_control_component_availability(self):
        """Test that feature flags control component availability."""
        # All disabled by default
        assert ComponentFactory.get_verification_gate() is None
        assert ComponentFactory.get_human_review_queue() is None

        # Enable verification gate
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        gate = ComponentFactory.get_verification_gate()
        assert gate is not None

        # Enable HITL
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        queue = ComponentFactory.get_human_review_queue()
        assert queue is not None

    def test_component_factory_caches_instances(self):
        """Test that ComponentFactory caches instances correctly."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)

        gate1 = ComponentFactory.get_verification_gate()
        gate2 = ComponentFactory.get_verification_gate()
        assert gate1 is gate2

    def test_component_status_reflects_runtime_state(self):
        """Test that component status accurately reflects runtime state."""
        status1 = ComponentFactory.get_component_status()
        assert status1["verification_gate"]["flag_enabled"] is False
        assert status1["verification_gate"]["instance_cached"] is False

        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        ComponentFactory.get_verification_gate()

        status2 = ComponentFactory.get_component_status()
        assert status2["verification_gate"]["flag_enabled"] is True
        assert status2["verification_gate"]["instance_cached"] is True


class TestE2EVerificationGateFlow:
    """E2E tests for verification gate workflow."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def test_verification_disabled_allows_all(self):
        """Test that disabled verification allows all actions."""
        adapter = VerificationGateAdapter()
        request = VerificationRequest(
            file_path="/nonexistent/file.py",
            action_type="modify_function",
            target_node="nonexistent_func",
        )

        result = adapter.verify_action(request)
        assert result.success is True
        assert result.reason == "verification_disabled"

    def test_verification_enabled_validates_real_file(self):
        """Test verification against a real file."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        # Create a real file with a function
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def existing_function():\n    pass\n\ndef another_func():\n    pass\n")
            temp_path = f.name

        try:
            # Test existing function
            request1 = VerificationRequest(
                file_path=temp_path,
                action_type="modify_function",
                target_node="existing_function",
            )
            result1 = adapter.verify_action(request1)
            assert result1.success is True

            # Test non-existing function
            request2 = VerificationRequest(
                file_path=temp_path,
                action_type="modify_function",
                target_node="nonexistent_function",
            )
            result2 = adapter.verify_action(request2)
            assert result2.success is False
            assert result2.reason == "target_not_found"
        finally:
            os.unlink(temp_path)


class TestE2EHumanReviewFlow:
    """E2E tests for human review workflow."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def test_review_disabled_auto_approves(self):
        """Test that disabled HITL auto-approves."""
        adapter = HumanReviewAdapter()
        request = ReviewRequest(
            request_id="REQ-001",
            agent_name="TestAgent",
            action_type="heal",
            target_file="/test.py",
            description="Test fix",
            risk_level="high",
        )

        result = adapter.submit_for_review(request)
        assert result.status == ReviewStatus.APPROVED
        assert result.reason == "hitl_disabled"

    def test_review_enabled_workflow(self):
        """Test complete review workflow when enabled."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        # Submit for review
        request = ReviewRequest(
            request_id="REQ-001",
            agent_name="TestAgent",
            action_type="heal",
            target_file="/test.py",
            description="Critical fix",
            risk_level="high",
        )
        result = adapter.submit_for_review(request)
        assert result.status == ReviewStatus.PENDING

        # Check pending reviews
        pending = adapter.get_pending_reviews()
        assert len(pending) == 1

        # Approve
        approval = adapter.approve("REQ-001", "admin@example.com", "Looks good")
        assert approval.status == ReviewStatus.APPROVED

        # Queue is now empty
        assert adapter.get_queue_depth() == 0


class TestE2EDomainAgentIntegration:
    """E2E tests for domain agent integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_rg_agent_inherits_all_capabilities(self):
        """Test that RG agent has all migration capabilities."""

        class TestRGAgent(RGDomainMixin):
            def __init__(self):
                super().__init__()

        agent = TestRGAgent()

        # Has domain methods
        assert hasattr(agent, "domain")
        assert agent.domain == "rg"
        assert agent.domain_prefix == "apps_rg"

        # Has feature-flagged methods
        assert hasattr(agent, "verify_action")
        assert hasattr(agent, "submit_for_review")
        assert hasattr(agent, "flagged_recall_or_execute")
        assert hasattr(agent, "log_audit_event")

        # Has RG-specific methods
        assert hasattr(agent, "store_resume_pattern")
        assert hasattr(agent, "get_rg_context")

    def test_lic_agent_inherits_all_capabilities(self):
        """Test that LIC agent has all migration capabilities."""

        class TestLICAgent(LICDomainMixin):
            def __init__(self):
                super().__init__()

        agent = TestLICAgent()

        # Has domain methods
        assert agent.domain == "lic"
        assert agent.domain_prefix == "apps_lic"

        # Has stricter thresholds
        assert agent._similarity_threshold == 0.92

        # Has LIC-specific methods
        assert hasattr(agent, "store_campaign_pattern")
        assert hasattr(agent, "get_lic_context")

    def test_domain_isolation_prevents_cross_contamination(self):
        """Test that domain isolation prevents cross-domain pattern usage."""

        class TestRGAgent(RGDomainMixin):
            def __init__(self):
                super().__init__()

        agent = TestRGAgent()

        # Same domain pattern allowed
        rg_pattern = {"_domain": "apps_rg", "data": "test"}
        assert agent.validate_domain_pattern(rg_pattern) is True

        # Different domain pattern rejected
        lic_pattern = {"_domain": "apps_lic", "data": "test"}
        assert agent.validate_domain_pattern(lic_pattern) is False


class TestE2EMigrationCompliance:
    """E2E tests for migration compliance checking."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_compliance_check_for_legacy_agent(self):
        """Test compliance check for legacy agent without mixin."""

        class LegacyAgent:
            def heal(self):
                pass

        result = check_agent_compliance(LegacyAgent)
        assert result.compliant is False
        assert result.has_feature_flag_mixin is False
        assert "FeatureFlaggedAgentMixin" in result.missing_components

    def test_compliance_check_for_migrated_agent(self):
        """Test compliance check for properly migrated agent."""

        class MigratedAgent(FeatureFlaggedAgentMixin):
            def __init__(self):
                super().__init__()

        result = check_agent_compliance(MigratedAgent)
        assert result.compliant is True
        assert result.has_feature_flag_mixin is True

    def test_migration_status_aggregation(self):
        """Test migration status aggregation across multiple agents."""

        class LegacyAgent1:
            pass

        class LegacyAgent2:
            pass

        class MigratedAgent(FeatureFlaggedAgentMixin):
            def __init__(self):
                super().__init__()

        agents = [LegacyAgent1, LegacyAgent2, MigratedAgent]
        status = MigrationHelper.get_migration_status(agents)

        assert status.total_agents == 3
        assert status.compliant_agents == 1
        assert status.non_compliant_agents == 2
        assert pytest.approx(status.compliance_percentage, rel=0.1) == 33.33


class TestE2ECompleteHealingWorkflow:
    """E2E tests for complete healing workflow with all safety checks."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_healing_workflow_all_disabled(self):
        """Test healing workflow when all flags disabled."""

        class TestAgent(DomainAgentMixin):
            def __init__(self):
                super().__init__(domain="test")

        agent = TestAgent()
        violation = {
            "file_path": "/test.py",
            "fix_type": "modify_function",
            "target": "test_func",
            "severity": "low",
            "message": "Test violation",
        }

        def heal_fn(v):
            return {
                "status": "success",
                "violations_found": 1,
                "violations_fixed": 1,
                "errors": [],
                "skipped": [],
            }

        result = agent.domain_heal_with_verification(violation, heal_fn)

        assert result["status"] == "success"
        assert result["_domain"] == "apps_test"

    def test_healing_workflow_verification_enabled(self):
        """Test healing workflow with verification enabled."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)

        class TestAgent(DomainAgentMixin):
            def __init__(self):
                super().__init__(domain="test")

        # Create a real file for verification
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def target_function():\n    pass\n")
            temp_path = f.name

        try:
            agent = TestAgent()
            violation = {
                "file_path": temp_path,
                "fix_type": "modify_function",
                "target": "target_function",
                "severity": "low",
                "message": "Test violation",
            }

            def heal_fn(v):
                return {
                    "status": "success",
                    "violations_found": 1,
                    "violations_fixed": 1,
                    "errors": [],
                    "skipped": [],
                }

            result = agent.domain_heal_with_verification(violation, heal_fn)
            # Should succeed because target exists
            assert result["status"] == "success"
        finally:
            os.unlink(temp_path)


class TestE2EConfigurationIntegration:
    """E2E tests for configuration integration."""

    def test_domain_config_matches_mixin_defaults(self):
        """Test that domain configs match mixin default values."""
        rg_config = get_domain_config("rg")

        class TestRGAgent(RGDomainMixin):
            def __init__(self):
                super().__init__()

        agent = TestRGAgent()

        assert rg_config.similarity_threshold == agent._similarity_threshold
        assert rg_config.ttl_seconds == agent._ttl_seconds

    def test_lic_config_stricter_than_rg(self):
        """Test that LIC config is stricter than RG config."""
        rg_config = get_domain_config("rg")
        lic_config = get_domain_config("lic")

        assert lic_config.similarity_threshold > rg_config.similarity_threshold
        assert lic_config.ttl_seconds > rg_config.ttl_seconds
        assert lic_config.rate_limit_requests < rg_config.rate_limit_requests
        assert "ENABLE_HITL_WORKFLOW" in lic_config.required_flags
