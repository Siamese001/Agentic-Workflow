"""Unit tests for agentic_core.runtime.contracts.judge_types.

Wave 6.1 (P2 untested-module coverage) — generic, app-agnostic judge/gate
result contracts: CandidateGateResult, JudgeResult, JudgeJuryResult. All three
are frozen+slots dataclasses with all-default fields and as_dict/as_json
round-trips. Covers construction/defaults, frozen/slots, sentinel constants,
the W6 alias fallbacks in as_dict, and JSON round-trip shape.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.runtime.contracts.judge_types import (
    GATE_RESULT_FAIL,
    GATE_RESULT_NOT_APPLICABLE,
    GATE_RESULT_PASS,
    GATE_RESULT_UNKNOWN,
    GATE_RESULT_WARN,
    _VALID_GATE_RESULTS,
    CandidateGateResult,
    JudgeJuryResult,
    JudgeResult,
)


class TestSentinels:
    def test_sentinel_values(self) -> None:
        assert GATE_RESULT_PASS == "PASS"
        assert GATE_RESULT_FAIL == "FAIL"
        assert GATE_RESULT_WARN == "WARN"
        assert GATE_RESULT_UNKNOWN == "UNKNOWN"
        assert GATE_RESULT_NOT_APPLICABLE == "NOT_APPLICABLE"

    def test_valid_gate_results_set(self) -> None:
        assert _VALID_GATE_RESULTS == frozenset(
            {"PASS", "FAIL", "WARN", "UNKNOWN", "NOT_APPLICABLE"}
        )


class TestCandidateGateResult:
    def test_defaults(self) -> None:
        r = CandidateGateResult()
        assert r.result == GATE_RESULT_UNKNOWN
        assert r.passed is False
        assert r.fail_closed is True
        assert r.repair_allowed is False
        assert r.evidence_refs == ()
        assert r.schema_version == "W6.a3f7e2"

    def test_frozen(self) -> None:
        r = CandidateGateResult()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.passed = True  # type: ignore[misc]

    def test_slots(self) -> None:
        r = CandidateGateResult()
        assert not hasattr(r, "__dict__")

    def test_as_dict_reason_falls_back_to_rejection_reason(self) -> None:
        r = CandidateGateResult(rejection_reason="too short")
        assert r.as_dict()["reason"] == "too short"

    def test_as_dict_reason_prefers_reason_field(self) -> None:
        r = CandidateGateResult(reason="explicit", rejection_reason="fallback")
        assert r.as_dict()["reason"] == "explicit"

    def test_as_dict_evidence_refs_listified(self) -> None:
        r = CandidateGateResult(evidence_refs=("a", "b"))
        d = r.as_dict()
        assert d["evidence_refs"] == ["a", "b"]
        assert isinstance(d["evidence_refs"], list)

    def test_as_json_round_trips(self) -> None:
        r = CandidateGateResult(gate_id="G1", result=GATE_RESULT_PASS, passed=True)
        parsed = json.loads(r.as_json())
        assert parsed["gate_id"] == "G1"
        assert parsed["result"] == "PASS"
        assert parsed["passed"] is True
        assert parsed == r.as_dict()


class TestJudgeResult:
    def test_defaults(self) -> None:
        j = JudgeResult()
        assert j.score == 0.0
        assert j.abstained is False
        assert j.required_for_exit is False
        assert j.informational_only is False
        assert j.rubric_dimensions_scored == ()
        assert j.schema_version == "W6.a3f7e2"

    def test_frozen_and_slots(self) -> None:
        j = JudgeResult()
        assert not hasattr(j, "__dict__")
        with pytest.raises(dataclasses.FrozenInstanceError):
            j.score = 1.0  # type: ignore[misc]

    def test_as_dict_latency_falls_back_to_duration(self) -> None:
        # latency_ms default 0 → falls back to execution_duration_ms
        j = JudgeResult(execution_duration_ms=42)
        assert j.as_dict()["latency_ms"] == 42

    def test_as_dict_latency_prefers_latency_ms(self) -> None:
        j = JudgeResult(latency_ms=10, execution_duration_ms=99)
        assert j.as_dict()["latency_ms"] == 10

    def test_as_json_round_trips(self) -> None:
        j = JudgeResult(judge_id="J1", score=0.8, per_dimension_scores=(0.5, 0.9))
        parsed = json.loads(j.as_json())
        assert parsed["judge_id"] == "J1"
        assert parsed["per_dimension_scores"] == [0.5, 0.9]
        assert parsed == j.as_dict()


class TestJudgeJuryResult:
    def test_defaults(self) -> None:
        jj = JudgeJuryResult()
        assert jj.consensus_status == ""
        assert jj.judge_count == 0
        assert jj.meets_threshold is False
        assert jj.missing_required_judges == ()
        assert jj.schema_version == "W6.a3f7e2"

    def test_frozen_and_slots(self) -> None:
        jj = JudgeJuryResult()
        assert not hasattr(jj, "__dict__")
        with pytest.raises(dataclasses.FrozenInstanceError):
            jj.judge_count = 3  # type: ignore[misc]

    def test_as_dict_aggregate_score_alias_fallback(self) -> None:
        # aggregate_score default 0 → falls back to aggregated_score
        jj = JudgeJuryResult(aggregated_score=0.7)
        assert jj.as_dict()["aggregate_score"] == 0.7
        # and the reverse alias
        jj2 = JudgeJuryResult(aggregate_score=0.6)
        assert jj2.as_dict()["aggregated_score"] == 0.6

    def test_as_dict_lists_tuples(self) -> None:
        jj = JudgeJuryResult(
            missing_required_judges=("groundedness",),
            judge_weights=(0.5, 0.5),
        )
        d = jj.as_dict()
        assert d["missing_required_judges"] == ["groundedness"]
        assert d["judge_weights"] == [0.5, 0.5]

    def test_as_json_round_trips(self) -> None:
        jj = JudgeJuryResult(candidate_id="C1", consensus_status="consensus")
        parsed = json.loads(jj.as_json())
        assert parsed["candidate_id"] == "C1"
        assert parsed["consensus_status"] == "consensus"
        assert parsed == jj.as_dict()
