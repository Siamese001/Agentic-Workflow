"""
W5 Determinism Digest Tests

Tests for W5-DETERMINISM-DIGEST computation and validation.
Validates exactly one digest per run and tamper detection.
"""

import hashlib
import json
import os
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler
from agentic_core.L3_orchestration.engines.deterministic_orchestrator import (
    DeterministicOrchestrator,
    compute_determinism_digest,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_determinism_digest")
# REMOVED: _emit_applies_guardrail("p0", "test_determinism_digest", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_determinism_digest", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_determinism_digest", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_determinism_digest", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_determinism_digest", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_determinism_digest", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_determinism_digest", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_determinism_digest", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_determinism_digest", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_determinism_digest", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_determinism_digest", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_determinism_digest", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_determinism_digest", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_determinism_digest", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_determinism_digest", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_determinism_digest", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_determinism_digest", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_determinism_digest", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_determinism_digest", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_determinism_digest", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_determinism_digest", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_determinism_digest", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_determinism_digest", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_determinism_digest", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_determinism_digest", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_determinism_digest", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_determinism_digest", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_determinism_digest", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_determinism_digest", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_determinism_digest", "write_through")
# REMOVED: _emit_writes_through("p1", "test_determinism_digest", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_determinism_digest", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_determinism_digest", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_determinism_digest", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_determinism_digest", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_determinism_digest", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_determinism_digest", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_determinism_digest", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_determinism_digest", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_determinism_digest", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_determinism_digest", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_determinism_digest", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_determinism_digest", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_determinism_digest", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_determinism_digest", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_determinism_digest")
# REMOVED: _emit_gated_by_confidence("p1", "test_determinism_digest", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_determinism_digest")
# REMOVED: emit_determinism_digest("p0", "test_determinism_digest")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_determinism_digest", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_determinism_digest", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_determinism_digest", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_determinism_digest", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_determinism_digest", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_determinism_digest", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_determinism_digest", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_determinism_digest", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_determinism_digest", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_determinism_digest", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_determinism_digest", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_determinism_digest", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_determinism_digest", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_determinism_digest", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_determinism_digest", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_determinism_digest", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_determinism_digest", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_determinism_digest", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_determinism_digest", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_determinism_digest", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestW5DeterminismDigest:
    """Test suite for W5 determinism digest functionality."""

    @pytest.fixture
    def orchestrator(self):
        """Create deterministic orchestrator instance."""
        return DeterministicOrchestrator()

    @pytest.fixture
    def sample_payload(self):
        """Create sample governed payload."""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt="Test prompt",
        )

    def test_determinism_digest_computation(self):
        """Test determinism digest computation from components."""
        plan_hash = "plan_hash_001"
        agent_registry_hash = "agent_hash_001"
        tool_key_hash = "tool_hash_001"
        handshake_sequence_hash = "handshake_hash_001"

        digest = compute_determinism_digest(
            plan_hash=plan_hash,
            agent_registry_hash=agent_registry_hash,
            tool_key_hash=tool_key_hash,
            handshake_sequence_hash=handshake_sequence_hash,
        )

        # Verify digest format
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

        # Verify digest is printed to stdout
        # Note: In real test, this would be captured in stdout

        # Verify digest computation
        expected_data = {
            "plan_hash": plan_hash,
            "agent_registry_hash": agent_registry_hash,
            "tool_key_hash": tool_key_hash,
            "handshake_sequence_hash": handshake_sequence_hash,
        }
        canonical = json.dumps(expected_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert digest == expected

    def test_determinism_digest_deterministic(self):
        """Test determinism digest is deterministic with same inputs."""
        inputs = {
            "plan_hash": "plan_hash_001",
            "agent_registry_hash": "agent_hash_001",
            "tool_key_hash": "tool_hash_001",
            "handshake_sequence_hash": "handshake_hash_001",
        }

        digest1 = compute_determinism_digest(**inputs)
        digest2 = compute_determinism_digest(**inputs)

        assert digest1 == digest2

    def test_determinism_digest_changes_with_inputs(self):
        """Test determinism digest changes with different inputs."""
        base_inputs = {
            "plan_hash": "plan_hash_001",
            "agent_registry_hash": "agent_hash_001",
            "tool_key_hash": "tool_hash_001",
            "handshake_sequence_hash": "handshake_hash_001",
        }

        base_digest = compute_determinism_digest(**base_inputs)

        # Change plan hash
        modified_inputs = base_inputs.copy()
        modified_inputs["plan_hash"] = "different_plan_hash"
        new_digest = compute_determinism_digest(**modified_inputs)
        assert base_digest != new_digest

        # Change agent registry hash
        modified_inputs = base_inputs.copy()
        modified_inputs["agent_registry_hash"] = "different_agent_hash"
        new_digest = compute_determinism_digest(**modified_inputs)
        assert base_digest != new_digest

        # Change tool key hash
        modified_inputs = base_inputs.copy()
        modified_inputs["tool_key_hash"] = "different_tool_hash"
        new_digest = compute_determinism_digest(**modified_inputs)
        assert base_digest != new_digest

        # Change handshake sequence hash
        modified_inputs = base_inputs.copy()
        modified_inputs["handshake_sequence_hash"] = "different_handshake_hash"
        new_digest = compute_determinism_digest(**modified_inputs)
        assert base_digest != new_digest

    def test_orchestrator_emits_determinism_digest(self, orchestrator, sample_payload):
        """Test that orchestrator emits determinism digest during orchestration."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_trace_001",
            policy_hash="policy_hash_001",
            allowed_tools=("tool1", "tool2"),
        )

        # Verify result contains determinism digest
        assert result.determinism_digest is not None
        assert len(result.determinism_digest) == 64
        assert all(c in "0123456789abcdef" for c in result.determinism_digest)

    def test_identical_digest_across_runs(self, orchestrator, sample_payload):
        """Test identical inputs produce identical digest across multiple runs."""
        orchestration_params = {
            "governed_payload": sample_payload,
            "route_mode": "B",
            "trace_id": "test_trace_deterministic",
            "policy_hash": "policy_hash_001",
            "allowed_tools": ("tool1", "tool2"),
        }

        # Run orchestration multiple times
        result1 = orchestrator.orchestrate(**orchestration_params)
        result2 = orchestrator.orchestrate(**orchestration_params)
        result3 = orchestrator.orchestrate(**orchestration_params)

        # All digests should be identical
        assert result1.determinism_digest == result2.determinism_digest
        assert result2.determinism_digest == result3.determinism_digest
        assert result1.determinism_digest == result3.determinism_digest

    def test_different_digest_for_different_routes(self, orchestrator, sample_payload):
        """Test different routes produce different digests."""
        base_params = {
            "governed_payload": sample_payload,
            "trace_id": "test_trace_routes",
            "policy_hash": "policy_hash_001",
            "allowed_tools": ("tool1", "tool2"),
        }

        # Run different routes
        result_b = orchestrator.orchestrate(route_mode="B", **base_params)
        result_c = orchestrator.orchestrate(route_mode="C", **base_params)
        result_d = orchestrator.orchestrate(route_mode="D", **base_params)

        # All digests should be different
        assert result_b.determinism_digest != result_c.determinism_digest
        assert result_c.determinism_digest != result_d.determinism_digest
        assert result_b.determinism_digest != result_d.determinism_digest

    def test_different_digest_for_different_payloads(self, orchestrator):
        """Test different payloads produce different digests."""
        params = {
            "route_mode": "B",
            "trace_id": "test_trace_payloads",
            "policy_hash": "policy_hash_001",
            "allowed_tools": ("tool1", "tool2"),
        }

        # Create different payloads
        payload1 = AirlockAssembler.assemble(
            s0_system="System 1",
            i0_instructional="Instructions 1",
            c0_context="Context 1",
            u0_user_prompt="Prompt 1",
        )

        payload2 = AirlockAssembler.assemble(
            s0_system="System 2",
            i0_instructional="Instructions 2",
            c0_context="Context 2",
            u0_user_prompt="Prompt 2",
        )

        result1 = orchestrator.orchestrate(governed_payload=payload1, **params)
        result2 = orchestrator.orchestrate(governed_payload=payload2, **params)

        # Digests should be different
        assert result1.determinism_digest != result2.determinism_digest

    @pytest.mark.xfail(strict=True, reason="Negative control: tampered digest differs from canonical")
    def test_negative_control_tamper_detection(self, orchestrator, sample_payload):
        """Test negative control: tamper toggle produces different digest, assertion fails."""
        params = {
            "governed_payload": sample_payload,
            "route_mode": "B",
            "trace_id": "test_trace_tamper",
            "policy_hash": "policy_hash_001",
            "allowed_tools": ("tool1", "tool2"),
        }
        # Canonical digest (no tamper)
        result_clean = orchestrator.orchestrate(**params)
        clean_digest = result_clean.determinism_digest

        # Tampered digest (reversed sort)
        with patch.dict(os.environ, {"W5_NEGCTRL_TAMPER": "1"}):
            result_tampered = orchestrator.orchestrate(**params)

        # This assertion MUST fail (different digests) → test is xfail strict → exit 0
        assert result_tampered.determinism_digest == clean_digest

    def test_negative_control_restore_behavior(self, orchestrator, sample_payload):
        """Test negative control: restore should pass after tamper env is unset."""
        # First, ensure normal behavior works
        result_normal = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_trace_normal",
            policy_hash="policy_hash_001",
            allowed_tools=("tool1", "tool2"),
        )

        # Verify normal operation
        assert result_normal.determinism_digest is not None
        assert result_normal.success is True

        # Ensure tamper environment is not set
        if "W5_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W5_NEGCTRL_TAMPER"]

        # Run again without tampering
        result_restore = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_trace_restore",
            policy_hash="policy_hash_001",
            allowed_tools=("tool1", "tool2"),
        )

        # Should pass normally
        assert result_restore.determinism_digest is not None
        assert result_restore.success is True

    def test_digest_component_hashes(self, orchestrator, sample_payload):
        """Test that digest components are properly computed."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_trace_components",
            policy_hash="policy_hash_001",
            allowed_tools=("tool1", "tool2"),
        )

        # Verify each component is a valid hash
        assert len(result.plan_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.plan_hash)

        # The orchestrator should compute these internally
        # We can't directly access them, but we can verify the final digest
        assert len(result.determinism_digest) == 64
        assert all(c in "0123456789abcdef" for c in result.determinism_digest)

    def test_exactly_one_digest_per_orchestration(self, orchestrator, sample_payload):
        """Test that exactly one digest is emitted per orchestration."""
        # Capture stdout to verify exactly one digest is printed
        import io
        import sys

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output

        try:
            result = orchestrator.orchestrate(
                governed_payload=sample_payload,
                route_mode="B",
                trace_id="test_trace_single",
                policy_hash="policy_hash_001",
                allowed_tools=("tool1", "tool2"),
            )
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()

        # Verify exactly one digest was printed
        digest_lines = [line for line in output.split("\n") if line.startswith("W5-DETERMINISM-DIGEST:")]
        assert len(digest_lines) == 1

        # Verify the digest matches the result
        printed_digest = digest_lines[0].split(": ")[1]
        assert printed_digest == result.determinism_digest

    def test_digest_format_consistency(self, orchestrator, sample_payload):
        """Test digest format is consistent across all operations."""
        routes = ["B", "C", "D"]
        digests = []

        for route in routes:
            result = orchestrator.orchestrate(
                governed_payload=sample_payload,
                route_mode=route,
                trace_id=f"test_trace_{route}",
                policy_hash="policy_hash_001",
                allowed_tools=("tool1", "tool2"),
            )
            digests.append(result.determinism_digest)

        # All digests should have same format
        for digest in digests:
            assert len(digest) == 64
            assert all(c in "0123456789abcdef" for c in digest)

        # All digests should be different
        assert len(set(digests)) == len(digests)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
