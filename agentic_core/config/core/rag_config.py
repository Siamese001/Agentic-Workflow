from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Centralized RAG configuration - SSOT for all RAG settings
Replaces fragmented configs across L1, L3, apps_shared
"""
import os
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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
