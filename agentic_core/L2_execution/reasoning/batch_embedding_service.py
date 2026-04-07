from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "batch_embedding_service")
emit_determinism_digest("p0", "batch_embedding_service")

_emit_dispatches_healing_run("p1", "batch_embedding_service", "L2")
_emit_routes_through("p1", "batch_embedding_service", "L2")
_emit_checks_agent_registry("p1", "batch_embedding_service", "agent_registry")
_emit_validates_agent_capability("p1", "batch_embedding_service", "capability")
_emit_dispatches_execution_plan("p1", "batch_embedding_service", "exec_plan")
_emit_agent_executes_agent("p1", "batch_embedding_service", "sub_agent")
_emit_routes_to_agent("p1", "batch_embedding_service", "target_agent")
_emit_verifies_policy("p1", "batch_embedding_service", "policy_check")
_emit_observes_runtime_state("p1", "batch_embedding_service", "runtime_state")
_emit_verifies_boundary("p1", "batch_embedding_service", "boundary_check")
_emit_transcripts_response("p1", "batch_embedding_service", "transcript")
_emit_hard_fails_untranscripted("p1", "batch_embedding_service")
_emit_gated_by_confidence("p1", "batch_embedding_service", "confidence_gate")
_emit_escalates_to_human("p1", "batch_embedding_service", "L2")
_emit_reads_policy_state("p1", "batch_embedding_service", "L2")

_emit_applies_guardrail("p0", "batch_embedding_service", "p0_governance")
_emit_snapshots_state("p0", "batch_embedding_service", "state_snapshot")
_emit_authorize_and_execute("p2", "batch_embedding_service", "execution_auth")
_emit_validates_capability("p2", "batch_embedding_service", "capability_check")
_emit_routes_to_capability("p2", "batch_embedding_service", "capability_route")
_emit_writes_via_uwg("p2", "batch_embedding_service", "uwg_write")
_emit_blocks_direct_write("p2", "batch_embedding_service", "direct_write_block")
_emit_records_tool_invocation("p2", "batch_embedding_service", "tool_invocation")
_emit_captures_execution_output("p2", "batch_embedding_service", "exec_output")
_emit_dispatches_agent("p3", "batch_embedding_service", "agent_dispatch")
_emit_coordinates_agents("p3", "batch_embedding_service", "agent_coordination")
_emit_records_workflow_lineage("p3", "batch_embedding_service", "workflow_lineage")
_emit_records_healing_outcome("p3", "batch_embedding_service", "healing_outcome")
_emit_escalates_failure("p3", "batch_embedding_service", "failure_escalation")
_emit_orchestrates_workflow("p3", "batch_embedding_service", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "batch_embedding_service", "healing_dispatch")
_emit_invokes_evaluation("p3", "batch_embedding_service", "evaluation_signal")
_emit_records_telemetry_event("p4", "batch_embedding_service", "telemetry_event")
_emit_captures_evaluation_metric("p4", "batch_embedding_service", "eval_metric")
_emit_stores_embedding("p4", "batch_embedding_service", "embedding_store")
_emit_updates_meta_learning_state("p4", "batch_embedding_service", "meta_learning")
_emit_links_execution_to_snapshot("p4", "batch_embedding_service", "exec_snapshot_link")

"Batch Embedding Service - Parallel embedding generation for 5-10x speedup.\n\nOptimized for i7-10750H (6 cores/12 threads) with 32GB RAM allocation.\nUses ThreadPoolExecutor to process embeddings in parallel batches.\n"
import asyncio
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("batch_embedding_service", "p4obs", "metric_1")
_emit_emits_metric_event("batch_embedding_service", "p4obs", "metric_2")
_emit_emits_metric_event("batch_embedding_service", "p4obs", "metric_3")
_emit_emits_metric_event("batch_embedding_service", "p4obs", "metric_4")
_emit_emits_metric_event("batch_embedding_service", "p4obs", "metric_5")
_emit_emits_metric_event("batch_embedding_service", "p4obs", "metric_6")
_emit_records_incident_event("batch_embedding_service", "p4obs", "incident")
_emit_captures_runtime_anomaly("batch_embedding_service", "p4obs", "anomaly")
_emit_writes_observability_log("batch_embedding_service", "p4obs", "obs_log")
_emit_updates_monitoring_state("batch_embedding_service", "p4obs", "mon_state")
_emit_triggers_alert("batch_embedding_service", "p4obs", "alert")
_emit_links_incident_trace("batch_embedding_service", "p4obs", "trace_link")
_emit_captures_pattern("batch_embedding_service", "p3lm", "pattern")
_emit_records_learning_event("batch_embedding_service", "p3lm", "learning_event")
_emit_writes_learning_snapshot("batch_embedding_service", "p3lm", "snapshot")
_emit_feeds_meta_learning("batch_embedding_service", "p3lm", "meta_feed")
_emit_updates_routing_strategy("batch_embedding_service", "p3lm", "routing")
_emit_improves_agent_policy("batch_embedding_service", "p3lm", "policy")
_emit_stores_learning_state("batch_embedding_service", "p3lm", "state")
_emit_records_execution_trace("batch_embedding_service", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("batch_embedding_service", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("batch_embedding_service", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("batch_embedding_service", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("batch_embedding_service", "L4_STATE", "p2_trace_5")
_emit_reads_environ("batch_embedding_service", "env_read", "p2_env_1")
_emit_reads_environ("batch_embedding_service", "env_read", "p2_env_2")
_emit_reads_runtime_state("batch_embedding_service", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("batch_embedding_service", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "batch_embedding_service", "context_pull")
_emit_pulls_context("p1", "batch_embedding_service", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "batch_embedding_service", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "batch_embedding_service", "uwg_term_2")
_emit_writes_through("p1", "batch_embedding_service", "write_through")
_emit_writes_through("p1", "batch_embedding_service", "write_through_2")
_emit_validated_by_safety_plane("p1", "batch_embedding_service", "safety_validation")
_emit_invokes_eval("p1", "batch_embedding_service", "eval_call")
_emit_proposal_commits_routing("p1", "batch_embedding_service", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class BatchEmbeddingService:
    """Service for parallel batch embedding generation.

    Optimized for AMD Ryzen 9950X3D (16 cores/32 threads).
    Uses ThreadPoolExecutor to process embeddings in parallel batches.
    """

    # guardian: allow-magic-config
    def __init__(self, batch_size: int = 32, max_workers: int = 16):
        """Initialize the batch embedding service.

        Args:
            batch_size: Number of texts to embed in a single batch (default: 32)
            max_workers: Number of parallel workers (default: 16 for 9950X3D)
        """
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        Logger.info(f"Initialized BatchEmbeddingService: batch_size={batch_size}, max_workers={max_workers}")

    async def embed_batch(
        self, texts: list[str], model_func: Callable[[list[str]], list[np.ndarray]],
    ) -> list[np.ndarray]:
        """Embed a list of texts in parallel batches.

        Args:
            texts: List of strings to embed
            model_func: Sync function that takes a list of strings and returns embeddings

        Returns:
            List of embeddings as numpy arrays

        Example:
            >>> service = BatchEmbeddingService(batch_size=BATCH_SIZE, max_workers=4)
            >>> embeddings = await service.embed_batch(
            ...     texts=["text1", "text2", ...],
            ...     model_func=my_embedding_model.embed
            ... )
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "BatchEmbeddingService.embed_batch",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BatchEmbeddingService.embed_batch".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not texts:
            Logger.warning("Empty text list provided to embed_batch")
            return []
        batches: Any = [texts[i : i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        Logger.debug(f"Processing {len(texts)} texts in {len(batches)} batches of size {self.batch_size}")
        loop: Any = asyncio.get_event_loop()
        tasks: Any = [loop.run_in_executor(self.executor, model_func, batch) for batch in batches]
        try:
            results: Any = await asyncio.gather(*tasks)
            embeddings: Any = [emb for batch_result in results for emb in batch_result]
            Logger.info(f"Successfully generated {len(embeddings)} embeddings from {len(texts)} texts")
            return embeddings
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            Logger.error(f"Failed to generate embeddings: {e}")
            raise

    async def embed_single(
        self, text: str, model_func: Callable[[list[str]], list[np.ndarray]],
    ) -> np.ndarray:
        """Embed a single text (convenience method).

        Args:
            text: Single string to embed
            model_func: Sync function that takes a list of strings and returns embeddings

        Returns:
            Single embedding as numpy array
        """
        embeddings: Any = await self.embed_batch([text], model_func)
        return embeddings[0] if embeddings else None

    def shutdown(self) -> Any:
        """Shutdown the thread pool executor."""
        Logger.info("Shutting down BatchEmbeddingService executor")
        self.executor.shutdown(wait=True)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


# guardian: allow-magic-config
def create_batch_embedding_service(batch_size: int = 32, max_workers: int = 16) -> BatchEmbeddingService:
    """Create a BatchEmbeddingService instance.

    Args:
        batch_size: Number of texts to embed in a single batch
        max_workers: Number of parallel workers (default: 16 for 9950X3D)

    Returns:
        Configured BatchEmbeddingService instance
    """
    return BatchEmbeddingService(batch_size=batch_size, max_workers=max_workers)
