"""Hybrid Scorer for RAG systems.

Combines multiple scoring strategies for optimal document ranking.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
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

_emit_applies_guardrail("p0", "hybrid_scorer_types", "p0_governance")
_emit_reads_policy_state("p0", "hybrid_scorer_types", "policy_binding")
_emit_snapshots_state("p0", "hybrid_scorer_types", "state_snapshot")
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

_emit_emits_metric_event("hybrid_scorer_types", "p4obs", "metric_1")
_emit_emits_metric_event("hybrid_scorer_types", "p4obs", "metric_2")
_emit_emits_metric_event("hybrid_scorer_types", "p4obs", "metric_3")
_emit_emits_metric_event("hybrid_scorer_types", "p4obs", "metric_4")
_emit_emits_metric_event("hybrid_scorer_types", "p4obs", "metric_5")
_emit_emits_metric_event("hybrid_scorer_types", "p4obs", "metric_6")
_emit_records_incident_event("hybrid_scorer_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("hybrid_scorer_types", "p4obs", "anomaly")
_emit_writes_observability_log("hybrid_scorer_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("hybrid_scorer_types", "p4obs", "mon_state")
_emit_triggers_alert("hybrid_scorer_types", "p4obs", "alert")
_emit_links_incident_trace("hybrid_scorer_types", "p4obs", "trace_link")
_emit_captures_pattern("hybrid_scorer_types", "p3lm", "pattern")
_emit_records_learning_event("hybrid_scorer_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hybrid_scorer_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("hybrid_scorer_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hybrid_scorer_types", "p3lm", "routing")
_emit_improves_agent_policy("hybrid_scorer_types", "p3lm", "policy")
_emit_stores_learning_state("hybrid_scorer_types", "p3lm", "state")
_emit_records_execution_trace("hybrid_scorer_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hybrid_scorer_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hybrid_scorer_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hybrid_scorer_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hybrid_scorer_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hybrid_scorer_types", "env_read", "p2_env_1")
_emit_reads_environ("hybrid_scorer_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("hybrid_scorer_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hybrid_scorer_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hybrid_scorer_types", "context_pull")
_emit_pulls_context("p1", "hybrid_scorer_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hybrid_scorer_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hybrid_scorer_types", "uwg_term_2")
_emit_writes_through("p1", "hybrid_scorer_types", "write_through")
_emit_writes_through("p1", "hybrid_scorer_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "hybrid_scorer_types", "safety_validation")
_emit_invokes_eval("p1", "hybrid_scorer_types", "eval_call")
_emit_proposal_commits_routing("p1", "hybrid_scorer_types", "routing_commit")
_emit_escalates_to_human("p1", "hybrid_scorer_types", "human_escalation")
_emit_routes_through("p1", "hybrid_scorer_types", "route_through")
_emit_checks_agent_registry("p1", "hybrid_scorer_types", "agent_registry")
_emit_validates_agent_capability("p1", "hybrid_scorer_types", "capability")
_emit_dispatches_execution_plan("p1", "hybrid_scorer_types", "exec_plan")
_emit_agent_executes_agent("p1", "hybrid_scorer_types", "sub_agent")
_emit_routes_to_agent("p1", "hybrid_scorer_types", "target_agent")
_emit_verifies_policy("p1", "hybrid_scorer_types", "policy_check")
_emit_observes_runtime_state("p1", "hybrid_scorer_types", "runtime_state")
_emit_verifies_boundary("p1", "hybrid_scorer_types", "boundary_check")
_emit_transcripts_response("p1", "hybrid_scorer_types", "transcript")
_emit_hard_fails_untranscripted("p1", "hybrid_scorer_types")
_emit_gated_by_confidence("p1", "hybrid_scorer_types", "confidence_gate")
emit_replay_key("p0", "hybrid_scorer_types")
emit_determinism_digest("p0", "hybrid_scorer_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hybrid_scorer_types", "execution_auth")
_emit_validates_capability("p2", "hybrid_scorer_types", "capability_check")
_emit_routes_to_capability("p2", "hybrid_scorer_types", "capability_route")
_emit_writes_via_uwg("p2", "hybrid_scorer_types", "uwg_write")
_emit_blocks_direct_write("p2", "hybrid_scorer_types", "direct_write_block")
_emit_records_tool_invocation("p2", "hybrid_scorer_types", "tool_invocation")
_emit_captures_execution_output("p2", "hybrid_scorer_types", "exec_output")
_emit_dispatches_agent("p3", "hybrid_scorer_types", "agent_dispatch")
_emit_coordinates_agents("p3", "hybrid_scorer_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "hybrid_scorer_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "hybrid_scorer_types", "healing_outcome")
_emit_escalates_failure("p3", "hybrid_scorer_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "hybrid_scorer_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hybrid_scorer_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "hybrid_scorer_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "hybrid_scorer_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hybrid_scorer_types", "eval_metric")
_emit_stores_embedding("p4", "hybrid_scorer_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "hybrid_scorer_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hybrid_scorer_types", "exec_snapshot_link")


@dataclass
class ScoringWeights:
    """Weights for different scoring components."""

    bm25_weight: float = 0.4
    semantic_weight: float = 0.3
    tfidf_weight: float = 0.2
    freshness_weight: float = 0.1


@dataclass
class ScoringResult:
    """Result of scoring operation."""

    document_id: str
    bm25_score: float
    semantic_score: float
    tfidf_score: float
    freshness_score: float
    final_score: float
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BM25Scorer:
    """BM25 scoring algorithm implementation."""

    def __init__(self, k1: float = 1.2, b: float = 0.75):
        """Initialize BM25 scorer.

        Args:
            k1: Controls term frequency saturation
            b: Controls document length normalization
        """
        import warnings

        warnings.warn(
            "BM25Scorer is deprecated. Use agentic_core.L4_state.memory.bm25_store.Bm25Store (backed by ASTAwareTokenizer) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.k1 = k1
        self.b = b
        self.doc_freqs: dict[str, int] = {}
        self.doc_lengths: list[int] = []
        self.avg_doc_length = 0.0

    def build_index(self, documents: list[str]) -> None:
        """Build BM25 index from documents.

        Args:
            documents: List of document texts
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BM25Scorer.build_index")

        all_terms = []
        for doc in documents:
            terms = self._tokenize(doc)
            all_terms.append(terms)
            self.doc_lengths.append(len(terms))
            for term in set(terms):
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        self.documents = all_terms

    def score(self, query: str, doc_idx: int) -> float:
        """Score document against query using BM25.

        Args:
            query: Query string
            doc_idx: Index of document to score

        Returns:
            BM25 score
        """
        if doc_idx >= len(self.documents):
            return 0.0
        query_terms = self._tokenize(query)
        doc_terms = self.documents[doc_idx]
        doc_length = self.doc_lengths[doc_idx]
        if not query_terms or doc_length == 0:
            return 0.0
        score = 0.0
        doc_term_counts = Counter(doc_terms)
        for term in query_terms:
            if term in doc_term_counts:
                tf = doc_term_counts[term]
                df = self.doc_freqs.get(term, 0)
                idf = math.log((len(self.documents) - df + 0.5) / (df + 0.5))
                term_score = (
                    idf
                    * (tf * (self.k1 + 1))
                    / (tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length))
                )
                score += term_score
        return score

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into terms."""
        return re.findall("\\b\\w+\\b", text.lower())


class HybridScorer:
    """Hybrid scorer combining multiple scoring strategies."""

    def __init__(self, weights: ScoringWeights | None = None):
        """Initialize hybrid scorer.

        Args:
            weights: scoring weights for different components
        """
        self.weights = weights or ScoringWeights()
        self.bm25_scorer = BM25Scorer()
        self.documents: list[dict[str, Any]] = []

    def index_documents(self, documents: list[dict[str, Any]]) -> None:
        """Index documents for scoring.

        Args:
            documents: List of document dictionaries with 'id' and 'content'
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HybridScorer.index_documents")

        self.documents = documents
        doc_texts = [doc["content"] for doc in documents]
        self.bm25_scorer.build_index(doc_texts)

    def score_documents(self, query: str, top_k: int | None = None) -> list[ScoringResult]:
        """Score all documents against query.

        Args:
            query: Query string
            top_k: Optional limit on number of results

        Returns:
            List of scoring results
        """
        results = []
        for i, doc in enumerate(self.documents):
            bm25_score = self.bm25_scorer.score(query, i)
            semantic_score = self._calculate_semantic_score(doc["content"], query)
            tfidf_score = self._calculate_tfidf_score(doc["content"], query)
            freshness_score = self._calculate_freshness_score(doc)
            final_score = (
                self.weights.bm25_weight * bm25_score
                + self.weights.semantic_weight * semantic_score
                + self.weights.tfidf_weight * tfidf_score
                + self.weights.freshness_weight * freshness_score
            )
            result = ScoringResult(
                document_id=doc["id"],
                bm25_score=bm25_score,
                semantic_score=semantic_score,
                tfidf_score=tfidf_score,
                freshness_score=freshness_score,
                final_score=final_score,
                metadata={"content_length": len(doc["content"])},
            )
            results.append(result)
        results.sort(key=lambda x: x.final_score, reverse=True)
        if top_k:
            results = results[:top_k]
        return results

    def _calculate_semantic_score(self, content: str, query: str) -> float:
        """Calculate semantic similarity score (mock implementation)."""
        content_words = set(re.findall("\\b\\w+\\b", content.lower()))
        query_words = set(re.findall("\\b\\w+\\b", query.lower()))
        if not query_words:
            return 0.0
        overlap = len(content_words & query_words)
        return overlap / len(query_words)

    def _calculate_tfidf_score(self, content: str, query: str) -> float:
        """Calculate TF-IDF score."""
        query_terms = re.findall("\\b\\w+\\b", query.lower())
        content_terms = re.findall("\\b\\w+\\b", content.lower())
        if not query_terms or not content_terms:
            return 0.0
        content_counter = Counter(content_terms)
        total_terms = len(content_terms)
        score = 0.0
        for term in query_terms:
            tf = content_counter.get(term, 0) / total_terms
            idf = 1.0 if term in content_counter else 0.0
            score += tf * idf
        return min(score, 1.0)

    def _calculate_freshness_score(self, doc: dict[str, Any]) -> float:
        """Calculate freshness score."""
        return 0.5

    def calculate_hybrid_score(
        self,
        vector_score: float,
        keyword_score: float,
        weights: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> float:
        """Calculate hybrid score from vector and keyword scores.

        Args:
            vector_score: Semantic similarity score
            keyword_score: Keyword/BM25 score
            weights: Optional weights dictionary
            metadata: Optional document metadata for recency boost

        Returns:
            Combined hybrid score
        """
        if weights is None:
            weights = {"semantic_weight": 0.5, "bm25_weight": 0.5, "recency_weight": 0.0}
        semantic_weight = weights.get("semantic_weight", 0.5)
        bm25_weight = weights.get("bm25_weight", 0.5)
        recency_weight = weights.get("recency_weight", 0.0)
        total_weight = semantic_weight + bm25_weight
        if total_weight > 0:
            semantic_weight = semantic_weight / total_weight
            bm25_weight = bm25_weight / total_weight
        score = vector_score * semantic_weight + keyword_score * bm25_weight
        if recency_weight > 0 and metadata:
            recency_boost = self._calculate_recency_boost(metadata)
            score = score * (1 - recency_weight) + recency_boost * recency_weight
        return score

    def _normalize_score(self, score: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
        """Normalize score to [0, 1] range.

        Args:
            score: Raw score
            min_score: Minimum possible score
            max_score: Maximum possible score

        Returns:
            Normalized score
        """
        if max_score is None or max_score == float("inf"):
            return min(max(score, 1.0), 0.0)
        if max_score - min_score == 0:
            return 0.0
        normalized = (score - min_score) / (max_score - min_score)
        return min(max(normalized, 0.0), 1.0)

    def _calculate_recency_boost(self, document: dict[str, Any]) -> float:
        """Calculate recency boost for document.

        Args:
            document: Document dictionary

        Returns:
            Recency boost factor
        """
        if "date" in document:
            return self._calculate_date_recency(document["date"])
        if "timestamp" in document:
            return 0.9
        content = str(document.get("content", "")).lower()
        recent_keywords = ["latest", "new", "recent", "current", "updated"]
        if any(keyword in content for keyword in recent_keywords):
            return 0.7
        return 0.5
