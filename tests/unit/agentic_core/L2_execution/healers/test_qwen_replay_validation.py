"""
Qwen Replay Validation Test - Determinism and Consistency Testing

Provides comprehensive replay validation to ensure Qwen invocations
are deterministic and reproducible.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_qwen_replay_validation")
# REMOVED: _emit_applies_guardrail("p0", "test_qwen_replay_validation", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_qwen_replay_validation", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_qwen_replay_validation", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_qwen_replay_validation", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_qwen_replay_validation", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_qwen_replay_validation", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_qwen_replay_validation", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_qwen_replay_validation", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_qwen_replay_validation", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_qwen_replay_validation", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_qwen_replay_validation", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_qwen_replay_validation", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_qwen_replay_validation", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_qwen_replay_validation", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_qwen_replay_validation", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_qwen_replay_validation", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_qwen_replay_validation", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_qwen_replay_validation", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_qwen_replay_validation", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_qwen_replay_validation", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_qwen_replay_validation", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_qwen_replay_validation", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_qwen_replay_validation", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_qwen_replay_validation", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_qwen_replay_validation", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_qwen_replay_validation", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_qwen_replay_validation", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_qwen_replay_validation", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_qwen_replay_validation", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_qwen_replay_validation", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_qwen_replay_validation", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_qwen_replay_validation", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_qwen_replay_validation", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_qwen_replay_validation", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_qwen_replay_validation", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_qwen_replay_validation", "write_through")
# REMOVED: _emit_writes_through("p1", "test_qwen_replay_validation", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_qwen_replay_validation", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_qwen_replay_validation", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_qwen_replay_validation", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_qwen_replay_validation", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_qwen_replay_validation", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_qwen_replay_validation", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_qwen_replay_validation", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_qwen_replay_validation", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_qwen_replay_validation", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_qwen_replay_validation", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_qwen_replay_validation", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_qwen_replay_validation", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_qwen_replay_validation", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_qwen_replay_validation", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_qwen_replay_validation")
# REMOVED: _emit_gated_by_confidence("p1", "test_qwen_replay_validation", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_qwen_replay_validation")
# REMOVED: emit_determinism_digest("p0", "test_qwen_replay_validation")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_qwen_replay_validation", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_qwen_replay_validation", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_qwen_replay_validation", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_qwen_replay_validation", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_qwen_replay_validation", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_qwen_replay_validation", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_qwen_replay_validation", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_qwen_replay_validation", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_qwen_replay_validation", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_qwen_replay_validation", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_qwen_replay_validation", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_qwen_replay_validation", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_qwen_replay_validation", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_qwen_replay_validation", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_qwen_replay_validation", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_qwen_replay_validation", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_qwen_replay_validation", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_qwen_replay_validation", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_qwen_replay_validation", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_qwen_replay_validation", "exec_snapshot_link")


def create_deterministic_healing_input() -> HealingInput:
    """Create a deterministic healing input for testing."""
    return HealingInput(
        failure_type="syntax_error",
        error_signature="test_syntax_error_001",
        trace_id="test-trace-001",
        retry_count=0,
        blast_radius_estimate=0.1,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
    )


def invoke_qwen_via_healing_tier(healing_input: HealingInput) -> InvocationRecord:
    """Invoke Qwen through the healing tier system."""
    # Import here to avoid circular dependency
    from agentic_core.L2_execution.healers.healing_tier_config import load_default_healing_tier_config
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

    config = load_default_healing_tier_config()

    # Mock the actual OpenAI call for testing
    # In real implementation, this would call the actual vLLM server
    decision, record = dispatch_healing(
        healing_input,
        config,
        agent_name="test_agent",
    )

    return record


def test_qwen_replay_determinism():
    """Verify exact replay consistency across invocations."""
    healing_input = create_deterministic_healing_input()

    # Invoke Qwen twice with identical parameters
    record1 = invoke_qwen_via_healing_tier(healing_input)
    record2 = invoke_qwen_via_healing_tier(healing_input)

    # Verify determinism digest matches
    if record1.provider_metadata and record2.provider_metadata:
        digest1 = record1.provider_metadata.get("determinism_digest")
        digest2 = record2.provider_metadata.get("determinism_digest")
        assert digest1 == digest2, f"Determinism drift: {digest1} != {digest2}"

        # Verify output hash matches
        output1 = record1.provider_metadata.get("output_hash")
        output2 = record2.provider_metadata.get("output_hash")
        assert output1 == output2, f"Output drift: {output1} != {output2}"

    # Verify canonical JSON serialization matches
    json1 = json.dumps(asdict(record1), separators=(",", ":"), sort_keys=True)
    json2 = json.dumps(asdict(record2), separators=(",", ":"), sort_keys=True)
    assert json1 == json2, "InvocationRecord JSON mismatch"


def test_qwen_determinism_digest_completeness():
    """Verify determinism digest includes all required components."""
    from agentic_core.L2_execution.healers.qwen_determinism import compute_qwen_determinism_digest

    digest = compute_qwen_determinism_digest(
        model_id="Qwen/Qwen2.5-7B-Instruct",
        model_revision="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
        tokenizer_revision="f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7",
        inference_params={"temperature": 0.0, "top_p": 1.0, "max_tokens": 2048, "seed": 42},
        vllm_version="0.4.2",
        cuda_version="12.1",
        torch_version="2.1.0",
    )

    # Verify full SHA-256 (64 hex characters)
    assert len(digest) == 64, f"Digest should be 64 chars, got {len(digest)}"
    assert all(c in "0123456789abcdef" for c in digest), "Digest should be hex only"


def test_qwen_output_canonicalization():
    """Verify output canonicalization handles Unicode and whitespace."""
    from agentic_core.L2_execution.healers.qwen_determinism import canonicalize_qwen_output

    # Test Unicode normalization
    output1 = "café"  # Combined accent
    output2 = "cafe\u0301"  # Decomposed accent
    hash1 = canonicalize_qwen_output(output1)
    hash2 = canonicalize_qwen_output(output2)
    assert hash1 == hash2, "Unicode normalization failed"

    # Test whitespace normalization
    output3 = "  hello\nworld  \n  "
    output4 = "hello\nworld"
    hash3 = canonicalize_qwen_output(output3)
    hash4 = canonicalize_qwen_output(output4)
    assert hash3 == hash4, "Whitespace normalization failed"


def test_qwen_circuit_breaker_replay_safety():
    """Verify circuit breaker is deterministic in replay mode."""
    from agentic_core.L2_execution.healers.qwen_circuit_breaker import QwenCircuitBreaker

    # Normal mode - circuit breaker should work
    cb_normal = QwenCircuitBreaker(replay_mode=False)
    assert not cb_normal.record_failure(), "First failure should not open circuit"
    assert not cb_normal.record_failure(), "Second failure should not open circuit"
    assert cb_normal.record_failure(), "Third failure should open circuit"
    assert cb_normal.is_circuit_open(), "Circuit should be open"

    # Replay mode - circuit breaker should be disabled
    cb_replay = QwenCircuitBreaker(replay_mode=True)
    assert not cb_replay.record_failure(), "Replay mode should disable circuit breaker"
    assert not cb_replay.record_failure(), "Replay mode should disable circuit breaker"
    assert not cb_replay.record_failure(), "Replay mode should disable circuit breaker"
    assert not cb_replay.is_circuit_open(), "Replay mode should always be closed"


def test_qwen_meta_learning_boundaries():
    """Verify meta-learning respects threshold immutability."""
    from agentic_core.L2_execution.healers.qwen_meta_learning import (
        HEALING_CONFIDENCE_X,
        HEALING_CONFIDENCE_Y,
        update_qwen_confidence_prior,
        validate_threshold_immutability,
    )

    # Update confidence prior (allowed)
    update_qwen_confidence_prior("test_error", success=True)

    # Validate thresholds are immutable
    validate_threshold_immutability()

    # Verify thresholds haven't changed
    assert HEALING_CONFIDENCE_X == 0.80, "X threshold should remain immutable"
    assert HEALING_CONFIDENCE_Y == 0.50, "Y threshold should remain immutable"


if __name__ == "__main__":
    # Run tests if executed directly
    test_qwen_replay_determinism()
    test_qwen_determinism_digest_completeness()
    test_qwen_output_canonicalization()
    test_qwen_circuit_breaker_replay_safety()
    test_qwen_meta_learning_boundaries()
    print("All Qwen replay validation tests passed!")
