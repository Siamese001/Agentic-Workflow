"""Unit tests for ResourcePredictor - deterministic, bounded resource predictions."""

import pytest

from agentic_core.L2_execution.engines.resource_predictor import (
    DefaultDeterministicResourcePredictor,
)
from agentic_core.L2_execution.types.resource_prediction_types import (
    FailureSignature,
    ResourceEnvelope,
    ResourcePrediction,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_resource_predictor", "p4obs", "metric_1")
_emit_emits_metric_event("test_resource_predictor", "p4obs", "metric_2")
_emit_emits_metric_event("test_resource_predictor", "p4obs", "metric_3")
_emit_emits_metric_event("test_resource_predictor", "p4obs", "metric_4")
_emit_emits_metric_event("test_resource_predictor", "p4obs", "metric_5")
_emit_emits_metric_event("test_resource_predictor", "p4obs", "metric_6")
_emit_records_incident_event("test_resource_predictor", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_resource_predictor", "p4obs", "anomaly")
_emit_writes_observability_log("test_resource_predictor", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_resource_predictor", "p4obs", "mon_state")
_emit_triggers_alert("test_resource_predictor", "p4obs", "alert")
_emit_links_incident_trace("test_resource_predictor", "p4obs", "trace_link")
_emit_captures_pattern("test_resource_predictor", "p3lm", "pattern")
_emit_records_learning_event("test_resource_predictor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_resource_predictor", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_resource_predictor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_resource_predictor", "p3lm", "routing")
_emit_improves_agent_policy("test_resource_predictor", "p3lm", "policy")
_emit_stores_learning_state("test_resource_predictor", "p3lm", "state")
_emit_records_execution_trace("test_resource_predictor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_resource_predictor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_resource_predictor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_resource_predictor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_resource_predictor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_resource_predictor", "env_read", "p2_env_1")
_emit_reads_environ("test_resource_predictor", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_resource_predictor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_resource_predictor", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_resource_predictor")
_emit_applies_guardrail("p0", "test_resource_predictor", "p0_governance")
_emit_reads_policy_state("p0", "test_resource_predictor", "policy_binding")
_emit_snapshots_state("p0", "test_resource_predictor", "state_snapshot")
_emit_pulls_context("p1", "test_resource_predictor", "context_pull")
_emit_pulls_context("p1", "test_resource_predictor", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_resource_predictor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_resource_predictor", "uwg_term_secondary")
_emit_writes_through("p1", "test_resource_predictor", "write_through")
_emit_writes_through("p1", "test_resource_predictor", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_resource_predictor", "safety_validation")
_emit_invokes_eval("p1", "test_resource_predictor", "eval_call")
_emit_proposal_commits_routing("p1", "test_resource_predictor", "routing_commit")
_emit_escalates_to_human("p1", "test_resource_predictor", "human_escalation")
_emit_routes_through("p1", "test_resource_predictor", "route_through")
_emit_checks_agent_registry("p1", "test_resource_predictor", "agent_registry")
_emit_validates_agent_capability("p1", "test_resource_predictor", "capability")
_emit_dispatches_execution_plan("p1", "test_resource_predictor", "exec_plan")
_emit_agent_executes_agent("p1", "test_resource_predictor", "sub_agent")
_emit_routes_to_agent("p1", "test_resource_predictor", "target_agent")
_emit_verifies_policy("p1", "test_resource_predictor", "policy_check")
_emit_observes_runtime_state("p1", "test_resource_predictor", "runtime_state")
_emit_verifies_boundary("p1", "test_resource_predictor", "boundary_check")
_emit_transcripts_response("p1", "test_resource_predictor", "transcript")
_emit_hard_fails_untranscripted("p1", "test_resource_predictor")
_emit_gated_by_confidence("p1", "test_resource_predictor", "confidence_gate")
emit_replay_key("p0", "test_resource_predictor")
emit_determinism_digest("p0", "test_resource_predictor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_resource_predictor", "execution_auth")
_emit_validates_capability("p2", "test_resource_predictor", "capability_check")
_emit_routes_to_capability("p2", "test_resource_predictor", "capability_route")
_emit_writes_via_uwg("p2", "test_resource_predictor", "uwg_write")
_emit_blocks_direct_write("p2", "test_resource_predictor", "direct_write_block")
_emit_records_tool_invocation("p2", "test_resource_predictor", "tool_invocation")
_emit_captures_execution_output("p2", "test_resource_predictor", "exec_output")
_emit_dispatches_agent("p3", "test_resource_predictor", "agent_dispatch")
_emit_coordinates_agents("p3", "test_resource_predictor", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_resource_predictor", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_resource_predictor", "healing_outcome")
_emit_escalates_failure("p3", "test_resource_predictor", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_resource_predictor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_resource_predictor", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_resource_predictor", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_resource_predictor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_resource_predictor", "eval_metric")
_emit_stores_embedding("p4", "test_resource_predictor", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_resource_predictor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_resource_predictor", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestResourcePredictor:
    """Test suite for ResourcePredictor deterministic behavior."""

    def test_determinism_same_input_same_hash(self):
        """Same inputs must produce identical outputs and hashes."""
        predictor = DefaultDeterministicResourcePredictor()

        signature = FailureSignature(
            component="test_component",
            failure_type="timeout",
            fingerprint="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        )

        # Run prediction twice
        prediction1 = predictor.predict(signature=signature, history_bytes=None)
        prediction2 = predictor.predict(signature=signature, history_bytes=None)

        # Must be identical
        assert prediction1.content_hash() == prediction2.content_hash()
        assert prediction1.envelope == prediction2.envelope
        assert prediction1.confidence == prediction2.confidence
        assert prediction1.reasons == prediction2.reasons

    def test_bounded_clamping(self):
        """Resource envelopes must be clamped to configured bounds."""
        # Test with very tight bounds
        predictor = DefaultDeterministicResourcePredictor(
            min_cpu_cores=2,
            max_cpu_cores=4,
            min_memory_mb=1024,
            max_memory_mb=2048,
            min_timeout_s=60,
            max_timeout_s=300,
        )

        signature = FailureSignature(
            component="test",
            failure_type="unknown",  # Uses baseline envelope
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        prediction = predictor.predict(signature=signature, history_bytes=None)

        # Must be within bounds
        assert 2 <= prediction.envelope.cpu_cores <= 4
        assert 1024 <= prediction.envelope.memory_mb <= 2048
        assert 60 <= prediction.envelope.timeout_s <= 300

    def test_history_influence_deterministic(self):
        """History must influence predictions deterministically."""
        predictor = DefaultDeterministicResourcePredictor()

        signature = FailureSignature(
            component="test",
            failure_type="memory_error",
            fingerprint="fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        )

        # Different history should produce different results than no history
        history1 = b"sample_history_data_1"

        prediction1 = predictor.predict(signature=signature, history_bytes=history1)
        prediction_no_history = predictor.predict(signature=signature, history_bytes=None)

        # Should be different when history is provided vs no history
        assert prediction1.content_hash() != prediction_no_history.content_hash()

        # History should increase confidence
        assert prediction1.confidence > prediction_no_history.confidence

        # Different history content should still be processed (even if result same due to deterministic hash)
        history2 = b"sample_history_data_2"
        prediction2 = predictor.predict(signature=signature, history_bytes=history2)

        # At minimum, history processing should work without errors
        assert prediction2 is not None
        assert prediction2.confidence > prediction_no_history.confidence

    def test_permutation_invariant_healing_inputs(self):
        """Permutation invariance test for healing inputs."""
        predictor = DefaultDeterministicResourcePredictor()

        # Same signature with different object construction should be identical
        signature1 = FailureSignature(
            component="component_a",
            failure_type="cpu_error",
            fingerprint="1111111111111111111111111111111111111111111111111111111111111111",
        )

        signature2 = FailureSignature(
            failure_type="cpu_error",  # Different order
            fingerprint="1111111111111111111111111111111111111111111111111111111111111111",
            component="component_a",
        )

        prediction1 = predictor.predict(signature=signature1, history_bytes=None)
        prediction2 = predictor.predict(signature=signature2, history_bytes=None)

        # Must be identical despite construction order
        assert prediction1.content_hash() == prediction2.content_hash()
        assert prediction1.envelope == prediction2.envelope

    def test_failure_type_baseline_envelopes(self):
        """Different failure types should use appropriate baseline envelopes."""
        predictor = DefaultDeterministicResourcePredictor()

        failure_types = ["timeout", "memory_error", "cpu_error", "io_error", "network_error", "unknown"]

        predictions = {}
        for failure_type in failure_types:
            signature = FailureSignature(
                component="test",
                failure_type=failure_type,
                fingerprint=f"{failure_type}_fingerprint_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            )
            prediction = predictor.predict(signature=signature, history_bytes=None)
            predictions[failure_type] = prediction

        # Should have different envelopes for different failure types
        timeout_env = predictions["timeout"].envelope
        memory_env = predictions["memory_error"].envelope
        cpu_env = predictions["cpu_error"].envelope

        # Memory errors should suggest more memory
        assert memory_env.memory_mb > timeout_env.memory_mb
        # CPU errors should suggest more CPU
        assert cpu_env.cpu_cores > timeout_env.cpu_cores

    def test_canonical_bytes_stability(self):
        """canonical_bytes() must be stable and ASCII-only."""
        signature = FailureSignature(
            component="test",
            failure_type="timeout",
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        envelope = ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300)

        prediction = ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=0.8,
            reasons=("test_reason", "another_reason"),
        )

        canonical = prediction.canonical_bytes()

        # Must be bytes
        assert isinstance(canonical, bytes)

        # Must be ASCII-only
        try:
            canonical.decode("ascii")
        except UnicodeDecodeError:
            pytest.fail("canonical_bytes() must be ASCII-only")

        # Must be stable across calls
        assert canonical == prediction.canonical_bytes()

    def test_confidence_bounds(self):
        """Confidence must always be within [0.0, 1.0]."""
        predictor = DefaultDeterministicResourcePredictor()

        signature = FailureSignature(
            component="test",
            failure_type="unknown",
            fingerprint="9999999999999999999999999999999999999999999999999999999999999999",
        )

        # Test with various scenarios
        scenarios = [
            None,  # No history
            b"short_history",
            b"very_long_history_data_" * 100,  # Long history
        ]

        for history in scenarios:
            prediction = predictor.predict(signature=signature, history_bytes=history)
            assert 0.0 <= prediction.confidence <= 1.0
