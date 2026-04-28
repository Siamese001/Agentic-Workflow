"""Tests for Gate evaluation and wiring invariants."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.composition import CompositionMode
from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.disposition import ReasonCode
from agentic_core.L3_orchestration.exit_eval.gates import (
    Gate,
    GateContext,
    GateWiringError,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    LLMJudgeGrader,
)
from agentic_core.L3_orchestration.exit_eval.rubric import rubric_from_mapping

from tests.agentic_core.L3_orchestration.exit_eval.conftest import (
    FakeCodeGrader,
    FakeJudge,
)


def _ctx(**kw: object) -> GateContext:
    return GateContext(
        run_id=str(kw.get("run_id", "r1")),
        track=str(kw.get("track", "regression")),
        trajectory_class=str(kw.get("trajectory_class", "demo")),
        payload={},
    )


def _binary_rubric() -> dict[str, object]:
    return {
        "gate": "X1A",
        "version": "X1A@v1",
        "composition": "binary",
        "dimensions": [
            {
                "name": "policy_match",
                "grader_class": "code_based",
                "is_hard_gate": True,
                "threshold": 1.0,
            }
        ],
    }


def _hybrid_rubric() -> dict[str, object]:
    return {
        "gate": "X1D",
        "version": "X1D@v1",
        "composition": "hybrid",
        "aggregate_threshold": 0.6,
        "dimensions": [
            {
                "name": "citation_support",
                "grader_class": "code_based",
                "is_hard_gate": True,
                "threshold": 1.0,
            },
            {
                "name": "groundedness",
                "grader_class": "model_based",
                "weight": 1.0,
                "threshold": 0.7,
                "abstain_allowed": True,
            },
        ],
    }


class TestGateWiring:
    def test_missing_grader_rejected(self) -> None:
        rubric = rubric_from_mapping(_binary_rubric())
        with pytest.raises(GateWiringError, match="missing graders"):
            Gate(rubric, graders={})

    def test_extra_grader_rejected(self) -> None:
        rubric = rubric_from_mapping(_binary_rubric())
        with pytest.raises(GateWiringError, match="unused graders"):
            Gate(
                rubric,
                graders={
                    "policy_match": FakeCodeGrader(),
                    "extra": FakeCodeGrader(),
                },
            )

    def test_hard_gate_requires_code_based(self) -> None:
        """H9 invariant: model-based graders cannot own hard sub-gates."""
        bad = dict(_binary_rubric())
        bad["dimensions"] = [
            {
                "name": "policy_match",
                "grader_class": "model_based",  # note: rubric itself allows this...
                "is_hard_gate": True,
                "threshold": 1.0,
                "abstain_allowed": True,
            }
        ]
        rubric = rubric_from_mapping(bad)
        # ... but wiring the gate with an LLM-judge grader is forbidden.
        with pytest.raises(GateWiringError, match="CODE_BASED"):
            Gate(rubric, graders={"policy_match": LLMJudgeGrader(FakeJudge())})


class TestGateEvaluate:
    def test_binary_pass(self) -> None:
        rubric = rubric_from_mapping(_binary_rubric())
        gate = Gate(rubric, graders={"policy_match": FakeCodeGrader(score=1.0)})
        result = gate.evaluate(_ctx())
        assert result.passed
        assert result.reason_codes == ()

    def test_binary_fail_emits_reason_code(self) -> None:
        rubric = rubric_from_mapping(_binary_rubric())
        gate = Gate(rubric, graders={"policy_match": FakeCodeGrader(score=0.0)})
        result = gate.evaluate(_ctx())
        assert not result.passed
        assert ReasonCode.POLICY_CONFLICT in result.reason_codes

    def test_hybrid_hard_fail(self) -> None:
        rubric = rubric_from_mapping(_hybrid_rubric())
        gate = Gate(
            rubric,
            graders={
                "citation_support": FakeCodeGrader(score=0.0),
                "groundedness": LLMJudgeGrader(FakeJudge(score=1.0)),
            },
        )
        result = gate.evaluate(_ctx())
        assert not result.passed
        assert ReasonCode.CITATION_INVALID in result.reason_codes

    def test_abstain_produces_judge_abstained(self) -> None:
        rubric = rubric_from_mapping(_hybrid_rubric())
        gate = Gate(
            rubric,
            graders={
                "citation_support": FakeCodeGrader(score=1.0),
                "groundedness": LLMJudgeGrader(FakeJudge(abstain=True)),
            },
        )
        result = gate.evaluate(_ctx())
        assert result.abstained
        assert not result.passed
        assert ReasonCode.JUDGE_ABSTAINED in result.reason_codes

    def test_judge_timeout_reason_code(self) -> None:
        rubric = rubric_from_mapping(_hybrid_rubric())
        gate = Gate(
            rubric,
            graders={
                "citation_support": FakeCodeGrader(score=1.0),
                "groundedness": LLMJudgeGrader(FakeJudge(raise_exc=TimeoutError("slow"))),
            },
        )
        result = gate.evaluate(_ctx())
        assert ReasonCode.JUDGE_TIMEOUT in result.reason_codes
        assert result.error is not None

    def test_code_grader_exception_denies_gate(self) -> None:
        rubric = rubric_from_mapping(_binary_rubric())
        gate = Gate(
            rubric,
            graders={
                "policy_match": FakeCodeGrader(
                    raise_exc=__import__(
                        "agentic_core.L3_orchestration.exit_eval.graders.base",
                        fromlist=["GraderError"],
                    ).GraderError("boom")
                )
            },
        )
        result = gate.evaluate(_ctx())
        assert not result.passed
        assert ReasonCode.GRADER_EXCEPTION in result.reason_codes

    def test_bus_row_shape(self) -> None:
        rubric = rubric_from_mapping(_hybrid_rubric())
        gate = Gate(
            rubric,
            graders={
                "citation_support": FakeCodeGrader(score=1.0),
                "groundedness": LLMJudgeGrader(FakeJudge(score=0.9)),
            },
        )
        result = gate.evaluate(_ctx())
        row = result.to_bus_row(run_id="r1", track="regression", trajectory_class="demo")
        assert row.gate == "X1D"
        assert row.rubric_version == "X1D@v1"
        assert row.composition == CompositionMode.HYBRID.value
        assert len(row.dimension_vector) == 2
        for dim_row in row.dimension_vector:
            assert "score" in dim_row
            assert "passed" in dim_row
