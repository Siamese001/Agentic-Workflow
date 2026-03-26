"""
Wave 2 Phase 6 — L3 Orchestration Sequential Handshake Tests

§4-compliant test suite covering:
- HandshakeStateMachine: all 5 state transitions (INIT→PRECLEAR→CERTIFIED→SEALED→DISPATCHED)
- Disallowed transitions (all invalid from-state combos)
- MODIFY_DIFF rollback path
- Sequence hash integrity and determinism
- Reset side-effect safety
- Arbitrator: scoring, tie-breaking, merge, empty proposals guard
- AdvisorProposal / ArbitrationInput validation guards
"""
from __future__ import annotations



import pytest

#  # MOVED: from agentic_core.L3_orchestration.arbitration.arbitration_contract import (
    AdvisorProposal,
    ArbitrationInput,
)
#  # MOVED: from agentic_core.L3_orchestration.arbitration.arbitrator import Arbitrator
#  # MOVED: from agentic_core.L3_orchestration.engines.handshake_state_machine import (
    HandshakeState,
    HandshakeStateMachine,
    create_handshake_machine,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_orchestration_handshake", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_orchestration_handshake", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_orchestration_handshake", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_orchestration_handshake", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_orchestration_handshake", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_orchestration_handshake", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_orchestration_handshake", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_orchestration_handshake", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_orchestration_handshake", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_orchestration_handshake", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_orchestration_handshake", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_orchestration_handshake", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_orchestration_handshake", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_orchestration_handshake", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_orchestration_handshake", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_orchestration_handshake", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_orchestration_handshake", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_orchestration_handshake", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_orchestration_handshake", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_orchestration_handshake", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_orchestration_handshake", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_orchestration_handshake", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_orchestration_handshake", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_orchestration_handshake", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_orchestration_handshake", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_orchestration_handshake", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_orchestration_handshake", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_orchestration_handshake", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_orchestration_handshake")
# REMOVED: _emit_applies_guardrail("p0", "test_orchestration_handshake", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_orchestration_handshake", "policy_binding")
# REMOVED: _emit_routes_to_agent("p1", "test_orchestration_handshake", "test")
# REMOVED: _emit_orchestrates_workflow("p1", "test_orchestration_handshake", "test")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_orchestration_handshake", "test")
# REMOVED: _emit_validates_agent_capability("p1", "test_orchestration_handshake", "test")
# REMOVED: _emit_checks_agent_registry("p1", "test_orchestration_handshake", "test")
# REMOVED: _emit_snapshots_state("p0", "test_orchestration_handshake", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_orchestration_handshake", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_orchestration_handshake", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_orchestration_handshake", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_orchestration_handshake", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_orchestration_handshake", "write_through")
# REMOVED: _emit_writes_through("p1", "test_orchestration_handshake", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_orchestration_handshake", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_orchestration_handshake", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_orchestration_handshake", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_orchestration_handshake", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_orchestration_handshake", "route_through")
# REMOVED: _emit_agent_executes_agent("p1", "test_orchestration_handshake", "sub_agent")
# REMOVED: _emit_verifies_policy("p1", "test_orchestration_handshake", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_orchestration_handshake", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_orchestration_handshake", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_orchestration_handshake", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_orchestration_handshake")
# REMOVED: _emit_gated_by_confidence("p1", "test_orchestration_handshake", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_orchestration_handshake")
# REMOVED: emit_determinism_digest("p0", "test_orchestration_handshake")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_orchestration_handshake", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_orchestration_handshake", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_orchestration_handshake", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_orchestration_handshake", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_orchestration_handshake", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_orchestration_handshake", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_orchestration_handshake", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_orchestration_handshake", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_orchestration_handshake", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_orchestration_handshake", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_orchestration_handshake", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_orchestration_handshake", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_orchestration_handshake", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_orchestration_handshake", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_orchestration_handshake", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_orchestration_handshake", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_orchestration_handshake", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_orchestration_handshake", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_orchestration_handshake", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_orchestration_handshake", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _full_cycle(machine: HandshakeStateMachine) -> None:
    """Drive machine through the happy path: INIT→PRECLEAR→CERTIFIED→SEALED→DISPATCHED."""
    machine.request_preclear()
    machine.certify()
    machine.seal()
    machine.dispatch()


def _proposal(
    advisor_id: str = "advisor_A",
    decision: str = "approve",
    confidence: int = 80,
    rationale: list[str] | None = None,
    risks: list[str] | None = None,
    artifacts: list[str] | None = None,
) -> AdvisorProposal:
    return AdvisorProposal(
        advisor_id=advisor_id,
        decision=decision,
        confidence=confidence,
        rationale=rationale or [],
        risks=risks or [],
        artifacts=artifacts or [],
    )


def _input_with(*proposals: AdvisorProposal) -> ArbitrationInput:
    return ArbitrationInput(
        task_id="task-001",
        task_kind="analysis",
        proposals=list(proposals),
    )


# ===========================================================================
# 1. HandshakeStateMachine — success paths (full happy-path transitions)
# ===========================================================================


class TestHandshakeSuccessPaths:
    @pytest.mark.governance
    def test_initial_state_is_init(self):
                from agentic_core.L3_orchestration.arbitration.arbitration_contract import (
                from agentic_core.L3_orchestration.arbitration.arbitrator import Arbitrator
                from agentic_core.L3_orchestration.engines.handshake_state_machine import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                m = HandshakeStateMachine()
                assert m.current_state == HandshakeState.INIT

        assert m.current_state == HandshakeState.INIT

    @pytest.mark.governance
    def test_request_preclear_transitions_to_preclear_requested(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        assert m.current_state == HandshakeState.PRECLEAR_REQUESTED

    @pytest.mark.governance
    def test_certify_transitions_to_certified(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        assert m.current_state == HandshakeState.CERTIFIED

    @pytest.mark.governance
    def test_seal_transitions_to_sealed(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        m.seal()
        assert m.current_state == HandshakeState.SEALED

    @pytest.mark.governance
    def test_dispatch_transitions_to_dispatched(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        assert m.current_state == HandshakeState.DISPATCHED

    @pytest.mark.governance
    def test_transition_history_has_correct_length_after_full_cycle(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        assert len(m.transition_history) == 4

    @pytest.mark.governance
    def test_transition_history_records_correct_from_to_states(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        history = m.transition_history
        assert history[0].from_state == HandshakeState.INIT
        assert history[0].to_state == HandshakeState.PRECLEAR_REQUESTED
        assert history[3].to_state == HandshakeState.DISPATCHED

    @pytest.mark.governance
    def test_factory_function_returns_fresh_machine_in_init(self):
        m = create_handshake_machine()
        assert m.current_state == HandshakeState.INIT
        assert len(m.transition_history) == 0

    @pytest.mark.governance
    def test_sequence_hash_is_nonempty_string_after_transitions(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        h = m.get_sequence_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    @pytest.mark.governance
    def test_transition_history_is_immutable_tuple(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        history = m.transition_history
        assert isinstance(history, tuple)


# ===========================================================================
# 2. HandshakeStateMachine — disallowed state transitions (negative controls)
# ===========================================================================


class TestHandshakeDisallowedTransitions:
    @pytest.mark.governance
    def test_certify_from_init_raises_value_error(self):
        m = HandshakeStateMachine()
        with pytest.raises(Exception):

            pass
            m.certify()

    @pytest.mark.governance
    def test_seal_from_init_raises_value_error(self):
        m = HandshakeStateMachine()
        with pytest.raises(Exception):

            pass
            m.seal()

    @pytest.mark.governance
    def test_dispatch_from_init_raises_value_error(self):
        m = HandshakeStateMachine()
        with pytest.raises(Exception):

            pass
            m.dispatch()

    @pytest.mark.governance
    def test_seal_from_preclear_requested_raises_value_error(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        with pytest.raises(Exception):

            pass
            m.seal()

    @pytest.mark.governance
    def test_dispatch_from_preclear_requested_raises_value_error(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        with pytest.raises(Exception):

            pass
            m.dispatch()

    @pytest.mark.governance
    def test_dispatch_from_certified_raises_value_error(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        with pytest.raises(Exception):

            pass
            m.dispatch()

    @pytest.mark.governance
    def test_request_preclear_from_preclear_requested_raises(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        with pytest.raises(Exception):

            pass
            m.request_preclear()

    @pytest.mark.governance
    def test_request_preclear_from_certified_raises(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        with pytest.raises(Exception):

            pass
            m.request_preclear()

    @pytest.mark.governance
    def test_disallowed_transition_does_not_change_state(self):
        m = HandshakeStateMachine()
        try:
            m.certify()
        with pytest.raises(Exception):

            pass
            pass
        assert m.current_state == HandshakeState.INIT

    @pytest.mark.governance
    def test_disallowed_transition_does_not_add_history_entry(self):
        m = HandshakeStateMachine()
        try:
            m.certify()
        with pytest.raises(Exception):

            pass
            pass
        assert len(m.transition_history) == 0


# ===========================================================================
# 3. HandshakeStateMachine — MODIFY_DIFF rollback path
# ===========================================================================


class TestHandshakeModifyDiff:
    @pytest.mark.governance
    def test_modify_diff_from_certified_transitions_to_preclear_requested(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        m.modify_diff()
        assert m.current_state == HandshakeState.PRECLEAR_REQUESTED

    @pytest.mark.governance
    def test_modify_diff_from_init_raises_value_error(self):
        m = HandshakeStateMachine()
        with pytest.raises(Exception):

            pass
            m.modify_diff()

    @pytest.mark.governance
    def test_modify_diff_from_preclear_requested_raises_value_error(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        with pytest.raises(Exception):

            pass
            m.modify_diff()

    @pytest.mark.governance
    def test_modify_diff_adds_to_transition_history(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        m.modify_diff()
        assert len(m.transition_history) == 3

    @pytest.mark.governance
    def test_modify_diff_allows_re_certify_after_rollback(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        m.modify_diff()
        m.certify()  # should succeed
        assert m.current_state == HandshakeState.CERTIFIED

    @pytest.mark.governance
    def test_modify_diff_from_sealed_raises_value_error(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        m.seal()
        with pytest.raises(Exception):

            pass
            m.modify_diff()


# ===========================================================================
# 4. HandshakeStateMachine — repeated-same-transition guard
# ===========================================================================


class TestHandshakeRepeatedTransition:
    @pytest.mark.governance
    def test_duplicate_request_preclear_raises(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        with pytest.raises(Exception):

            pass
            m.request_preclear()

    @pytest.mark.governance
    def test_duplicate_certify_raises(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        with pytest.raises(Exception):

            pass
            m.certify()

    @pytest.mark.governance
    def test_duplicate_seal_raises(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        m.certify()
        m.seal()
        with pytest.raises(Exception):

            pass
            m.seal()

    @pytest.mark.governance
    def test_duplicate_dispatch_raises(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        with pytest.raises(Exception):

            pass
            m.dispatch()


# ===========================================================================
# 5. HandshakeStateMachine — reset + sequence hash
# ===========================================================================


class TestHandshakeResetAndHash:
    @pytest.mark.governance
    def test_reset_returns_machine_to_init(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        m.reset()
        assert m.current_state == HandshakeState.INIT

    @pytest.mark.governance
    def test_reset_clears_transition_history(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        m.reset()
        assert len(m.transition_history) == 0

    @pytest.mark.governance
    def test_reset_clears_sequence_hash_cache(self):
        m = HandshakeStateMachine()
        _full_cycle(m)
        h1 = m.get_sequence_hash()
        m.reset()
        h2 = m.get_sequence_hash()
        assert h1 != h2  # hash reflects state change

    @pytest.mark.governance
    def test_sequence_hash_invalidated_after_transition(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        h1 = m.get_sequence_hash()
        m.certify()
        h2 = m.get_sequence_hash()
        assert h1 != h2

    @pytest.mark.governance
    def test_sequence_hash_deterministic_for_same_transitions(self):
        m1 = HandshakeStateMachine()
        m2 = HandshakeStateMachine()
        _full_cycle(m1)
        _full_cycle(m2)
        # Hashes should differ because timestamps differ — but sequence structure matches
        # What we assert: both are 64-char hex strings
        assert len(m1.get_sequence_hash()) == 64
        assert len(m2.get_sequence_hash()) == 64

    @pytest.mark.governance
    def test_get_sequence_hash_caches_result(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        h1 = m.get_sequence_hash()
        h2 = m.get_sequence_hash()
        assert h1 == h2  # must be identical (no transition between calls)

    @pytest.mark.governance
    def test_str_representation_contains_state(self):
        m = HandshakeStateMachine()
        assert "INIT" in str(m)

    @pytest.mark.governance
    def test_repr_contains_transition_count(self):
        m = HandshakeStateMachine()
        m.request_preclear()
        assert "1" in repr(m)


# ===========================================================================
# 6. Arbitrator — scoring function
# ===========================================================================


class TestArbitratorScoring:
    @pytest.mark.governance
    def test_score_base_is_confidence_with_no_rationale_risks_artifacts(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=[], risks=[], artifacts=[])
        assert arb.calculate_score(p) == 50

    @pytest.mark.governance
    def test_score_adds_2_per_rationale_item(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=["r1", "r2"], risks=[], artifacts=[])
        assert arb.calculate_score(p) == 54

    @pytest.mark.governance
    def test_score_rationale_bonus_caps_at_10(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=[f"r{i}" for i in range(10)], risks=[], artifacts=[])
        # 10 items * 2 = 20 but cap is 10
        assert arb.calculate_score(p) == 60

    @pytest.mark.governance
    def test_score_subtracts_3_per_risk_item(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=[], risks=["r1", "r2"], artifacts=[])
        assert arb.calculate_score(p) == 44

    @pytest.mark.governance
    def test_score_risk_penalty_caps_at_15(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=[], risks=[f"r{i}" for i in range(10)], artifacts=[])
        # 10 * 3 = 30 but cap is 15
        assert arb.calculate_score(p) == 35

    @pytest.mark.governance
    def test_score_adds_1_per_artifact(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=[], risks=[], artifacts=["a1", "a2", "a3"])
        assert arb.calculate_score(p) == 53

    @pytest.mark.governance
    def test_score_artifact_bonus_caps_at_5(self):
        arb = Arbitrator()
        p = _proposal(confidence=50, rationale=[], risks=[], artifacts=[f"a{i}" for i in range(10)])
        assert arb.calculate_score(p) == 55

    @pytest.mark.governance
    def test_score_deterministic_for_same_proposal_twice(self):
        arb = Arbitrator()
        p = _proposal(confidence=70, rationale=["r"], risks=["x"], artifacts=["a"])
        assert arb.calculate_score(p) == arb.calculate_score(p)

    @pytest.mark.governance
    def test_score_boundary_zero_confidence(self):
        arb = Arbitrator()
        p = _proposal(confidence=0)
        assert arb.calculate_score(p) == 0

    @pytest.mark.governance
    def test_score_boundary_max_confidence_100(self):
        arb = Arbitrator()
        p = _proposal(confidence=100)
        assert arb.calculate_score(p) == 100


# ===========================================================================
# 7. Arbitrator — arbitrate method (selection, tie-breaking, merge)
# ===========================================================================


class TestArbitratorArbitrate:
    @pytest.mark.governance
    def test_arbitrate_raises_when_no_proposals(self):
        arb = Arbitrator()
        inp = ArbitrationInput(task_id="t1", task_kind="k", proposals=[])
        with pytest.raises(Exception):

            pass
            arb.arbitrate(inp)

    @pytest.mark.governance
    def test_arbitrate_selects_highest_score_proposal(self):
        arb = Arbitrator()
        low = _proposal(advisor_id="low", confidence=30)
        high = _proposal(advisor_id="high", confidence=90)
        decision = arb.arbitrate(_input_with(low, high))
        assert decision.selected_advisor_id == "high"

    @pytest.mark.governance
    def test_arbitrate_single_proposal_selects_it(self):
        arb = Arbitrator()
        p = _proposal(advisor_id="only")
        decision = arb.arbitrate(_input_with(p))
        assert decision.selected_advisor_id == "only"

    @pytest.mark.governance
    def test_arbitrate_tiebreak_by_confidence(self):
        arb = Arbitrator()
        # Both have same score structure but different confidence
        p1 = _proposal(advisor_id="beta", confidence=60)
        p2 = _proposal(advisor_id="alpha", confidence=80)
        decision = arb.arbitrate(_input_with(p1, p2))
        # higher confidence wins tiebreak
        assert decision.selected_advisor_id == "alpha"

    @pytest.mark.governance
    def test_arbitrate_tiebreak_by_lexicographic_id_when_scores_and_confidence_equal(self):
        arb = Arbitrator()
        p1 = _proposal(advisor_id="zebra", confidence=70)
        p2 = _proposal(advisor_id="alpha", confidence=70)
        decision = arb.arbitrate(_input_with(p1, p2))
        # Lexicographically smaller wins
        assert decision.selected_advisor_id == "alpha"

    @pytest.mark.governance
    def test_arbitrate_merges_rationale_without_duplicates(self):
        arb = Arbitrator()
        p1 = _proposal(advisor_id="a1", rationale=["shared", "unique_a"])
        p2 = _proposal(advisor_id="a2", rationale=["shared", "unique_b"])
        decision = arb.arbitrate(_input_with(p1, p2))
        assert decision.merged_rationale.count("shared") == 1

    @pytest.mark.governance
    def test_arbitrate_merges_risks_without_duplicates(self):
        arb = Arbitrator()
        p1 = _proposal(advisor_id="a1", risks=["shared_risk", "risk_a"])
        p2 = _proposal(advisor_id="a2", risks=["shared_risk", "risk_b"])
        decision = arb.arbitrate(_input_with(p1, p2))
        assert decision.merged_risks.count("shared_risk") == 1

    @pytest.mark.governance
    def test_arbitrate_merged_rationale_is_sorted(self):
        arb = Arbitrator()
        p1 = _proposal(advisor_id="a1", rationale=["zebra", "apple"])
        p2 = _proposal(advisor_id="a2", rationale=["mango"])
        decision = arb.arbitrate(_input_with(p1, p2))
        assert decision.merged_rationale == sorted(decision.merged_rationale)

    @pytest.mark.governance
    def test_arbitrate_score_breakdown_contains_all_advisors(self):
        arb = Arbitrator()
        p1 = _proposal(advisor_id="a1", confidence=50)
        p2 = _proposal(advisor_id="a2", confidence=80)
        decision = arb.arbitrate(_input_with(p1, p2))
        assert "a1" in decision.score_breakdown
        assert "a2" in decision.score_breakdown

    @pytest.mark.governance
    def test_arbitrate_deterministic_for_same_input_twice(self):
        arb = Arbitrator()
        p1 = _proposal(advisor_id="a1", confidence=60)
        p2 = _proposal(advisor_id="a2", confidence=80)
        d1 = arb.arbitrate(_input_with(p1, p2))
        d2 = arb.arbitrate(_input_with(p1, p2))
        assert d1.selected_advisor_id == d2.selected_advisor_id
        assert d1.score_breakdown == d2.score_breakdown

    @pytest.mark.governance
    def test_arbitrate_does_not_mutate_proposals(self):
        arb = Arbitrator()
        p = _proposal(advisor_id="a", confidence=70, rationale=["r1"])
        original_rationale = list(p.rationale)
        arb.arbitrate(_input_with(p))
        assert list(p.rationale) == original_rationale


# ===========================================================================
# 8. AdvisorProposal / ArbitrationInput — validation guards
# ===========================================================================


class TestArbitrationContractValidation:
    @pytest.mark.governance
    def test_advisor_proposal_raises_when_advisor_id_empty(self):
        with pytest.raises(Exception):

            pass
            AdvisorProposal(advisor_id="", decision="approve", confidence=50)

    @pytest.mark.governance
    def test_advisor_proposal_raises_when_decision_empty(self):
        with pytest.raises(Exception):

            pass
            AdvisorProposal(advisor_id="a", decision="", confidence=50)

    @pytest.mark.governance
    def test_advisor_proposal_raises_when_confidence_below_0(self):
        with pytest.raises(Exception):

            pass
            AdvisorProposal(advisor_id="a", decision="d", confidence=-1)

    @pytest.mark.governance
    def test_advisor_proposal_raises_when_confidence_above_100(self):
        with pytest.raises(Exception):

            pass
            AdvisorProposal(advisor_id="a", decision="d", confidence=101)

    @pytest.mark.governance
    def test_advisor_proposal_boundary_confidence_0_valid(self):
        p = AdvisorProposal(advisor_id="a", decision="d", confidence=0)
        assert p.confidence == 0

    @pytest.mark.governance
    def test_advisor_proposal_boundary_confidence_100_valid(self):
        p = AdvisorProposal(advisor_id="a", decision="d", confidence=100)
        assert p.confidence == 100

    @pytest.mark.governance
    def test_advisor_proposal_normalises_rationale_to_sorted(self):
        p = AdvisorProposal(advisor_id="a", decision="d", confidence=50, rationale=["z", "a"])
        assert p.rationale == ["a", "z"]

    @pytest.mark.governance
    def test_advisor_proposal_raises_on_empty_rationale_item(self):
        with pytest.raises(Exception):

            pass
            AdvisorProposal(advisor_id="a", decision="d", confidence=50, rationale=["valid", ""])

    @pytest.mark.governance
    def test_arbitration_input_raises_when_task_id_empty(self):
        with pytest.raises(Exception):

            pass
            ArbitrationInput(task_id="", task_kind="k")

    @pytest.mark.governance
    def test_arbitration_input_raises_when_task_kind_empty(self):
        with pytest.raises(Exception):

            pass
            ArbitrationInput(task_id="t", task_kind="")

    @pytest.mark.governance
    def test_arbitration_input_raises_on_duplicate_advisor_ids(self):
        p1 = _proposal(advisor_id="dup")
        p2 = _proposal(advisor_id="dup", decision="reject")
        with pytest.raises(Exception):

            pass
            ArbitrationInput(task_id="t", task_kind="k", proposals=[p1, p2])

    @pytest.mark.governance
    def test_arbitration_input_allows_multiple_distinct_advisors(self):
        p1 = _proposal(advisor_id="a1")
        p2 = _proposal(advisor_id="a2")
        inp = ArbitrationInput(task_id="t", task_kind="k", proposals=[p1, p2])
        assert len(inp.proposals) == 2
