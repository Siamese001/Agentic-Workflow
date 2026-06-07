"""D1 tests — apps_qna C0 wiring + RAG judges.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-deferred-e9c5b3.md D1.1 + D1.2

Coverage:
- D1.1: call_c0 returns a valid FinalEvidenceContract-shaped dict via run_c0
- D1.1: fail-closed on C0 error (C0UnavailableError raised)
- D1.1: output fields are correct types
- D1.2: ContextRecallJudge scoring paths
- D1.2: ContextPrecisionJudge scoring paths
- D1.2: AnswerRelevancyJudge scoring paths
- D1.2: module-level grade() callables delegate to class instances
- D1.2: IS_STUB=False, IS_CALIBRATED=True on all three judges
- D1.2: GRADER_UNKNOWN_SENTINEL returned on empty input
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)
from apps_qna.c0_adapter import C0UnavailableError, call_c0
from apps_qna.engines.judges.answer_relevancy_judge import (
    AnswerRelevancyJudge,
    grade as grade_answer_relevancy,
)
from apps_qna.engines.judges.context_precision_judge import (
    ContextPrecisionJudge,
    grade as grade_context_precision,
)
from apps_qna.engines.judges.context_recall_judge import (
    ContextRecallJudge,
    grade as grade_context_recall,
)


# ---------------------------------------------------------------------------
# D1.1 — C0 adapter wiring
# ---------------------------------------------------------------------------


class TestCallC0:
    def test_returns_dict_with_required_keys(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        required = {
            "schema_version", "producer", "grounded", "retrieval_sources",
            "route_id", "evidence_sufficiency", "interview_slug", "query_text",
            "source_register", "freshness_assessment", "claim_confidence",
            "contradiction_flags",
        }
        assert required.issubset(result.keys())

    def test_producer_is_canonical_c0(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        assert result["producer"] == "agentic_core.C0"

    def test_route_id_propagated(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        assert result["route_id"] == "R4_SINGLE_ACTION"

    def test_interview_slug_propagated(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        assert result["interview_slug"] == "acme-swe-2026"

    def test_query_text_propagated(self) -> None:
        result = call_c0(
            interview_slug="acme-swe-2026",
            route_id="R4_SINGLE_ACTION",
            query_text="Tell me about the role",
        )
        assert result["query_text"] == "Tell me about the role"

    def test_claim_confidence_is_float_in_range(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        assert isinstance(result["claim_confidence"], float)
        assert 0.0 <= result["claim_confidence"] <= 1.0

    def test_stub_fetcher_gives_template_only_sufficiency(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        assert result["evidence_sufficiency"] in ("grounded", "template_only")

    def test_c0_unavailable_error_is_raised_on_invalid_execution_form(self) -> None:
        from unittest.mock import patch
        with patch(
            "apps_qna.c0_adapter._call_canonical_c0",
            side_effect=RuntimeError("injected failure"),
        ):
            with pytest.raises(C0UnavailableError):
                call_c0(interview_slug="bad", route_id="R4_SINGLE_ACTION")

    def test_empty_query_text_defaults(self) -> None:
        result = call_c0(interview_slug="acme-swe-2026", route_id="R4_SINGLE_ACTION")
        assert isinstance(result["query_text"], str)


# ---------------------------------------------------------------------------
# D1.2 — ContextRecallJudge
# ---------------------------------------------------------------------------


class TestContextRecallJudge:
    def test_is_not_stub(self) -> None:
        from apps_qna.engines.judges import context_recall_judge as m
        assert m.IS_STUB is False
        assert m.IS_CALIBRATED is True

    def test_precomputed_score_takes_precedence(self) -> None:
        ctx = {"output": {"dim_scores": {"context_recall": 0.92}}}
        score, refs = ContextRecallJudge().grade(None, ctx)
        assert score == pytest.approx(0.92)
        assert "precomputed" in refs[0]

    def test_full_overlap_scores_1(self) -> None:
        ctx = {"output": {"retrieval_sources": ["a", "b"], "required_sources": ["a", "b"]}}
        score, _ = ContextRecallJudge().grade(None, ctx)
        assert score == pytest.approx(1.0)

    def test_no_overlap_scores_0(self) -> None:
        ctx = {"output": {"retrieval_sources": ["x"], "required_sources": ["a", "b"]}}
        score, _ = ContextRecallJudge().grade(None, ctx)
        assert score == pytest.approx(0.0)

    def test_no_required_heuristic_3_sources(self) -> None:
        ctx = {"output": {"retrieval_sources": ["a", "b", "c"]}}
        score, _ = ContextRecallJudge().grade(None, ctx)
        assert score == pytest.approx(1.0)

    def test_no_required_heuristic_0_sources_returns_unknown(self) -> None:
        ctx = {"output": {"retrieval_sources": []}}
        score, _ = grade_context_recall(None, ctx)
        assert score is GRADER_UNKNOWN_SENTINEL

    def test_empty_output_returns_unknown(self) -> None:
        score, _ = ContextRecallJudge().grade(None, {"output": {}})
        assert score is GRADER_UNKNOWN_SENTINEL

    def test_none_context_returns_unknown(self) -> None:
        score, _ = ContextRecallJudge().grade(None, None)  # type: ignore[arg-type]
        assert score is GRADER_UNKNOWN_SENTINEL


# ---------------------------------------------------------------------------
# D1.2 — ContextPrecisionJudge
# ---------------------------------------------------------------------------


class TestContextPrecisionJudge:
    def test_is_not_stub(self) -> None:
        from apps_qna.engines.judges import context_precision_judge as m
        assert m.IS_STUB is False
        assert m.IS_CALIBRATED is True

    def test_precomputed_score_takes_precedence(self) -> None:
        ctx = {"output": {"dim_scores": {"context_precision": 0.75}}}
        score, refs = ContextPrecisionJudge().grade(None, ctx)
        assert score == pytest.approx(0.75)

    def test_all_retrieved_cited_scores_1(self) -> None:
        ctx = {"output": {"retrieval_sources": ["a", "b"], "cited_sources": ["a", "b"]}}
        score, _ = ContextPrecisionJudge().grade(None, ctx)
        assert score == pytest.approx(1.0)

    def test_no_cited_tight_retrieval_scores_1(self) -> None:
        ctx = {"output": {"retrieval_sources": ["a", "b", "c"]}}
        score, _ = ContextPrecisionJudge().grade(None, ctx)
        assert score == pytest.approx(1.0)

    def test_no_cited_loose_retrieval_scores_06(self) -> None:
        ctx = {"output": {"retrieval_sources": ["a", "b", "c", "d", "e", "f"]}}
        score, _ = grade_context_precision(None, ctx)
        assert score == pytest.approx(0.6)

    def test_no_retrieved_returns_unknown(self) -> None:
        score, _ = ContextPrecisionJudge().grade(None, {"output": {}})
        assert score is GRADER_UNKNOWN_SENTINEL


# ---------------------------------------------------------------------------
# D1.2 — AnswerRelevancyJudge
# ---------------------------------------------------------------------------


class TestAnswerRelevancyJudge:
    def test_is_not_stub(self) -> None:
        from apps_qna.engines.judges import answer_relevancy_judge as m
        assert m.IS_STUB is False
        assert m.IS_CALIBRATED is True

    def test_precomputed_score_takes_precedence(self) -> None:
        ctx = {"output": {"dim_scores": {"answer_relevancy": 0.88}, "answer": "x", "question": "y"}}
        score, refs = AnswerRelevancyJudge().grade(None, ctx)
        assert score == pytest.approx(0.88)

    def test_high_overlap_scores_well(self) -> None:
        ctx = {"output": {
            "answer": "The role requires Python and machine learning experience.",
            "question": "What Python and machine learning experience is required for this role?",
        }}
        score, _ = AnswerRelevancyJudge().grade(None, ctx)
        assert score > 0.5

    def test_empty_answer_returns_unknown(self) -> None:
        score, _ = AnswerRelevancyJudge().grade(None, {"output": {"answer": "", "question": "Q?"}})
        assert score is GRADER_UNKNOWN_SENTINEL

    def test_empty_question_returns_unknown(self) -> None:
        score, _ = grade_answer_relevancy(None, {"output": {"answer": "Some answer.", "question": ""}})
        assert score is GRADER_UNKNOWN_SENTINEL

    def test_score_in_range(self) -> None:
        ctx = {"output": {"answer": "Python is great for ML tasks.", "question": "What is Python?"}}
        score, _ = AnswerRelevancyJudge().grade(None, ctx)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_none_context_returns_unknown(self) -> None:
        score, _ = AnswerRelevancyJudge().grade(None, None)  # type: ignore[arg-type]
        assert score is GRADER_UNKNOWN_SENTINEL
