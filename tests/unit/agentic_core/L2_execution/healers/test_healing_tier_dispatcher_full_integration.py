"""Tests for healing_tier_dispatcher full meta-learning integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

#  # MOVED: from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
#  # MOVED: from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
    dispatch_healing,
)
#  # MOVED: from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
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

# REMOVED: _emit_authorize_and_execute("p2", "test_healing_tier_dispatcher_full_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_tier_dispatcher_full_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_tier_dispatcher_full_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_tier_dispatcher_full_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_tier_dispatcher_full_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_tier_dispatcher_full_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_tier_dispatcher_full_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_tier_dispatcher_full_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_tier_dispatcher_full_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_tier_dispatcher_full_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_tier_dispatcher_full_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_tier_dispatcher_full_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_tier_dispatcher_full_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_tier_dispatcher_full_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_tier_dispatcher_full_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_tier_dispatcher_full_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_tier_dispatcher_full_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_tier_dispatcher_full_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_tier_dispatcher_full_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_tier_dispatcher_full_integration", "exec_snapshot_link")
#  # MOVED: from system_learning.engines.default_healing_pattern_advisor import (
    DefaultHealingPatternAdvisor,
)
#  # MOVED: from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
#  # MOVED: from system_learning.ports.healing_pattern_advisor import (
    NullHealingPatternAdvisor,
)
#  # MOVED: from system_learning.ports.meta_outcome_bus_hook import (
    NullMetaOutcomeBusHook,
)
#  # MOVED: from system_learning.ports.meta_prior_provider import (
    NeutralMetaPriorProvider,
)
#  # MOVED: from system_learning.ports.outcome_write_back_hook import (
    DefaultOutcomeWriteBackHook,
    NullOutcomeWriteBackHook,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_tier_dispatcher_full_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_tier_dispatcher_full_integration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_tier_dispatcher_full_integration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_tier_dispatcher_full_integration", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_full_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_full_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_full_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_full_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_full_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_full_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_tier_dispatcher_full_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_tier_dispatcher_full_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_tier_dispatcher_full_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_tier_dispatcher_full_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_tier_dispatcher_full_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_tier_dispatcher_full_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_tier_dispatcher_full_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_tier_dispatcher_full_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_tier_dispatcher_full_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_tier_dispatcher_full_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_tier_dispatcher_full_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_tier_dispatcher_full_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_tier_dispatcher_full_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_full_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_full_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_full_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_full_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_full_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_tier_dispatcher_full_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_tier_dispatcher_full_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_tier_dispatcher_full_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_tier_dispatcher_full_integration", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_tier_dispatcher_full_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_tier_dispatcher_full_integration", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_full_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_full_integration", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_tier_dispatcher_full_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_tier_dispatcher_full_integration", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_tier_dispatcher_full_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_tier_dispatcher_full_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_tier_dispatcher_full_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_tier_dispatcher_full_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_tier_dispatcher_full_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_tier_dispatcher_full_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_tier_dispatcher_full_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_tier_dispatcher_full_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_tier_dispatcher_full_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_tier_dispatcher_full_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_tier_dispatcher_full_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_tier_dispatcher_full_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_tier_dispatcher_full_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_tier_dispatcher_full_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_tier_dispatcher_full_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_tier_dispatcher_full_integration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healing_tier_dispatcher_full_integration")
# REMOVED: emit_determinism_digest("p0", "test_healing_tier_dispatcher_full_integration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class MockMetaPriorProvider:
    """Mock provider with configurable priors."""

    def __init__(self, priors: dict[str, float]) -> None:
        self._priors = priors

    def get_prior(self, error_signature: str) -> float:
        return self._priors.get(error_signature, 0.50)


class MockHealingProviderInvoker:
    """Mock invoker that always succeeds."""

    def invoke_local(self, healing_input, decision, config, agent_name=""):
#  # MOVED: from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord

        return InvocationRecord(
            tier=decision.tier,
            method_called="invoke_local",
            model_id="",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
        )


def test_full_integration_all_phases() -> None:
    from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
    from agentic_core.L2_execution.healers.healing_tier_types import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from system_learning.engines.default_healing_pattern_advisor import (
    from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
    from system_learning.ports.healing_pattern_advisor import (
    from system_learning.ports.meta_outcome_bus_hook import (
    from system_learning.ports.meta_prior_provider import (
    from system_learning.ports.outcome_write_back_hook import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    """Full integration of all meta-learning phases."""
    # Phase 1: Meta prior provider
    meta_prior_provider = MockMetaPriorProvider({"test_sig": 0.90})

    # Phase 2: Outcome write-back hook
    store = HealingSuccessRateStore()
    outcome_write_back_hook = DefaultOutcomeWriteBackHook(store)

    # Phase 3: Pattern advisor
    mock_ml_client = MagicMock()
    mock_patterns = [
        {
            "pattern_id": "pattern_1",
            "pattern_name": "test_pattern",
            "confidence_boost": 0.08,
            "description": "Test pattern",
        },
    ]
    mock_ml_client.retrieve_healing_patterns.return_value = mock_patterns
    pattern_advisor = DefaultHealingPatternAdvisor(mock_ml_client)

    # Phase 4: Meta outcome bus hook (mock the hook directly to assert publish_outcome)
    mock_bus_hook = MagicMock()

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=meta_prior_provider,
        outcome_write_back_hook=outcome_write_back_hook,
        pattern_advisor=pattern_advisor,
        meta_outcome_bus_hook=mock_bus_hook,
    )

    # Phase 1: Should have used meta prior in routing
    assert decision.tier in HealingTier
    assert any("historical_success_rate=0.9000" in code for code in decision.reason_codes)

    # Phase 2: Should have recorded outcome in store
    assert store.get_counts().get("test_sig", 0) == 1

    # Phase 3: Should have queried ML client for patterns
    mock_ml_client.retrieve_healing_patterns.assert_called_once_with(error_signature="test_sig")

    # Phase 4: Should have published outcome to meta bus
    mock_bus_hook.publish_outcome.assert_called_once()

    # Should have successful invocation record
    assert record.tier == decision.tier


def test_full_integration_with_null_hooks() -> None:
"""Test full_integration_with_null_hooks runtime behavior."""
# Arrange
# TODO: Set up test data for full_integration_with_null_hooks
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute full_integration_with_null_hooks
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=NeutralMetaPriorProvider(),
        outcome_write_back_hook=NullOutcomeWriteBackHook(),
        pattern_advisor=NullHealingPatternAdvisor(),
        meta_outcome_bus_hook=NullMetaOutcomeBusHook(),
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_full_integration_hooks_fail_gracefully() -> None:
"""Test full_integration_hooks_fail_gracefully runtime behavior."""
# Arrange
# TODO: Set up test data for full_integration_hooks_fail_gracefully
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute full_integration_hooks_fail_gracefully
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    with patch("system_learning.engines.default_healing_pattern_advisor.logger"):
        with patch("system_learning.ports.meta_outcome_bus_hook.logger"):
            decision, record = dispatch_healing(
                healing_input,
                config,
                invoker=invoker,
                agent_name="test-agent",
                timestamp_utc=1234567890,
                outcome_write_back_hook=failing_outcome_hook,
                pattern_advisor=failing_pattern_advisor,
                meta_outcome_bus_hook=failing_bus_hook,
            )

    # Should still succeed despite hook failures
    assert decision.tier in HealingTier
    assert record.tier == decision.tier

    # All hooks should have been called
    failing_outcome_hook.on_outcome.assert_called_once()
    failing_pattern_advisor.advise.assert_called_once()
    failing_bus_hook.publish_outcome.assert_called_once()


def test_full_integration_invocation_failure() -> None:
"""Test full_integration_invocation_failure runtime behavior."""
# Arrange
# TODO: Set up error condition
error_input = {}  # Replace with actual error condition

# Act & Assert
# TODO: Test error handling in full_integration_invocation_failure
with pytest.raises(Exception):  # Replace with expected exception
    # Execute operation that should raise error
    pass  # Replace with actual error test

# TODO: Add error message and handling assertions

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should raise invocation exception
    with pytest.raises(Exception, match="Invocation failed"):
        dispatch_healing(
            healing_input,
            config,
            invoker=invoker,
            agent_name="test-agent",
            timestamp_utc=1234567890,
            outcome_write_back_hook=outcome_hook,
            meta_outcome_bus_hook=mock_bus_hook,
        )

    # Hooks should still have been called with failure info
    assert store.get_counts().get("test_sig", 0) == 1
    mock_bus_hook.publish_outcome.assert_called_once()


def test_full_integration_backward_compatibility() -> None:
"""Test full_integration_backward_compatibility runtime behavior."""
# Arrange
# TODO: Set up test data for full_integration_backward_compatibility
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute full_integration_backward_compatibility
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
    # Should work with all hooks as None
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=None,
        outcome_write_back_hook=None,
        pattern_advisor=None,
        meta_outcome_bus_hook=None,
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_full_integration_phase_order() -> None:
"""Test full_integration_phase_order runtime behavior."""
# Arrange
# TODO: Set up test data for full_integration_phase_order
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute full_integration_phase_order
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
    pattern_advisor.advise = MagicMock(
        return_value={
            "pattern_match": False,
            "pattern_name": None,
            "pattern_boost": 0.0,
            "extra_reason_codes": (),
        }
    )
    pattern_advisor.advise = track_call("pattern")

    bus_hook = MagicMock()
    bus_hook.publish_outcome = track_call("bus")

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        outcome_write_back_hook=outcome_hook,
        pattern_advisor=pattern_advisor,
        meta_outcome_bus_hook=bus_hook,
    )

    # Should be called in order: outcome -> pattern -> bus
    assert call_order == ["outcome", "pattern", "bus"]
