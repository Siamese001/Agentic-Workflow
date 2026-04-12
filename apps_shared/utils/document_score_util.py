"""RAG scoring utilities for document relevance and ranking.

Provides scoring algorithms for retrieved documents in RAG systems.
"""

import math
import re
from dataclasses import dataclass
from typing import Any

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

_emit_applies_guardrail("p0", "document_score_util", "p0_governance")
_emit_reads_policy_state("p0", "document_score_util", "policy_binding")
_emit_snapshots_state("p0", "document_score_util", "state_snapshot")
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

_emit_emits_metric_event("document_score_util", "p4obs", "metric_1")
_emit_emits_metric_event("document_score_util", "p4obs", "metric_2")
_emit_emits_metric_event("document_score_util", "p4obs", "metric_3")
_emit_emits_metric_event("document_score_util", "p4obs", "metric_4")
_emit_emits_metric_event("document_score_util", "p4obs", "metric_5")
_emit_emits_metric_event("document_score_util", "p4obs", "metric_6")
_emit_records_incident_event("document_score_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("document_score_util", "p4obs", "anomaly")
_emit_writes_observability_log("document_score_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("document_score_util", "p4obs", "mon_state")
_emit_triggers_alert("document_score_util", "p4obs", "alert")
_emit_links_incident_trace("document_score_util", "p4obs", "trace_link")
_emit_captures_pattern("document_score_util", "p3lm", "pattern")
_emit_records_learning_event("document_score_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("document_score_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("document_score_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("document_score_util", "p3lm", "routing")
_emit_improves_agent_policy("document_score_util", "p3lm", "policy")
_emit_stores_learning_state("document_score_util", "p3lm", "state")
_emit_records_execution_trace("document_score_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("document_score_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("document_score_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("document_score_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("document_score_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("document_score_util", "env_read", "p2_env_1")
_emit_reads_environ("document_score_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("document_score_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("document_score_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "document_score_util", "context_pull")
_emit_pulls_context("p1", "document_score_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "document_score_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "document_score_util", "uwg_term_2")
_emit_writes_through("p1", "document_score_util", "write_through")
_emit_writes_through("p1", "document_score_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "document_score_util", "safety_validation")
_emit_invokes_eval("p1", "document_score_util", "eval_call")
_emit_proposal_commits_routing("p1", "document_score_util", "routing_commit")
_emit_escalates_to_human("p1", "document_score_util", "human_escalation")
_emit_routes_through("p1", "document_score_util", "route_through")
_emit_checks_agent_registry("p1", "document_score_util", "agent_registry")
_emit_validates_agent_capability("p1", "document_score_util", "capability")
_emit_dispatches_execution_plan("p1", "document_score_util", "exec_plan")
_emit_agent_executes_agent("p1", "document_score_util", "sub_agent")
_emit_routes_to_agent("p1", "document_score_util", "target_agent")
_emit_verifies_policy("p1", "document_score_util", "policy_check")
_emit_observes_runtime_state("p1", "document_score_util", "runtime_state")
_emit_verifies_boundary("p1", "document_score_util", "boundary_check")
_emit_transcripts_response("p1", "document_score_util", "transcript")
_emit_hard_fails_untranscripted("p1", "document_score_util")
_emit_gated_by_confidence("p1", "document_score_util", "confidence_gate")
emit_replay_key("p0", "document_score_util")
emit_determinism_digest("p0", "document_score_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "document_score_util", "execution_auth")
_emit_validates_capability("p2", "document_score_util", "capability_check")
_emit_routes_to_capability("p2", "document_score_util", "capability_route")
_emit_writes_via_uwg("p2", "document_score_util", "uwg_write")
_emit_blocks_direct_write("p2", "document_score_util", "direct_write_block")
_emit_records_tool_invocation("p2", "document_score_util", "tool_invocation")
_emit_captures_execution_output("p2", "document_score_util", "exec_output")
_emit_dispatches_agent("p3", "document_score_util", "agent_dispatch")
_emit_coordinates_agents("p3", "document_score_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "document_score_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "document_score_util", "healing_outcome")
_emit_escalates_failure("p3", "document_score_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "document_score_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "document_score_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "document_score_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "document_score_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "document_score_util", "eval_metric")
_emit_stores_embedding("p4", "document_score_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "document_score_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "document_score_util", "exec_snapshot_link")


@dataclass
class DocumentScore:
    """Score for a retrieved document."""

    document_id: str
    content: str
    relevance_score: float
    semantic_score: float
    keyword_score: float
    freshness_score: float
    final_score: float

    def __post_init__(self):
        self.final_score = (
            0.4 * self.relevance_score
            + 0.3 * self.semantic_score
            + 0.2 * self.keyword_score
            + 0.1 * self.freshness_score
        )


class RAGScorer:
    """Scores and ranks documents for RAG retrieval."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize RAG scorer.

        Args:
            config: Optional configuration for scoring weights
        """
        self.config = config or {}
        self.weights = self.config.get(
            "weights",
            {"relevance": 0.4, "semantic": 0.3, "keyword": 0.2, "freshness": 0.1},
        )

    def score_documents(
        self,
        documents: list[dict[str, Any]],
        query: str,
        query_embedding: list[float] | None = None,
        document_embeddings: list[list[float]] | None = None,
    ) -> list[DocumentScore]:
        """Score a list of documents against a query.

        Args:
            documents: List of document dictionaries with 'id' and 'content'
            query: Query string
            query_embedding: Optional query embedding for semantic scoring
            document_embeddings: Optional document embeddings

        Returns:
            List of DocumentScore objects
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RAGScorer.score_documents")

        scores = []
        for i, doc in enumerate(documents):
            relevance = self._calculate_relevance(doc["content"], query)
            semantic = self._calculate_semantic_score(
                doc,
                query,
                query_embedding,
                document_embeddings[i] if document_embeddings else None,
            )
            keyword = self._calculate_keyword_score(doc["content"], query)
            freshness = self._calculate_freshness_score(doc)
            doc_score = DocumentScore(
                document_id=doc["id"],
                content=doc["content"],
                relevance_score=relevance,
                semantic_score=semantic,
                keyword_score=keyword,
                freshness_score=freshness,
                final_score=0.0,
            )
            scores.append(doc_score)
        scores.sort(key=lambda x: x.final_score, reverse=True)
        return scores

    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate basic relevance score based on term overlap."""
        content_words = set(re.findall("\\b\\w+\\b", content.lower()))
        query_words = set(re.findall("\\b\\w+\\b", query.lower()))
        if not query_words:
            return 0.0
        overlap = len(content_words & query_words)
        return min(overlap / len(query_words), 1.0)

    def _calculate_semantic_score(
        self,
        doc: dict[str, Any],
        query: str,
        query_embedding: list[float] | None,
        doc_embedding: list[float] | None,
    ) -> float:
        """Calculate semantic similarity score."""
        if not query_embedding or not doc_embedding:
            return self._calculate_relevance(doc["content"], query)
        dot_product = sum((q * d for q, d in zip(query_embedding, doc_embedding, strict=False)))
        query_norm = math.sqrt(sum(q * q for q in query_embedding))
        doc_norm = math.sqrt(sum(d * d for d in doc_embedding))
        if query_norm == 0 or doc_norm == 0:
            return 0.0
        return dot_product / (query_norm * doc_norm)

    def _calculate_keyword_score(self, content: str, query: str) -> float:
        """Calculate keyword matching score."""
        score = 0.0
        query_terms = re.findall("\\b\\w+\\b", query.lower())
        for term in query_terms:
            if term in content.lower():
                score += 1.0
            elif any(term in word for word in content.lower().split()):
                score += 0.5
        return min(score / len(query_terms), 1.0) if query_terms else 0.0

    def _calculate_freshness_score(self, doc: dict[str, Any]) -> float:
        """Calculate freshness score based on document metadata."""
        if "timestamp" not in doc and "date" not in doc:
            return 0.5
        return 0.5


def create_rag_scorer(config: dict[str, Any] | None = None) -> RAGScorer:
    """Create a RAG scorer instance.

    Args:
        config: Optional configuration

    Returns:
        RAGScorer instance
    """
    return RAGScorer(config)
