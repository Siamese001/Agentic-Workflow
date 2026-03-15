"""Embedding retention scheduler for Plan A Phase 4.

Provides deterministic prune triggers and rebuild cycles with
invalidation enforcement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata


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
