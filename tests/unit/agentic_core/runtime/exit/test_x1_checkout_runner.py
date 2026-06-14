"""Wave 6.1 P2 hotspot tests — agentic_core.runtime.exit.x1_checkout_runner.

Covers the deterministic ``run_ag5_x1_checkout`` evaluator wiring over a v6
ExitReviewPacket: X1A policy-alignment, X1B output-present, X1C neutral
envelope, X1G replay-receipt, X1H otel-span coverage, plus the fixed
NOT_APPLICABLE gates and identity propagation. Pure function — no live deps.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
from agentic_core.runtime.contracts.x1_checkout_result import (
    X1CheckoutResult,
    X1Verdict,
)
from agentic_core.runtime.exit.x1_checkout_runner import run_ag5_x1_checkout


_REQUIRED_SPAN_KEYS = {
    "trace_root",
    "route_contract",
    "tool_invocations",
    "evidence_contracts",
    "step_outputs",
    "exit_disposition",
}


def _packet(**overrides) -> ExitReviewPacket:
    base = {"source_type": SourceType.RET_FALLBACK}
    base.update(overrides)
    return ExitReviewPacket(**base)


class TestReturnShape:
    def test_returns_x1_checkout_result(self) -> None:
        result = run_ag5_x1_checkout(_packet())
        assert isinstance(result, X1CheckoutResult)

    def test_identity_propagated(self) -> None:
        result = run_ag5_x1_checkout(
            _packet(request_id="req-1", run_id="run-1", trace_root="trace-1")
        )
        assert result.request_id == "req-1"
        assert result.run_id == "run-1"
        assert result.trace_root == "trace-1"


class TestX1APolicyAlignment:
    def test_aligned_policy_hash_passes(self) -> None:
        packet = _packet(
            policy_hash="ph-123",
            route_contract={"policy_hash": "ph-123"},
        )
        assert run_ag5_x1_checkout(packet).x1a_todays_rules.verdict is X1Verdict.PASS

    def test_mismatched_policy_hash_fails(self) -> None:
        packet = _packet(
            policy_hash="ph-123",
            route_contract={"policy_hash": "other"},
        )
        assert run_ag5_x1_checkout(packet).x1a_todays_rules.verdict is X1Verdict.FAIL

    def test_empty_policy_hash_fails(self) -> None:
        packet = _packet(policy_hash="", route_contract={"policy_hash": ""})
        assert run_ag5_x1_checkout(packet).x1a_todays_rules.verdict is X1Verdict.FAIL


class TestX1BOutputPresent:
    def test_output_present_passes(self) -> None:
        result = run_ag5_x1_checkout(_packet(output={"answer": "x"}))
        assert result.x1b_answered_it.verdict is X1Verdict.PASS

    def test_empty_output_fails(self) -> None:
        result = run_ag5_x1_checkout(_packet(output={}))
        assert result.x1b_answered_it.verdict is X1Verdict.FAIL


class TestX1CNeutralEnvelope:
    def test_neutral_binding_and_answer_only_passes(self) -> None:
        packet = _packet(
            source_type=SourceType.APP_BINDING_COMPATIBILITY_PACKAGE,
            terminal_class="answer_only",
        )
        assert run_ag5_x1_checkout(packet).x1c_safe_to_leave.verdict is X1Verdict.PASS

    def test_non_neutral_binding_fails(self) -> None:
        packet = _packet(
            source_type=SourceType.RET_FALLBACK,
            terminal_class="answer_only",
        )
        item = run_ag5_x1_checkout(packet).x1c_safe_to_leave
        assert item.verdict is X1Verdict.FAIL
        assert item.decisive_reason == "envelope_requires_review"

    def test_neutral_binding_wrong_terminal_class_fails(self) -> None:
        packet = _packet(
            source_type=SourceType.APP_BINDING_COMPATIBILITY_PACKAGE,
            terminal_class="with_state_diff",
        )
        assert run_ag5_x1_checkout(packet).x1c_safe_to_leave.verdict is X1Verdict.FAIL


class TestX1HObservability:
    def test_full_span_coverage_passes(self) -> None:
        packet = _packet(otel_spans={"spans": {k: 1 for k in _REQUIRED_SPAN_KEYS}})
        assert run_ag5_x1_checkout(packet).x1h_observable.verdict is X1Verdict.PASS

    def test_partial_span_coverage_fails(self) -> None:
        packet = _packet(otel_spans={"spans": {"trace_root": 1}})
        assert run_ag5_x1_checkout(packet).x1h_observable.verdict is X1Verdict.FAIL

    def test_missing_spans_fails(self) -> None:
        assert run_ag5_x1_checkout(_packet()).x1h_observable.verdict is X1Verdict.FAIL


class TestX1GReplayEligibility:
    def test_replay_receipts_present_passes(self) -> None:
        packet = _packet(exec_trace={"replay_receipts_present": True})
        result = run_ag5_x1_checkout(packet)
        assert result.x1g_replay_eligible.verdict is X1Verdict.PASS
        assert result.replay_manifest_ref == "replay-manifest:native-proof"

    def test_no_replay_receipts_fails(self) -> None:
        result = run_ag5_x1_checkout(_packet(exec_trace={}))
        assert result.x1g_replay_eligible.verdict is X1Verdict.FAIL
        assert result.replay_manifest_ref == ""


class TestNotApplicableGates:
    @pytest.mark.parametrize(
        "attr",
        [
            "x1d_answer_good",
            "x1e_trajectory_ok",
            "x1f_story_adds_up",
            "x1i_consistent_across_runs",
            "x1j_write_eligibility",
        ],
    )
    def test_na_gates_are_not_applicable_with_reason(self, attr: str) -> None:
        item = getattr(run_ag5_x1_checkout(_packet()), attr)
        assert item.verdict is X1Verdict.NOT_APPLICABLE
        assert item.not_applicable_reason == "neutral compatibility envelope"


class TestOtelSpanRefs:
    def test_span_refs_populated_when_observable(self) -> None:
        packet = _packet(otel_spans={"spans": {k: 1 for k in _REQUIRED_SPAN_KEYS}})
        result = run_ag5_x1_checkout(packet)
        assert result.otel_span_refs == ("otel:span-bundle-present",)

    def test_span_refs_empty_when_not_observable(self) -> None:
        assert run_ag5_x1_checkout(_packet()).otel_span_refs == ()
