"""
W5 L3 Orchestrator Path Tests

Tests for deterministic L3 orchestration kernel path behaviors.
Validates Path B, C, and D orchestration with proper state transitions.
"""

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler
from agentic_core.L3_orchestration.engines.deterministic_orchestrator import (
    DeterministicOrchestrator,
)
from agentic_core.L3_orchestration.engines.handshake_state_machine import HandshakeState
from agentic_core.L3_orchestration.types.human_decision_artifact_types import HumanAction
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_l3_orchestrator_paths", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_l3_orchestrator_paths", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_l3_orchestrator_paths", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_l3_orchestrator_paths", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_l3_orchestrator_paths", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_l3_orchestrator_paths", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_l3_orchestrator_paths", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_l3_orchestrator_paths", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_l3_orchestrator_paths", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_l3_orchestrator_paths", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_l3_orchestrator_paths", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_l3_orchestrator_paths", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_l3_orchestrator_paths", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_l3_orchestrator_paths", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_l3_orchestrator_paths", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_l3_orchestrator_paths", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_l3_orchestrator_paths", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_l3_orchestrator_paths", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_l3_orchestrator_paths", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_l3_orchestrator_paths", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_l3_orchestrator_paths", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_l3_orchestrator_paths", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_l3_orchestrator_paths", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_l3_orchestrator_paths", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_l3_orchestrator_paths", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_l3_orchestrator_paths", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_l3_orchestrator_paths", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_l3_orchestrator_paths", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_l3_orchestrator_paths")
# REMOVED: _emit_applies_guardrail("p0", "test_l3_orchestrator_paths", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_l3_orchestrator_paths", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_l3_orchestrator_paths", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_l3_orchestrator_paths", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_l3_orchestrator_paths", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l3_orchestrator_paths", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l3_orchestrator_paths", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_l3_orchestrator_paths", "write_through")
# REMOVED: _emit_writes_through("p1", "test_l3_orchestrator_paths", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_l3_orchestrator_paths", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_l3_orchestrator_paths", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_l3_orchestrator_paths", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_l3_orchestrator_paths", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_l3_orchestrator_paths", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_l3_orchestrator_paths", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_l3_orchestrator_paths", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_l3_orchestrator_paths", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_l3_orchestrator_paths", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_l3_orchestrator_paths", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_l3_orchestrator_paths", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_l3_orchestrator_paths", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_l3_orchestrator_paths", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_l3_orchestrator_paths", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_l3_orchestrator_paths")
# REMOVED: _emit_gated_by_confidence("p1", "test_l3_orchestrator_paths", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_l3_orchestrator_paths")
# REMOVED: emit_determinism_digest("p0", "test_l3_orchestrator_paths")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_l3_orchestrator_paths", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_l3_orchestrator_paths", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_l3_orchestrator_paths", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_l3_orchestrator_paths", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_l3_orchestrator_paths", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_l3_orchestrator_paths", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_l3_orchestrator_paths", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_l3_orchestrator_paths", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_l3_orchestrator_paths", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_l3_orchestrator_paths", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_l3_orchestrator_paths", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_l3_orchestrator_paths", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_l3_orchestrator_paths", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_l3_orchestrator_paths", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_l3_orchestrator_paths", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_l3_orchestrator_paths", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_l3_orchestrator_paths", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_l3_orchestrator_paths", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_l3_orchestrator_paths", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_l3_orchestrator_paths", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestW5L3OrchestratorPaths:
    """Test suite for W5 L3 orchestrator path behaviors."""

    @pytest.fixture
    def orchestrator(self):
        """Create deterministic orchestrator instance."""
        return DeterministicOrchestrator()

    @pytest.fixture
    def sample_payload(self):
        """Create sample governed payload for testing."""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt="Single task prompt",
        )

    @pytest.fixture
    def multi_task_payload(self):
        """Create multi-task payload for Path D testing."""
        prompt = """1. First task
2. Second task
3. Third task"""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt=prompt,
        )

    @pytest.fixture
    def tool_execution_payload(self):
        """Create payload with tool execution intent for Path C testing."""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt="Execute the data analysis tool",
        )

    def test_path_b_policy_check_first(self, orchestrator, sample_payload):
        """Test Path B: Policy Check First orchestration."""
        trace_id = "test_trace_b_001"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2")

        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "B"
        assert result.plan_hash is not None
        assert result.execution_trace is not None
        assert result.handshake_state == HandshakeState.SEALED
        assert result.determinism_digest is not None
        assert result.metadata is not None

        # Verify Path B specific metadata
        assert result.metadata["policy_check"] == "completed"
        assert result.metadata["certification"] == "granted"
        assert result.metadata["sealed"] is True

        # Verify execution trace
        assert result.execution_trace["trace_id"] == trace_id
        assert result.execution_trace["plan_hash"] == result.plan_hash
        assert result.execution_trace["actor"] == "L3_Orchestrator"

    def test_path_c_execute_script_directly(self, orchestrator, tool_execution_payload):
        """Test Path C: Execute Script Directly orchestration."""
        trace_id = "test_trace_c_001"
        policy_hash = "policy_hash_001"
        allowed_tools = ("data_analysis", "execute")

        result = orchestrator.orchestrate(
            governed_payload=tool_execution_payload,
            route_mode="C",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "C"
        assert result.plan_hash is not None
        assert result.execution_trace is not None
        assert result.handshake_state == HandshakeState.SEALED
        assert result.determinism_digest is not None

        # Verify Path C specific metadata
        assert result.metadata["tool_execution_detected"] is True
        assert result.metadata["certification_required"] is True
        assert result.metadata["sealed"] is True

    def test_path_c_without_tool_intent(self, orchestrator, sample_payload):
        """Test Path C without tool execution intent."""
        trace_id = "test_trace_c_002"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2")

        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="C",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "C"

        # Verify no tool execution detected
        assert result.metadata["tool_execution_detected"] is False
        assert result.metadata["certification_required"] is False

    def test_path_d_human_review_first(self, orchestrator, multi_task_payload):
        """Test Path D: Human Review First orchestration."""
        trace_id = "test_trace_d_001"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2", "tool3")

        result = orchestrator.orchestrate(
            governed_payload=multi_task_payload,
            route_mode="D",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Verify result structure
        assert result.success is True
        assert result.route_mode == "D"
        assert result.plan_hash is not None
        assert result.execution_trace is not None
        assert result.determinism_digest is not None

        # Verify Path D specific properties
        assert result.human_decision_artifact is not None
        assert result.metadata["human_review_required"] is True
        assert result.metadata["dispatched_to_l2"] is False
        assert result.metadata["awaiting_human_decision"] is True

        # Verify human decision artifact
        artifact = result.human_decision_artifact
        assert artifact["trace_id"] == trace_id
        assert artifact["policy_hash"] == policy_hash
        assert artifact["original_plan_hash"] == result.plan_hash
        assert artifact["reviewer_id"] is None  # Draft state
        assert artifact["action"] == HumanAction.MODIFY_DIFF.value

    def test_invalid_route_mode_raises_error(self, orchestrator, sample_payload):
        """Test that invalid route mode raises ValueError."""
        with pytest.raises(ValueError, match="is not a valid RouteMode"):
            orchestrator.orchestrate(
                governed_payload=sample_payload,
                route_mode="INVALID",
                trace_id="test_trace",
                policy_hash="policy_hash",
                allowed_tools=(),
            )

    def test_deterministic_plan_hash(self, orchestrator, sample_payload):
        """Test that plan hash is deterministic across runs."""
        trace_id = "test_trace_deterministic"
        policy_hash = "policy_hash_001"
        allowed_tools = ("tool1", "tool2")

        # Run orchestration twice with identical inputs
        result1 = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        result2 = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
        )

        # Plan hashes should be identical
        assert result1.plan_hash == result2.plan_hash

        # Verify plan hash is valid SHA256
        assert len(result1.plan_hash) == 64
        assert all(c in "0123456789abcdef" for c in result1.plan_hash)

    def test_determinism_digest_format(self, orchestrator, sample_payload):
        """Test that determinism digest has correct format."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_trace",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Verify digest format
        assert result.determinism_digest is not None
        assert len(result.determinism_digest) == 64
        assert all(c in "0123456789abcdef" for c in result.determinism_digest)

        # Verify digest was printed to stdout (captured in test output)
        assert f"W5-DETERMINISM-DIGEST: {result.determinism_digest}" in result.metadata.get(
            "digest_output", ""
        )

    def test_execution_trace_structure(self, orchestrator, sample_payload):
        """Test execution trace has proper structure."""
        trace_id = "test_trace_structure"
        policy_hash = "policy_hash_001"

        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=(),
        )

        trace = result.execution_trace
        assert trace is not None
        assert "trace_id" in trace
        assert "plan_hash" in trace
        assert "actor" in trace
        assert "governed_payload_hash" in trace
        assert "timestamp" in trace

        assert trace["trace_id"] == trace_id
        assert trace["plan_hash"] == result.plan_hash
        assert trace["actor"] == "L3_Orchestrator"

    def test_handshake_state_transitions_path_b(self, orchestrator, sample_payload):
        """Test proper handshake state transitions for Path B."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="B",
            trace_id="test_handshake",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Path B should end in SEALED state after certification
        assert result.handshake_state == HandshakeState.SEALED

    def test_handshake_state_transitions_path_c(self, orchestrator, sample_payload):
        """Test proper handshake state transitions for Path C."""
        result = orchestrator.orchestrate(
            governed_payload=sample_payload,
            route_mode="C",
            trace_id="test_handshake",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Path C should end in SEALED state
        assert result.handshake_state == HandshakeState.SEALED

    def test_handshake_state_transitions_path_d(self, orchestrator, multi_task_payload):
        """Test proper handshake state transitions for Path D."""
        result = orchestrator.orchestrate(
            governed_payload=multi_task_payload,
            route_mode="D",
            trace_id="test_handshake",
            policy_hash="policy_hash",
            allowed_tools=(),
        )

        # Path D should not reach SEALED state (stops for human review)
        assert result.handshake_state == HandshakeState.INIT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
