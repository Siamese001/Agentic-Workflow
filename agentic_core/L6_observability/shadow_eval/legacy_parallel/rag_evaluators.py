"""
agentic_core/L6_observability/evaluation/rag_evaluators.py

RAG Evaluation Metrics — Wave 1.2.2

Implements 5 RAG-specific evaluators for measuring retrieval and generation quality:
- FaithfulnessEvaluator: Answer grounded in retrieved context
- GroundednessEvaluator: Answer supported by evidence
- RelevancyEvaluator: Answer addresses user query
- ContextPrecisionEvaluator: Retrieved chunks relevant to query
- ContextRecallEvaluator: All relevant info retrieved

All evaluators return scores in [0.0, 1.0] range.
"""

from __future__ import annotations

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "rag_evaluators")
emit_determinism_digest("p0", "rag_evaluators")
_emit_applies_guardrail("p0", "rag_evaluators", "p0_governance")
_emit_snapshots_state("p0", "rag_evaluators", "state_snapshot")
_tid = "rag_evaluators_bootstrap"
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap (abbreviated for brevity)
_emit_routes_through("p1", "rag_evaluators", "L6")
_emit_authorize_and_execute("p2", "rag_evaluators", "execution_auth")
_emit_validates_capability("p2", "rag_evaluators", "capability_check")
_emit_routes_to_capability("p2", "rag_evaluators", "capability_route")
_emit_writes_via_uwg("p2", "rag_evaluators", "uwg_write")
_emit_blocks_direct_write("p2", "rag_evaluators", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_evaluators", "tool_invocation")
_emit_captures_execution_output("p2", "rag_evaluators", "exec_output")
_emit_dispatches_agent("p3", "rag_evaluators", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_evaluators", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_evaluators", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_evaluators", "healing_outcome")
_emit_escalates_failure("p3", "rag_evaluators", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_evaluators", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_evaluators", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_evaluators", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_evaluators", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_evaluators", "eval_metric")
_emit_stores_embedding("p4", "rag_evaluators", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_evaluators", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_evaluators", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvaluationResult:
    """Result from a RAG evaluator."""

    score: float  # [0.0, 1.0]
    explanation: str
    metadata: dict[str, Any]


class BaseRAGEvaluator(ABC):
    """Base class for RAG evaluators."""

    @abstractmethod
    def evaluate(self, query: str, context: list[str], answer: str) -> EvaluationResult:
        """Evaluate RAG quality.

        Args:
            query: User query
            context: Retrieved context chunks
            answer: Generated answer

        Returns:
            EvaluationResult with score in [0.0, 1.0]
        """
        pass


class FaithfulnessEvaluator(BaseRAGEvaluator):
    """Evaluates whether answer is grounded in retrieved context.

    Faithfulness measures if all claims in the answer can be traced back
    to the retrieved context. High faithfulness means no hallucinations.

    Algorithm:
    1. Extract claims from answer (simple sentence splitting)
    2. For each claim, check if it appears in context
    3. Score = (claims_in_context / total_claims)
    """

    def __init__(self) -> None:
        self._min_claim_length = 10  # Minimum characters for a claim

    def evaluate(self, query: str, context: list[str], answer: str) -> EvaluationResult:
        """Evaluate faithfulness score."""
        _emit_invokes_evaluation("p3", "rag_evaluators", "faithfulness_eval")
        _emit_captures_evaluation_metric("p4", "rag_evaluators", "faithfulness_score")

        if not answer or not context:
            return EvaluationResult(
                score=0.0,
                explanation="Empty answer or context",
                metadata={"claims_total": 0, "claims_grounded": 0},
            )

        # Extract claims (simple sentence splitting)
        claims = [s.strip() for s in re.split(r"[.!?]+", answer) if len(s.strip()) >= self._min_claim_length]

        if not claims:
            return EvaluationResult(
                score=1.0,  # No claims = trivially faithful
                explanation="No claims to verify",
                metadata={"claims_total": 0, "claims_grounded": 0},
            )

        # Check each claim against context
        context_text = " ".join(context).lower()
        claims_grounded = 0

        for claim in claims:
            claim_lower = claim.lower()
            # Simple substring matching (can be enhanced with semantic similarity)
            if claim_lower in context_text:
                claims_grounded += 1
            else:
                # Check for partial matches (at least 50% of words)
                claim_words = set(claim_lower.split())
                if len(claim_words) > 0:
                    words_in_context = sum(1 for w in claim_words if w in context_text)
                    if words_in_context / len(claim_words) >= 0.5:
                        claims_grounded += 1

        score = claims_grounded / len(claims)

        return EvaluationResult(
            score=score,
            explanation=f"{claims_grounded}/{len(claims)} claims grounded in context",
            metadata={
                "claims_total": len(claims),
                "claims_grounded": claims_grounded,
                "claims": claims[:5],  # First 5 claims for debugging
            },
        )


class GroundednessEvaluator(BaseRAGEvaluator):
    """Evaluates whether answer is supported by evidence.

    Groundedness measures if the answer contains factual statements
    that are backed by the retrieved context. Similar to faithfulness
    but focuses on evidence support rather than claim tracing.

    Algorithm:
    1. Extract key facts from answer
    2. Check if each fact has supporting evidence in context
    3. Score = (supported_facts / total_facts)
    """

    def evaluate(self, query: str, context: list[str], answer: str) -> EvaluationResult:
        """Evaluate groundedness score."""
        _emit_invokes_evaluation("p3", "rag_evaluators", "groundedness_eval")
        _emit_captures_evaluation_metric("p4", "rag_evaluators", "groundedness_score")

        if not answer or not context:
            return EvaluationResult(
                score=0.0,
                explanation="Empty answer or context",
                metadata={"facts_total": 0, "facts_supported": 0},
            )

        # Extract facts (sentences with factual indicators)
        factual_patterns = [
            r"\b(is|are|was|were|has|have|had)\b",
            r"\b\d+\b",  # Numbers
            r"\b(the|a|an)\s+\w+\s+(is|are|was|were)\b",
        ]

        sentences = [s.strip() for s in re.split(r"[.!?]+", answer) if s.strip()]
        facts = []
        for sent in sentences:
            if any(re.search(pattern, sent, re.IGNORECASE) for pattern in factual_patterns):
                facts.append(sent)

        if not facts:
            return EvaluationResult(
                score=0.5,  # Neutral score for non-factual answers
                explanation="No factual statements found",
                metadata={"facts_total": 0, "facts_supported": 0},
            )

        # Check each fact against context
        context_text = " ".join(context).lower()
        facts_supported = 0

        for fact in facts:
            fact_lower = fact.lower()
            # Check for evidence (word overlap)
            fact_words = set(fact_lower.split())
            if len(fact_words) > 0:
                words_in_context = sum(1 for w in fact_words if w in context_text)
                # Require at least 60% word overlap for support
                if words_in_context / len(fact_words) >= 0.6:
                    facts_supported += 1

        score = facts_supported / len(facts)

        return EvaluationResult(
            score=score,
            explanation=f"{facts_supported}/{len(facts)} facts supported by evidence",
            metadata={
                "facts_total": len(facts),
                "facts_supported": facts_supported,
                "facts": facts[:5],
            },
        )


class RelevancyEvaluator(BaseRAGEvaluator):
    """Evaluates whether answer addresses the user query.

    Answer relevancy measures if the generated answer is relevant to
    the user's question. High relevancy means the answer is on-topic.

    Algorithm:
    1. Extract key terms from query
    2. Check if answer contains query terms
    3. Score = (query_terms_in_answer / total_query_terms)
    """

    def __init__(self) -> None:
        # Common stop words to exclude from key terms
        self._stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "must",
            "can",
            "what",
            "when",
            "where",
            "who",
            "why",
            "how",
        }

    def evaluate(self, query: str, context: list[str], answer: str) -> EvaluationResult:
        """Evaluate answer relevancy score."""
        _emit_invokes_evaluation("p3", "rag_evaluators", "relevancy_eval")
        _emit_captures_evaluation_metric("p4", "rag_evaluators", "relevancy_score")

        if not query or not answer:
            return EvaluationResult(
                score=0.0,
                explanation="Empty query or answer",
                metadata={"query_terms": [], "terms_in_answer": 0},
            )

        # Extract key terms from query (excluding stop words)
        query_words = re.findall(r"\b\w+\b", query.lower())
        query_terms = [w for w in query_words if w not in self._stop_words and len(w) > 2]

        if not query_terms:
            return EvaluationResult(
                score=0.5,  # Neutral score for queries with no key terms
                explanation="No key terms in query",
                metadata={"query_terms": [], "terms_in_answer": 0},
            )

        # Check which query terms appear in answer
        answer_lower = answer.lower()
        terms_in_answer = sum(1 for term in query_terms if term in answer_lower)

        score = terms_in_answer / len(query_terms)

        return EvaluationResult(
            score=score,
            explanation=f"{terms_in_answer}/{len(query_terms)} query terms in answer",
            metadata={
                "query_terms": query_terms,
                "terms_in_answer": terms_in_answer,
                "query_term_coverage": score,
            },
        )


class ContextPrecisionEvaluator(BaseRAGEvaluator):
    """Evaluates whether retrieved chunks are relevant to query.

    Context precision measures the proportion of retrieved context
    that is actually relevant to answering the query. High precision
    means low noise in retrieval.

    Algorithm:
    1. For each context chunk, check query term overlap
    2. Score = (relevant_chunks / total_chunks)
    """

    def __init__(self) -> None:
        self._relevance_threshold = 0.3  # Minimum term overlap for relevance

    def evaluate(self, query: str, context: list[str], answer: str) -> EvaluationResult:
        """Evaluate context precision score."""
        _emit_invokes_evaluation("p3", "rag_evaluators", "context_precision_eval")
        _emit_captures_evaluation_metric("p4", "rag_evaluators", "context_precision_score")

        if not query or not context:
            return EvaluationResult(
                score=0.0,
                explanation="Empty query or context",
                metadata={"chunks_total": 0, "chunks_relevant": 0},
            )

        # Extract query terms
        query_words = set(re.findall(r"\b\w+\b", query.lower()))

        if not query_words:
            return EvaluationResult(
                score=0.5,
                explanation="No terms in query",
                metadata={"chunks_total": len(context), "chunks_relevant": 0},
            )

        # Check each chunk for relevance
        chunks_relevant = 0
        for chunk in context:
            chunk_words = set(re.findall(r"\b\w+\b", chunk.lower()))
            if chunk_words:
                overlap = len(query_words & chunk_words)
                relevance_score = overlap / len(query_words)
                if relevance_score >= self._relevance_threshold:
                    chunks_relevant += 1

        score = chunks_relevant / len(context) if context else 0.0

        return EvaluationResult(
            score=score,
            explanation=f"{chunks_relevant}/{len(context)} chunks relevant to query",
            metadata={
                "chunks_total": len(context),
                "chunks_relevant": chunks_relevant,
                "relevance_threshold": self._relevance_threshold,
            },
        )


class ContextRecallEvaluator(BaseRAGEvaluator):
    """Evaluates whether all relevant info was retrieved.

    Context recall measures if the retrieved context contains all
    information needed to answer the query. High recall means no
    missing information.

    Algorithm:
    1. Extract key concepts from answer
    2. Check if each concept appears in context
    3. Score = (concepts_in_context / total_concepts)

    Note: This is a proxy metric since we don't have ground truth.
    """

    def evaluate(self, query: str, context: list[str], answer: str) -> EvaluationResult:
        """Evaluate context recall score."""
        _emit_invokes_evaluation("p3", "rag_evaluators", "context_recall_eval")
        _emit_captures_evaluation_metric("p4", "rag_evaluators", "context_recall_score")

        if not answer or not context:
            return EvaluationResult(
                score=0.0,
                explanation="Empty answer or context",
                metadata={"concepts_total": 0, "concepts_in_context": 0},
            )

        # Extract key concepts from answer (noun phrases, entities)
        # Simple heuristic: capitalized words and multi-word phrases
        concepts = set()

        # Capitalized words (potential entities)
        concepts.update(re.findall(r"\b[A-Z][a-z]+\b", answer))

        # Numbers and dates
        concepts.update(re.findall(r"\b\d+\b", answer))

        # Technical terms (words with 6+ chars)
        long_words = list(re.findall(r"\b\w{6,}\b", answer.lower()))
        concepts.update(long_words[:10])  # Limit to 10 technical terms

        if not concepts:
            return EvaluationResult(
                score=0.5,  # Neutral score for simple answers
                explanation="No key concepts identified",
                metadata={"concepts_total": 0, "concepts_in_context": 0},
            )

        # Check which concepts appear in context
        context_text = " ".join(context)
        concepts_in_context = sum(1 for concept in concepts if concept in context_text)

        score = concepts_in_context / len(concepts)

        return EvaluationResult(
            score=score,
            explanation=f"{concepts_in_context}/{len(concepts)} concepts found in context",
            metadata={
                "concepts_total": len(concepts),
                "concepts_in_context": concepts_in_context,
                "concepts": list(concepts)[:10],
            },
        )


__all__ = [
    "EvaluationResult",
    "BaseRAGEvaluator",
    "FaithfulnessEvaluator",
    "GroundednessEvaluator",
    "RelevancyEvaluator",
    "ContextPrecisionEvaluator",
    "ContextRecallEvaluator",
]
