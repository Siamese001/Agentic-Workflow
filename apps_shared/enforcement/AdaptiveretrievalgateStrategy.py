"""Adaptive Retrieval Gate - Smart Guard for RAG Queries.

This component acts as a smart gatekeeper that decides whether a query
requires retrieval from the vector database or can be handled from context.
"""

import logging
import re

from pydantic import BaseModel, Field
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class RetrievalDecision(BaseModel):
    """Decision about whether to retrieve from vector database."""

    should_retrieve: bool = Field(..., description="Whether retrieval is needed")
    reason: str = Field(..., description="Explanation for the decision")
    query_type: str = Field(..., description="Type of query classified")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in decision")


class AdaptiveRetrievalGate:
    """Smart gate that determines if retrieval is necessary for a query.

    Uses pattern matching and complexity analysis to avoid unnecessary
    vector database searches for simple or contextual queries.
    """

    def __init__(self):
        """Initialize the Adaptive Retrieval Gate."""
        self.patterns = {
            "conversational": re.compile(
                "^(hi|hello|hey|thanks|thank you|ok|okay|bye|goodbye|yes|no|sure|got it|understood|cool|awesome|great|perfect)$",
                re.IGNORECASE,
            ),
            "reference": re.compile(
                "\\b(previous|last|that|above|mentioned|earlier|said|told|asked|discussed)\\b", re.IGNORECASE
            ),
            "self_reference": re.compile(
                "\\b(who are you|what are you|what can you do|how do you work|your name|help)\\b",
                re.IGNORECASE,
            ),
            "continuation": re.compile(
                "^(and|but|so|then|also|plus|however|therefore|meanwhile)\\b", re.IGNORECASE
            ),
        }
        self.complex_keywords = {
            "metrics",
            "how to",
            "latest",
            "compare",
            "strategy",
            "plan",
            "analyze",
            "evaluate",
            "recommend",
            "implement",
            "design",
            "architecture",
            "framework",
            "best practices",
            "guidelines",
            "statistics",
            "data",
            "performance",
            "optimization",
            "trends",
            "forecast",
            "roadmap",
            "timeline",
            "requirements",
        }
        self.question_patterns = [
            "\\bwhat\\s+(is|are|were|do|does|did)\\b",
            "\\bwhen\\s+(was|were|is|are|did|do)\\b",
            "\\bwhere\\s+(is|are|was|were|did|do)\\b",
            "\\bwhich\\s+(is|are|was|were|did|do)\\b",
            "\\bwho\\s+(is|are|was|were|did|do)\\b",
            "\\bwhy\\s+(is|are|was|were|did|do|does)\\b",
            "\\bhow\\s+(can|could|should|would|will|do|does|did)\\b",
        ]
        self.compiled_questions = [re.compile(p, re.IGNORECASE) for p in self.question_patterns]
        logger.info("Initialized AdaptiveRetrievalGate")

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query.

        Args:
            query: Query string to classify

        Returns:
            Query type string
        """
        query_lower = query.lower().strip()
        if self.patterns["conversational"].match(query):
            return "CONVERSATIONAL"
        if self.patterns["self_reference"].search(query):
            return "SELF_REFERENCE"
        if self.patterns["reference"].search(query):
            return "REFERENCE"
        if self.patterns["continuation"].match(query):
            return "CONTINUATION"
        if any(keyword in query_lower for keyword in self.complex_keywords):
            return "COMPLEX"
        if any(pattern.search(query) for pattern in self.compiled_questions):
            return "FACTUAL"
        return "COMPLEX"

    def _calculate_complexity_score(self, query: str, query_type: str) -> float:
        """Calculate complexity score for the query.

        Args:
            query: Query string
            query_type: Classified query type

        Returns:
            Complexity score (0-1)
        """
        type_scores = {
            "CONVERSATIONAL": 0.0,
            "SELF_REFERENCE": 0.0,
            "REFERENCE": 0.1,
            "CONTINUATION": 0.2,
            "FACTUAL": 0.6,
            "COMPLEX": 0.8,
        }
        base_score = type_scores.get(query_type, 0.5)
        word_count = len(query.split())
        if word_count > 10:
            base_score = min(1.0, base_score + 0.2)
        elif word_count < 3:
            base_score = max(0.0, base_score - 0.1)
        if query.endswith("?"):
            base_score = min(1.0, base_score + 0.1)
        complex_count = sum(1 for keyword in self.complex_keywords if keyword in query.lower())
        if complex_count > 0:
            base_score = min(1.0, base_score + 0.1 * min(complex_count, 2))
        return base_score

    def should_retrieve(self, query: str, history: list[dict] | None = None) -> RetrievalDecision:
        """Determine if retrieval is needed for the query.

        Args:
            query: Query string to evaluate
            history: Optional conversation history for context

        Returns:
            RetrievalDecision with recommendation
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AdaptiveRetrievalGate.should_retrieve")

        query = query.strip()
        if not query:
            return RetrievalDecision(
                should_retrieve=False, reason="Empty query", query_type="EMPTY", confidence=1.0
            )
        query_type = self._classify_query_type(query)
        complexity_score = self._calculate_complexity_score(query, query_type)
        should_retrieve = False
        reason = ""
        confidence = 0.9
        if query_type == "CONVERSATIONAL":
            should_retrieve = False
            reason = "Conversational query - no retrieval needed"
            confidence = 0.95
        elif query_type == "SELF_REFERENCE":
            should_retrieve = False
            reason = "Query about assistant - use internal knowledge"
            confidence = 0.9
        elif query_type == "REFERENCE":
            should_retrieve = False
            reason = "Reference to previous context - check conversation history"
            confidence = 0.85
        elif query_type == "CONTINUATION":
            should_retrieve = False
            reason = "Continuation marker - context should provide information"
            confidence = 0.8
        elif query_type == "FACTUAL":
            if complexity_score > 0.4:
                should_retrieve = True
                reason = "Factual question requiring external knowledge"
            else:
                should_retrieve = False
                reason = "Simple factual query - may be handled from context"
        elif query_type == "COMPLEX":
            should_retrieve = True
            reason = "Complex query requiring retrieval"
            confidence = 0.85
        if should_retrieve:
            if len(query.split()) < 4 and (
                not any(pattern.search(query) for pattern in self.compiled_questions)
            ):
                should_retrieve = False
                reason = "Short query likely a clarification"
                confidence = 0.7
        logger.info(
            f"Retrieval decision: {should_retrieve} | Type: {query_type} | Reason: {reason} | Query: {query[:50]}..."
        )
        return RetrievalDecision(
            should_retrieve=should_retrieve, reason=reason, query_type=query_type, confidence=confidence
        )

    def get_statistics(self, decisions: list[RetrievalDecision]) -> dict[str, float]:
        """Calculate statistics from a list of retrieval decisions.

        Args:
            decisions: List of RetrievalDecision objects

        Returns:
            Dictionary with statistics
        """
        if not decisions:
            return {}
        total = len(decisions)
        retrieve_count = sum(1 for d in decisions if d.should_retrieve)
        type_counts = {}
        for decision in decisions:
            type_counts[decision.query_type] = type_counts.get(decision.query_type, 0) + 1
        return {
            "total_queries": total,
            "retrieval_rate": retrieve_count / total,
            "type_distribution": {k: v / total for k, v in type_counts.items()},
            "avg_confidence": sum(d.confidence for d in decisions) / total,
        }


def should_retrieve(query: str, history: list[dict] | None = None) -> bool:
    """Quick check if retrieval is needed.

    Args:
        query: Query string
        history: Optional conversation history

    Returns:
        Boolean indicating if retrieval is needed
    """
    gate = AdaptiveRetrievalGate()
    decision = gate.should_retrieve(query, history)
    return decision.should_retrieve
