"""E2 tests — LLM-backed RAG judges with heuristic fallback.

Plan: .windsurf/plans/apps-qna-deferred-e5-f7a2b1.md E2.1–E2.3
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from apps_qna.engines.judges.context_recall_judge import (
    GRADER_ID as RECALL_GRADER_ID,
    ContextRecallJudge,
    _parse_llm_score as recall_parse,
    grade as grade_recall,
)
from apps_qna.engines.judges.context_precision_judge import (
    GRADER_ID as PRECISION_GRADER_ID,
    ContextPrecisionJudge,
    _parse_llm_score as precision_parse,
    grade as grade_precision,
)
from apps_qna.engines.judges.answer_relevancy_judge import (
    GRADER_ID as RELEVANCY_GRADER_ID,
    AnswerRelevancyJudge,
    _parse_llm_score as relevancy_parse,
    grade as grade_relevancy,
)


# ---------------------------------------------------------------------------
# Shared: _parse_llm_score
# ---------------------------------------------------------------------------


class TestParseLlmScore:
    def test_json_score(self):
        assert recall_parse('{"score": 0.85, "rationale": "good"}') == 0.85

    def test_bare_float(self):
        assert precision_parse("The score is 0.72 because...") == 0.72

    def test_out_of_range_rejected(self):
        assert relevancy_parse('{"score": 1.5}') is None

    def test_empty_response(self):
        assert recall_parse("") is None

    def test_garbage_response(self):
        assert precision_parse("I don't understand the question") is None

    def test_boundary_1_0(self):
        assert relevancy_parse('{"score": 1.0}') == 1.0

    def test_boundary_0_0(self):
        assert recall_parse('{"score": 0.0}') == 0.0


# ---------------------------------------------------------------------------
# E2.1: Context Recall Judge
# ---------------------------------------------------------------------------


class TestContextRecallJudgeLLM:
    def test_grader_id_v2(self):
        assert RECALL_GRADER_ID == "qna::context_recall_judge::v2"

    def test_llm_path_used_when_provider_available(self):
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.return_value = '{"score": 0.90, "rationale": "most evidence present"}'

        run_context = {
            "output": {
                "retrieval_sources": ["src1", "src2", "src3"],
                "required_sources": ["src1", "src2", "src3", "src4"],
                "question": "How do you handle conflict?",
            },
            "provider_context": mock_ctx,
        }
        score, refs = grade_recall(None, run_context)
        assert score == 0.90
        assert any("llm_judge" in r for r in refs)
        mock_ctx.dispatch.assert_called_once()

    def test_heuristic_fallback_when_no_provider(self):
        run_context = {
            "output": {
                "retrieval_sources": ["src1", "src2"],
                "required_sources": ["src1", "src2", "src3"],
            },
        }
        score, refs = grade_recall(None, run_context)
        assert 0.0 <= score <= 1.0
        assert any("heuristic" in r for r in refs)

    def test_heuristic_fallback_when_llm_returns_garbage(self):
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.return_value = "I cannot evaluate this."

        run_context = {
            "output": {
                "retrieval_sources": ["s1", "s2"],
                "required_sources": ["s1"],
                "question": "test",
            },
            "provider_context": mock_ctx,
        }
        score, refs = grade_recall(None, run_context)
        assert 0.0 <= score <= 1.0
        assert any("heuristic" in r for r in refs)

    def test_precomputed_still_takes_precedence(self):
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True

        run_context = {
            "output": {
                "retrieval_sources": ["s1"],
                "dim_scores": {"context_recall": 0.55},
            },
            "provider_context": mock_ctx,
        }
        score, refs = grade_recall(None, run_context)
        assert score == 0.55
        mock_ctx.dispatch.assert_not_called()


# ---------------------------------------------------------------------------
# E2.2: Context Precision Judge
# ---------------------------------------------------------------------------


class TestContextPrecisionJudgeLLM:
    def test_grader_id_v2(self):
        assert PRECISION_GRADER_ID == "qna::context_precision_judge::v2"

    def test_llm_path_used(self):
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.return_value = '{"score": 0.80, "rationale": "mostly relevant"}'

        run_context = {
            "output": {
                "retrieval_sources": ["a", "b", "c"],
                "question": "What is REST?",
                "answer": "REST is an architectural style for APIs.",
            },
            "provider_context": mock_ctx,
        }
        score, refs = grade_precision(None, run_context)
        assert score == 0.80
        assert any("llm_judge" in r for r in refs)

    def test_heuristic_fallback_no_provider(self):
        run_context = {
            "output": {
                "retrieval_sources": ["a", "b"],
                "cited_sources": ["a"],
            },
        }
        score, refs = grade_precision(None, run_context)
        assert score == 0.5  # 1/2
        assert any("heuristic" in r for r in refs)


# ---------------------------------------------------------------------------
# E2.3: Answer Relevancy Judge
# ---------------------------------------------------------------------------


class TestAnswerRelevancyJudgeLLM:
    def test_grader_id_v2(self):
        assert RELEVANCY_GRADER_ID == "qna::answer_relevancy_judge::v2"

    def test_llm_path_used(self):
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.return_value = '{"score": 0.95, "rationale": "directly answers"}'

        run_context = {
            "output": {
                "question": "What is a microservice?",
                "answer": "A microservice is a small, independently deployable service.",
            },
            "provider_context": mock_ctx,
        }
        score, refs = grade_relevancy(None, run_context)
        assert score == 0.95
        assert any("llm_judge" in r for r in refs)

    def test_heuristic_fallback_no_provider(self):
        run_context = {
            "output": {
                "question": "What is Python?",
                "answer": "Python is a programming language known for readability.",
            },
        }
        score, refs = grade_relevancy(None, run_context)
        assert 0.0 <= score <= 1.0
        assert any("heuristic" in r for r in refs)

    def test_empty_answer_returns_unknown(self):
        run_context = {
            "output": {
                "question": "What is Java?",
                "answer": "",
            },
        }
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        score, refs = grade_relevancy(None, run_context)
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_llm_dispatch_error_falls_back_to_heuristic(self):
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.return_value = ""  # empty = fail-open from dispatch

        run_context = {
            "output": {
                "question": "What is Docker?",
                "answer": "Docker is a containerization platform for deploying apps.",
            },
            "provider_context": mock_ctx,
        }
        score, refs = grade_relevancy(None, run_context)
        assert 0.0 <= score <= 1.0
        assert any("heuristic" in r for r in refs)
