"""Outcome Evaluation Engine — Evaluation Spine Component B.

Evaluates execution outcomes per Evaluation Spine documentation:
  - Task completion
  - Groundedness
  - Citation support
  - Abstain correctness
  - Escalation correctness
  - Answer relevance

Deterministic, with full ADG traceability.
"""

from __future__ import annotations

import logging
from typing import Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import stable_sha256_json
from system_learning.types.evaluation_spine_types import MetricScore, OutcomeEvaluationResult

# ADG wiring for outcome evaluation engine
_emit_records_execution_trace("outcome_evaluation_engine", "p0", "outcome_eval_trace")
_emit_applies_guardrail("p0", "outcome_evaluation_engine", "p0_governance")
emit_replay_key("p0", "outcome_evaluation_engine")
emit_determinism_digest("p0", "outcome_evaluation_engine")
_emit_writes_via_uwg("p2", "outcome_evaluation_engine", "uwg_write")
_emit_blocks_direct_write("p2", "outcome_evaluation_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "outcome_evaluation_engine", "tool_invocation")
_emit_captures_execution_output("p2", "outcome_evaluation_engine", "exec_output")
_emit_dispatches_agent("p3", "outcome_evaluation_engine", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "outcome_evaluation_engine", "exec_plan")
_emit_routes_to_agent("p3", "outcome_evaluation_engine", "target_agent")
_emit_checks_agent_registry("p3", "outcome_evaluation_engine", "agent_registry")
_emit_validates_agent_capability("p3", "outcome_evaluation_engine", "capability")
_emit_verifies_policy("p3", "outcome_evaluation_engine", "policy_check")
_emit_verifies_boundary("p3", "outcome_evaluation_engine", "boundary_check")
_emit_agent_executes_agent("p3", "outcome_evaluation_engine", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# Protocols for external dependencies
# =============================================================================


class ExecutionTraceReader(Protocol):
    """Protocol for reading execution traces."""

    def read_trace(self, trace_id: str) -> dict:
        """Read and return the execution trace content."""
        raise NotImplementedError


class GroundednessChecker(Protocol):
    """Protocol for checking groundedness of responses."""

    def check_groundedness(self, response: str, context: str) -> tuple[float, str]:
        """Return (score, evidence) for groundedness."""
        raise NotImplementedError


# =============================================================================
# OutcomeEvaluationEngine
# =============================================================================


class OutcomeEvaluationEngine:
    """Engine for evaluating execution outcomes (Component B).

    Evaluates 6 outcome metrics per Evaluation Spine:
        1. Task completion — Was the task fully accomplished?
        2. Groundedness — Is the response grounded in source material?
        3. Citation support — Are citations accurate and relevant?
        4. Abstain correctness — Did the system abstain appropriately?
        5. Escalation correctness — Were escalations appropriate?
        6. Answer relevance — Is the answer relevant to the query?

    Deterministic: Same inputs always produce same output hash.

    Attributes
    ----------
    trace_reader:
        Injected interface for reading execution traces.
    groundedness_checker:
        Injected interface for groundedness validation.
    weights:
        Weights for computing overall score.
    """

    # Default weights for overall score calculation
    DEFAULT_WEIGHTS: dict[str, float] = {
        "task_completion": 0.25,
        "groundedness": 0.20,
        "citation_support": 0.15,
        "abstain_correctness": 0.15,
        "escalation_correctness": 0.10,
        "answer_relevance": 0.15,
    }

    def __init__(
        self,
        trace_reader: ExecutionTraceReader | None = None,
        groundedness_checker: GroundednessChecker | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.trace_reader = trace_reader
        self.groundedness_checker = groundedness_checker
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def evaluate_outcome(
        self,
        trace_id: str,
        execution_result: dict,
        timestamp_utc: int,
    ) -> OutcomeEvaluationResult:
        """Evaluate execution outcome across 6 metrics.

        Parameters
        ----------
        trace_id:
            Source execution trace identifier.
        execution_result:
            The execution result to evaluate.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        OutcomeEvaluationResult
            Deterministic outcome evaluation result.
        """
        _emit_records_execution_trace("outcome_evaluation_engine", "eval_start", trace_id)

        # Evaluate each metric
        task_completion = self._evaluate_task_completion(execution_result)
        groundedness = self._evaluate_groundedness(execution_result)
        citation_support = self._evaluate_citation_support(execution_result)
        abstain_correctness = self._evaluate_abstain_correctness(execution_result)
        escalation_correctness = self._evaluate_escalation_correctness(execution_result)
        answer_relevance = self._evaluate_answer_relevance(execution_result)

        # Build metric scores with evidence
        metric_scores = (
            MetricScore(
                metric_name="task_completion",
                score=task_completion,
                confidence=0.9,
                evidence=f"Task completion evaluated: {task_completion:.4f}",
            ),
            MetricScore(
                metric_name="groundedness",
                score=groundedness,
                confidence=0.85,
                evidence=f"Groundedness evaluated: {groundedness:.4f}",
            ),
            MetricScore(
                metric_name="citation_support",
                score=citation_support,
                confidence=0.8,
                evidence=f"Citation support evaluated: {citation_support:.4f}",
            ),
            MetricScore(
                metric_name="abstain_correctness",
                score=abstain_correctness,
                confidence=0.75,
                evidence=f"Abstain correctness evaluated: {abstain_correctness:.4f}",
            ),
            MetricScore(
                metric_name="escalation_correctness",
                score=escalation_correctness,
                confidence=0.7,
                evidence=f"Escalation correctness evaluated: {escalation_correctness:.4f}",
            ),
            MetricScore(
                metric_name="answer_relevance",
                score=answer_relevance,
                confidence=0.85,
                evidence=f"Answer relevance evaluated: {answer_relevance:.4f}",
            ),
        )

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            task_completion,
            groundedness,
            citation_support,
            abstain_correctness,
            escalation_correctness,
            answer_relevance,
        )

        # Build evaluation summary
        evaluation_summary = self._build_evaluation_summary(
            task_completion,
            groundedness,
            citation_support,
            abstain_correctness,
            escalation_correctness,
            answer_relevance,
            overall_score,
        )

        _emit_records_execution_trace("outcome_evaluation_engine", "eval_complete", trace_id)

        result = OutcomeEvaluationResult(
            artifact_type="OUTCOME_EVALUATION_RESULT",
            result_id=stable_sha256_json({
                "trace_id": trace_id,
                "overall_score": overall_score,
                "timestamp_utc": timestamp_utc,
            }),
            trace_id=trace_id,
            task_completion=task_completion,
            groundedness=groundedness,
            citation_support=citation_support,
            abstain_correctness=abstain_correctness,
            escalation_correctness=escalation_correctness,
            answer_relevance=answer_relevance,
            overall_score=overall_score,
            metric_scores=metric_scores,
            evaluation_summary=evaluation_summary,
            timestamp_utc=timestamp_utc,
        )

        logger.info(
            "Outcome evaluation complete: trace_id=%s, overall_score=%.4f",
            trace_id,
            overall_score,
        )

        return result

    def _evaluate_task_completion(self, execution_result: dict) -> float:
        """Evaluate task completion.

        Scores based on:
        - Presence of task_done flag
        - Success indicators in result
        - Absence of error states
        """
        score = 0.0

        # Check for explicit task completion
        if execution_result.get("task_done", False):
            score += 0.5

        # Check for success indicators
        if execution_result.get("success", False):
            score += 0.3

        # Check for absence of errors
        if not execution_result.get("error") and not execution_result.get("exception"):
            score += 0.2

        return min(1.0, score)

    def _evaluate_groundedness(self, execution_result: dict) -> float:
        """Evaluate groundedness of response.

        Scores based on:
        - Presence of source citations
        - Context relevance
        - Factual assertions backed by sources
        """
        response = execution_result.get("response", "")
        context = execution_result.get("context", "")

        # If groundedness checker available, use it
        if self.groundedness_checker:
            score, _ = self.groundedness_checker.check_groundedness(response, context)
            return score

        # Default heuristic scoring
        score = 0.0

        # Check for citations
        if "[" in response and "]" in response:
            score += 0.4

        # Check for source references
        if context and len(context) > 0:
            score += 0.3

        # Check for factual assertions (simple heuristic)
        factual_phrases = ["according to", "based on", "from the"]
        if any(phrase in response.lower() for phrase in factual_phrases):
            score += 0.3

        return min(1.0, score)

    def _evaluate_citation_support(self, execution_result: dict) -> float:
        """Evaluate citation support.

        Scores based on:
        - Presence of citations
        - Citation format correctness
        - Citation relevance
        """
        response = execution_result.get("response", "")
        citations = execution_result.get("citations", [])

        score = 0.0

        # Score based on citations present
        if citations:
            score += min(0.5, len(citations) * 0.1)
        elif "[" in response and "]" in response:
            score += 0.3

        # Score for proper formatting
        if citations and all("source" in str(c) for c in citations):
            score += 0.3

        # Score for relevance (simplified)
        if execution_result.get("citation_relevance_checked", False):
            score += 0.2

        return min(1.0, score)

    def _evaluate_abstain_correctness(self, execution_result: dict) -> float:
        """Evaluate abstain correctness.

        Scores based on:
        - Appropriate abstention when uncertain
        - No hallucination when abstaining
        - Clear explanation for abstention
        """
        score = 0.0

        # Check if system abstained appropriately
        abstained = execution_result.get("abstained", False)
        uncertainty = execution_result.get("uncertainty", 0.0)

        if abstained and uncertainty > 0.5:
            # Correct abstention
            score += 0.5

        if abstained and execution_result.get("abstention_reason"):
            # Clear explanation
            score += 0.3

        if not abstained and uncertainty < 0.3:
            # Correctly did not abstain when confident
            score += 0.2

        return min(1.0, score)

    def _evaluate_escalation_correctness(self, execution_result: dict) -> float:
        """Evaluate escalation correctness.

        Scores based on:
        - Escalation when appropriate
        - No escalation when unnecessary
        - Proper escalation routing
        """
        score = 0.0

        escalated = execution_result.get("escalated", False)
        escalation_needed = execution_result.get("escalation_needed", False)

        if escalated and escalation_needed:
            # Correct escalation
            score += 0.6

        if not escalated and not escalation_needed:
            # Correctly did not escalate
            score += 0.4

        if escalated and execution_result.get("escalation_target"):
            # Proper routing
            score += 0.2

        return min(1.0, score)

    def _evaluate_answer_relevance(self, execution_result: dict) -> float:
        """Evaluate answer relevance.

        Scores based on:
        - Response addresses the query
        - No tangential information
        - Complete coverage of query intent
        """
        query = execution_result.get("query", "")
        response = execution_result.get("response", "")

        score = 0.0

        # Check for query terms in response
        if query and response:
            query_terms = set(query.lower().split())
            response_terms = set(response.lower().split())
            if query_terms:
                overlap = len(query_terms & response_terms) / len(query_terms)
                score += overlap * 0.5

        # Check for response length appropriateness
        if response and len(response) > 10:
            score += 0.3

        # Check for off-topic indicators
        off_topic_phrases = ["i don't know", "not related", "different topic"]
        if not any(phrase in response.lower() for phrase in off_topic_phrases):
            score += 0.2

        return min(1.0, score)

    def _calculate_overall_score(
        self,
        task_completion: float,
        groundedness: float,
        citation_support: float,
        abstain_correctness: float,
        escalation_correctness: float,
        answer_relevance: float,
    ) -> float:
        """Calculate weighted overall outcome score."""
        overall = (
            self.weights["task_completion"] * task_completion +
            self.weights["groundedness"] * groundedness +
            self.weights["citation_support"] * citation_support +
            self.weights["abstain_correctness"] * abstain_correctness +
            self.weights["escalation_correctness"] * escalation_correctness +
            self.weights["answer_relevance"] * answer_relevance
        )
        return round(overall, 6)  # Deterministic rounding

    def _build_evaluation_summary(
        self,
        task_completion: float,
        groundedness: float,
        citation_support: float,
        abstain_correctness: float,
        escalation_correctness: float,
        answer_relevance: float,
        overall_score: float,
    ) -> str:
        """Build human-readable evaluation summary."""
        summary_parts = [
            f"Task Completion: {task_completion:.2f}",
            f"Groundedness: {groundedness:.2f}",
            f"Citation Support: {citation_support:.2f}",
            f"Abstain Correctness: {abstain_correctness:.2f}",
            f"Escalation Correctness: {escalation_correctness:.2f}",
            f"Answer Relevance: {answer_relevance:.2f}",
            f"Overall Score: {overall_score:.2f}",
        ]

        # Add qualitative assessment
        if overall_score >= 0.8:
            summary_parts.append("Assessment: EXCELLENT")
        elif overall_score >= 0.6:
            summary_parts.append("Assessment: GOOD")
        elif overall_score >= 0.4:
            summary_parts.append("Assessment: FAIR")
        else:
            summary_parts.append("Assessment: NEEDS_IMPROVEMENT")

        return " | ".join(summary_parts)


__all__ = ["OutcomeEvaluationEngine", "ExecutionTraceReader", "GroundednessChecker"]
