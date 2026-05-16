"""Tests for ``aggregate_x1_for_exit``."""

from __future__ import annotations

from agentic_core.runtime.contracts.x1_checkout_result import (
    X1CheckoutResult,
    X1Item,
    X1Verdict,
)
from agentic_core.runtime.exit.exit_disposition import X3A_DENY_REROUTE, X3D_ALLOW_FINISH
from agentic_core.runtime.exit.x2_aggregator import aggregate_x1_for_exit


def _neutral_pass_checkout() -> X1CheckoutResult:
    na = lambda gid: X1Item(
        gate_id=gid,
        verdict=X1Verdict.NOT_APPLICABLE,
        not_applicable_reason="neutral compatibility envelope",
    )
    return X1CheckoutResult(
        x1a_todays_rules=X1Item(gate_id="X1A", verdict=X1Verdict.PASS),
        x1b_answered_it=X1Item(gate_id="X1B", verdict=X1Verdict.PASS),
        x1c_safe_to_leave=X1Item(gate_id="X1C", verdict=X1Verdict.PASS),
        x1d_answer_good=na("X1D"),
        x1e_trajectory_ok=na("X1E"),
        x1f_story_adds_up=na("X1F"),
        x1g_replay_eligible=na("X1G"),
        x1h_observable=na("X1H"),
        x1i_consistent_across_runs=na("X1I"),
        x1j_write_eligibility=na("X1J"),
    )


def test_aggregate_allow_finish_when_x1_passes() -> None:
    checkout = _neutral_pass_checkout()
    assert checkout.is_overall_pass()
    x2 = aggregate_x1_for_exit(checkout)
    assert x2.disposition_candidate == X3D_ALLOW_FINISH
    assert x2.emits_final_x3 is False


def test_aggregate_deny_on_material_deterministic_failure() -> None:
    na = lambda gid: X1Item(
        gate_id=gid,
        verdict=X1Verdict.NOT_APPLICABLE,
        not_applicable_reason="not evaluated in this smoke case",
    )
    checkout = X1CheckoutResult(
        x1a_todays_rules=X1Item(gate_id="X1A", verdict=X1Verdict.PASS),
        x1b_answered_it=X1Item(gate_id="X1B", verdict=X1Verdict.PASS),
        x1c_safe_to_leave=X1Item(gate_id="X1C", verdict=X1Verdict.FAIL),
        x1d_answer_good=na("X1D"),
        x1e_trajectory_ok=na("X1E"),
        x1f_story_adds_up=na("X1F"),
        x1g_replay_eligible=na("X1G"),
        x1h_observable=na("X1H"),
        x1i_consistent_across_runs=na("X1I"),
        x1j_write_eligibility=na("X1J"),
    )
    assert not checkout.is_overall_pass()
    x2 = aggregate_x1_for_exit(checkout)
    assert x2.disposition_candidate == X3A_DENY_REROUTE
