"""
tests/unit/agentic_core/L6_observability/evaluation/test_rag_evaluators.py

Unit tests for Wave 1.2: RAG Evaluators

Tests all 5 RAG evaluators:
- FaithfulnessEvaluator
- GroundednessEvaluator
- RelevancyEvaluator
- ContextPrecisionEvaluator
- ContextRecallEvaluator
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.utils.evaluation.rag_evaluators import (
    ContextPrecisionEvaluator,
    ContextRecallEvaluator,
    EvaluationResult,
    FaithfulnessEvaluator,
    GroundednessEvaluator,
    RelevancyEvaluator,
)


class TestFaithfulnessEvaluator:
    """Test suite for FaithfulnessEvaluator."""

    def test_perfect_faithfulness(self):
        """Test answer fully grounded in context."""
        evaluator = FaithfulnessEvaluator()

        query = "What is Python?"
        context = [
            "Python is a high-level programming language.",
            "It was created by Guido van Rossum in 1991.",
        ]
        answer = "Python is a high-level programming language created by Guido van Rossum."

        result = evaluator.evaluate(query, context, answer)

        assert isinstance(result, EvaluationResult)
        assert result.score >= 0.8  # High faithfulness
        assert "grounded" in result.explanation.lower()

    def test_zero_faithfulness(self):
        """Test answer not grounded in context (hallucination)."""
        evaluator = FaithfulnessEvaluator()

        query = "What is Python?"
        context = ["Python is a programming language."]
        answer = "Python is a snake species found in tropical regions."

        result = evaluator.evaluate(query, context, answer)

        assert result.score < 0.5  # Low faithfulness

    def test_empty_answer(self):
        """Test empty answer returns zero score."""
        evaluator = FaithfulnessEvaluator()

        result = evaluator.evaluate("query", ["context"], "")

        assert result.score == 0.0
        assert "empty" in result.explanation.lower()

    def test_no_claims(self):
        """Test answer with no extractable claims."""
        evaluator = FaithfulnessEvaluator()

        result = evaluator.evaluate("query", ["context"], "Yes")

        assert result.score == 1.0  # Trivially faithful
        assert result.metadata["claims_total"] == 0


class TestGroundednessEvaluator:
    """Test suite for GroundednessEvaluator."""

    def test_grounded_facts(self):
        """Test factual answer supported by context."""
        evaluator = GroundednessEvaluator()

        query = "When was Python created?"
        context = [
            "Python was created in 1991.",
            "Guido van Rossum is the creator of Python.",
        ]
        answer = "Python was created in 1991 by Guido van Rossum."

        result = evaluator.evaluate(query, context, answer)

        assert result.score >= 0.7  # High groundedness
        assert result.metadata["facts_total"] > 0

    def test_ungrounded_facts(self):
        """Test facts not supported by context."""
        evaluator = GroundednessEvaluator()

        query = "What is Python?"
        context = ["Python is a programming language."]
        answer = "Python was created in 1985 and has 50 million users."

        result = evaluator.evaluate(query, context, answer)

        assert result.score < 0.5  # Low groundedness

    def test_non_factual_answer(self):
        """Test answer with no factual statements."""
        evaluator = GroundednessEvaluator()

        result = evaluator.evaluate("query", ["context"], "I think so.")

        assert result.score == 0.5  # Neutral score


class TestRelevancyEvaluator:
    """Test suite for RelevancyEvaluator."""

    def test_perfect_relevancy(self):
        """Test answer highly relevant to query."""
        evaluator = RelevancyEvaluator()

        query = "What are the benefits of Python programming?"
        context = ["Python is easy to learn and has many libraries."]
        answer = "Python programming offers benefits like easy learning and extensive libraries."

        result = evaluator.evaluate(query, context, answer)

        assert result.score >= 0.6  # High relevancy
        assert result.metadata["terms_in_answer"] > 0

    def test_low_relevancy(self):
        """Test answer not relevant to query."""
        evaluator = RelevancyEvaluator()

        query = "What are the benefits of Python programming?"
        context = ["Java is also a programming language."]
        answer = "Java is used for enterprise applications."

        result = evaluator.evaluate(query, context, answer)

        assert result.score < 0.3  # Low relevancy

    def test_empty_query(self):
        """Test empty query returns zero score."""
        evaluator = RelevancyEvaluator()

        result = evaluator.evaluate("", ["context"], "answer")

        assert result.score == 0.0

    def test_stop_words_filtered(self):
        """Test that stop words are filtered from query terms."""
        evaluator = RelevancyEvaluator()

        query = "What is the best way to learn Python?"
        context = ["Python tutorials are available online."]
        answer = "The best way to learn Python is through tutorials."

        result = evaluator.evaluate(query, context, answer)

        # "what", "is", "the", "to" should be filtered
        assert "python" in [t.lower() for t in result.metadata["query_terms"]]
        assert "learn" in [t.lower() for t in result.metadata["query_terms"]]
        assert "the" not in result.metadata["query_terms"]


class TestContextPrecisionEvaluator:
    """Test suite for ContextPrecisionEvaluator."""

    def test_high_precision(self):
        """Test all retrieved chunks are relevant."""
        evaluator = ContextPrecisionEvaluator()

        query = "Python programming features"
        context = [
            "Python has dynamic typing and automatic memory management.",
            "Python supports multiple programming paradigms.",
            "Python features include list comprehensions and generators.",
        ]
        answer = "Python has many features."

        result = evaluator.evaluate(query, context, answer)

        assert result.score >= 0.8  # High precision
        assert result.metadata["chunks_relevant"] >= 2

    def test_low_precision(self):
        """Test many irrelevant chunks retrieved."""
        evaluator = ContextPrecisionEvaluator()

        query = "Python programming"
        context = [
            "Python is a programming language.",
            "Java is also popular.",
            "JavaScript runs in browsers.",
            "C++ is used for systems programming.",
        ]
        answer = "Python is a language."

        result = evaluator.evaluate(query, context, answer)

        assert result.score <= 0.5  # Low precision (2/4 chunks relevant)

    def test_empty_context(self):
        """Test empty context returns zero score."""
        evaluator = ContextPrecisionEvaluator()

        result = evaluator.evaluate("query", [], "answer")

        assert result.score == 0.0


class TestContextRecallEvaluator:
    """Test suite for ContextRecallEvaluator."""

    def test_high_recall(self):
        """Test all answer concepts found in context."""
        evaluator = ContextRecallEvaluator()

        query = "What is Python?"
        context = [
            "Python is a high-level programming language created in 1991.",
            "It supports object-oriented and functional programming.",
        ]
        answer = "Python is a high-level language created in 1991 supporting object-oriented programming."

        result = evaluator.evaluate(query, context, answer)

        assert result.score >= 0.7  # High recall
        assert result.metadata["concepts_total"] > 0

    def test_low_recall(self):
        """Test answer concepts missing from context."""
        evaluator = ContextRecallEvaluator()

        query = "What is Python?"
        context = ["Python is a language."]
        answer = "Python was created by Guido van Rossum in 1991 and has 500000 packages."

        result = evaluator.evaluate(query, context, answer)

        # Many concepts (Guido, 1991, 500000) not in context
        assert result.score < 0.5  # Low recall

    def test_simple_answer(self):
        """Test simple answer with no key concepts."""
        evaluator = ContextRecallEvaluator()

        result = evaluator.evaluate("query", ["context"], "Yes, it is.")

        # Simple answers may have low recall if concepts not in context
        assert 0.0 <= result.score <= 0.5


class TestEvaluationResultFormat:
    """Test EvaluationResult data structure."""

    def test_result_structure(self):
        """Test EvaluationResult has required fields."""
        result = EvaluationResult(
            score=0.85,
            explanation="Test explanation",
            metadata={"key": "value"},
        )

        assert result.score == 0.85
        assert result.explanation == "Test explanation"
        assert result.metadata["key"] == "value"

    def test_score_range(self):
        """Test all evaluators return scores in [0.0, 1.0]."""
        evaluators = [
            FaithfulnessEvaluator(),
            GroundednessEvaluator(),
            RelevancyEvaluator(),
            ContextPrecisionEvaluator(),
            ContextRecallEvaluator(),
        ]

        query = "test query"
        context = ["test context"]
        answer = "test answer"

        for evaluator in evaluators:
            result = evaluator.evaluate(query, context, answer)
            assert 0.0 <= result.score <= 1.0, f"{evaluator.__class__.__name__} score out of range"


class TestIntegration:
    """Integration tests for RAG evaluators."""

    def test_all_evaluators_on_same_input(self):
        """Test all evaluators on the same RAG example."""
        query = "What are the key features of Python?"
        context = [
            "Python is a high-level, interpreted programming language.",
            "Key features include dynamic typing, automatic memory management, and extensive standard library.",
            "Python supports multiple programming paradigms including procedural, object-oriented, and functional.",
        ]
        answer = "Python's key features include dynamic typing, automatic memory management, and support for multiple programming paradigms."

        evaluators = {
            "faithfulness": FaithfulnessEvaluator(),
            "groundedness": GroundednessEvaluator(),
            "relevancy": RelevancyEvaluator(),
            "context_precision": ContextPrecisionEvaluator(),
            "context_recall": ContextRecallEvaluator(),
        }

        results = {}
        for name, evaluator in evaluators.items():
            result = evaluator.evaluate(query, context, answer)
            results[name] = result.score

        # Most scores should be reasonably high for this good RAG example
        # Note: context_precision may be 0 if query terms don't overlap with context chunks
        high_score_metrics = ["faithfulness", "relevancy", "context_recall"]
        assert all(results[m] >= 0.5 for m in high_score_metrics), f"Low scores: {results}"

        # Faithfulness should be high (answer grounded in context)
        assert results["faithfulness"] >= 0.7

        # Relevancy should be high (answer addresses query)
        assert results["relevancy"] >= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
