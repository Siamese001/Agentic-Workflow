"""Unit tests for agentic_core.runtime.contracts.x1_checkout_result.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 Exit/X3 spine.
``x1_checkout_result`` (fan_in=15, L_RUNTIME) carries the ten X1A..X1J gate
verdicts. AG-4 invariant: UNKNOWN is NEVER PASS; NOT_APPLICABLE needs a reason.
Exhaustive coverage of the enums, X1Item guards, and X1CheckoutResult roll-up.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.x1_checkout_result import (
    X1_PASSING_VERDICTS,
    X1CheckoutResult,
    X1EvaluatorType,
    X1Item,
    X1Verdict,
)

_GATE_IDS = [f"X1{c}" for c in "ABCDEFGHIJ"]


def _pass(gate_id: str) -> X1Item:
    return X1Item(gate_id=gate_id, verdict=X1Verdict.PASS)


def _all_pass_result(**overrides: object) -> X1CheckoutResult:
    slots = {
        "x1a_todays_rules": _pass("X1A"),
        "x1b_answered_it": _pass("X1B"),
        "x1c_safe_to_leave": _pass("X1C"),
        "x1d_answer_good": _pass("X1D"),
        "x1e_trajectory_ok": _pass("X1E"),
        "x1f_story_adds_up": _pass("X1F"),
        "x1g_replay_eligible": _pass("X1G"),
        "x1h_observable": _pass("X1H"),
        "x1i_consistent_across_runs": _pass("X1I"),
        "x1j_write_eligibility": _pass("X1J"),
    }
    slots.update(overrides)
    return X1CheckoutResult(**slots)  # type: ignore[arg-type]


class TestEnums:
    def test_verdict_members(self) -> None:
        assert {v.value for v in X1Verdict} == {"PASS", "FAIL", "WARN", "UNKNOWN", "NOT_APPLICABLE"}

    def test_evaluator_members(self) -> None:
        assert {e.value for e in X1EvaluatorType} == {
            "code", "LLM-judge", "hybrid", "human-calibrated", "unknown",
        }

    def test_only_pass_is_passing_verdict(self) -> None:
        assert X1_PASSING_VERDICTS == frozenset({X1Verdict.PASS})


class TestX1Item:
    def test_defaults(self) -> None:
        item = X1Item(gate_id="X1A", verdict=X1Verdict.PASS)
        assert item.confidence == 1.0
        assert item.evaluator_type == X1EvaluatorType.CODE
        assert item.evidence_refs == ()

    @pytest.mark.parametrize("gate_id", _GATE_IDS)
    def test_all_valid_gate_ids_accepted(self, gate_id: str) -> None:
        assert X1Item(gate_id=gate_id, verdict=X1Verdict.PASS).gate_id == gate_id

    @pytest.mark.parametrize("bad", ["X1K", "X2A", "x1a", "A1X", ""])
    def test_invalid_gate_id_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="X1A..X1J"):
            X1Item(gate_id=bad, verdict=X1Verdict.PASS)

    def test_not_applicable_without_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires a reason"):
            X1Item(gate_id="X1D", verdict=X1Verdict.NOT_APPLICABLE)

    def test_not_applicable_with_reason_ok(self) -> None:
        item = X1Item(gate_id="X1D", verdict=X1Verdict.NOT_APPLICABLE, not_applicable_reason="cache-hit route")
        assert item.verdict == X1Verdict.NOT_APPLICABLE

    @pytest.mark.parametrize(
        "verdict,passing",
        [
            (X1Verdict.PASS, True),
            (X1Verdict.FAIL, False),
            (X1Verdict.WARN, False),
            (X1Verdict.UNKNOWN, False),
        ],
    )
    def test_is_passing(self, verdict: X1Verdict, passing: bool) -> None:
        assert X1Item(gate_id="X1A", verdict=verdict).is_passing() is passing

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _pass("X1A").verdict = X1Verdict.FAIL  # type: ignore[misc]


class TestX1CheckoutResultDefaults:
    def test_default_slots_are_unknown(self) -> None:
        r = X1CheckoutResult()
        assert len(r.items()) == 10
        assert all(item.verdict == X1Verdict.UNKNOWN for item in r.items())
        assert r.x1a_todays_rules.decisive_reason == "not yet evaluated"

    def test_items_in_canonical_order(self) -> None:
        r = X1CheckoutResult()
        assert tuple(i.gate_id for i in r.items()) == tuple(_GATE_IDS)

    def test_default_is_not_overall_pass(self) -> None:
        # All-UNKNOWN must NOT pass (AG-4: UNKNOWN never PASS).
        assert X1CheckoutResult().is_overall_pass() is False


class TestX1CheckoutResultRollup:
    def test_all_pass_is_overall_pass(self) -> None:
        assert _all_pass_result().is_overall_pass() is True

    def test_not_applicable_is_non_blocking(self) -> None:
        na = X1Item(gate_id="X1D", verdict=X1Verdict.NOT_APPLICABLE, not_applicable_reason="n/a route")
        assert _all_pass_result(x1d_answer_good=na).is_overall_pass() is True

    def test_single_fail_blocks(self) -> None:
        fail = X1Item(gate_id="X1B", verdict=X1Verdict.FAIL)
        assert _all_pass_result(x1b_answered_it=fail).is_overall_pass() is False

    def test_first_blocking_gate(self) -> None:
        fail = X1Item(gate_id="X1C", verdict=X1Verdict.FAIL)
        blocker = _all_pass_result(x1c_safe_to_leave=fail).first_blocking_gate()
        assert blocker is not None and blocker.gate_id == "X1C"

    def test_first_blocking_gate_none_when_all_pass(self) -> None:
        assert _all_pass_result().first_blocking_gate() is None


class TestX1ConsistencyInvariants:
    def test_x1g_pass_requires_replay_manifest(self) -> None:
        r = _all_pass_result(replay_manifest_ref="")
        assert r.x1g_replay_eligibility_is_consistent() is False
        r2 = _all_pass_result(replay_manifest_ref="manifest-1")
        assert r2.x1g_replay_eligibility_is_consistent() is True

    def test_x1g_non_pass_is_vacuously_consistent(self) -> None:
        unknown_g = X1Item(gate_id="X1G", verdict=X1Verdict.UNKNOWN, unknown_reason="n")
        r = _all_pass_result(x1g_replay_eligible=unknown_g, replay_manifest_ref="")
        assert r.x1g_replay_eligibility_is_consistent() is True

    def test_x1h_pass_requires_otel_spans(self) -> None:
        assert _all_pass_result(otel_span_refs=()).x1h_observability_is_consistent() is False
        assert _all_pass_result(otel_span_refs=("span-1",)).x1h_observability_is_consistent() is True

    def test_x1d_pass_requires_intent_evidence_output(self) -> None:
        # X1D PASS with no surrounding refs → inconsistent.
        assert _all_pass_result().x1d_groundedness_has_required_refs() is False
        ok = _all_pass_result(intent_ref="i", evidence_refs=("e",), output_ref="o")
        assert ok.x1d_groundedness_has_required_refs() is True

    def test_x1d_non_pass_is_vacuously_consistent(self) -> None:
        na = X1Item(gate_id="X1D", verdict=X1Verdict.NOT_APPLICABLE, not_applicable_reason="n/a")
        assert _all_pass_result(x1d_answer_good=na).x1d_groundedness_has_required_refs() is True
