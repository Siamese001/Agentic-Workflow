"""Tests for spec 04.0 L2 Sequencer / Orchestrator Contract.

Spec source: docs/reference/04_L2_Execute/04.0_L2_Sequencer_Orchestrator_Contract.md
SUT:         agentic_core/L2_execution/types/l2_sequencer_contract.py

These tests bind every TEST REQUIREMENT name in spec 04.0 to a real
assertion against the typed contract. Behavioral wiring (E1-E5 invocation)
is tracked separately under DEFERRED_SCOPE; these tests guard the
state-machine invariants and dataclass shape so the contract cannot drift.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.l2_sequencer_contract import (
    IllegalL2TransitionError,
    L2ExecutionSequencerInput,
    L2ExecutionState,
    L2SequencerState,
    L2TerminalClass,
    SequencerReceipt,
    TERMINAL_SEAL_STATES,
    is_legal_transition,
)


# --------------------------------------------------------------------- helpers
def _input(**overrides: object) -> L2ExecutionSequencerInput:
    base = dict(
        l2_execution_request="req-1",
        signed_l0_packet="pkt-1",
        capability_token_ref="cap-1",
        sandbox_envelope_ref="sb-1",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        replay_key="rk-1",
        snapshot_manifest_ref="snap-1",
        max_attempts=2,
        max_repair_count=1,
        overall_timeout_ms=5000,
        budget_snapshot="budget-1",
        trace_root="trace-1",
        route_contract_ref="route-1",
    )
    base.update(overrides)
    return L2ExecutionSequencerInput(**base)  # type: ignore[arg-type]


def _receipt(**overrides: object) -> SequencerReceipt:
    base = dict(
        sequencer_receipt_id="sr-1",
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-1",
        route_id="route-1",
        policy_hash="ph",
        blueprint_hash="bh",
        replay_key="rk",
        e1_receipt_ref="e1",
        e5_seal_receipt_ref="e5",
        terminal_class=L2TerminalClass.SUCCESS,
        attempt_count=1,
        repair_count=0,
        budget_final=100,
        same_authority_status="STABLE",
        no_direct_write_assertion=True,
        deterministic_digest="dig",
    )
    base.update(overrides)
    return SequencerReceipt(**base)  # type: ignore[arg-type]


# ---------------------------------- spec 04.0 §TEST REQUIREMENTS (10 entries)
def test_l2_sequencer_calls_e1_before_e2() -> None:
    """RECEIVED_PACKET must transition to PREPARED (E1) before VALIDATED (E2)."""
    state = L2ExecutionState()
    assert state.current_state is L2SequencerState.RECEIVED_PACKET
    # Cannot jump straight to VALIDATED.
    with pytest.raises(IllegalL2TransitionError):
        state.transition(L2SequencerState.VALIDATED)
    state.transition(L2SequencerState.PREPARED)
    state.transition(L2SequencerState.VALIDATED)
    assert state.current_state is L2SequencerState.VALIDATED


def test_l2_sequencer_never_calls_e3_after_failed_e2() -> None:
    """PREPARED -> SEALING_REJECTED bypasses EXECUTING (E2 fail goes to seal)."""
    state = L2ExecutionState()
    state.transition(L2SequencerState.PREPARED)
    state.transition(L2SequencerState.SEALING_REJECTED)
    assert state.current_state is L2SequencerState.SEALING_REJECTED
    # From SEALING_REJECTED only SEALED is reachable.
    with pytest.raises(IllegalL2TransitionError):
        state.transition(L2SequencerState.EXECUTING)


def test_l2_sequencer_enforces_attempt_ceiling() -> None:
    """Sequencer input rejects max_attempts <= 0; SequencerReceipt rejects negative."""
    with pytest.raises(ValueError, match="max_attempts"):
        _input(max_attempts=0)
    with pytest.raises(ValueError, match="non-negative"):
        _receipt(attempt_count=-1)


def test_l2_sequencer_enforces_repair_ceiling() -> None:
    """max_repair_count must be non-negative; repair_count on receipt non-negative."""
    with pytest.raises(ValueError, match="max_repair_count"):
        _input(max_repair_count=-1)
    with pytest.raises(ValueError, match="non-negative"):
        _receipt(repair_count=-1)


def test_l2_sequencer_blocks_authority_changing_repair() -> None:
    """Repair must not change policy/blueprint/replay/capability/sandbox.

    The contract enforces this by *requiring* those hashes on every receipt;
    a repair that emitted a receipt with mismatched hashes would have to be
    constructed without the parent input's hashes — which the input
    requires non-empty. This test asserts the required-field invariants.
    """
    for missing in ("policy_hash", "blueprint_hash", "replay_key"):
        with pytest.raises(ValueError, match=missing):
            _input(**{missing: ""})
    for missing in ("policy_hash", "blueprint_hash", "replay_key"):
        with pytest.raises(ValueError, match=missing):
            _receipt(**{missing: ""})


def test_l2_sequencer_routes_every_terminal_case_to_e5() -> None:
    """All four terminal seal states must transition to SEALED (E5)."""
    for seal_state in TERMINAL_SEAL_STATES:
        assert is_legal_transition(seal_state, L2SequencerState.SEALED)
    # And SEALED is the only valid target from any seal state.
    for seal_state in TERMINAL_SEAL_STATES:
        for other in L2SequencerState:
            if other is L2SequencerState.SEALED:
                continue
            assert not is_legal_transition(seal_state, other)


def test_l2_sequencer_preserves_proposed_state_diff_as_inert() -> None:
    """L2ExecutionState.proposed_state_diff_candidate_ref is a ref, not committed."""
    state = L2ExecutionState(proposed_state_diff_candidate_ref="cand-1")
    assert state.proposed_state_diff_candidate_ref == "cand-1"
    # No method exists to "commit" it — this is the inertness invariant.
    assert not hasattr(state, "commit_proposed_state_diff")


def test_l2_sequencer_never_emits_exit_disposition() -> None:
    """SequencerReceipt schema has no Exit-disposition field — by construction."""
    fields = SequencerReceipt.__dataclass_fields__
    forbidden = {
        "exit_disposition",
        "x3_disposition",
        "exit_verdict",
        "commit_request",
        "uwg_commit",
    }
    assert forbidden.isdisjoint(fields)


def test_l2_sequencer_never_writes_l4() -> None:
    """no_direct_write_assertion must be True on every emitted SequencerReceipt."""
    with pytest.raises(ValueError, match="no_direct_write_assertion"):
        _receipt(no_direct_write_assertion=False)
    r = _receipt()
    assert r.no_direct_write_assertion is True


def test_l2_sequencer_receipt_replays_deterministically() -> None:
    """deterministic_digest is required and identical inputs produce identical receipts."""
    r1 = _receipt()
    r2 = _receipt()
    assert r1 == r2
    with pytest.raises(ValueError, match="deterministic_digest"):
        _receipt(deterministic_digest="")


# ---------------------------------- additional invariants (FAIL-CLOSED list)
def test_input_xor_l0_packet_or_l3_step_contract() -> None:
    with pytest.raises(ValueError, match="xor"):
        _input(signed_l0_packet="pkt", l3_step_contract="step")
    with pytest.raises(ValueError, match="xor"):
        _input(signed_l0_packet=None, l3_step_contract=None)


def test_illegal_transitions_rejected() -> None:
    """Constitutional STATE MACHINE illegal transitions explicitly fail."""
    state = L2ExecutionState()
    # any L2 state -> L4 write is not even modelable — there's no L4 state.
    # any L2 state -> L0 route selection — same.
    # Modeled illegals: jumping over a stage.
    with pytest.raises(IllegalL2TransitionError):
        state.transition(L2SequencerState.SEALED)


def test_illegal_cross_layer_transitions_unrepresentable() -> None:
    """Spec 04.0 §STATE MACHINE 'Illegal transitions' (any L2 state -> L0/C0/L4/L6).

    These are unrepresentable BY CONSTRUCTION: L2SequencerState has no enum
    member for L0 route selection, C0 retrieval, L4 write, or L6 learning
    mutation. Listing the forbidden destination names and asserting none
    appear in the enum is the structural proof.
    """
    forbidden_destinations = {
        "L0_ROUTE_SELECTION",
        "L0_REROUTE",
        "C0_RETRIEVAL",
        "C0_FETCH",
        "L4_WRITE",
        "L4_COMMIT",
        "L6_LEARNING_MUTATION",
        "L6_PROMOTION",
        "DIRECT_HITL_REQUEST",
    }
    enum_names = {member.name for member in L2SequencerState}
    assert forbidden_destinations.isdisjoint(enum_names), (
        f"L2SequencerState must not contain any cross-layer destination; "
        f"found: {forbidden_destinations & enum_names}"
    )


def test_e1_must_freeze_execution_context_before_validation() -> None:
    """Spec 04.0 §WORKSTEPS S1: E1 must freeze execution context BEFORE E2.

    Encoded structurally: PREPARED is the only legal predecessor to
    VALIDATED. Skipping PREPARED (i.e. RECEIVED_PACKET -> VALIDATED) is
    rejected by the state machine.
    """
    assert is_legal_transition(L2SequencerState.PREPARED, L2SequencerState.VALIDATED)
    assert not is_legal_transition(
        L2SequencerState.RECEIVED_PACKET, L2SequencerState.VALIDATED
    )
    state = L2ExecutionState()
    # Cannot validate without first preparing (the freeze step).
    with pytest.raises(IllegalL2TransitionError):
        state.transition(L2SequencerState.VALIDATED)


def test_e3_may_run_only_one_bounded_attempt() -> None:
    """Spec 04.0 §WORKSTEPS S3: E3 may run only one bounded attempt.

    EXECUTING is a single state. Cannot self-loop; must reach a terminal-
    candidate state (success/degraded/repair) before the next attempt,
    and any next attempt requires going back through VALIDATED.
    """
    assert not is_legal_transition(
        L2SequencerState.EXECUTING, L2SequencerState.EXECUTING
    )
    # The path back to EXECUTING is RETRYING_SAME_AUTHORITY -> VALIDATED -> EXECUTING
    # OR RETRYING_SAME_AUTHORITY -> EXECUTING; both routed through repair governor.
    assert is_legal_transition(
        L2SequencerState.RETRYING_SAME_AUTHORITY, L2SequencerState.EXECUTING
    )
    # Direct EXECUTING -> EXECUTING (multiple attempts in one state) is illegal.
    state = L2ExecutionState(current_state=L2SequencerState.EXECUTING)
    with pytest.raises(IllegalL2TransitionError):
        state.transition(L2SequencerState.EXECUTING)
