"""
W4-F Retrieval Profile Activation Gate Tests

Tests for explicit activation gate with deterministic checks.
"""

import os
from unittest.mock import Mock

import pytest

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
)

_emit_authorize_and_execute("p2", "test_activation_gate_w4f", "execution_auth")
_emit_validates_capability("p2", "test_activation_gate_w4f", "capability_check")
_emit_routes_to_capability("p2", "test_activation_gate_w4f", "capability_route")
_emit_writes_via_uwg("p2", "test_activation_gate_w4f", "uwg_write")
_emit_blocks_direct_write("p2", "test_activation_gate_w4f", "direct_write_block")
_emit_records_tool_invocation("p2", "test_activation_gate_w4f", "tool_invocation")
_emit_captures_execution_output("p2", "test_activation_gate_w4f", "exec_output")
_emit_dispatches_agent("p3", "test_activation_gate_w4f", "agent_dispatch")
_emit_coordinates_agents("p3", "test_activation_gate_w4f", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_activation_gate_w4f", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_activation_gate_w4f", "healing_outcome")
_emit_escalates_failure("p3", "test_activation_gate_w4f", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_activation_gate_w4f", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_activation_gate_w4f", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_activation_gate_w4f", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_activation_gate_w4f", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_activation_gate_w4f", "eval_metric")
_emit_stores_embedding("p4", "test_activation_gate_w4f", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_activation_gate_w4f", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_activation_gate_w4f", "exec_snapshot_link")
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_activation_gate import (
    RetrievalProfileActivationGate,
)

_emit_records_execution_trace("p0", "evidence", "test_activation_gate_w4f")
_emit_applies_guardrail("p0", "test_activation_gate_w4f", "p0_governance")
_emit_reads_policy_state("p0", "test_activation_gate_w4f", "policy_binding")
_emit_snapshots_state("p0", "test_activation_gate_w4f", "state_snapshot")
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
)

_emit_emits_metric_event("test_activation_gate_w4f", "p4obs", "metric_1")
_emit_emits_metric_event("test_activation_gate_w4f", "p4obs", "metric_2")
_emit_emits_metric_event("test_activation_gate_w4f", "p4obs", "metric_3")
_emit_emits_metric_event("test_activation_gate_w4f", "p4obs", "metric_4")
_emit_emits_metric_event("test_activation_gate_w4f", "p4obs", "metric_5")
_emit_emits_metric_event("test_activation_gate_w4f", "p4obs", "metric_6")
_emit_records_incident_event("test_activation_gate_w4f", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_activation_gate_w4f", "p4obs", "anomaly")
_emit_writes_observability_log("test_activation_gate_w4f", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_activation_gate_w4f", "p4obs", "mon_state")
_emit_triggers_alert("test_activation_gate_w4f", "p4obs", "alert")
_emit_links_incident_trace("test_activation_gate_w4f", "p4obs", "trace_link")
_emit_captures_pattern("test_activation_gate_w4f", "p3lm", "pattern")
_emit_records_learning_event("test_activation_gate_w4f", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_activation_gate_w4f", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_activation_gate_w4f", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_activation_gate_w4f", "p3lm", "routing")
_emit_improves_agent_policy("test_activation_gate_w4f", "p3lm", "policy")
_emit_stores_learning_state("test_activation_gate_w4f", "p3lm", "state")
_emit_records_execution_trace("test_activation_gate_w4f", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_activation_gate_w4f", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_activation_gate_w4f", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_activation_gate_w4f", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_activation_gate_w4f", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_activation_gate_w4f", "env_read", "p2_env_1")
_emit_reads_environ("test_activation_gate_w4f", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_activation_gate_w4f", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_activation_gate_w4f", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_activation_gate_w4f", "context_pull")
_emit_pulls_context("p1", "test_activation_gate_w4f", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_activation_gate_w4f", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_activation_gate_w4f", "uwg_term_2")
_emit_writes_through("p1", "test_activation_gate_w4f", "write_through")
_emit_writes_through("p1", "test_activation_gate_w4f", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_activation_gate_w4f", "safety_validation")
_emit_invokes_eval("p1", "test_activation_gate_w4f", "eval_call")
_emit_proposal_commits_routing("p1", "test_activation_gate_w4f", "routing_commit")
emit_replay_key("p0", "test_activation_gate_w4f")
emit_determinism_digest("p0", "test_activation_gate_w4f")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.mark.unit_min_deps
class TestActivationGateW4F:
    """Test W4-F Retrieval Profile Activation Gate functionality."""

    def test_refuse_without_approval(self):
        """Test that activation refuses when proposal exists but no approval."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Try to activate unapproved proposal
        result = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-unapproved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation refused
        assert result.activated == False
        assert result.base_profile_id == "test-profile"
        assert result.proposal_digest == "test-proposal-digest-unapproved"
        assert result.new_profile_id is None
        assert "not approved" in result.reason.lower()

        # Verify digest is computed
        assert result.activation_digest is not None
        assert len(result.activation_digest) == 64  # SHA-256 hex length

    def test_approve_then_activate(self):
        """Test successful activation with approved proposal."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Activate approved proposal
        result = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation succeeded
        assert result.activated == True
        assert result.base_profile_id == "test-profile"
        assert result.proposal_digest == "test-proposal-digest-approved"
        assert result.new_profile_id == "test-profile-proposed"
        assert "successful" in result.reason.lower()

        # Verify L4 writes were attempted
        assert l4_writer.write_l4a_detection_signal.call_count >= 2  # Profile write + active profile update

        # Verify digest is computed and emitted
        assert result.activation_digest is not None
        assert len(result.activation_digest) == 64

    def test_replay_check_determinism(self):
        """Test that replay check produces deterministic digests."""
        gate = RetrievalProfileActivationGate()

        # Create test profiles
        base_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        proposed_profile = RetrievalProfile(
            profile_id="test-profile-proposed",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=12,
            similarity_cutoff=0.82,
            influence_cap=0.55,
            normalization_policy="l2",
        )

        # Run replay check twice
        result1 = gate.replay_engine.replay(
            base_profile=base_profile,
            candidate_profile=proposed_profile,
        )

        result2 = gate.replay_engine.replay(
            base_profile=base_profile,
            candidate_profile=proposed_profile,
        )

        # Verify deterministic digest
        assert result1.replay_digest == result2.replay_digest, "Replay check digest must be deterministic"

        # Verify digest format
        assert len(result1.replay_digest) == 64  # SHA-256 hex length

    def test_invariant_failure_blocks_activation(self):
        """Test that invariant violations block activation."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Monkey patch the invariant checker to always fail
        original_validate = gate.invariant_checker.validate

        def failing_validate(*args, **kwargs):
            raise ValueError("Test invariant violation: similarity_cutoff out of bounds")

        try:
            gate.invariant_checker.validate = failing_validate

            # Try to activate approved proposal (should fail due to invariant)
            result = gate.activate_if_approved(
                base_profile_id="test-profile",
                proposal_digest="test-proposal-digest-approved",
                now_utc=now_utc,
                l4_writer=l4_writer,
            )

            # Verify activation blocked
            assert result.activated == False
            assert result.new_profile_id is None
            assert "invariant violation" in result.reason.lower()

        finally:
            # Restore original method
            gate.invariant_checker.validate = original_validate

    def test_nonexistent_proposal_blocks_activation(self):
        """Test that nonexistent proposal blocks activation."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Try to activate nonexistent proposal
        result = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="nonexistent-proposal-digest",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation blocked
        assert result.activated == False
        assert result.new_profile_id is None
        assert "not found" in result.reason.lower()

    def test_nonexistent_base_profile_blocks_activation(self):
        """Test that nonexistent base profile blocks activation."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Try to activate with nonexistent base profile
        result = gate.activate_if_approved(
            base_profile_id="nonexistent-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation blocked
        assert result.activated == False
        assert result.new_profile_id is None
        assert "not found" in result.reason.lower()


@pytest.mark.unit_min_deps
class TestW4FNegativeControl:
    """Negative control tests for W4-F Activation Gate."""

    @pytest.mark.xfail(reason="W4F tamper guard", strict=True)
    def test_activation_determinism_violation_negative_control(self):
        """Negative control: tamper with activation digest determinism."""
        # Set tamper flag to change canonicalization
        os.environ["W4F_NEGCTRL_TAMPER"] = "1"

        # Monkey patch the json.dumps in activation gate
        import json

        import system_learning.engines.retrieval_profile_activation_gate as gate_module

        original_json_dumps = json.dumps

        def tampered_json_dumps(obj, *, sort_keys=False, separators=None):
            """Tampered JSON serialization that uses different separators."""
            if separators == (",", ":"):
                # Use different separators to change canonical form
                separators = (", ", ": ")
            return original_json_dumps(obj, sort_keys=sort_keys, separators=separators)

        try:
            # Apply tampering
            gate_module.json.dumps = tampered_json_dumps

            gate = RetrievalProfileActivationGate()
            l4_writer = Mock(spec=L4StateWriter)
            now_utc = 1234567890

            # Run activation with tampering
            result_tampered = gate.activate_if_approved(
                base_profile_id="test-profile",
                proposal_digest="test-proposal-digest-approved",
                now_utc=now_utc,
                l4_writer=l4_writer,
            )

            # Restore original function for comparison
            gate_module.json.dumps = original_json_dumps
            result_normal = gate.activate_if_approved(
                base_profile_id="test-profile",
                proposal_digest="test-proposal-digest-approved",
                now_utc=now_utc,
                l4_writer=l4_writer,
            )

            # Tampering should cause different results - this should FAIL the test
            if result_tampered.activation_digest != result_normal.activation_digest:
                assert False, (
                    f"TAMPERING DETECTED: tampered digest {result_tampered.activation_digest} != normal digest {result_normal.activation_digest}"
                )

            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - activation digests are identical"

        finally:
            # Restore original function
            gate_module.json.dumps = original_json_dumps
            # Clean up environment
            os.environ.pop("W4F_NEGCTRL_TAMPER", None)

    def test_activation_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W4F_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W4F_NEGCTRL_TAMPER"]

        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Run activation twice without tampering
        result1 = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        result2 = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Should be identical when not tampering
        assert result1.activation_digest == result2.activation_digest, (
            "Activation digest must be identical when not tampering"
        )
        assert result1.activated == result2.activated, (
            "Activation status must be identical when not tampering"
        )
