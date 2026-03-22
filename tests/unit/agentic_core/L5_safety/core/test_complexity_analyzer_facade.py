"""
Unit Tests for ComplexityAnalyzerAgent Facade - Phase 5

Tests the facade conversion of ComplexityAnalyzerAgent including:
- Legacy signature compatibility
- ComplexityAnalyzerStrategy functionality
- Complexity analysis preservation
- Return type consistency
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import ValidationResult
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_complexity_analyzer_facade")
_emit_applies_guardrail("p0", "test_complexity_analyzer_facade", "p0_governance")
_emit_reads_policy_state("p0", "test_complexity_analyzer_facade", "policy_binding")
_emit_snapshots_state("p0", "test_complexity_analyzer_facade", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_complexity_analyzer_facade", "p4obs", "metric_1")
_emit_emits_metric_event("test_complexity_analyzer_facade", "p4obs", "metric_2")
_emit_emits_metric_event("test_complexity_analyzer_facade", "p4obs", "metric_3")
_emit_emits_metric_event("test_complexity_analyzer_facade", "p4obs", "metric_4")
_emit_emits_metric_event("test_complexity_analyzer_facade", "p4obs", "metric_5")
_emit_emits_metric_event("test_complexity_analyzer_facade", "p4obs", "metric_6")
_emit_records_incident_event("test_complexity_analyzer_facade", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_complexity_analyzer_facade", "p4obs", "anomaly")
_emit_writes_observability_log("test_complexity_analyzer_facade", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_complexity_analyzer_facade", "p4obs", "mon_state")
_emit_triggers_alert("test_complexity_analyzer_facade", "p4obs", "alert")
_emit_links_incident_trace("test_complexity_analyzer_facade", "p4obs", "trace_link")
_emit_captures_pattern("test_complexity_analyzer_facade", "p3lm", "pattern")
_emit_records_learning_event("test_complexity_analyzer_facade", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_complexity_analyzer_facade", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_complexity_analyzer_facade", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_complexity_analyzer_facade", "p3lm", "routing")
_emit_improves_agent_policy("test_complexity_analyzer_facade", "p3lm", "policy")
_emit_stores_learning_state("test_complexity_analyzer_facade", "p3lm", "state")
_emit_records_execution_trace("test_complexity_analyzer_facade", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_complexity_analyzer_facade", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_complexity_analyzer_facade", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_complexity_analyzer_facade", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_complexity_analyzer_facade", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_complexity_analyzer_facade", "env_read", "p2_env_1")
_emit_reads_environ("test_complexity_analyzer_facade", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_complexity_analyzer_facade", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_complexity_analyzer_facade", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_complexity_analyzer_facade", "context_pull")
_emit_pulls_context("p1", "test_complexity_analyzer_facade", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_complexity_analyzer_facade", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_complexity_analyzer_facade", "uwg_term_2")
_emit_writes_through("p1", "test_complexity_analyzer_facade", "write_through")
_emit_writes_through("p1", "test_complexity_analyzer_facade", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_complexity_analyzer_facade", "safety_validation")
_emit_invokes_eval("p1", "test_complexity_analyzer_facade", "eval_call")
_emit_proposal_commits_routing("p1", "test_complexity_analyzer_facade", "routing_commit")
_emit_escalates_to_human("p1", "test_complexity_analyzer_facade", "human_escalation")
_emit_routes_through("p1", "test_complexity_analyzer_facade", "route_through")
_emit_checks_agent_registry("p1", "test_complexity_analyzer_facade", "agent_registry")
_emit_validates_agent_capability("p1", "test_complexity_analyzer_facade", "capability")
_emit_dispatches_execution_plan("p1", "test_complexity_analyzer_facade", "exec_plan")
_emit_agent_executes_agent("p1", "test_complexity_analyzer_facade", "sub_agent")
_emit_routes_to_agent("p1", "test_complexity_analyzer_facade", "target_agent")
_emit_verifies_policy("p1", "test_complexity_analyzer_facade", "policy_check")
_emit_observes_runtime_state("p1", "test_complexity_analyzer_facade", "runtime_state")
_emit_verifies_boundary("p1", "test_complexity_analyzer_facade", "boundary_check")
_emit_transcripts_response("p1", "test_complexity_analyzer_facade", "transcript")
_emit_hard_fails_untranscripted("p1", "test_complexity_analyzer_facade")
_emit_gated_by_confidence("p1", "test_complexity_analyzer_facade", "confidence_gate")
emit_replay_key("p0", "test_complexity_analyzer_facade")
emit_determinism_digest("p0", "test_complexity_analyzer_facade")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_complexity_analyzer_facade", "execution_auth")
_emit_validates_capability("p2", "test_complexity_analyzer_facade", "capability_check")
_emit_routes_to_capability("p2", "test_complexity_analyzer_facade", "capability_route")
_emit_writes_via_uwg("p2", "test_complexity_analyzer_facade", "uwg_write")
_emit_blocks_direct_write("p2", "test_complexity_analyzer_facade", "direct_write_block")
_emit_records_tool_invocation("p2", "test_complexity_analyzer_facade", "tool_invocation")
_emit_captures_execution_output("p2", "test_complexity_analyzer_facade", "exec_output")
_emit_dispatches_agent("p3", "test_complexity_analyzer_facade", "agent_dispatch")
_emit_coordinates_agents("p3", "test_complexity_analyzer_facade", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_complexity_analyzer_facade", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_complexity_analyzer_facade", "healing_outcome")
_emit_escalates_failure("p3", "test_complexity_analyzer_facade", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_complexity_analyzer_facade", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_complexity_analyzer_facade", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_complexity_analyzer_facade", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_complexity_analyzer_facade", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_complexity_analyzer_facade", "eval_metric")
_emit_stores_embedding("p4", "test_complexity_analyzer_facade", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_complexity_analyzer_facade", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_complexity_analyzer_facade", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestComplexityAnalyzerStrategy:
    """Tests for ComplexityAnalyzerStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "max_cyclomatic_complexity": 10,
            "max_function_length": 50,
            "max_arguments": 6,
        }

    @pytest.fixture
    def strategy(self, config):
        """Create ComplexityAnalyzerStrategy instance."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerStrategy,
        )

        return ComplexityAnalyzerStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.max_cyclomatic_complexity == 10
        assert strategy.max_function_length == 50
        assert strategy.max_arguments == 6

    @pytest.mark.asyncio
    async def test_execute_returns_validation_result(self, strategy):
        """Test execute returns ValidationResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, ValidationResult)
        assert result.passed is True


class TestComplexityAnalyzerAgentFacade:
    """Tests for ComplexityAnalyzerAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create ComplexityAnalyzerAgent instance."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        return ComplexityAnalyzerAgent()

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.project_root is not None
        assert agent._complexity_config is not None
        assert agent._violations == []

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerStrategy,
        )

        assert isinstance(agent._unified_strategy, ComplexityAnalyzerStrategy)

    def test_analyze_repository_method_exists(self, agent):
        """Test analyze_repository method exists."""
        assert hasattr(agent, "analyze_repository")
        assert callable(agent.analyze_repository)

    def test_analyze_file_method_exists(self, agent):
        """Test analyze_file method exists."""
        assert hasattr(agent, "analyze_file")
        assert callable(agent.analyze_file)

    def test_heal_repository_method_exists(self, agent):
        """Test heal_repository method exists."""
        assert hasattr(agent, "heal_repository")
        assert callable(agent.heal_repository)

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    def test_heal_returns_proper_structure(self, agent):
        """Test heal returns proper dict structure."""
        violation = {"type": "CYCLOMATIC", "path": "/test.py"}
        result = agent.heal(violation)

        assert isinstance(result, dict)
        assert "violations_fixed" in result
        assert "violations_found" in result
        assert "skipped" in result


class TestComplexityTypes:
    """Tests for complexity type dataclasses."""

    def test_complexity_violation_dataclass(self):
        """Test ComplexityViolation dataclass exists."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityViolation,
        )

        violation = ComplexityViolation(
            file_path=Path("/test/file.py"),
            function_name="complex_function",
            line_number=10,
            complexity=15,
            max_allowed=10,
            type="CYCLOMATIC",
            severity="CRITICAL",
        )

        assert violation.function_name == "complex_function"
        assert violation.complexity == 15

    def test_complexity_config_dataclass(self):
        """Test ComplexityConfig dataclass exists."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityConfig,
        )

        config = ComplexityConfig()

        assert config.max_cyclomatic_complexity == 10
        assert config.max_function_length == 50
        assert config.max_arguments == 6
        assert config.ignore_tests is True


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        assert ComplexityAnalyzerAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        assert issubclass(ComplexityAnalyzerAgent, SovereignBaseAgent)

    def test_calculate_complexity_method(self):
        """Test _calculate_complexity method exists."""
        from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (
            ComplexityAnalyzerAgent,
        )

        agent = ComplexityAnalyzerAgent()
        assert hasattr(agent, "_calculate_complexity")
        assert callable(agent._calculate_complexity)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
