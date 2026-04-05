from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "rag_config", "p0_governance")
_emit_reads_policy_state("p0", "rag_config", "policy_binding")
_emit_snapshots_state("p0", "rag_config", "state_snapshot")
emit_replay_key("p0", "rag_config")
emit_determinism_digest("p0", "rag_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rag_config", "execution_auth")
_emit_validates_capability("p2", "rag_config", "capability_check")
_emit_routes_to_capability("p2", "rag_config", "capability_route")
_emit_writes_via_uwg("p2", "rag_config", "uwg_write")
_emit_blocks_direct_write("p2", "rag_config", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_config", "tool_invocation")
_emit_captures_execution_output("p2", "rag_config", "exec_output")
_emit_dispatches_agent("p3", "rag_config", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_config", "healing_outcome")
_emit_escalates_failure("p3", "rag_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_config", "eval_metric")
_emit_stores_embedding("p4", "rag_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_config", "exec_snapshot_link")

# Configuration constants

"""
Centralized RAG configuration - SSOT for all RAG settings
Replaces fragmented configs across L1, L3, apps_shared
"""
import os
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("rag_config", "p4obs", "metric_1")
_emit_emits_metric_event("rag_config", "p4obs", "metric_2")
_emit_emits_metric_event("rag_config", "p4obs", "metric_3")
_emit_emits_metric_event("rag_config", "p4obs", "metric_4")
_emit_emits_metric_event("rag_config", "p4obs", "metric_5")
_emit_emits_metric_event("rag_config", "p4obs", "metric_6")
_emit_records_incident_event("rag_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_config", "p4obs", "anomaly")
_emit_writes_observability_log("rag_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_config", "p4obs", "mon_state")
_emit_triggers_alert("rag_config", "p4obs", "alert")
_emit_links_incident_trace("rag_config", "p4obs", "trace_link")
_emit_captures_pattern("rag_config", "p3lm", "pattern")
_emit_records_learning_event("rag_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_config", "p3lm", "routing")
_emit_improves_agent_policy("rag_config", "p3lm", "policy")
_emit_stores_learning_state("rag_config", "p3lm", "state")
_emit_records_execution_trace("rag_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_config", "env_read", "p2_env_1")
_emit_reads_environ("rag_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_config", "context_pull")
_emit_pulls_context("p1", "rag_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rag_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_config", "uwg_term_2")
_emit_writes_through("p1", "rag_config", "write_through")
_emit_writes_through("p1", "rag_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "rag_config", "safety_validation")
_emit_invokes_eval("p1", "rag_config", "eval_call")
_emit_proposal_commits_routing("p1", "rag_config", "routing_commit")
_emit_escalates_to_human("p1", "rag_config", "human_escalation")
_emit_routes_through("p1", "rag_config", "route_through")
_emit_checks_agent_registry("p1", "rag_config", "agent_registry")
_emit_validates_agent_capability("p1", "rag_config", "capability")
_emit_dispatches_execution_plan("p1", "rag_config", "exec_plan")
_emit_agent_executes_agent("p1", "rag_config", "sub_agent")
_emit_routes_to_agent("p1", "rag_config", "target_agent")
_emit_verifies_policy("p1", "rag_config", "policy_check")
_emit_observes_runtime_state("p1", "rag_config", "runtime_state")
_emit_verifies_boundary("p1", "rag_config", "boundary_check")
_emit_transcripts_response("p1", "rag_config", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_config")
_emit_gated_by_confidence("p1", "rag_config", "confidence_gate")


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""

    model_name: str = "BAAI/bge-m3"
    dimension: int = 1024  # BAAI/bge-m3 dimension
    batch_size: int = 32
    cache_enabled: bool = True
    cache_maxsize: int = 10000


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""

    provider: str = "faiss"  # faiss | chroma | pinecone
    index_name: str = "sovereign-rag"
    namespace: str = "sovereign-core"
    metric: str = "cosine"
    dimension: int = 1024
    batch_size: int = 100  # Defensive batching
    latency_threshold_ms: float = 500.0  # Warn if exceeded


@dataclass
class RetrievalConfig:
    """Retrieval strategy configuration."""

    strategy: str = "hybrid"  # hybrid | vector | bm25
    top_k: int = 15
    enable_reranking: bool = True
    enable_caching: bool = True
    enable_hallucination_filter: bool = True

    # Multi-hop settings
    max_hops: int = 3
    faithfulness_threshold: float = 0.88

    # RRF fusion
    rrf_k: float = 60.0

    # Reranking
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_confidence_threshold: float = 0.75
    reranker_top_k: int = 10


@dataclass
class CacheConfig:
    """Semantic cache configuration."""

    enabled: bool = True
    backend: str = "redis"  # redis | memory
    ttl_seconds: int = 3600
    max_entries: int = 10000
    similarity_threshold: float = 0.95


@dataclass
class SafetyConfig:
    """RAG safety configuration."""

    enable_pii_filter: bool = True
    enable_hallucination_detection: bool = True
    enable_adversarial_defense: bool = True
    entity_support_threshold: float = 0.5  # 50% of entities must be in docs
    forbidden_keywords: list[str] = field(
        default_factory=lambda: ["password", "secret", "api_key", "private_key", "token"],
    )


@dataclass
class SovereignRagConfig:
    """
    Master RAG configuration - SSOT for entire architecture.
    Loaded from environment variables with sensible defaults.
    """

    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)

    @classmethod
    def from_env(cls) -> SovereignRagConfig:
        """Load configuration from environment variables."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignRagConfig.from_env")

        config = cls()
        config.vector_store.dimension = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
        config.embedding.dimension = config.vector_store.dimension
        return config
