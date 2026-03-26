"""
Unit Tests for LocationHealerAgent Facade - Phase 3

Tests the facade conversion of LocationHealerAgent including:
- Legacy signature compatibility
- LocationHealingStrategy functionality
- Healing preservation
- Return type consistency
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

#  # MOVED: from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
    HealingResult,
    LocationHealingStrategy,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_location_healer_facade")
# REMOVED: _emit_applies_guardrail("p0", "test_location_healer_facade", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_location_healer_facade", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_location_healer_facade", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_location_healer_facade", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_location_healer_facade", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_location_healer_facade", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_location_healer_facade", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_location_healer_facade", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_location_healer_facade", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_location_healer_facade", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_location_healer_facade", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_location_healer_facade", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_location_healer_facade", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_location_healer_facade", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_location_healer_facade", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_location_healer_facade", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_location_healer_facade", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_location_healer_facade", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_location_healer_facade", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_location_healer_facade", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_location_healer_facade", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_location_healer_facade", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_location_healer_facade", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_location_healer_facade", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_location_healer_facade", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_location_healer_facade", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_location_healer_facade", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_location_healer_facade", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_location_healer_facade", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_location_healer_facade", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_location_healer_facade", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_location_healer_facade", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_location_healer_facade", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_location_healer_facade", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_location_healer_facade", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_location_healer_facade", "write_through")
# REMOVED: _emit_writes_through("p1", "test_location_healer_facade", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_location_healer_facade", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_location_healer_facade", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_location_healer_facade", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_location_healer_facade", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_location_healer_facade", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_location_healer_facade", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_location_healer_facade", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_location_healer_facade", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_location_healer_facade", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_location_healer_facade", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_location_healer_facade", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_location_healer_facade", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_location_healer_facade", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_location_healer_facade", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_location_healer_facade")
# REMOVED: _emit_gated_by_confidence("p1", "test_location_healer_facade", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_location_healer_facade")
# REMOVED: emit_determinism_digest("p0", "test_location_healer_facade")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_location_healer_facade", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_location_healer_facade", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_location_healer_facade", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_location_healer_facade", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_location_healer_facade", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_location_healer_facade", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_location_healer_facade", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_location_healer_facade", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_location_healer_facade", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_location_healer_facade", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_location_healer_facade", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_location_healer_facade", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_location_healer_facade", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_location_healer_facade", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_location_healer_facade", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_location_healer_facade", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_location_healer_facade", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_location_healer_facade", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_location_healer_facade", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_location_healer_facade", "exec_snapshot_link")


class TestLocationHealingStrategy:
    """Tests for LocationHealingStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "project_root": "/test/project",
            "backup_enabled": True,
            "auto_fix_imports": True,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create LocationHealingStrategy instance."""
        return LocationHealingStrategy(config)

    def test_initialization(self, strategy, config):
                from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L3_orchestration.reasoning.UnifiedAgent import LocationHealingStrategy
                from agentic_core.L3_orchestration.reasoning.UnifiedAgent import __all__
                from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
                """Test strategy initialization."""
                assert strategy.project_root == "/test/project"
                assert strategy.backup_enabled is True
                assert strategy.auto_fix_imports is True

        assert strategy.auto_fix_imports is True

    def test_initialization_with_disabled_features(self):
        """Test strategy initialization with disabled features."""
        config = {
            "project_root": "/other/project",
            "backup_enabled": False,
            "auto_fix_imports": False,
        }
        strategy = LocationHealingStrategy(config)

        assert strategy.project_root == "/other/project"
        assert strategy.backup_enabled is False
        assert strategy.auto_fix_imports is False

    @pytest.mark.asyncio
    async def test_execute_returns_healing_result(self, strategy):
        """Test execute returns HealingResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, HealingResult)
        assert result.violations_found >= 0
        assert result.violations_fixed >= 0

    @pytest.mark.asyncio
    async def test_execute_with_violation(self, strategy):
        """Test execute with violation parameter."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.heal = Mock(return_value={"status": "success", "artifacts": []})

        result = await strategy.execute(mock_agent, violation={"type": "DEPTH", "file": "/test/file.py"})

        assert isinstance(result, HealingResult)

    def test_heal_repository_returns_dict(self, strategy):
        """Test heal_repository returns proper dict structure."""
        mock_agent = Mock()
        mock_agent.heal_repository = Mock(return_value={"violations_found": 0, "violations_fixed": 0})

        result = strategy.heal_repository(mock_agent, dry_run=True, execute=False)

        assert isinstance(result, dict)


class TestLocationHealerAgentFacade:
    """Tests for LocationHealerAgent facade."""

    def test_class_exists(self):
        """Test LocationHealerAgent class exists."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert LocationHealerAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
#  # MOVED: from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert issubclass(LocationHealerAgent, SovereignBaseAgent)

    def test_is_dataclass(self):
        """Test LocationHealerAgent is a dataclass."""
        from dataclasses import is_dataclass

#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert is_dataclass(LocationHealerAgent)

    def test_has_project_root_field(self):
        """Test LocationHealerAgent has project_root field."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        # Check field exists in annotations
        assert "project_root" in LocationHealerAgent.__dataclass_fields__


class TestLocationHealerMethods:
    """Tests for LocationHealerAgent methods existence."""

    def test_heal_method_signature(self):
        """Test heal method exists with correct signature."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "heal")
        assert callable(LocationHealerAgent.heal)

    def test_heal_repository_method_signature(self):
        """Test heal_repository method exists."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "heal_repository")
        assert callable(LocationHealerAgent.heal_repository)

    def test_safe_move_method_exists(self):
        """Test safe_move method exists."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "safe_move")
        assert callable(LocationHealerAgent.safe_move)

    def test_safe_delete_method_exists(self):
        """Test safe_delete method exists."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "safe_delete")
        assert callable(LocationHealerAgent.safe_delete)

    def test_post_heal_validation_method_exists(self):
        """Test post_heal_validation method exists."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "post_heal_validation")
        assert callable(LocationHealerAgent.post_heal_validation)

    def test_fix_imports_after_move_method_exists(self):
        """Test fix_imports_after_move method exists."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert hasattr(LocationHealerAgent, "fix_imports_after_move")
        assert callable(LocationHealerAgent.fix_imports_after_move)


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        assert LocationHealerAgent is not None

    def test_docstring_updated(self):
        """Test docstring mentions facade pattern."""
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
            LocationHealerAgent,
        )

        docstring = LocationHealerAgent.__doc__
        assert "FACADE" in docstring or "facade" in docstring.lower()

    def test_unified_strategy_import(self):
        """Test LocationHealingStrategy can be imported."""
#  # MOVED: from agentic_core.L3_orchestration.reasoning.UnifiedAgent import LocationHealingStrategy

        assert LocationHealingStrategy is not None


class TestStrategyIntegration:
    """Tests for strategy integration."""

    def test_strategy_in_UnifiedAgent_exports(self):
        """Test LocationHealingStrategy is in UnifiedAgent exports."""
#  # MOVED: from agentic_core.L3_orchestration.reasoning.UnifiedAgent import __all__

        assert "LocationHealingStrategy" in __all__

    def test_strategy_inherits_from_healing_strategy(self):
        """Test LocationHealingStrategy inherits from HealingStrategy."""
#  # MOVED: from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
            HealingStrategy,
            LocationHealingStrategy,
        )

        assert issubclass(LocationHealingStrategy, HealingStrategy)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
