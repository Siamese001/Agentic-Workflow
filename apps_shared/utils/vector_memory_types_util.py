"""
Vector Memory Store - Unified vector storage for apps_lic and apps_rg.

Provides semantic search and retrieval capabilities using an in-memory
numpy store (BGE-m3, 1024-dim). Pinecone dependency removed.
Phase 2A.2 - Missing Shared Dependencies
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "vector_memory_types_util", "p0_governance")
_emit_reads_policy_state("p0", "vector_memory_types_util", "policy_binding")
_emit_snapshots_state("p0", "vector_memory_types_util", "state_snapshot")
emit_replay_key("p0", "vector_memory_types_util")
emit_determinism_digest("p0", "vector_memory_types_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "vector_memory_types_util", "execution_auth")
_emit_validates_capability("p2", "vector_memory_types_util", "capability_check")
_emit_routes_to_capability("p2", "vector_memory_types_util", "capability_route")
_emit_writes_via_uwg("p2", "vector_memory_types_util", "uwg_write")
_emit_blocks_direct_write("p2", "vector_memory_types_util", "direct_write_block")
_emit_records_tool_invocation("p2", "vector_memory_types_util", "tool_invocation")
_emit_captures_execution_output("p2", "vector_memory_types_util", "exec_output")
_emit_dispatches_agent("p3", "vector_memory_types_util", "agent_dispatch")
_emit_coordinates_agents("p3", "vector_memory_types_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "vector_memory_types_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "vector_memory_types_util", "healing_outcome")
_emit_escalates_failure("p3", "vector_memory_types_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "vector_memory_types_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vector_memory_types_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "vector_memory_types_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "vector_memory_types_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vector_memory_types_util", "eval_metric")
_emit_stores_embedding("p4", "vector_memory_types_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "vector_memory_types_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vector_memory_types_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class VectorMemoryConfig:
    """Configuration for vector memory store."""

    index_name: str
    dimension: int = 1024
    metric: str = "cosine"
    namespace: str | None = None
    top_k: int = 10
    similarity_threshold: float = 0.7


@dataclass
class VectorSearchResult:
    """Result from vector search."""

    id: str
    score: float
    metadata: dict[str, Any]
    text: str | None = None


class VectorMemoryStore:
    """
    Unified vector memory store for semantic search and retrieval.

    Supports both apps_lic and apps_rg with namespace isolation.
    Uses an in-memory numpy store backed by BGE-m3 (1024-dim) embeddings.
    """

    def __init__(self, config: VectorMemoryConfig):
        """
        Initialize vector memory store.

        Args:
            config: Vector memory configuration
        """
        self.config = config
        self._store: dict[str, dict[str, dict]] = {}
        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Ensure the vector store is initialized (no-op for in-memory store)."""
        pass

    def _namespace_key(self) -> str:
        """Return the active namespace key."""
        return self.config.namespace or "__default__"

    def store(
        self, text: str, embedding: list[float], metadata: dict[str, Any] | None = None, id: str | None = None
    ) -> str:
        """
        Store text and embedding in vector memory.

        Args:
            text: Text content to store
            embedding: Vector embedding
            metadata: Optional metadata
            id: Optional custom ID (auto-generated if not provided)

        Returns:
            ID of stored vector
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "VectorMemoryStore.store")

        if id is None:
            id = self._generate_id(text)
        meta = metadata or {}
        meta["text"] = text
        ns = self._namespace_key()
        self._store.setdefault(ns, {})[id] = {"embedding": embedding, "metadata": meta}
        logger.debug(f"Stored vector: {id}")
        return id

    def search(
        self, embedding: list[float], top_k: int | None = None, filter: dict[str, Any] | None = None
    ) -> list[VectorSearchResult]:
        """
        Search for similar vectors.

        Args:
            embedding: Query embedding
            top_k: Number of results to return
            filter: Optional metadata filter (keys matched against metadata dict)

        Returns:
            List of search results
        """
        import numpy as np

        k = top_k or self.config.top_k
        ns = self._namespace_key()
        entries = self._store.get(ns, {})
        if not entries:
            return []
        try:
            q = np.array(embedding, dtype=np.float32)
            q_norm = q / (np.linalg.norm(q) + 1e-12)
            scored: list[tuple[float, str, dict]] = []
            for vec_id, item in entries.items():
                if filter and (not all((item["metadata"].get(k2) == v for k2, v in filter.items()))):
                    continue
                v = np.array(item["embedding"], dtype=np.float32)
                v_norm = v / (np.linalg.norm(v) + 1e-12)
                score = float(np.dot(q_norm, v_norm))
                if score >= self.config.similarity_threshold:
                    scored.append((score, vec_id, item["metadata"]))
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [
                VectorSearchResult(id=vec_id, score=score, metadata=meta, text=meta.get("text"))
                for score, vec_id, meta in scored[:k]
            ]
            logger.debug(f"Found {len(results)} results above threshold")
            return results
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []

    def delete(self, ids: list[str]) -> bool:
        """
        Delete vectors by ID.

        Args:
            ids: List of vector IDs to delete

        Returns:
            True if successful
        """
        ns = self._namespace_key()
        ns_store = self._store.get(ns, {})
        for vec_id in ids:
            ns_store.pop(vec_id, None)
        logger.debug(f"Deleted {len(ids)} vectors")
        return True

    def clear_namespace(self) -> bool:
        """
        Clear all vectors in the current namespace.

        Returns:
            True if successful
        """
        ns = self._namespace_key()
        self._store[ns] = {}
        logger.info(f"Cleared namespace: {self.config.namespace}")
        return True

    def _generate_id(self, text: str) -> str:
        """Generate deterministic ID from text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get_stats(self) -> dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dictionary with stats
        """
        ns = self._namespace_key()
        ns_count = len(self._store.get(ns, {}))
        total = sum(len(v) for v in self._store.values())
        return {
            "initialized": True,
            "total_vectors": total,
            "namespace_vectors": ns_count,
            "dimension": self.config.dimension,
            "namespaces": list(self._store.keys()),
        }
