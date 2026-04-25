"""Tests for code-based graders and LLM-judge adapter."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.graders.code_based import (
    CitationGrader,
    SchemaGrader,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    LLMJudgeGrader,
)

from tests.agentic_core.L3_orchestration.exit_eval.conftest import FakeJudge


SCHEMA_DIM = Dimension(
    name="schema_complete",
    grader_class=GraderClass.CODE_BASED,
    scale=(0.0, 1.0),
    weight=1.0,
    is_hard_gate=True,
    threshold=1.0,
)

JUDGE_DIM = Dimension(
    name="groundedness",
    grader_class=GraderClass.MODEL_BASED,
    scale=(0.0, 1.0),
    weight=0.4,
    is_hard_gate=False,
    threshold=0.8,
    abstain_allowed=True,
)


class TestSchemaGrader:
    def test_pass(self) -> None:
        g = SchemaGrader(lambda out: (True, "ok"))
        out = g.grade(SCHEMA_DIM, {"output": {"x": 1}})
        result = g.score_to_result(SCHEMA_DIM, out)
        assert result.passed
        assert result.score == 1.0

    def test_fail(self) -> None:
        g = SchemaGrader(lambda out: (False, "missing field"))
        out = g.grade(SCHEMA_DIM, {"output": {}})
        result = g.score_to_result(SCHEMA_DIM, out)
        assert not result.passed
        assert result.score == 0.0
        assert "missing" in result.evidence["reason"]

    def test_missing_output_raises(self) -> None:
        g = SchemaGrader(lambda out: (True, ""))
        with pytest.raises(GraderError, match="missing 'output'"):
            g.grade(SCHEMA_DIM, {})

    def test_predicate_exception_wrapped(self) -> None:
        def bad(_o: object) -> tuple[bool, str]:
            raise ValueError("pred boom")

        g = SchemaGrader(bad)
        with pytest.raises(GraderError, match="predicate failed"):
            g.grade(SCHEMA_DIM, {"output": 1})


class TestCitationGrader:
    def test_all_resolved(self) -> None:
        g = CitationGrader()
        out = g.grade(
            SCHEMA_DIM,
            {"citations": ["c1", "c2"], "resolver": lambda cid: True},
        )
        assert out.score == 1.0
        assert out.evidence["unresolved"] == []

    def test_unresolved_denies(self) -> None:
        g = CitationGrader()
        out = g.grade(
            SCHEMA_DIM,
            {"citations": ["c1", "c2"], "resolver": lambda cid: cid == "c1"},
        )
        assert out.score == 0.0
        assert out.evidence["unresolved"] == ["c2"]

    def test_resolver_exception_wrapped(self) -> None:
        def bad(_cid: str) -> bool:
            raise RuntimeError("bad resolver")

        g = CitationGrader()
        with pytest.raises(GraderError, match="resolver raised"):
            g.grade(SCHEMA_DIM, {"citations": ["c1"], "resolver": bad})


class TestLLMJudgeGrader:
    def test_score_pass(self) -> None:
        g = LLMJudgeGrader(FakeJudge(score=0.9))
        out = g.grade(JUDGE_DIM, {"output": "text"})
        result = g.score_to_result(JUDGE_DIM, out)
        assert result.passed
        assert result.score == 0.9

    def test_abstain_routes_to_non_passed(self) -> None:
        g = LLMJudgeGrader(FakeJudge(abstain=True))
        out = g.grade(JUDGE_DIM, {"output": "text"})
        result = g.score_to_result(JUDGE_DIM, out)
        assert result.abstain
        assert not result.passed

    def test_abstain_on_non_abstainable_raises(self) -> None:
        # Dimension that forbids abstain
        dim = Dimension(
            name="faith",
            grader_class=GraderClass.MODEL_BASED,
            scale=(0.0, 1.0),
            threshold=0.7,
            abstain_allowed=False,
        )
        g = LLMJudgeGrader(FakeJudge(abstain=True))
        out = g.grade(dim, {})
        with pytest.raises(GraderError, match="non-abstainable"):
            g.score_to_result(dim, out)

    def test_timeout_propagates(self) -> None:
        g = LLMJudgeGrader(FakeJudge(raise_exc=TimeoutError("judge slow")))
        with pytest.raises(TimeoutError):
            g.grade(JUDGE_DIM, {})

    def test_generic_exception_wrapped_as_grader_error(self) -> None:
        g = LLMJudgeGrader(FakeJudge(raise_exc=RuntimeError("boom")))
        with pytest.raises(GraderError, match="judge raised"):
            g.grade(JUDGE_DIM, {})

    def test_wrong_dimension_class_raises(self) -> None:
        code_dim = Dimension(name="x", grader_class=GraderClass.CODE_BASED, threshold=0.5)
        g = LLMJudgeGrader(FakeJudge(score=0.5))
        with pytest.raises(GraderError, match="MODEL_BASED"):
            g.grade(code_dim, {})

    def test_score_clamped_to_scale(self) -> None:
        g = LLMJudgeGrader(FakeJudge(score=2.5))
        out = g.grade(JUDGE_DIM, {})
        result = g.score_to_result(JUDGE_DIM, out)
        assert result.score == 1.0  # clamped to scale high
