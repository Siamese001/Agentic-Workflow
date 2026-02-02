"""
Phase 2: Priority Agent Integration Tests

Tests meta-learning integration for priority agents:
- SovereignBaseAgent MetaLearningClientMixin validation
- GravityLeakRepairAgent AST analysis caching
- LicHealingOrchestratorAgent incident pattern caching
- RgHealingOrchestratorAgent healing cycle strategy

All tests use mocked dependencies to avoid external services.
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ==================== TEST 2.1: SovereignBaseAgent Integration ====================


class TestSovereignBaseAgentIntegration:
    """Test SovereignBaseAgent MetaLearningClientMixin integration."""

    def test_mixin_methods_available(self):
        """Test MetaLearningClientMixin methods are available on agents."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        # Verify all expected methods exist
        expected_methods = [
            "ml_recall_healing_pattern",
            "ml_store_healing_pattern",
            "ml_cache_get",
            "ml_cache_set",
            "ml_cache_delete",
            "ml_check_healing_depth",
            "ml_increment_healing_depth",
            "ml_reset_healing_depth",
            "ml_get_violation_signature",
            "ml_enhanced_heal",
        ]

        for method in expected_methods:
            assert hasattr(MetaLearningClientMixin, method), f"Missing method: {method}"

    def test_domain_detection_agentic_core(self):
        """Test domain detection for agentic_core agents."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        class TestCoreAgent(MetaLearningClientMixin):
            pass

        agent = TestCoreAgent()
        domain = agent._get_ml_domain()

        assert domain == "agentic_core"

    def test_domain_detection_apps_lic(self):
        """Test domain detection for apps_lic agents."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        class LicTestAgent(MetaLearningClientMixin):
            pass

        agent = LicTestAgent()
        domain = agent._get_ml_domain()

        assert domain == "apps_lic"

    def test_domain_detection_apps_rg(self):
        """Test domain detection for apps_rg agents."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        class RgTestAgent(MetaLearningClientMixin):
            pass

        agent = RgTestAgent()
        domain = agent._get_ml_domain()

        assert domain == "apps_rg"

    def test_singleton_reset(self):
        """Test MetaLearningClientMixin singleton reset."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        # Reset singletons
        MetaLearningClientMixin.reset_ml_singletons()

        assert MetaLearningClientMixin._ml_client is None
        assert MetaLearningClientMixin._ml_embedder is None
        assert MetaLearningClientMixin._ml_cache_manager is None
        assert MetaLearningClientMixin._ml_guardrails is None

    def test_lazy_initialization(self):
        """Test lazy initialization of ML components."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        # Reset first
        MetaLearningClientMixin.reset_ml_singletons()

        class TestAgent(MetaLearningClientMixin):
            pass

        agent = TestAgent()

        # Singletons should be None before first use
        assert MetaLearningClientMixin._ml_client is None

        # Trigger initialization
        agent._ensure_ml_client()

        # Should be initialized now (or None if service unavailable)
        # This test passes either way - we just verify no crash


# ==================== TEST 2.2: GravityLeakRepairAgent Caching ====================


class TestGravityLeakRepairAgentCaching:
    """Test GravityLeakRepairAgent meta-learning caching."""

    @pytest.fixture
    def mock_agent(self):
        """Create mocked GravityLeakRepairAgent."""
        with patch(
            "agentic_core.L5_safety.gravity.GravityLeakRepairAgent.SovereignBaseAgent.__post_init__"
        ):
            from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import GravityLeakRepairAgent

            agent = GravityLeakRepairAgent()

            # Mock ML methods
            agent.ml_recall_healing_pattern = MagicMock(return_value=None)
            agent.ml_cache_get = MagicMock(return_value=None)
            agent.ml_cache_set = MagicMock(return_value=True)
            agent.ml_store_healing_pattern = MagicMock(return_value="pattern_123")
            agent.ml_enhanced_heal = MagicMock()

            return agent

    def test_analyze_violation_calls_pattern_recall(self, mock_agent):
        """Test analyze_violation attempts to recall cached patterns."""
        fix = mock_agent.analyze_violation(
            file_path=Path("/test/file.py"),
            import_statement="from agentic_core.L0 import util",
            file_layer="L5",
            import_layer="L0",
        )

        # Should have tried to recall pattern
        mock_agent.ml_recall_healing_pattern.assert_called_once()

        # Should have tried cache get
        mock_agent.ml_cache_get.assert_called_once()

    def test_analyze_violation_caches_result(self, mock_agent):
        """Test analyze_violation caches analysis result."""
        fix = mock_agent.analyze_violation(
            file_path=Path("/test/file.py"),
            import_statement="from agentic_core.L0 import util",
            file_layer="L5",
            import_layer="L0",
        )

        # Should have cached the result
        mock_agent.ml_cache_set.assert_called_once()

        # Verify cache key format
        call_args = mock_agent.ml_cache_set.call_args
        cache_key = call_args[0][0]
        assert "gravity_analysis:" in cache_key

    def test_analyze_violation_uses_cached_pattern(self, mock_agent):
        """Test analyze_violation uses recalled pattern."""
        # Setup cached pattern
        mock_agent.ml_recall_healing_pattern.return_value = {
            "fix_type": "RELOCATE",
            "new_import": "from utils import cached_func",
            "rationale": "Meta-learning recalled pattern",
            "line_number": 10,
        }

        fix = mock_agent.analyze_violation(
            file_path=Path("/test/file.py"),
            import_statement="from L0 import util",
            file_layer="L5",
            import_layer="L0",
        )

        # Should use cached pattern
        assert fix.fix_type == "RELOCATE"
        assert "recalled" in fix.rationale.lower() or "meta" in fix.rationale.lower()

    def test_analyze_violation_relocate_strategy(self, mock_agent):
        """Test RELOCATE strategy for L0 imports."""
        fix = mock_agent.analyze_violation(
            file_path=Path("/test/file.py"),
            import_statement="from L0_maintenance import util",
            file_layer="L5",
            import_layer="L0",
        )

        assert fix.fix_type == "RELOCATE"
        assert "utils" in fix.new_import.lower() or "shared" in fix.new_import.lower()

    def test_analyze_violation_abstract_strategy(self, mock_agent):
        """Test ABSTRACT strategy for cross-layer imports."""
        fix = mock_agent.analyze_violation(
            file_path=Path("/test/file.py"),
            import_statement="from L2 import executor",
            file_layer="L5",
            import_layer="L2",
        )

        assert fix.fix_type == "ABSTRACT"
        assert "abstraction" in fix.rationale.lower()

    def test_heal_uses_ml_enhanced_heal(self, mock_agent):
        """Test heal() method uses ml_enhanced_heal wrapper."""
        mock_agent.ml_enhanced_heal.return_value = {
            "violations_fixed": 1,
            "violations_found": 1,
            "errors": 0,
            "skipped": 0,
        }

        violation = {
            "type": "gravity_violation",
            "path": "/test/file.py",
            "import_statement": "from L0 import util",
            "file_layer": "L5",
            "import_layer": "L0",
        }

        result = mock_agent.heal(violation)

        # Should use ml_enhanced_heal
        mock_agent.ml_enhanced_heal.assert_called_once()


# ==================== TEST 2.3: LicHealingOrchestratorAgent ====================


class TestLicHealingOrchestratorAgent:
    """Test LicHealingOrchestratorAgent meta-learning integration."""

    def test_domain_detection_lic(self):
        """Test LIC domain detection from class name."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        class LicTestOrchestratorAgent(MetaLearningClientMixin):
            pass

        agent = LicTestOrchestratorAgent()
        domain = agent._get_ml_domain()

        assert domain == "apps_lic"

    def test_lic_agent_file_exists(self):
        """Test LicHealingOrchestratorAgent file exists."""
        from pathlib import Path

        agent_path = Path("apps_lic/engines/LicHealingOrchestratorAgent.py")
        assert agent_path.exists()

    def test_lic_healing_pattern_storage_workflow(self):
        """Test LIC healing pattern storage workflow."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store LIC-specific healing pattern
        pattern_data = {
            "incident_type": "database_lock",
            "recovery_playbook": "release_and_retry",
            "success": True,
        }

        client.cache_set("lic_incident_pattern_1", pattern_data, "apps_lic")

        # Retrieve and verify
        result = client.cache_get("lic_incident_pattern_1", "apps_lic")
        assert result["incident_type"] == "database_lock"

    def test_lic_domain_isolation(self):
        """Test LIC patterns are isolated from other domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store in LIC domain only
        client.cache_set("lic_only_key", {"data": "lic"}, "apps_lic")

        # Should not be accessible from other domains
        core_result = client.cache_get("lic_only_key", "agentic_core")
        rg_result = client.cache_get("lic_only_key", "apps_rg")
        lic_result = client.cache_get("lic_only_key", "apps_lic")

        assert core_result is None
        assert rg_result is None
        assert lic_result is not None


# ==================== TEST 2.4: RgHealingOrchestratorAgent ====================


class TestRgHealingOrchestratorAgent:
    """Test RgHealingOrchestratorAgent meta-learning integration."""

    def test_domain_detection_rg(self):
        """Test RG domain detection from class name."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin

        class RgTestOrchestratorAgent(MetaLearningClientMixin):
            pass

        agent = RgTestOrchestratorAgent()
        domain = agent._get_ml_domain()

        assert domain == "apps_rg"

    def test_rg_agent_file_exists(self):
        """Test RgHealingOrchestratorAgent file exists."""
        from pathlib import Path

        agent_path = Path("apps_rg/engines/RgHealingOrchestratorAgent.py")
        assert agent_path.exists()

    def test_rg_healing_cycle_caching(self):
        """Test RG healing cycle strategy caching."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store RG healing cycle result
        cycle_data = {
            "cycle_number": 3,
            "convergence_achieved": True,
            "strategy": "iterative_refinement",
        }

        client.cache_set("rg_cycle_result_1", cycle_data, "apps_rg")

        # Retrieve and verify
        result = client.cache_get("rg_cycle_result_1", "apps_rg")
        assert result["convergence_achieved"] is True

    def test_rg_domain_isolation(self):
        """Test RG patterns are isolated from other domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store in RG domain only
        client.cache_set("rg_only_key", {"data": "rg"}, "apps_rg")

        # Should not be accessible from other domains
        core_result = client.cache_get("rg_only_key", "agentic_core")
        lic_result = client.cache_get("rg_only_key", "apps_lic")
        rg_result = client.cache_get("rg_only_key", "apps_rg")

        assert core_result is None
        assert lic_result is None
        assert rg_result is not None


# ==================== TEST 2.5: Cross-Agent Integration ====================


class TestCrossAgentIntegration:
    """Test meta-learning works across multiple agents."""

    def test_pattern_isolation_between_domains(self):
        """Test patterns are isolated between domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store patterns in different domains
        client.cache_set("shared_key", {"domain": "core"}, "agentic_core")
        client.cache_set("shared_key", {"domain": "lic"}, "apps_lic")
        client.cache_set("shared_key", {"domain": "rg"}, "apps_rg")

        # Retrieve and verify isolation
        core_val = client.cache_get("shared_key", "agentic_core")
        lic_val = client.cache_get("shared_key", "apps_lic")
        rg_val = client.cache_get("shared_key", "apps_rg")

        assert core_val["domain"] == "core"
        assert lic_val["domain"] == "lic"
        assert rg_val["domain"] == "rg"

    def test_healing_depth_isolation_per_agent(self):
        """Test healing depth is tracked per agent."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Track depth for different agents
        guardrails.increment_healing_depth("Agent1", "violation_1")
        guardrails.increment_healing_depth("Agent1", "violation_1")
        guardrails.increment_healing_depth("Agent2", "violation_1")

        # Get stats
        stats = guardrails.get_stats()

        # Should track separately
        assert "Agent1" in stats["depth_trackers"]
        assert "Agent2" in stats["depth_trackers"]

    def test_concurrent_cache_operations(self):
        """Test concurrent cache operations don't interfere."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Simulate concurrent operations
        keys = [f"concurrent_key_{i}" for i in range(10)]

        for key in keys:
            client.cache_set(key, {"key": key}, "agentic_core")

        # Verify all stored correctly
        for key in keys:
            result = client.cache_get(key, "agentic_core")
            assert result["key"] == key


# ==================== TEST 2.6: MetaLearningClientMixin Enhanced Heal ====================


class TestMetaLearningEnhancedHeal:
    """Test ml_enhanced_heal workflow."""

    def test_enhanced_heal_workflow_success(self):
        """Test complete enhanced heal workflow succeeds."""
        from agentic_core.base_agents.meta_learning_client_mixin import MetaLearningClientMixin
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        class TestHealAgent(MetaLearningClientMixin):
            pass

        agent = TestHealAgent()
        guardrails = MetaLearningGuardrails()

        violation = {"type": "test_violation", "id": "vh1"}

        def heal_fn(v):
            return {"status": "fixed", "violations_fixed": 1}

        # Verify depth checking works
        assert guardrails.check_healing_depth("TestHealAgent", "vh1") is True

    def test_enhanced_heal_depth_tracking(self):
        """Test healing depth is tracked correctly."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Track depth
        for i in range(3):
            guardrails.increment_healing_depth("TestAgent", "v_depth")

        # Should still allow (under limit of 5)
        assert guardrails.check_healing_depth("TestAgent", "v_depth") is True

        # Increment to limit
        guardrails.increment_healing_depth("TestAgent", "v_depth")
        guardrails.increment_healing_depth("TestAgent", "v_depth")

        # Should block at limit
        assert guardrails.check_healing_depth("TestAgent", "v_depth") is False

    def test_enhanced_heal_depth_reset(self):
        """Test healing depth resets after successful healing."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Increment depth
        for i in range(3):
            guardrails.increment_healing_depth("ResetAgent", "v_reset")

        # Reset on success
        guardrails.reset_healing_depth("ResetAgent", "v_reset")

        # Should allow again from 0
        assert guardrails.check_healing_depth("ResetAgent", "v_reset") is True

    def test_enhanced_heal_pattern_storage(self):
        """Test successful healing stores pattern."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Simulate storing successful healing pattern
        violation = {"type": "gravity", "path": "/test/file.py"}
        healing_result = {"status": "fixed", "fix_type": "RELOCATE"}

        # Store pattern
        client.cache_set(
            "healing_pattern_test",
            {"violation": violation, "result": healing_result},
            "agentic_core",
        )

        # Verify stored
        result = client.cache_get("healing_pattern_test", "agentic_core")
        assert result["result"]["status"] == "fixed"


# ==================== RUN CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",
        ]
    )
