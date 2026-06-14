"""Unit tests for agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
The X1 checkout adapter is the AG-5 bridge: it converts legacy ``GateVerdict``
(Exit-emit layer) into ``X1Item`` (Exit-input layer) and assembles a
``X1CheckoutResult`` from a verdict list + ``ExitReviewPacket``, preserving the
AG-4 invariants (UNKNOWN carries unknown_reason, NOT_APPLICABLE carries
not_applicable_reason). Covers the verdict/grader-type mapping tables, the
per-gate conversion, the full ``build_x1_checkout_result`` ref-forwarding, and
the ``x1_checkout_to_gate_verdicts`` round-trip.

Real ``GateVerdict``/``ExitReviewPacket`` objects — no mocks.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
    build_x1_checkout_result,
    gate_verdict_to_x1_item,
    x1_checkout_to_gate_verdicts,
)
from agentic_core.runtime.contracts.x1_checkout_result import (
    X1EvaluatorType,
    X1Verdict,
)

_GATE_IDS = [f"X1{c}" for c in "ABCDEFGHIJ"]


def _packet(**overrides: object) -> ExitReviewPacket:
    kwargs: dict[str, object] = dict(source_type=SourceType.L2_SEALED_ARTIFACT)
    kwargs.update(overrides)
    return ExitReviewPacket(**kwargs)  # type: ignore[arg-type]


def _all_pass_verdicts() -> list[GateVerdict]:
    return [GateVerdict(gate_id=gid, result=GateResult.PASS) for gid in _GATE_IDS]


class TestVerdictMapping:
    @pytest.mark.parametrize(
        "gate_result,x1_verdict",
        [
            (GateResult.PASS, X1Verdict.PASS),
            (GateResult.FAIL, X1Verdict.FAIL),
            (GateResult.WARN, X1Verdict.WARN),
            (GateResult.UNKNOWN, X1Verdict.UNKNOWN),
        ],
    )
    def test_result_maps_to_verdict(self, gate_result: GateResult, x1_verdict: X1Verdict) -> None:
        item = gate_verdict_to_x1_item(GateVerdict(gate_id="X1A", result=gate_result))
        assert item.verdict == x1_verdict

    def test_not_applicable_maps_and_carries_reason(self) -> None:
        v = GateVerdict(gate_id="X1D", result=GateResult.NOT_APPLICABLE, remediation_hint="cache route")
        item = gate_verdict_to_x1_item(v)
        assert item.verdict == X1Verdict.NOT_APPLICABLE
        assert item.not_applicable_reason == "cache route"


class TestGraderTypeMapping:
    @pytest.mark.parametrize(
        "grader_type,evaluator",
        [
            ("code", X1EvaluatorType.CODE),
            ("LLM-judge", X1EvaluatorType.LLM_JUDGE),
            ("hybrid", X1EvaluatorType.HYBRID),
            ("human-calibrated", X1EvaluatorType.HUMAN_CALIBRATED),
            ("nonsense", X1EvaluatorType.CODE),  # unknown → CODE default
        ],
    )
    def test_grader_type_maps_to_evaluator(self, grader_type: str, evaluator: X1EvaluatorType) -> None:
        v = GateVerdict(gate_id="X1A", result=GateResult.PASS, grader_type=grader_type)
        assert gate_verdict_to_x1_item(v).evaluator_type == evaluator


class TestGateVerdictToX1Item:
    def test_decisive_reason_from_remediation_hint(self) -> None:
        v = GateVerdict(gate_id="X1A", result=GateResult.FAIL, remediation_hint="fix this")
        assert gate_verdict_to_x1_item(v).decisive_reason == "fix this"

    def test_decisive_reason_from_reason_codes(self) -> None:
        v = GateVerdict(gate_id="X1A", result=GateResult.FAIL, reason_codes=["a", "b"])
        assert gate_verdict_to_x1_item(v).decisive_reason == "a; b"

    def test_unknown_gets_default_reason(self) -> None:
        item = gate_verdict_to_x1_item(GateVerdict(gate_id="X1A", result=GateResult.UNKNOWN))
        assert item.unknown_reason == "Gate evaluator returned UNKNOWN"

    def test_not_applicable_gets_default_reason(self) -> None:
        item = gate_verdict_to_x1_item(GateVerdict(gate_id="X1A", result=GateResult.NOT_APPLICABLE))
        assert item.not_applicable_reason == "Gate not applicable for this route"

    def test_score_and_evidence_forwarded(self) -> None:
        v = GateVerdict(
            gate_id="X1A",
            result=GateResult.PASS,
            score=0.9,
            threshold=0.8,
            evidence_refs=["e1", "e2"],
            confidence=0.7,
        )
        item = gate_verdict_to_x1_item(v)
        assert item.score == 0.9
        assert item.threshold == 0.8
        assert item.evidence_refs == ("e1", "e2")
        assert item.confidence == 0.7


class TestBuildX1CheckoutResult:
    def test_all_ten_slots_populated(self) -> None:
        result = build_x1_checkout_result(_all_pass_verdicts(), _packet())
        assert len(result.items()) == 10
        assert tuple(i.gate_id for i in result.items()) == tuple(_GATE_IDS)

    def test_identity_forwarded_from_packet(self) -> None:
        pkt = _packet(request_id="req-1", run_id="run-1", trace_root="trace-1")
        result = build_x1_checkout_result(_all_pass_verdicts(), pkt)
        assert result.request_id == "req-1"
        assert result.run_id == "run-1"
        assert result.trace_root == "trace-1"

    def test_missing_gate_becomes_explicit_unknown(self) -> None:
        # Only X1A provided; X1B..X1J should be UNKNOWN with explicit reason.
        verdicts = [GateVerdict(gate_id="X1A", result=GateResult.PASS)]
        result = build_x1_checkout_result(verdicts, _packet())
        assert result.x1b_answered_it.verdict == X1Verdict.UNKNOWN
        assert result.x1b_answered_it.unknown_reason == "Missing gate verdict in X1 run"
        assert result.x1b_answered_it.evaluator_type == X1EvaluatorType.UNKNOWN

    def test_replay_manifest_ref_from_packet_replay_key(self) -> None:
        result = build_x1_checkout_result(_all_pass_verdicts(), _packet(replay_key="rk-99"))
        assert result.replay_manifest_ref == "rk-99"

    def test_otel_refs_from_spans_and_trace_root(self) -> None:
        pkt = _packet(otel_spans={"spans": {"s1": {}, "s2": {}}}, trace_root="root-1")
        result = build_x1_checkout_result(_all_pass_verdicts(), pkt)
        assert "s1" in result.otel_span_refs
        assert "s2" in result.otel_span_refs
        assert "trace:root-1" in result.otel_span_refs

    def test_evidence_refs_from_final_evidence_contract(self) -> None:
        fec = {
            "evidence_items": [{"source": "doc-a"}, {"source": "doc-b"}],
            "compilation_hash": "hash-1",
        }
        result = build_x1_checkout_result(_all_pass_verdicts(), _packet(final_evidence_contract=fec))
        assert "evidence:0:doc-a" in result.evidence_refs
        assert "evidence:1:doc-b" in result.evidence_refs
        assert "fec:hash-1" in result.evidence_refs

    def test_evidence_refs_from_bundle(self) -> None:
        result = build_x1_checkout_result(
            _all_pass_verdicts(), _packet(evidence_bundle={"bundle_id": "b-7"})
        )
        assert "bundle:b-7" in result.evidence_refs

    def test_intent_ref_deterministic_from_route_contract(self) -> None:
        rc = {"intent_text": "stable intent"}
        r1 = build_x1_checkout_result(_all_pass_verdicts(), _packet(route_contract=rc))
        r2 = build_x1_checkout_result(_all_pass_verdicts(), _packet(route_contract=dict(rc)))
        assert r1.intent_ref.startswith("intent:")
        assert r1.intent_ref == r2.intent_ref

    def test_output_ref_from_output_id(self) -> None:
        result = build_x1_checkout_result(_all_pass_verdicts(), _packet(output={"output_id": "o-1"}))
        assert result.output_ref == "output:o-1"

    def test_output_ref_falls_back_to_run_id(self) -> None:
        # output dict present but no output_id → falls back to run_id.
        pkt = _packet(output={"foo": "bar"}, run_id="run-x")
        result = build_x1_checkout_result(_all_pass_verdicts(), pkt)
        assert result.output_ref == "output:run-x"


class TestRoundTrip:
    def test_checkout_to_gate_verdicts_count(self) -> None:
        checkout = build_x1_checkout_result(_all_pass_verdicts(), _packet())
        verdicts = x1_checkout_to_gate_verdicts(checkout)
        assert len(verdicts) == 10
        assert {v.gate_id for v in verdicts} == set(_GATE_IDS)

    def test_round_trip_preserves_pass(self) -> None:
        checkout = build_x1_checkout_result(_all_pass_verdicts(), _packet())
        for v in x1_checkout_to_gate_verdicts(checkout):
            assert v.result == GateResult.PASS

    def test_unknown_sets_abstain_flag(self) -> None:
        # No verdicts → every slot UNKNOWN → abstain_flag True on round-trip.
        checkout = build_x1_checkout_result([], _packet())
        verdicts = x1_checkout_to_gate_verdicts(checkout)
        assert all(v.abstain_flag for v in verdicts)
        assert all(v.result == GateResult.UNKNOWN for v in verdicts)
