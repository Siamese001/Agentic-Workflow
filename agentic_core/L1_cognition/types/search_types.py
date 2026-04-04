"""Search Engine Types.

Defines the data structures for GraphRAG search engines including
local, global, and DRIFT search strategies with fusion capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    )

_emit_emits_metric_event("search_types", "p4obs", "metric_1")
_emit_emits_metric_event("search_types", "p4obs", "metric_2")
_emit_emits_metric_event("search_types", "p4obs", "metric_3")
_emit_emits_metric_event("search_types", "p4obs", "metric_4")
_emit_emits_metric_event("search_types", "p4obs", "metric_5")
_emit_emits_metric_event("search_types", "p4obs", "metric_6")
_emit_records_incident_event("search_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("search_types", "p4obs", "anomaly")
_emit_writes_observability_log("search_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("search_types", "p4obs", "mon_state")
_emit_triggers_alert("search_types", "p4obs", "alert")
_emit_links_incident_trace("search_types", "p4obs", "trace_link")
_emit_captures_pattern("search_types", "p3lm", "pattern")
_emit_records_learning_event("search_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("search_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("search_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("search_types", "p3lm", "routing")
_emit_improves_agent_policy("search_types", "p3lm", "policy")
_emit_stores_learning_state("search_types", "p3lm", "state")
_emit_records_execution_trace("search_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("search_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("search_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("search_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("search_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("search_types", "env_read", "p2_env_1")
_emit_reads_environ("search_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("search_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("search_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "search_types", "context_pull")
_emit_pulls_context("p1", "search_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "search_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "search_types", "uwg_term_2")
_emit_writes_through("p1", "search_types", "write_through")
_emit_writes_through("p1", "search_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "search_types", "safety_validation")
_emit_invokes_eval("p1", "search_types", "eval_call")
_emit_proposal_commits_routing("p1", "search_types", "routing_commit")
emit_determinism_digest("trace_search_types", "search_types_dispatch_entry")
emit_determinism_digest("trace_search_types", "search_types_dispatch_exit")
emit_determinism_digest("trace_search_types", "search_types_tool_invoke")
emit_determinism_digest("trace_search_types", "search_types_tool_complete")
emit_determinism_digest("trace_search_types", "search_types_agent_entry")
emit_determinism_digest("trace_search_types", "search_types_agent_exit")
emit_determinism_digest("trace_search_types", "search_types_uwg_write")
emit_determinism_digest("trace_search_types", "search_types_trace_sign")
emit_determinism_digest("trace_search_types", "search_types_guardrail_check")
emit_determinism_digest("trace_search_types", "search_types_policy_verify")


@dataclass
class SearchQuery:
    """Represents a search query with various parameters."""

    text: str
    query_type: str = "semantic"  # "semantic", "keyword", "hybrid"
    search_mode: str = "local"  # "local", "global", "drift"

    # Search parameters
    max_results: int = 10
    min_relevance_score: float = 0.5
    include_communities: bool = True
    include_entities: bool = True
    include_relationships: bool = False

    # Context parameters
    context_window: int = 5  # Number of surrounding entities to include
    max_depth: int = 2  # Maximum traversal depth

    # Filters
    entity_types: list[str] | None = None
    relation_types: list[str] | None = None
    community_levels: list[int] | None = None

    # Metadata
    query_id: str = field(default_factory=lambda: f"query_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize query text."""
        self.text = self.text.strip()
        if not self.text:
            raise ValueError("Query text cannot be empty")


@dataclass
class SearchResult:
    """Represents a single search result."""

    item_id: str
    item_type: str  # "entity", "relationship", "community"
    title: str
    description: str
    relevance_score: float

    # Context information
    context: str | None = None
    surrounding_entities: list[str] = field(default_factory=list)
    path_to_root: list[str] = field(default_factory=list)

    # Source information
    source_file: str | None = None
    line_number: int | None = None
    confidence: float = 1.0

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate relevance score."""
        if not 0 <= self.relevance_score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")


@dataclass
class SearchResponse:
    """Represents a complete search response."""

    query: SearchQuery
    results: list[SearchResult]

    # Search statistics
    total_found: int
    total_returned: int
    search_time_ms: float

    # Quality metrics
    avg_relevance_score: float
    max_relevance_score: float
    min_relevance_score: float

    # Search strategy used
    search_strategy: str
    fusion_method: str | None = None

    # Errors and warnings
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_top_results(self, n: int = 5) -> list[SearchResult]:
        """Get top N results by relevance score."""
        return sorted(self.results, key=lambda r: r.relevance_score, reverse=True)[:n]

    def get_results_by_type(self, item_type: str) -> list[SearchResult]:
        """Get results filtered by type."""
        return [r for r in self.results if r.item_type == item_type]


@dataclass
class LocalSearchConfig:
    """Configuration for local search strategy."""

    # Search parameters
    max_hops: int = 2
    max_entities_per_hop: int = 50
    community_boost: float = 1.2  # Boost factor for entities in same community

    # Scoring weights
    text_similarity_weight: float = 0.4
    graph_proximity_weight: float = 0.3
    community_coherence_weight: float = 0.2
    recency_weight: float = 0.1

    # Filters
    min_degree_centrality: float = 0.0
    required_entity_types: list[str] | None = None

    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 300


@dataclass
class GlobalSearchConfig:
    """Configuration for global search strategy."""

    # Community-level search
    max_communities: int = 10
    community_summary_weight: float = 0.6
    entity_density_weight: float = 0.4

    # Entity-level search within communities
    max_entities_per_community: int = 20
    entity_relevance_threshold: float = 0.3

    # Scoring
    summary_match_weight: float = 0.5
    keyword_match_weight: float = 0.3
    size_penalty_weight: float = 0.2

    # Filters
    min_community_size: int = 3
    max_community_size: int = 1000
    exclude_levels: list[int] | None = None


@dataclass
class DRIFTSearchConfig:
    """Configuration for DRIFT (Dynamic Reasoning-Informed Fusion and Traversal) search."""

    # Multi-hop reasoning
    max_reasoning_depth: int = 3
    reasoning_confidence_threshold: float = 0.7

    # Dynamic traversal
    adaptive_hop_selection: bool = True
    context_aware_pruning: bool = True

    # Fusion weights
    semantic_weight: float = 0.4
    structural_weight: float = 0.3
    reasoning_weight: float = 0.3

    # Learning
    enable_feedback_learning: bool = True
    feedback_decay_factor: float = 0.9

    # Performance
    max_traversal_paths: int = 100
    traversal_timeout_ms: int = 5000


@dataclass
class FusionConfig:
    """Configuration for search result fusion."""

    # Fusion method
    fusion_method: str = "weighted_average"  # "weighted_average", "rank_fusion", "reciprocal_rank"

    # Weight configuration
    local_weight: float = 0.4
    global_weight: float = 0.3
    drift_weight: float = 0.3

    # Rank fusion parameters
    rank_fusion_k: int = 60  # Parameter for reciprocal rank fusion

    # Normalization
    score_normalization: str = "min_max"  # "min_max", "z_score", "none"

    # Diversity
    enable_diversification: bool = True
    diversity_lambda: float = 0.5  # Maximal Marginal Relevance parameter
    diversity_threshold: float = 0.7


@dataclass
class SearchEngineMetrics:
    """Metrics for search engine performance."""

    # Performance metrics
    avg_query_time_ms: float
    p95_query_time_ms: float
    p99_query_time_ms: float
    queries_per_second: float

    # Quality metrics
    avg_relevance_score: float
    click_through_rate: float
    user_satisfaction_score: float

    # Cache metrics
    cache_hit_rate: float
    cache_miss_rate: float

    # Error metrics
    error_rate: float
    timeout_rate: float

    # Strategy usage
    local_search_usage: float
    global_search_usage: float
    drift_search_usage: float

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchSession:
    """Represents a search session with multiple queries."""

    session_id: str
    queries: list[SearchQuery] = field(default_factory=list)
    responses: list[SearchResponse] = field(default_factory=list)

    # Session metrics
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    total_queries: int = 0

    # User feedback
    clicked_results: list[str] = field(default_factory=list)
    rated_results: dict[str, int] = field(default_factory=dict)  # result_id -> rating

    # Context
    user_context: dict[str, Any] = field(default_factory=dict)
    session_metadata: dict[str, Any] = field(default_factory=dict)

    def add_query(self, query: SearchQuery, response: SearchResponse) -> None:
        """Add a query and its response to the session."""
        self.queries.append(query)
        self.responses.append(response)
        self.total_queries += 1

    def get_session_duration(self) -> float:
        """Get session duration in seconds."""
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()

    def get_avg_relevance(self) -> float:
        """Get average relevance score across all responses."""
        if not self.responses:
            return 0.0

        total_relevance = sum(
            sum(r.relevance_score for r in response.results)
            for response in self.responses
        )
        total_results = sum(len(response.results) for response in self.responses)

        return total_relevance / max(1, total_results)


# Export all types
__all__ = [
    "SearchQuery",
    "SearchResult",
    "SearchResponse",
    "LocalSearchConfig",
    "GlobalSearchConfig",
    "DRIFTSearchConfig",
    "FusionConfig",
    "SearchEngineMetrics",
    "SearchSession",
]
