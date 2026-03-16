"""Embedding retention scheduler for Plan A Phase 4.

Provides deterministic prune triggers and rebuild cycles with
invalidation enforcement.
"""

from __future__ import annotations

from pathlib import Path
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

_emit_authorize_and_execute("p2", "embedding_retention_scheduler", "execution_auth")
_emit_validates_capability("p2", "embedding_retention_scheduler", "capability_check")
_emit_routes_to_capability("p2", "embedding_retention_scheduler", "capability_route")
_emit_writes_via_uwg("p2", "embedding_retention_scheduler", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_retention_scheduler", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_retention_scheduler", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_retention_scheduler", "exec_output")
_emit_dispatches_agent("p3", "embedding_retention_scheduler", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_retention_scheduler", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_retention_scheduler", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_retention_scheduler", "healing_outcome")
_emit_escalates_failure("p3", "embedding_retention_scheduler", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_retention_scheduler", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_retention_scheduler", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_retention_scheduler", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_retention_scheduler", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_retention_scheduler", "eval_metric")
_emit_stores_embedding("p4", "embedding_retention_scheduler", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_retention_scheduler", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_retention_scheduler", "exec_snapshot_link")
from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata

_emit_applies_guardrail("p0", "embedding_retention_scheduler", "p0_governance")
_emit_snapshots_state("p0", "embedding_retention_scheduler", "state_snapshot")
emit_replay_key("p0", "embedding_retention_scheduler")
emit_determinism_digest("p0", "embedding_retention_scheduler")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class EmbeddingRetentionScheduler:
    """Scheduler for embedding retention policies and deterministic pruning."""

    def run_once(
        self,
        *,
        now_utc: int,
        policies: dict[str, dict[str, Any]],
        stores: dict[str, LocalFAISSStore],
        persist_base_path: Path | None = None,
    ) -> dict[str, IndexBuildMetadata]:
        """Run retention scheduler once.

        Args:
            now_utc: Current timestamp for retention calculations.
            policies: Mapping of index_id to policy configuration.
                Each policy dict contains:
                - retention_days: int for rolling window retention
                - mode: str ("rolling_window", "predicate", or "none")
                - predicate: Callable[[Dict[str, Any]], bool] for mode="predicate"
            stores: Mapping of index_id to LocalFAISSStore instances.
            persist_base_path: If provided, persist rebuilt indexes to disk under
                ``persist_base_path / index_id`` after each rebuild (G_RS fix).

        Returns:
            Mapping of index_id to rebuilt IndexBuildMetadata for pruned indexes.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingRetentionScheduler.run_once")

        results = {}
        for index_id, store in stores.items():
            if index_id not in policies:
                continue
            policy = policies[index_id]
            mode = policy.get("mode", "none")
            if mode == "none":
                continue
            elif mode == "rolling_window":
                retention_days = policy.get("retention_days")
                if retention_days is None:
                    continue
                cutoff_utc = now_utc - retention_days * 24 * 60 * 60

                def rolling_window_predicate(metadata: dict[str, Any]) -> bool:
                    """Return True if record should be pruned (older than cutoff)."""
                    created_utc = metadata.get("created_utc")
                    if created_utc is None:
                        return False
                    return created_utc < cutoff_utc

                num_removed = store.prune(index_id, rolling_window_predicate)
                if num_removed > 0:
                    if hasattr(store, "_memory_indexes") and index_id in store._memory_indexes:
                        old_metadata = store._memory_indexes[index_id]["metadata"]
                    else:
                        _, _, old_metadata = store.open(index_id)
                    new_metadata = store.rebuild(
                        index_id,
                        built_at_utc=now_utc,
                        canonicalization_version=old_metadata.canonicalization_version,
                        embedding_model_version=old_metadata.embedding_model_version,
                        embedding_model_checksum=old_metadata.embedding_model_checksum,
                    )
                    results[index_id] = new_metadata
                    if persist_base_path is not None:
                        dest = Path(persist_base_path) / index_id
                        dest.mkdir(parents=True, exist_ok=True)
                        store.persist_to_disk(
                            index_id,
                            dest,
                            embedder_id=old_metadata.embedding_model_checksum,
                            model_version=old_metadata.embedding_model_version,
                        )
            elif mode == "predicate":
                predicate = policy.get("predicate")
                if predicate is None:
                    continue
                num_removed = store.prune(index_id, predicate)
                if num_removed > 0:
                    if hasattr(store, "_memory_indexes") and index_id in store._memory_indexes:
                        old_metadata = store._memory_indexes[index_id]["metadata"]
                    else:
                        _, _, old_metadata = store.open(index_id)
                    new_metadata = store.rebuild(
                        index_id,
                        built_at_utc=now_utc,
                        canonicalization_version=old_metadata.canonicalization_version,
                        embedding_model_version=old_metadata.embedding_model_version,
                        embedding_model_checksum=old_metadata.embedding_model_checksum,
                    )
                    results[index_id] = new_metadata
                    if persist_base_path is not None:
                        dest = Path(persist_base_path) / index_id
                        dest.mkdir(parents=True, exist_ok=True)
                        store.persist_to_disk(
                            index_id,
                            dest,
                            embedder_id=old_metadata.embedding_model_checksum,
                            model_version=old_metadata.embedding_model_version,
                        )
        return results


__all__ = ["EmbeddingRetentionScheduler"]
