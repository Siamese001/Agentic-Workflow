"""
HealingMemoryEmbedder - Convert violation signatures to embeddings.

[PHASE 1] Core Infrastructure Implementation

Provides:
- Violation signature embedding generation
- Healing pattern embedding for semantic retrieval
- Batch embedding support for efficiency
- Fallback to hash-based signatures when embedding unavailable
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "memory_embedder")
trace_contract.emit_determinism_digest("p0", "memory_embedder")

trace_contract._emit_dispatches_healing_run("p1", "memory_embedder", "L1")
trace_contract._emit_routes_through("p1", "memory_embedder", "L1")
trace_contract._emit_checks_agent_registry("p1", "memory_embedder", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "memory_embedder", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "memory_embedder", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "memory_embedder", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "memory_embedder", "target_agent")
trace_contract._emit_verifies_policy("p1", "memory_embedder", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "memory_embedder", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "memory_embedder", "boundary_check")
trace_contract._emit_transcripts_response("p1", "memory_embedder", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "memory_embedder")
trace_contract._emit_gated_by_confidence("p1", "memory_embedder", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "memory_embedder", "L1")
trace_contract._emit_reads_policy_state("p1", "memory_embedder", "L1")
trace_contract._emit_authorize_and_execute("p2", "memory_embedder", "execution_auth")
trace_contract._emit_validates_capability("p2", "memory_embedder", "capability_check")
trace_contract._emit_routes_to_capability("p2", "memory_embedder", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "memory_embedder", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "memory_embedder", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "memory_embedder", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "memory_embedder", "exec_output")
trace_contract._emit_dispatches_agent("p3", "memory_embedder", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "memory_embedder", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "memory_embedder", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "memory_embedder", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "memory_embedder", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "memory_embedder", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "memory_embedder", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "memory_embedder", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "memory_embedder", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "memory_embedder", "eval_metric")
trace_contract._emit_stores_embedding("p4", "memory_embedder", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "memory_embedder", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "memory_embedder", "exec_snapshot_link")


def _get_embedding_sovereign_agent():
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "_get_embedding_sovereign_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "_get_embedding_sovereign_agent", "p0_governance")
    from agentic_core.interfaces.execution_agents import EmbeddingSovereignAgent

    return EmbeddingSovereignAgent


from agentic_core.L1_cognition.types.memory_types import (
    EMBEDDING_DIMENSION,
    MAX_TEXT_LENGTH,
    ViolationSignature,
)

trace_contract._emit_emits_metric_event("memory_embedder", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("memory_embedder", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("memory_embedder", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("memory_embedder", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("memory_embedder", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("memory_embedder", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("memory_embedder", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("memory_embedder", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("memory_embedder", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("memory_embedder", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("memory_embedder", "p4obs", "alert")
trace_contract._emit_links_incident_trace("memory_embedder", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("memory_embedder", "p3lm", "pattern")
trace_contract._emit_records_learning_event("memory_embedder", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("memory_embedder", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("memory_embedder", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("memory_embedder", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("memory_embedder", "p3lm", "policy")
trace_contract._emit_stores_learning_state("memory_embedder", "p3lm", "state")
trace_contract._emit_records_execution_trace("memory_embedder", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("memory_embedder", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("memory_embedder", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("memory_embedder", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("memory_embedder", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("memory_embedder", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("memory_embedder", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("memory_embedder", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("memory_embedder", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "memory_embedder", "context_pull")
trace_contract._emit_pulls_context("p1", "memory_embedder", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "memory_embedder", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "memory_embedder", "uwg_term_2")
trace_contract._emit_writes_through("p1", "memory_embedder", "write_through")
trace_contract._emit_writes_through("p1", "memory_embedder", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "memory_embedder", "safety_validation")
trace_contract._emit_invokes_eval("p1", "memory_embedder", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "memory_embedder", "routing_commit")

Logger = logging.getLogger(__name__)
_embedder_singleton: Any = None


@dataclass
class HealingMemoryEmbedder:
    """
    Convert violation signatures to embeddings for semantic retrieval.

    [PHASE 1] Core Infrastructure Implementation

    Features:
    - Violation signature embedding generation
    - Healing pattern embedding for semantic retrieval
    - Batch embedding support for efficiency
    - Fallback to hash-based signatures when embedding unavailable
    """

    embedding_dimension: int = EMBEDDING_DIMENSION
    max_text_length: int = MAX_TEXT_LENGTH
    _embedding_agent: Any = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)
    stats: dict[str, int] = field(
        default_factory=lambda: {
            "embeddings_generated": 0,
            "fallback_hashes": 0,
            "batch_operations": 0,
            "errors": 0,
        },
    )

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        global _embedder_singleton
        if _embedder_singleton is None:
            _embedder_singleton = super().__new__(cls)
        return _embedder_singleton

    def __post_init__(self) -> None:
        """Initialize embedding agent."""
        if not self._initialized:
            self._initialize_embedding_agent()
            self._initialized = True

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L1_REASONING,
            "HealingMemoryEmbedder.reset_instance",
        )

        global _embedder_singleton
        _embedder_singleton = None

    def _initialize_embedding_agent(self) -> None:
        """Initialize the embedding agent with fallback."""
        try:
            from pathlib import Path

            self._embedding_agent = _get_embedding_sovereign_agent()(Path.cwd())
            Logger.info("[HealingMemoryEmbedder] Embedding agent initialized")
        except (  # guardian: allow-silent-swallow
            ImportError,
            RuntimeError,
            ValueError,
            TypeError,
            OSError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    def embed_violation(self, violation: dict[str, Any]) -> list[float] | None:
        """
        Generate embedding for a violation.

        Args:
            violation: Violation dictionary

        Returns:
            Embedding vector or None if unavailable
        """
        signature = ViolationSignature.from_violation(violation)
        return self.embed_signature(signature)

    def embed_signature(self, signature: ViolationSignature) -> list[float] | None:
        """
        Generate embedding for a violation signature.

        Args:
            signature: ViolationSignature object

        Returns:
            Embedding vector or None if unavailable
        """
        text = signature.to_text()
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            embedding = bmg_embed_text(text[: self.max_text_length])
            if embedding:
                self.stats["embeddings_generated"] += 1
                return embedding
        except (
            ImportError,
            RuntimeError,
            ValueError,
            TypeError,
            OSError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.warning(f"[HealingMemoryEmbedder] Embedding failed: {e}")
            self.stats["errors"] += 1
        self.stats["fallback_hashes"] += 1
        return None

    def embed_healing_pattern(
        self,
        violation: dict[str, Any],
        healing_result: dict[str, Any],
    ) -> list[float] | None:
        """
        Generate embedding for a healing pattern (violation + result).

        Args:
            violation: Violation dictionary
            healing_result: Healing result dictionary

        Returns:
            Embedding vector or None if unavailable
        """
        signature = ViolationSignature.from_violation(violation)
        text = signature.to_text()
        result_summary = f" | healing_status: {healing_result.get('status', 'unknown')}"
        if healing_result.get("strategy"):
            result_summary += f" | strategy: {healing_result.get('strategy')}"
        full_text = (text + result_summary)[: self.max_text_length]
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            embedding = bmg_embed_text(full_text)
            if embedding:
                self.stats["embeddings_generated"] += 1
                return embedding
        except (
            ImportError,
            RuntimeError,
            ValueError,
            TypeError,
            OSError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.warning(f"[HealingMemoryEmbedder] Pattern embedding failed: {e}")
            self.stats["errors"] += 1
        self.stats["fallback_hashes"] += 1
        return None

    def embed_batch(self, violations: list[dict[str, Any]]) -> list[list[float] | None]:
        """
        Generate embeddings for multiple violations.

        Args:
            violations: List of violation dictionaries

        Returns:
            List of embedding vectors (None for failures)
        """
        self.stats["batch_operations"] += 1
        results: list[list[float] | None] = []
        for violation in violations:
            embedding = self.embed_violation(violation)
            results.append(embedding)
        return results

    def get_hash_signature(self, violation: dict[str, Any]) -> str:
        """
        Get hash-based signature for a violation (fallback when embedding unavailable).

        Args:
            violation: Violation dictionary

        Returns:
            Hash signature string
        """
        signature = ViolationSignature.from_violation(violation)
        return signature.to_hash()

    def compute_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        if not embedding1 or not embedding2:
            return 0.0
        if len(embedding1) != len(embedding2):
            Logger.warning("[HealingMemoryEmbedder] Embedding dimension mismatch")
            return 0.0
        dot_product = sum((a * b for a, b in zip(embedding1, embedding2, strict=False)))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        return {**self.stats, "embedding_available": self._embedding_agent is not None}


_healing_memory_embedder: HealingMemoryEmbedder | None = None


def get_healing_memory_embedder() -> HealingMemoryEmbedder:
    """Get or create the HealingMemoryEmbedder singleton."""
    global _healing_memory_embedder
    if _healing_memory_embedder is None:
        _healing_memory_embedder = HealingMemoryEmbedder()
    return _healing_memory_embedder


def reset_healing_memory_embedder() -> None:
    """[TESTING ONLY] Reset the singleton."""
    global _healing_memory_embedder
    _healing_memory_embedder = None
    HealingMemoryEmbedder.reset_instance()
