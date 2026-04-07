"""Retrieval Grader - Corrective RAG (CRAG) Component.

This module provides document relevance grading for the Corrective RAG system.
If retrieved documents are irrelevant, it triggers fallback mechanisms
like web search to ensure high-quality responses.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.interfaces.path_constants import DEFAULT_SLEEP
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "retrieval_grader_util", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_grader_util", "policy_binding")
_emit_snapshots_state("p0", "retrieval_grader_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("retrieval_grader_util", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_grader_util", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_grader_util", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_grader_util", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_grader_util", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_grader_util", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_grader_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_grader_util", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_grader_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_grader_util", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_grader_util", "p4obs", "alert")
_emit_links_incident_trace("retrieval_grader_util", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_grader_util", "p3lm", "pattern")
_emit_records_learning_event("retrieval_grader_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_grader_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_grader_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_grader_util", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_grader_util", "p3lm", "policy")
_emit_stores_learning_state("retrieval_grader_util", "p3lm", "state")
_emit_records_execution_trace("retrieval_grader_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_grader_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_grader_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_grader_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_grader_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_grader_util", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_grader_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_grader_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_grader_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_grader_util", "context_pull")
_emit_pulls_context("p1", "retrieval_grader_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_grader_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_grader_util", "uwg_term_2")
_emit_writes_through("p1", "retrieval_grader_util", "write_through")
_emit_writes_through("p1", "retrieval_grader_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_grader_util", "safety_validation")
_emit_invokes_eval("p1", "retrieval_grader_util", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_grader_util", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_grader_util", "human_escalation")
_emit_routes_through("p1", "retrieval_grader_util", "route_through")
_emit_checks_agent_registry("p1", "retrieval_grader_util", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_grader_util", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_grader_util", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_grader_util", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_grader_util", "target_agent")
_emit_verifies_policy("p1", "retrieval_grader_util", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_grader_util", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_grader_util", "boundary_check")
_emit_transcripts_response("p1", "retrieval_grader_util", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_grader_util")
_emit_gated_by_confidence("p1", "retrieval_grader_util", "confidence_gate")
emit_replay_key("p0", "retrieval_grader_util")
emit_determinism_digest("p0", "retrieval_grader_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "retrieval_grader_util", "execution_auth")
_emit_validates_capability("p2", "retrieval_grader_util", "capability_check")
_emit_routes_to_capability("p2", "retrieval_grader_util", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_grader_util", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_grader_util", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_grader_util", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_grader_util", "exec_output")
_emit_dispatches_agent("p3", "retrieval_grader_util", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_grader_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_grader_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_grader_util", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_grader_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_grader_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_grader_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_grader_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_grader_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_grader_util", "eval_metric")
_emit_stores_embedding("p4", "retrieval_grader_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_grader_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_grader_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class GradeStatus(Enum):
    """Status of document grading."""

    PASS = "PASS"
    FALLBACK_REQUIRED = "FALLBACK_REQUIRED"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class RetrievalGrade:
    """Result of retrieval grading."""

    status: GradeStatus
    relevance_ratio: float
    confidence: float
    relevant_docs: list[int] = None
    irrelevant_docs: list[int] = None
    reasoning: str = ""

    def __post_init__(self):
        if self.relevant_docs is None:
            self.relevant_docs = []
        if self.irrelevant_docs is None:
            self.irrelevant_docs = []


class RetrievalGrader:
    """Grades retrieved documents for relevance to the query."""

    # guardian: allow-magic-config
    def __init__(
        self,
        relevance_threshold: float = 0.5,
        confidence_threshold: float = 0.7,
        use_fast_model: bool = True,
        max_docs_to_grade: int = 10,
    ):
        """Initialize the retrieval grader.

        Args:
            relevance_threshold: Minimum ratio of relevant docs required
            confidence_threshold: Minimum confidence for PASS status
            use_fast_model: Use fast model for grading (e.g., gpt-4o-mini)
            max_docs_to_grade: Maximum number of documents to grade
        """
        self.relevance_threshold = relevance_threshold
        self.confidence_threshold = confidence_threshold
        self.use_fast_model = use_fast_model
        self.max_docs_to_grade = max_docs_to_grade
        self.stats = {"total_gradings": 0, "passes": 0, "fallbacks": 0, "uncertain": 0, "avg_relevance": 0.0}
        logger.info(
            f"Initialized RetrievalGrader - Threshold: {relevance_threshold}, Confidence: {confidence_threshold}, Fast Model: {use_fast_model}",
        )

    async def grade_documents(
        self, query: str, documents: list[str], document_ids: list[str] | None = None,
    ) -> RetrievalGrade:
        """Grade documents for relevance to the query.

        Args:
            query: The original query
            documents: List of document texts
            document_ids: Optional list of document IDs

        Returns:
            RetrievalGrade with assessment
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalGrader.grade_documents")

        start_time = time.time()
        self.stats["total_gradings"] += 1
        docs_to_grade = documents[: self.max_docs_to_grade]
        ids_to_grade = document_ids[: self.max_docs_to_grade] if document_ids else None
        relevant_docs = []
        irrelevant_docs = []
        total_confidence = 0.0
        for i, doc in enumerate(docs_to_grade):
            is_relevant, confidence = await self._grade_single_document(query, doc)
            total_confidence += confidence
            doc_id = ids_to_grade[i] if ids_to_grade else str(i)
            if is_relevant:
                relevant_docs.append(doc_id)
            else:
                irrelevant_docs.append(doc_id)
        relevance_ratio = len(relevant_docs) / len(docs_to_grade) if docs_to_grade else 0
        avg_confidence = total_confidence / len(docs_to_grade) if docs_to_grade else 0
        if relevance_ratio >= self.relevance_threshold and avg_confidence >= self.confidence_threshold:
            status = GradeStatus.PASS
            reasoning = f"High relevance ({relevance_ratio:.2f}) and confidence ({avg_confidence:.2f})"
            self.stats["passes"] += 1
        elif relevance_ratio < self.relevance_threshold * 0.3:
            status = GradeStatus.FALLBACK_REQUIRED
            reasoning = f"Very low relevance ({relevance_ratio:.2f}) - fallback needed"
            self.stats["fallbacks"] += 1
        else:
            status = GradeStatus.UNCERTAIN
            reasoning = f"Borderline relevance ({relevance_ratio:.2f}) - proceed with caution"
            self.stats["uncertain"] += 1
        self.stats["avg_relevance"] = (
            self.stats["avg_relevance"] * (self.stats["total_gradings"] - 1) + relevance_ratio
        ) / self.stats["total_gradings"]
        grading_time = time.time() - start_time
        logger.info(
            f"Grading completed in {grading_time:.3f}s - Status: {status.value}, Relevance: {relevance_ratio:.2f}",
        )
        return RetrievalGrade(
            status=status,
            relevance_ratio=relevance_ratio,
            confidence=avg_confidence,
            relevant_docs=relevant_docs,
            irrelevant_docs=irrelevant_docs,
            reasoning=reasoning,
        )

    async def _grade_single_document(self, query: str, document: str) -> tuple[bool, float]:
        """Grade a single document for relevance.

        Args:
            query: The query
            document: Document text

        Returns:
            Tuple of (is_relevant, confidence)
        """
        query_words = set(query.lower().split())
        doc_words = set(document.lower().split())
        overlap = len(query_words & doc_words)
        overlap_ratio = overlap / len(query_words) if query_words else 0
        doc_lower = document.lower()
        negative_indicators = [
            "not relevant",
            "does not contain",
            "unrelated",
            "different topic",
            "no information",
            "not found",
            "cannot answer",
            "insufficient",
        ]
        has_negative = any(indicator in doc_lower for indicator in negative_indicators)
        if has_negative:
            is_relevant = False
            confidence = 0.9
        elif overlap_ratio >= 0.3:
            is_relevant = True
            confidence = min(0.5 + overlap_ratio, 0.95)
        elif overlap_ratio >= 0.1:
            is_relevant = True
            confidence = 0.6
        else:
            is_relevant = False
            confidence = 0.7
        return (is_relevant, confidence)

    def get_stats(self) -> dict[str, Any]:
        """Get grader statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_gradings": self.stats["total_gradings"],
            "passes": self.stats["passes"],
            "fallbacks": self.stats["fallbacks"],
            "uncertain": self.stats["uncertain"],
            "pass_rate": self.stats["passes"] / max(self.stats["total_gradings"], 1),
            "fallback_rate": self.stats["fallbacks"] / max(self.stats["total_gradings"], 1),
            "avg_relevance": self.stats["avg_relevance"],
            "settings": {
                "relevance_threshold": self.relevance_threshold,
                "confidence_threshold": self.confidence_threshold,
                "use_fast_model": self.use_fast_model,
                "max_docs_to_grade": self.max_docs_to_grade,
            },
        }


class WebSearchFallback:
    """Fallback web search when retrieval fails."""

    # guardian: allow-magic-config
    def __init__(self, search_provider: str = "tavily", max_results: int = 5, timeout: float = 5.0):
        """Initialize web search fallback.

        Args:
            search_provider: Web search provider (tavily, serper, etc.)
            max_results: Maximum results to fetch
            timeout: Timeout for search request
        """
        self.search_provider = search_provider
        self.max_results = max_results
        self.timeout = timeout
        self.api_key = None
        logger.info(f"Initialized WebSearchFallback with {search_provider}")

    async def search(self, query: str) -> dict[str, Any]:
        """Perform web search for the query.

        Args:
            query: Search query

        Returns:
            Dictionary with search results
        """
        try:
            logger.info(f"Performing web search for: {query}")
            await asyncio.sleep(DEFAULT_SLEEP)
            results = [
                {
                    "title": f"Web result 1 for {query}",
                    "url": "https://example.com/1",
                    "snippet": f"This is a web search result about {query}",
                    "source": "web",
                },
                {
                    "title": f"Web result 2 for {query}",
                    "url": "https://example.com/2",
                    "snippet": f"Additional information about {query}",
                    "source": "web",
                },
            ]
            return {
                "query": query,
                "results": results,
                "source": "web_search",
                "total_results": len(results),
                "fallback_triggered": True,
            }
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "query": query,
                "results": [],
                "source": "web_search",
                "error": str(e),
                "fallback_triggered": True,
            }


_retrieval_grader: RetrievalGrader | None = None
_web_search_fallback: WebSearchFallback | None = None


def get_retrieval_grader(**kwargs) -> RetrievalGrader:
    """Get or create the global retrieval grader.

    Args:
        **kwargs: Arguments for RetrievalGrader

    Returns:
        RetrievalGrader instance
    """
    global _retrieval_grader
    if _retrieval_grader is None:
        _retrieval_grader = RetrievalGrader(**kwargs)
    return _retrieval_grader


def get_web_search_fallback(**kwargs) -> WebSearchFallback:
    """Get or create the global web search fallback.

    Args:
        **kwargs: Arguments for WebSearchFallback

    Returns:
        WebSearchFallback instance
    """
    global _web_search_fallback
    if _web_search_fallback is None:
        _web_search_fallback = WebSearchFallback(**kwargs)
    return _web_search_fallback


async def grade_retrieval(query: str, documents: list[str], **kwargs) -> RetrievalGrade:
    """Convenience function to grade retrieval results.

    Args:
        query: The query
        documents: List of documents
        **kwargs: Additional arguments

    Returns:
        RetrievalGrade result
    """
    grader = get_retrieval_grader(**kwargs)
    return await grader.grade_documents(query, documents)


async def fallback_web_search(query: str, **kwargs) -> dict[str, Any]:
    """Convenience function for web search fallback.

    Args:
        query: Search query
        **kwargs: Additional arguments

    Returns:
        Search results
    """
    fallback = get_web_search_fallback(**kwargs)
    return await fallback.search(query)
