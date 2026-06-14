"""Unit tests for agentic_core.runtime_gates.definitions.

Wave 6.1 (P2 untested-module coverage) — runtime gate definition contracts.
Covers GatePlacement / GateEnforcement enum value-sets, frozen GateDefinition /
GateVerdict / JudgeVerdict construction + defaults, __post_init__ ValueError and
string-normalization branches, is_blocking enforcement logic, JudgeVerdict score
range validation, and to_gate_verdict normalization.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L5_safety.runtime_gates.contracts import Result
from agentic_core.runtime_gates.definitions import (
    GateDefinition,
    GateEnforcement,
    GatePlacement,
    GateVerdict,
    JudgeVerdict,
)


class TestEnumValueSets:
    def test_gate_placement_values(self):
        assert {m.value for m in GatePlacement} == {
            "PRE_LLM",
            "PER_CAND",
            "POST_ENS",
            "POST_NARR",
            "PRE_EXPORT",
        }

    def test_gate_enforcement_values(self):
        assert {m.value for m in GateEnforcement} == {
            "FAIL_CLOSED",
            "WARN",
            "CONFIGURABLE",
        }

    def test_enums_are_str(self):
        assert GatePlacement.PRE_LLM == "PRE_LLM"
        assert GateEnforcement.WARN == "WARN"


class TestGateDefinition:
    def test_construction_defaults(self):
        d = GateDefinition(
            gate_id="g1",
            placement=GatePlacement.PRE_LLM,
            enforcement=GateEnforcement.FAIL_CLOSED,
        )
        assert d.bypassable is False
        assert d.dependencies == ()
        assert d.description == ""
        assert d.default_tolerance == 0.0

    def test_frozen(self):
        d = GateDefinition(
            gate_id="g1",
            placement=GatePlacement.PRE_LLM,
            enforcement=GateEnforcement.WARN,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.gate_id = "g2"  # type: ignore[misc]

    def test_empty_gate_id_raises(self):
        with pytest.raises(ValueError, match="gate_id is required"):
            GateDefinition(
                gate_id="",
                placement=GatePlacement.PRE_LLM,
                enforcement=GateEnforcement.WARN,
            )

    def test_string_placement_normalized(self):
        d = GateDefinition(
            gate_id="g1",
            placement="POST_ENS",  # type: ignore[arg-type]
            enforcement="CONFIGURABLE",  # type: ignore[arg-type]
        )
        assert d.placement is GatePlacement.POST_ENS
        assert d.enforcement is GateEnforcement.CONFIGURABLE

    def test_invalid_string_placement_raises(self):
        with pytest.raises(ValueError):
            GateDefinition(
                gate_id="g1",
                placement="NOPE",  # type: ignore[arg-type]
                enforcement=GateEnforcement.WARN,
            )


class TestGateVerdict:
    def test_construction_defaults(self):
        v = GateVerdict(gate_id="g1", result=Result.PASS)
        assert v.reason == ""
        assert v.reason_codes == ()
        assert v.evidence_refs == ()
        assert v.latency_ms == 0.0
        assert v.deterministic_digest == ""

    def test_empty_gate_id_raises(self):
        with pytest.raises(ValueError, match="gate_id is required"):
            GateVerdict(gate_id="", result=Result.PASS)

    def test_string_result_normalized(self):
        v = GateVerdict(gate_id="g1", result="FAIL")  # type: ignore[arg-type]
        assert v.result is Result.FAIL

    @pytest.mark.parametrize(
        "result,expected",
        [
            (Result.FAIL, True),
            (Result.UNKNOWN, True),
            (Result.PASS, False),
            (Result.WARN, False),
            (Result.NOT_APPLICABLE, False),
        ],
    )
    def test_is_blocking_fail_closed(self, result, expected):
        v = GateVerdict(gate_id="g1", result=result)
        assert v.is_blocking(GateEnforcement.FAIL_CLOSED) is expected

    @pytest.mark.parametrize("enforcement", [GateEnforcement.WARN, GateEnforcement.CONFIGURABLE])
    def test_is_blocking_non_fail_closed_never_blocks(self, enforcement):
        v = GateVerdict(gate_id="g1", result=Result.FAIL)
        assert v.is_blocking(enforcement) is False


class TestJudgeVerdict:
    def _kwargs(self, **over):
        base = dict(
            judge_id="j1",
            judge_version="1.0.0",
            rubric_version="r1",
            threshold_profile_id="tp1",
            gate_id="g1",
            placement=GatePlacement.PER_CAND,
        )
        base.update(over)
        return base

    def test_construction_defaults(self):
        j = JudgeVerdict(**self._kwargs())
        assert j.score == 0.0
        assert j.accepted is False
        assert j.result is Result.UNKNOWN

    @pytest.mark.parametrize(
        "field_name",
        ["judge_id", "judge_version", "rubric_version", "threshold_profile_id", "gate_id"],
    )
    def test_required_identifier_empty_raises(self, field_name):
        with pytest.raises(ValueError, match=f"{field_name} is required"):
            JudgeVerdict(**self._kwargs(**{field_name: ""}))

    @pytest.mark.parametrize("bad_score", [-0.01, 1.01, 2.0, -5.0])
    def test_score_out_of_range_raises(self, bad_score):
        with pytest.raises(ValueError, match="score must be in"):
            JudgeVerdict(**self._kwargs(score=bad_score))

    @pytest.mark.parametrize("ok_score", [0.0, 0.5, 1.0])
    def test_score_in_range_ok(self, ok_score):
        j = JudgeVerdict(**self._kwargs(score=ok_score))
        assert j.score == ok_score

    def test_string_enums_normalized(self):
        j = JudgeVerdict(**self._kwargs(placement="POST_ENS", result="PASS"))
        assert j.placement is GatePlacement.POST_ENS
        assert j.result is Result.PASS

    def test_to_gate_verdict(self):
        j = JudgeVerdict(
            **self._kwargs(
                accepted=True,
                result=Result.PASS,
                reason_codes=("rc1",),
                evidence_refs=("ev1",),
                deterministic_digest="dig",
            )
        )
        gv = j.to_gate_verdict()
        assert isinstance(gv, GateVerdict)
        assert gv.gate_id == "g1"
        assert gv.result is Result.PASS
        assert gv.reason_codes == ("rc1",)
        assert gv.evidence_refs == ("ev1", "judge:j1")
        assert gv.deterministic_digest == "dig"
        assert "accepted=True" in gv.reason
