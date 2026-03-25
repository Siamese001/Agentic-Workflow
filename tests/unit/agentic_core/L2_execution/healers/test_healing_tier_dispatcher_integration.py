"""Tests for healing_tier_dispatcher Phase 2 integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
    dispatch_healing,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_healing_tier_dispatcher_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_tier_dispatcher_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_tier_dispatcher_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_tier_dispatcher_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_tier_dispatcher_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_tier_dispatcher_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_tier_dispatcher_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_tier_dispatcher_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_tier_dispatcher_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_tier_dispatcher_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_tier_dispatcher_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_tier_dispatcher_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_tier_dispatcher_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_tier_dispatcher_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_tier_dispatcher_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_tier_dispatcher_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_tier_dispatcher_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_tier_dispatcher_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_tier_dispatcher_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_tier_dispatcher_integration", "exec_snapshot_link")
from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
from system_learning.ports.meta_prior_provider import (
    NeutralMetaPriorProvider,
)
from system_learning.ports.outcome_write_back_hook import (
    DefaultOutcomeWriteBackHook,
    NullOutcomeWriteBackHook,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_tier_dispatcher_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_tier_dispatcher_integration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_tier_dispatcher_integration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_tier_dispatcher_integration", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_tier_dispatcher_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_tier_dispatcher_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_tier_dispatcher_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_tier_dispatcher_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_tier_dispatcher_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_tier_dispatcher_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_tier_dispatcher_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_tier_dispatcher_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_tier_dispatcher_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_tier_dispatcher_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_tier_dispatcher_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_tier_dispatcher_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_tier_dispatcher_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_tier_dispatcher_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_tier_dispatcher_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_tier_dispatcher_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_tier_dispatcher_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_tier_dispatcher_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_tier_dispatcher_integration", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_tier_dispatcher_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_tier_dispatcher_integration", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_integration", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_tier_dispatcher_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_tier_dispatcher_integration", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_tier_dispatcher_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_tier_dispatcher_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_tier_dispatcher_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_tier_dispatcher_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_tier_dispatcher_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_tier_dispatcher_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_tier_dispatcher_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_tier_dispatcher_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_tier_dispatcher_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_tier_dispatcher_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_tier_dispatcher_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_tier_dispatcher_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_tier_dispatcher_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_tier_dispatcher_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_tier_dispatcher_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_tier_dispatcher_integration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_healing_tier_dispatcher_integration")
# REMOVED: emit_determinism_digest("p0", "test_healing_tier_dispatcher_integration")
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
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord

        return InvocationRecord(
            tier=decision.tier,
            method_called="invoke_local",
            model_id="",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
        )


def test_dispatch_healing_phase2_integration() -> None:
"""Test dispatch_healing_phase2_integration runtime behavior."""
# Arrange
# TODO: Set up test data for dispatch_healing_phase2_integration
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute dispatch_healing_phase2_integration
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
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
    )

    # Should have used meta prior in routing
    assert decision.tier in HealingTier
    assert any("historical_success_rate=0.9000" in code for code in decision.reason_codes)

    # Should have recorded outcome in store
    assert store.get_counts().get("test_sig", 0) == 1

    # Should have successful invocation record
    assert record.tier == decision.tier


def test_dispatch_healing_without_phase2_hooks() -> None:
"""Test dispatch_healing_without_phase2_hooks runtime behavior."""
# Arrange
# TODO: Set up test data for dispatch_healing_without_phase2_hooks
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute dispatch_healing_without_phase2_hooks
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
    # Should not raise with None hooks
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=None,
        outcome_write_back_hook=None,
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_dispatch_healing_null_hooks() -> None:
"""Test dispatch_healing_null_hooks runtime behavior."""
# Arrange
# TODO: Set up test data for dispatch_healing_null_hooks
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute dispatch_healing_null_hooks
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
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_dispatch_healing_outcome_hook_failure() -> None:
"""Test dispatch_healing_outcome_hook_failure runtime behavior."""
# Arrange
# TODO: Set up error condition
error_input = {}  # Replace with actual error condition

# Act & Assert
# TODO: Test error handling in dispatch_healing_outcome_hook_failure
with pytest.raises(Exception):  # Replace with expected exception
    # Execute operation that should raise error
    pass  # Replace with actual error test

# TODO: Add error message and handling assertions
        retry_count=0,
        trace_id="test-trace",
    )

    # Should not raise despite hook failure
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        outcome_write_back_hook=failing_hook,
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier
    failing_hook.on_outcome.assert_called_once()


def test_dispatch_healing_invocation_failure_still_calls_hook() -> None:
"""Test dispatch_healing_invocation_failure_still_calls_hook runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute dispatch_healing_invocation_failure_still_calls_hook
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should raise invocation exception but still call hook
    with pytest.raises(Exception, match="Invocation failed"):
        dispatch_healing(
            healing_input,
            config,
            invoker=invoker,
            agent_name="test-agent",
            timestamp_utc=1234567890,
            outcome_write_back_hook=outcome_hook,
        )

    # Hook should have been called with success=False and record=None
    assert store.get_counts().get("test_sig", 0) == 1
