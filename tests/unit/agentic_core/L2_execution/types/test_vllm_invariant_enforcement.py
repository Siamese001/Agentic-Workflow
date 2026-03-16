"""
End-to-end tests for Phase 5 invariant enforcement at adapter seam.

Tests that FAIL violations trigger Gemini fallback with violations in telemetry.
"""

import pytest

from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (
    VLLMGatewayAdapter,
    reset_singletons,
)
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
)
from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_vllm_invariant_enforcement")
_emit_applies_guardrail("p0", "test_vllm_invariant_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_invariant_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_invariant_enforcement", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_vllm_invariant_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("test_vllm_invariant_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("test_vllm_invariant_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("test_vllm_invariant_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("test_vllm_invariant_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("test_vllm_invariant_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("test_vllm_invariant_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_vllm_invariant_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("test_vllm_invariant_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_vllm_invariant_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("test_vllm_invariant_enforcement", "p4obs", "alert")
_emit_links_incident_trace("test_vllm_invariant_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("test_vllm_invariant_enforcement", "p3lm", "pattern")
_emit_records_learning_event("test_vllm_invariant_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_vllm_invariant_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_vllm_invariant_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_vllm_invariant_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("test_vllm_invariant_enforcement", "p3lm", "policy")
_emit_stores_learning_state("test_vllm_invariant_enforcement", "p3lm", "state")
_emit_records_execution_trace("test_vllm_invariant_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_vllm_invariant_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_vllm_invariant_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_vllm_invariant_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_vllm_invariant_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_vllm_invariant_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("test_vllm_invariant_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_vllm_invariant_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_vllm_invariant_enforcement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_vllm_invariant_enforcement", "context_pull")
_emit_pulls_context("p1", "test_vllm_invariant_enforcement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_vllm_invariant_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_vllm_invariant_enforcement", "uwg_term_2")
_emit_writes_through("p1", "test_vllm_invariant_enforcement", "write_through")
_emit_writes_through("p1", "test_vllm_invariant_enforcement", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_vllm_invariant_enforcement", "safety_validation")
_emit_invokes_eval("p1", "test_vllm_invariant_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "test_vllm_invariant_enforcement", "routing_commit")
_emit_escalates_to_human("p1", "test_vllm_invariant_enforcement", "human_escalation")
_emit_routes_through("p1", "test_vllm_invariant_enforcement", "route_through")
_emit_checks_agent_registry("p1", "test_vllm_invariant_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "test_vllm_invariant_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "test_vllm_invariant_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "test_vllm_invariant_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "test_vllm_invariant_enforcement", "target_agent")
_emit_verifies_policy("p1", "test_vllm_invariant_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "test_vllm_invariant_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "test_vllm_invariant_enforcement", "boundary_check")
_emit_transcripts_response("p1", "test_vllm_invariant_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_vllm_invariant_enforcement")
_emit_gated_by_confidence("p1", "test_vllm_invariant_enforcement", "confidence_gate")
emit_replay_key("p0", "test_vllm_invariant_enforcement")
emit_determinism_digest("p0", "test_vllm_invariant_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vllm_invariant_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_vllm_invariant_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_vllm_invariant_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_vllm_invariant_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_vllm_invariant_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vllm_invariant_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_vllm_invariant_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_vllm_invariant_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vllm_invariant_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vllm_invariant_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vllm_invariant_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_vllm_invariant_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vllm_invariant_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vllm_invariant_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vllm_invariant_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vllm_invariant_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vllm_invariant_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_vllm_invariant_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vllm_invariant_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vllm_invariant_enforcement", "exec_snapshot_link")

pytestmark = pytest.mark.integration_full_deps


@pytest.fixture(autouse=True)
def reset_adapter_state():
    """Reset adapter singletons before each test."""
    reset_singletons()
    yield
    reset_singletons()


def test_adapter_local_success_with_zero_violations():
    """Test that valid local request produces zero violations."""
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Should route to local (no violations)
    assert not result.route_to_gemini
    assert result.local_request is not None
    assert result.invariant_violations == []


def test_adapter_with_fingerprint_produces_no_violations():
    """Test that providing fingerprint produces no violations.

    NOTE: When fingerprint=None, evaluate_gateway_call uses deterministic_test_instance,
    so telemetry always has fingerprint_hash. This is by design for Phase 4 compatibility.
    """
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Should route to local (no violations)
    assert not result.route_to_gemini
    assert result.local_request is not None

    # Should have no violations
    assert result.invariant_violations == []


def test_adapter_result_has_invariant_violations_field():
    """Test that result always has invariant_violations field."""
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Result should always have invariant_violations field
    assert hasattr(result, "invariant_violations")
    assert isinstance(result.invariant_violations, list)


def test_adapter_preserves_phase_1_4_behavior():
    """Test that Phase 5 preserves Phase 1-4 routing behavior when no violations."""
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    # Test local success path
    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Should route to local (Phase 1-4 behavior preserved)
    assert not result.route_to_gemini
    assert result.local_request is not None
    assert result.telemetry is not None
    assert result.preflight is not None
    assert result.backpressure is not None

    # Phase 5 addition: invariant_violations
    assert result.invariant_violations == []


def test_adapter_fail_violation_triggers_gemini_with_violations_attached():
    """Test that FAIL violation triggers Gemini fallback with violations in telemetry.

    This test uses monkey-patching to force a FAIL violation and verify the
    adapter's enforcement behavior.
    """
    from unittest.mock import patch

    from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
        InvariantViolation,
    )

    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    # Create a mock FAIL violation
    mock_violation = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test FAIL violation",
        context={"test": True},
    )

    # Patch the verifier to return a FAIL violation
    with patch(
        "agentic_core.L2_execution.types.vllm_invariant_verifier_types.verify_gateway_invariants"
    ) as mock_verify:
        mock_verify.return_value = [mock_violation]

        result = adapter.evaluate(
            prompt="hello",
            task_class="patch_suggestion",
            severity="low",
            oldest_wait_seconds=0.0,
            fingerprint=fp,
        )

    # CRITICAL: FAIL violation should trigger Gemini fallback
    assert result.route_to_gemini, "FAIL violation must trigger Gemini fallback"
    assert result.local_request is None, "Local request should be None when routing to Gemini"

    # CRITICAL: FAIL violation must set failure_type=INVARIANT_VIOLATION
    assert result.telemetry.failure_type == "INVARIANT_VIOLATION", (
        "FAIL violation must set failure_type=INVARIANT_VIOLATION"
    )

    # Violations should be attached to result
    assert len(result.invariant_violations) == 1
    assert (
        result.invariant_violations[0].invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    )
    assert result.invariant_violations[0].severity == InvariantSeverity.FAIL.value

    # Violations should be serializable with hashes
    violation_dict = result.invariant_violations[0].as_dict()
    assert "violation_hash" in violation_dict
    assert len(violation_dict["violation_hash"]) == 64
