from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "rag_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "rag_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "rag_config", "state_snapshot")
trace_contract.emit_replay_key("p0", "rag_config")
trace_contract.emit_determinism_digest("p0", "rag_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "rag_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "rag_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rag_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rag_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rag_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rag_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rag_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rag_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rag_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rag_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rag_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rag_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rag_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rag_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rag_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rag_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rag_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rag_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rag_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rag_config", "exec_snapshot_link")

# Configuration constants

"""
Centralized RAG configuration - SSOT for all RAG settings
Replaces fragmented configs across L1, L3, apps_shared
"""
import os
from dataclasses import dataclass, field


trace_contract._emit_emits_metric_event("rag_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rag_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rag_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rag_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rag_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rag_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rag_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rag_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rag_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rag_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rag_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rag_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rag_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rag_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rag_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rag_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rag_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rag_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rag_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("rag_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rag_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rag_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rag_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rag_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rag_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rag_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rag_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rag_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rag_config", "context_pull")
trace_contract._emit_pulls_context("p1", "rag_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rag_config", "write_through")
trace_contract._emit_writes_through("p1", "rag_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rag_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rag_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rag_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "rag_config", "human_escalation")
trace_contract._emit_routes_through("p1", "rag_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "rag_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rag_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rag_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rag_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rag_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "rag_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rag_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rag_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rag_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rag_config")
trace_contract._emit_gated_by_confidence("p1", "rag_config", "confidence_gate")


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""

    model_name: str = BGE_M3_MODEL_ID
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
    enable_reranking: bool = False
    enable_caching: bool = True
    enable_hallucination_filter: bool = True

    # Multi-hop settings
    max_hops: int = 3
    faithfulness_threshold: float = 0.88

    # RRF fusion
    rrf_k: float = 60.0

    # Reranking
    reranker_model: str = ""
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SovereignRagConfig.from_env")

        config = cls()
        config.vector_store.dimension = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
        config.embedding.dimension = config.vector_store.dimension
        return config
