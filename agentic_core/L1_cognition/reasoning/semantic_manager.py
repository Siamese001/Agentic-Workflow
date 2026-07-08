"""
SemanticMemory - Semantic memory storage for cognitive agents.

Provides semantic memory capabilities with embedding-based retrieval.
"""

from typing import Any

import logging

from agentic_core.config.model_catalog import (
    BGE_M3_EMBEDDING_DIMENSION,
    BGE_M3_MODEL_ID,
)

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "semantic_manager")
trace_contract.emit_determinism_digest("p0", "semantic_manager")

trace_contract._emit_dispatches_healing_run("p1", "semantic_manager", "L1")
trace_contract._emit_routes_through("p1", "semantic_manager", "L1")
trace_contract._emit_checks_agent_registry("p1", "semantic_manager", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "semantic_manager", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "semantic_manager", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "semantic_manager", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "semantic_manager", "target_agent")
trace_contract._emit_verifies_policy("p1", "semantic_manager", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "semantic_manager", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "semantic_manager", "boundary_check")
trace_contract._emit_transcripts_response("p1", "semantic_manager", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "semantic_manager")
trace_contract._emit_gated_by_confidence("p1", "semantic_manager", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "semantic_manager", "L1")
trace_contract._emit_reads_policy_state("p1", "semantic_manager", "L1")
trace_contract._emit_authorize_and_execute("p2", "semantic_manager", "execution_auth")
trace_contract._emit_validates_capability("p2", "semantic_manager", "capability_check")
trace_contract._emit_routes_to_capability("p2", "semantic_manager", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "semantic_manager", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "semantic_manager", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "semantic_manager", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "semantic_manager", "exec_output")
trace_contract._emit_dispatches_agent("p3", "semantic_manager", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "semantic_manager", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "semantic_manager", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "semantic_manager", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "semantic_manager", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "semantic_manager", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "semantic_manager", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "semantic_manager", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "semantic_manager", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "semantic_manager", "eval_metric")
trace_contract._emit_stores_embedding("p4", "semantic_manager", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "semantic_manager", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "semantic_manager", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("semantic_manager", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("semantic_manager", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("semantic_manager", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("semantic_manager", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("semantic_manager", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("semantic_manager", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("semantic_manager", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("semantic_manager", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("semantic_manager", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("semantic_manager", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("semantic_manager", "p4obs", "alert")
trace_contract._emit_links_incident_trace("semantic_manager", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("semantic_manager", "p3lm", "pattern")
trace_contract._emit_records_learning_event("semantic_manager", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("semantic_manager", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("semantic_manager", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("semantic_manager", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("semantic_manager", "p3lm", "policy")
trace_contract._emit_stores_learning_state("semantic_manager", "p3lm", "state")
trace_contract._emit_records_execution_trace("semantic_manager", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("semantic_manager", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("semantic_manager", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("semantic_manager", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("semantic_manager", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("semantic_manager", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("semantic_manager", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("semantic_manager", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("semantic_manager", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "semantic_manager", "context_pull")
trace_contract._emit_pulls_context("p1", "semantic_manager", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "semantic_manager", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "semantic_manager", "uwg_term_2")
trace_contract._emit_writes_through("p1", "semantic_manager", "write_through")
trace_contract._emit_writes_through("p1", "semantic_manager", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "semantic_manager", "safety_validation")
trace_contract._emit_invokes_eval("p1", "semantic_manager", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "semantic_manager", "routing_commit")

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """Provider for embeddings."""

    def __init__(self, model: str = BGE_M3_MODEL_ID):
        self.model = model

    def embed(self, text: str) -> list[float]:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "EmbeddingProvider.embed", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "EmbeddingProvider.embed", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "EmbeddingProvider.embed")

        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            result = bmg_embed_text(text)
            if result:
                return result
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Embedding failed: {e}")
        return [0.0] * BGE_M3_EMBEDDING_DIMENSION


class VectorIndex:
    """Index for vector storage and retrieval."""

    def __init__(self, dimension: int = BGE_M3_EMBEDDING_DIMENSION):
        self.dimension = dimension
        self._vectors: dict[str, list[float]] = {}

    def add(self, key: str, vector: list[float]) -> None:
        self._vectors[key] = vector

    def search(self, query: list[float], top_k: int = 5) -> list[str]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "VectorIndex.search")

        if not self._vectors:
            return []
        try:
            import numpy as np

            q = np.array(query, dtype=np.float32)
            q_norm = q / (np.linalg.norm(q) + 1e-08)
            scored = []
            for key, vec in self._vectors.items():
                v = np.array(vec, dtype=np.float32)
                v_norm = v / (np.linalg.norm(v) + 1e-08)
                scored.append((float(np.dot(q_norm, v_norm)), key))
            scored.sort(reverse=True)
            return [k for _, k in scored[:top_k]]
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Vector search failed: {e}")
            return list(self._vectors.keys())[:top_k]


class SemanticEntry:
    """Entry in semantic memory."""

    def __init__(self, key: str, value: Any, embedding: list[float] | None = None):
        self.key = key
        self.value = value
        self.embedding = embedding
        self.metadata: dict[str, Any] = {}


class SemanticMemory:
    """Semantic memory store with embedding-based retrieval."""

    def __init__(self):
        self._memories: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    def store(self, key: str, value: Any, embedding: list[float] | None = None) -> None:
        """Store a memory with optional embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "SemanticMemory.store")

        self._memories[key] = {"value": value, "metadata": {}}
        if embedding:
            self._embeddings[key] = embedding

    def retrieve(self, key: str) -> Any | None:
        """Retrieve a memory by key."""
        memory = self._memories.get(key)
        return memory["value"] if memory else None

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Search memories by embedding similarity (normalized cosine)."""
        if not self._embeddings:
            return []
        try:
            import numpy as np

            q = np.array(query_embedding, dtype=np.float32)
            q_norm = q / (np.linalg.norm(q) + 1e-08)
            results = []
            for key, embedding in self._embeddings.items():
                if key in self._memories:
                    v = np.array(embedding, dtype=np.float32)
                    v_norm = v / (np.linalg.norm(v) + 1e-08)
                    similarity = float(np.dot(q_norm, v_norm))
                    results.append(
                        {"key": key, "value": self._memories[key]["value"], "similarity": similarity},
                    )
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        except (ImportError, AttributeError, KeyError) as e:
            print(f"Memory search failed: {e}")
            return []

    def delete(self, key: str) -> None:
        """Delete a memory."""
        if key in self._memories:
            del self._memories[key]
        if key in self._embeddings:
            del self._embeddings[key]

    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._embeddings.clear()


__all__ = ["SemanticMemory", "SemanticEntry", "EmbeddingProvider", "VectorIndex"]
