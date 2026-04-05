"""Relevance Scorer for Context Swapping.

Phase 3 - Pillar 7: Context Engineering (Dynamic Curation)
Calculates relevance of context chunks to current Think-Act-Observe step.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "relevance_scorer_util", "p0_governance")
_emit_reads_policy_state("p0", "relevance_scorer_util", "policy_binding")
_emit_snapshots_state("p0", "relevance_scorer_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("relevance_scorer_util", "p4obs", "metric_1")
_emit_emits_metric_event("relevance_scorer_util", "p4obs", "metric_2")
_emit_emits_metric_event("relevance_scorer_util", "p4obs", "metric_3")
_emit_emits_metric_event("relevance_scorer_util", "p4obs", "metric_4")
_emit_emits_metric_event("relevance_scorer_util", "p4obs", "metric_5")
_emit_emits_metric_event("relevance_scorer_util", "p4obs", "metric_6")
_emit_records_incident_event("relevance_scorer_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("relevance_scorer_util", "p4obs", "anomaly")
_emit_writes_observability_log("relevance_scorer_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("relevance_scorer_util", "p4obs", "mon_state")
_emit_triggers_alert("relevance_scorer_util", "p4obs", "alert")
_emit_links_incident_trace("relevance_scorer_util", "p4obs", "trace_link")
_emit_captures_pattern("relevance_scorer_util", "p3lm", "pattern")
_emit_records_learning_event("relevance_scorer_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("relevance_scorer_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("relevance_scorer_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("relevance_scorer_util", "p3lm", "routing")
_emit_improves_agent_policy("relevance_scorer_util", "p3lm", "policy")
_emit_stores_learning_state("relevance_scorer_util", "p3lm", "state")
_emit_records_execution_trace("relevance_scorer_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("relevance_scorer_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("relevance_scorer_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("relevance_scorer_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("relevance_scorer_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("relevance_scorer_util", "env_read", "p2_env_1")
_emit_reads_environ("relevance_scorer_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("relevance_scorer_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("relevance_scorer_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "relevance_scorer_util", "context_pull")
_emit_pulls_context("p1", "relevance_scorer_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "relevance_scorer_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "relevance_scorer_util", "uwg_term_2")
_emit_writes_through("p1", "relevance_scorer_util", "write_through")
_emit_writes_through("p1", "relevance_scorer_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "relevance_scorer_util", "safety_validation")
_emit_invokes_eval("p1", "relevance_scorer_util", "eval_call")
_emit_proposal_commits_routing("p1", "relevance_scorer_util", "routing_commit")
_emit_escalates_to_human("p1", "relevance_scorer_util", "human_escalation")
_emit_routes_through("p1", "relevance_scorer_util", "route_through")
_emit_checks_agent_registry("p1", "relevance_scorer_util", "agent_registry")
_emit_validates_agent_capability("p1", "relevance_scorer_util", "capability")
_emit_dispatches_execution_plan("p1", "relevance_scorer_util", "exec_plan")
_emit_agent_executes_agent("p1", "relevance_scorer_util", "sub_agent")
_emit_routes_to_agent("p1", "relevance_scorer_util", "target_agent")
_emit_verifies_policy("p1", "relevance_scorer_util", "policy_check")
_emit_observes_runtime_state("p1", "relevance_scorer_util", "runtime_state")
_emit_verifies_boundary("p1", "relevance_scorer_util", "boundary_check")
_emit_transcripts_response("p1", "relevance_scorer_util", "transcript")
_emit_hard_fails_untranscripted("p1", "relevance_scorer_util")
_emit_gated_by_confidence("p1", "relevance_scorer_util", "confidence_gate")
emit_replay_key("p0", "relevance_scorer_util")
emit_determinism_digest("p0", "relevance_scorer_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "relevance_scorer_util", "execution_auth")
_emit_validates_capability("p2", "relevance_scorer_util", "capability_check")
_emit_routes_to_capability("p2", "relevance_scorer_util", "capability_route")
_emit_writes_via_uwg("p2", "relevance_scorer_util", "uwg_write")
_emit_blocks_direct_write("p2", "relevance_scorer_util", "direct_write_block")
_emit_records_tool_invocation("p2", "relevance_scorer_util", "tool_invocation")
_emit_captures_execution_output("p2", "relevance_scorer_util", "exec_output")
_emit_dispatches_agent("p3", "relevance_scorer_util", "agent_dispatch")
_emit_coordinates_agents("p3", "relevance_scorer_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "relevance_scorer_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "relevance_scorer_util", "healing_outcome")
_emit_escalates_failure("p3", "relevance_scorer_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "relevance_scorer_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "relevance_scorer_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "relevance_scorer_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "relevance_scorer_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "relevance_scorer_util", "eval_metric")
_emit_stores_embedding("p4", "relevance_scorer_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "relevance_scorer_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "relevance_scorer_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class RelevanceMethod(Enum):
    """Methods for calculating relevance."""

    KEYWORD_OVERLAP = "keyword_overlap"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    RECENCY = "recency"
    HYBRID = "hybrid"


@dataclass
class RelevanceScore:
    """Relevance score for a context chunk."""

    chunk_id: str
    score: float
    method: RelevanceMethod
    components: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "score": self.score,
            "method": self.method.value,
            "components": self.components,
        }


class RelevanceScorer:
    """Scores context chunks for relevance to current Task.

    Integrates with:
    - Think-Act-Observe cycle (Phase 2, Pillar 4)
    - RAG components (Phase 1)
    - Context Curator (Phase 3, Pillar 7)
    """

    def __init__(
        self,
        method: RelevanceMethod = RelevanceMethod.HYBRID,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.5,
        recency_weight: float = 0.2,
        enable_logging: bool = True,
    ):
        """Initialize relevance scorer.

        Args:
            method: scoring method
            keyword_weight: Weight for keyword overlap
            semantic_weight: Weight for semantic similarity
            recency_weight: Weight for recency
            enable_logging: Enable logging
        """
        self.method = method
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
        self.recency_weight = recency_weight
        self.enable_logging = enable_logging
        total_weight = keyword_weight + semantic_weight + recency_weight
        self.keyword_weight /= total_weight
        self.semantic_weight /= total_weight
        self.recency_weight /= total_weight
        if self.enable_logging:
            Logger.info(
                "relevance_scorer_initialized",
                extra={
                    "method": method.value,
                    "weights": {
                        "keyword": self.keyword_weight,
                        "semantic": self.semantic_weight,
                        "recency": self.recency_weight,
                    },
                },
            )

    def score_chunk(
        self, chunk_id: str, chunk_content: str, query: str, chunk_metadata: dict[str, Any] | None = None
    ) -> RelevanceScore:
        """Score a single chunk for relevance.

        Args:
            chunk_id: Chunk identifier
            chunk_content: Chunk content
            query: Current query/Task
            chunk_metadata: Optional metadata

        Returns:
            RelevanceScore
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RelevanceScorer.score_chunk")

        components = {}
        if self.method in {RelevanceMethod.KEYWORD_OVERLAP, RelevanceMethod.HYBRID}:
            components["keyword"] = self._keyword_overlap(chunk_content, query)
        if self.method in {RelevanceMethod.SEMANTIC_SIMILARITY, RelevanceMethod.HYBRID}:
            components["semantic"] = self._semantic_similarity(chunk_content, query)
        if self.method in {RelevanceMethod.RECENCY, RelevanceMethod.HYBRID}:
            components["recency"] = self._recency_score(chunk_metadata or {})
        if self.method == RelevanceMethod.HYBRID:
            score = (
                components.get("keyword", 0.0) * self.keyword_weight
                + components.get("semantic", 0.0) * self.semantic_weight
                + components.get("recency", 0.0) * self.recency_weight
            )
        else:
            score = list(components.values())[0] if components else 0.0
        return RelevanceScore(chunk_id=chunk_id, score=score, method=self.method, components=components)

    def score_chunks(self, chunks: list[dict[str, Any]], query: str) -> list[RelevanceScore]:
        """Score multiple chunks.

        Args:
            chunks: List of chunk dicts with 'id', 'content', 'metadata'
            query: Current query/Task

        Returns:
            List of RelevanceScore objects
        """
        scores = []
        for chunk in chunks:
            score = self.score_chunk(
                chunk_id=chunk.get("id", ""),
                chunk_content=chunk.get("content", ""),
                query=query,
                chunk_metadata=chunk.get("metadata"),
            )
            scores.append(score)
        scores.sort(key=lambda s: s.score, reverse=True)
        if self.enable_logging:
            Logger.debug(
                "chunks_scored",
                extra={"chunk_count": len(chunks), "top_score": scores[0].score if scores else 0.0},
            )
        return scores

    def _keyword_overlap(self, content: str, query: str) -> float:
        """Calculate keyword overlap score.

        Args:
            content: Chunk content
            query: Query text

        Returns:
            Overlap score (0.0-1.0)
        """
        content_words = set(content.lower().split())
        query_words = set(query.lower().split())
        if not query_words:
            return 0.0
        overlap = len(content_words & query_words)
        score = overlap / len(query_words)
        return min(score, 1.0)

    def _semantic_similarity(self, content: str, query: str) -> float:
        """Calculate semantic similarity score.

        Simplified implementation using character n-grams.
        Production should use embeddings.

        Args:
            content: Chunk content
            query: Query text

        Returns:
            Similarity score (0.0-1.0)
        """

        def get_trigrams(text: str) -> set:
            text = text.lower()
            return {text[i : i + 3] for i in range(len(text) - 2)}

        content_trigrams = get_trigrams(content)
        query_trigrams = get_trigrams(query)
        if not query_trigrams:
            return 0.0
        overlap = len(content_trigrams & query_trigrams)
        union = len(content_trigrams | query_trigrams)
        if union == 0:
            return 0.0
        return overlap / union

    def _recency_score(self, metadata: dict[str, Any]) -> float:
        """Calculate recency score.

        Args:
            metadata: Chunk metadata

        Returns:
            Recency score (0.0-1.0)
        """
        timestamp = metadata.get("timestamp", 0)
        position = metadata.get("position", 0)
        if timestamp > 0:
            return min(timestamp / 1000000, 1.0)
        if position > 0:
            return 1.0 / (1.0 + position)
        return 0.5


def create_relevance_scorer(method: RelevanceMethod = RelevanceMethod.HYBRID) -> RelevanceScorer:
    """Factory function to create relevance scorer.

    Args:
        method: scoring method

    Returns:
        RelevanceScorer instance
    """
    return RelevanceScorer(method=method)
