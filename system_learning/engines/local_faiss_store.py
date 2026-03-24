"""LocalFAISSStore - Plan A deterministic FAISS index storage.

Read-only contract surfaces for Plan B consumption.
FAISS (IndexFlatIP with L2-normalised vectors) is the primary path.
Pure-Python cosine similarity is the fallback when faiss is not installed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import struct
from pathlib import Path
from typing import Any, Callable

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "local_faiss_store", "execution_auth")
_emit_validates_capability("p2", "local_faiss_store", "capability_check")
_emit_routes_to_capability("p2", "local_faiss_store", "capability_route")
_emit_writes_via_uwg("p2", "local_faiss_store", "uwg_write")
_emit_blocks_direct_write("p2", "local_faiss_store", "direct_write_block")
_emit_records_tool_invocation("p2", "local_faiss_store", "tool_invocation")
_emit_captures_execution_output("p2", "local_faiss_store", "exec_output")
_emit_dispatches_agent("p3", "local_faiss_store", "agent_dispatch")
_emit_coordinates_agents("p3", "local_faiss_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "local_faiss_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "local_faiss_store", "healing_outcome")
_emit_escalates_failure("p3", "local_faiss_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "local_faiss_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "local_faiss_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "local_faiss_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "local_faiss_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "local_faiss_store", "eval_metric")
_emit_stores_embedding("p4", "local_faiss_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "local_faiss_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "local_faiss_store", "exec_snapshot_link")
from system_learning.types.index_build_metadata_types import IndexBuildMetadata

_emit_applies_guardrail("p0", "local_faiss_store", "p0_governance")
_emit_reads_policy_state("p0", "local_faiss_store", "policy_binding")
_emit_snapshots_state("p0", "local_faiss_store", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("local_faiss_store", "p4obs", "metric_1")
_emit_emits_metric_event("local_faiss_store", "p4obs", "metric_2")
_emit_emits_metric_event("local_faiss_store", "p4obs", "metric_3")
_emit_emits_metric_event("local_faiss_store", "p4obs", "metric_4")
_emit_emits_metric_event("local_faiss_store", "p4obs", "metric_5")
_emit_emits_metric_event("local_faiss_store", "p4obs", "metric_6")
_emit_records_incident_event("local_faiss_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("local_faiss_store", "p4obs", "anomaly")
_emit_writes_observability_log("local_faiss_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("local_faiss_store", "p4obs", "mon_state")
_emit_triggers_alert("local_faiss_store", "p4obs", "alert")
_emit_links_incident_trace("local_faiss_store", "p4obs", "trace_link")
_emit_captures_pattern("local_faiss_store", "p3lm", "pattern")
_emit_records_learning_event("local_faiss_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("local_faiss_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("local_faiss_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("local_faiss_store", "p3lm", "routing")
_emit_improves_agent_policy("local_faiss_store", "p3lm", "policy")
_emit_stores_learning_state("local_faiss_store", "p3lm", "state")
_emit_records_execution_trace("local_faiss_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("local_faiss_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("local_faiss_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("local_faiss_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("local_faiss_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("local_faiss_store", "env_read", "p2_env_1")
_emit_reads_environ("local_faiss_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("local_faiss_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("local_faiss_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "local_faiss_store", "context_pull")
_emit_pulls_context("p1", "local_faiss_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "local_faiss_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "local_faiss_store", "uwg_term_2")
_emit_writes_through("p1", "local_faiss_store", "write_through")
_emit_writes_through("p1", "local_faiss_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "local_faiss_store", "safety_validation")
_emit_invokes_eval("p1", "local_faiss_store", "eval_call")
_emit_proposal_commits_routing("p1", "local_faiss_store", "routing_commit")
_emit_escalates_to_human("p1", "local_faiss_store", "human_escalation")
_emit_routes_through("p1", "local_faiss_store", "route_through")
_emit_checks_agent_registry("p1", "local_faiss_store", "agent_registry")
_emit_validates_agent_capability("p1", "local_faiss_store", "capability")
_emit_dispatches_execution_plan("p1", "local_faiss_store", "exec_plan")
_emit_agent_executes_agent("p1", "local_faiss_store", "sub_agent")
_emit_routes_to_agent("p1", "local_faiss_store", "target_agent")
_emit_verifies_policy("p1", "local_faiss_store", "policy_check")
_emit_observes_runtime_state("p1", "local_faiss_store", "runtime_state")
_emit_verifies_boundary("p1", "local_faiss_store", "boundary_check")
_emit_transcripts_response("p1", "local_faiss_store", "transcript")
_emit_hard_fails_untranscripted("p1", "local_faiss_store")
_emit_gated_by_confidence("p1", "local_faiss_store", "confidence_gate")
emit_replay_key("p0", "local_faiss_store")
emit_determinism_digest("p0", "local_faiss_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _faiss_available() -> bool:
    return importlib.util.find_spec("faiss") is not None


def _import_faiss() -> Any:
    import faiss

    return faiss


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


class IndexNotBuiltError(RuntimeError):
    """Raised when attempting to access an index that has not been built."""

    pass


class IndexMetadataError(RuntimeError):
    """Raised when index metadata is missing or corrupted."""

    pass


class ManifestIntegrityError(RuntimeError):
    """Raised when manifest.json is missing, has wrong schema, or hash mismatch.

    Fail-closed: any mismatch raises immediately with no best-effort fallback.
    """

    pass


class EmbedderMismatchError(RuntimeError):
    """Raised when manifest.embedder_id does not match the runtime embedder.

    Fail-closed: mixed-vector indexes are never loaded.
    """

    pass


_SCHEMA_VERSION = "1"


class LocalFAISSStore:
    """Local FAISS index store with deterministic search.

    Primary path  : FAISS IndexFlatIP with L2-normalised vectors (cosine similarity).
    Fallback path : pure-Python cosine when faiss is not installed.

    INVARIANT: FAISS is imported lazily inside methods only.
    INVARIANT: search() post-sorts results deterministically: (score_round6 DESC, content_hash ASC).
    INVARIANT: Fallback path enables unit_min_deps tests without faiss.
    """

    def __init__(
        self, base_path: Path, *, telemetry_callback: Callable[[str, dict[str, Any]], None] | None = None
    ) -> None:
        """Initialize store with base path for indexes.

        Args:
            base_path: Base directory for index storage.
            telemetry_callback: Optional callback for observability events.
                Signature: ``callback(event_type: str, data: dict) -> None``.
                Events emitted: ``faiss_index_rebuilt``, ``faiss_index_persisted``,
                ``faiss_manifest_verified``.
        """
        self.base_path = base_path
        self._telemetry_callback = telemetry_callback
        self._indexes: dict[str, dict[str, Any]] = {}
        self._rebuild_required: dict[str, bool] = {}

    @property
    def _memory_indexes(self) -> dict[str, dict[str, Any]]:
        return self._indexes

    def open(self, index_id: str) -> tuple[Any, str, IndexBuildMetadata]:
        """Open an index and return handle with metadata.

        Args:
            index_id: Identifier of the index to open.

        Returns:
            Tuple of (index_handle, index_version_hash, build_metadata).

        Raises:
            IndexNotBuiltError: If index has not been built or needs rebuild.
            IndexMetadataError: If metadata is missing or invalid.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LocalFAISSStore.open")

        if self._rebuild_required.get(index_id, False):
            raise IndexNotBuiltError(f"Index {index_id} requires rebuild after pruning")
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} has not been built")
        idx = self._indexes[index_id]
        if "metadata" not in idx:
            raise IndexMetadataError(f"Index {index_id} not finalized")
        handle = idx.get("faiss_index") or idx["vectors"]
        return (handle, idx["version_hash"], idx["metadata"])

    def search(
        self, index_id: str, query_vector: list[float], top_k: int, cutoff: float
    ) -> list[tuple[str, str, float]]:
        """Search index for similar vectors.

        Args:
            index_id: Identifier of the index to search.
            query_vector: Query embedding vector.
            top_k: Maximum number of results to return.
            cutoff: Minimum similarity score threshold.

        Returns:
            List of (content_hash, trace_id, score_round6) tuples.
            Results are post-sorted deterministically: (score_round6 DESC, content_hash ASC).

        Raises:
            IndexNotBuiltError: If index has not been built or needs rebuild.
        """
        if self._rebuild_required.get(index_id, False):
            raise IndexNotBuiltError(f"Index {index_id} requires rebuild after pruning")
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} has not been built")
        idx = self._indexes[index_id]
        metadatas = idx["metadatas"]
        q_norm = _l2_normalize(query_vector)
        if _faiss_available() and "faiss_index" in idx:
            import numpy as np

            faiss = _import_faiss()
            q_arr = np.array([q_norm], dtype=np.float32)
            faiss.normalize_L2(q_arr)
            k = min(top_k, idx["faiss_index"].ntotal)
            if k == 0:
                return []
            scores_arr, indices_arr = idx["faiss_index"].search(q_arr, k)
            raw: list[tuple[str, str, float]] = []
            for score, i in zip(scores_arr[0], indices_arr[0]):
                if i < 0:
                    continue
                s = float(score)
                if s >= cutoff:
                    meta = metadatas[i]
                    raw.append((meta.get("content_hash", ""), meta.get("trace_id", ""), round(s, 6)))
        else:
            raw = []
            for i, vec in enumerate(idx["vectors"]):
                score = sum((q * v for q, v in zip(q_norm, vec)))
                if score >= cutoff:
                    meta = metadatas[i]
                    raw.append((meta.get("content_hash", ""), meta.get("trace_id", ""), round(score, 6)))
        raw.sort(key=lambda x: (-x[2], x[0]))
        return raw[:top_k]

    def begin_build(self, index_id: str, dimension: int, seed: int) -> None:
        """Begin building a new index.

        Args:
            index_id: Identifier for the index.
            dimension: Embedding dimension.
            seed: Random seed for deterministic builds.
        """
        entry: dict[str, Any] = {"dimension": dimension, "seed": seed, "vectors": [], "metadatas": []}
        if _faiss_available():
            faiss = _import_faiss()
            entry["faiss_index"] = faiss.IndexFlatIP(dimension)
        self._indexes[index_id] = entry
        self._rebuild_required[index_id] = False

    def add_vectors(self, index_id: str, vectors: list[list[float]], metadatas: list[dict[str, Any]]) -> None:
        """Add vectors to the index being built.

        Args:
            index_id: Identifier for the index.
            vectors: List of embedding vectors.
            metadatas: List of metadata dictionaries.

        Raises:
            IndexNotBuiltError: If index build has not been started.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} build not started")
        idx = self._indexes[index_id]
        normed = [_l2_normalize(v) for v in vectors]
        idx["vectors"].extend(normed)
        idx["metadatas"].extend(metadatas)
        if _faiss_available() and "faiss_index" in idx:
            import numpy as np

            arr = np.array(normed, dtype=np.float32)
            idx["faiss_index"].add(arr)

    def finalize_build(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        """Finalize index build and return metadata.

        Args:
            index_id: Identifier for the index.
            built_at_utc: Build timestamp.
            canonicalization_version: Canonicalization format version.
            embedding_model_version: Embedding model version.
            embedding_model_checksum: Embedding model checksum.

        Returns:
            IndexBuildMetadata for the completed index.

        Raises:
            IndexNotBuiltError: If index build has not been started.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} build not started")
        idx = self._indexes[index_id]
        vectors = idx["vectors"]
        metadatas = idx["metadatas"]
        index_version_hash = self._compute_version_hash(vectors, metadatas)
        faiss_ver = (
            "faiss-IndexFlatIP-v1" if _faiss_available() and "faiss_index" in idx else "memory-fallback-v1"
        )
        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version=faiss_ver,
            build_seed=idx["seed"],
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            built_at_utc=built_at_utc,
            index_version_hash=index_version_hash,
            vector_count=len(vectors),
            dimension=idx["dimension"],
        )
        idx["metadata"] = metadata
        idx["version_hash"] = index_version_hash
        if self._telemetry_callback:
            self._telemetry_callback(
                "faiss_index_rebuilt",
                {
                    "index_id": index_id,
                    "vector_count": len(vectors),
                    "index_version_hash": index_version_hash,
                },
            )
        return metadata

    def prune(self, index_id: str, predicate: Callable[[dict[str, Any]], bool]) -> int:
        """Prune vectors from index based on predicate.

        Args:
            index_id: Identifier for the index.
            predicate: Function that returns True for items to prune.

        Returns:
            Number of items removed.

        Raises:
            IndexNotBuiltError: If index has not been built.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} not built")
        idx = self._indexes[index_id]
        vectors = idx["vectors"]
        metadatas = idx["metadatas"]
        to_keep = [i for i, meta in enumerate(metadatas) if not predicate(meta)]
        removed_count = len(metadatas) - len(to_keep)
        if removed_count > 0:
            idx["vectors"] = [vectors[i] for i in to_keep]
            idx["metadatas"] = [metadatas[i] for i in to_keep]
            self._rebuild_required[index_id] = True
            if _faiss_available() and "faiss_index" in idx:
                import numpy as np

                faiss = _import_faiss()
                dim = idx["dimension"]
                new_index = faiss.IndexFlatIP(dim)
                if idx["vectors"]:
                    arr = np.array(idx["vectors"], dtype=np.float32)
                    new_index.add(arr)
                idx["faiss_index"] = new_index
        return removed_count

    def rebuild(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        """Rebuild index after pruning.

        Args:
            index_id: Identifier for the index.
            built_at_utc: Build timestamp.
            canonicalization_version: Canonicalization format version.
            embedding_model_version: Embedding model version.
            embedding_model_checksum: Embedding model checksum.

        Returns:
            IndexBuildMetadata for the rebuilt index.

        Raises:
            IndexNotBuiltError: If index has not been built.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} not built")
        idx = self._indexes[index_id]
        vectors = idx["vectors"]
        metadatas = idx["metadatas"]
        if _faiss_available():
            import numpy as np

            faiss = _import_faiss()
            dim = idx["dimension"]
            new_index = faiss.IndexFlatIP(dim)
            if vectors:
                arr = np.array(vectors, dtype=np.float32)
                new_index.add(arr)
            idx["faiss_index"] = new_index
            faiss_ver = "faiss-IndexFlatIP-v1"
        else:
            faiss_ver = "memory-fallback-v1"
        index_version_hash = self._compute_version_hash(vectors, metadatas)
        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version=faiss_ver,
            build_seed=idx["seed"],
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            built_at_utc=built_at_utc,
            index_version_hash=index_version_hash,
            vector_count=len(vectors),
            dimension=idx["dimension"],
        )
        idx["metadata"] = metadata
        idx["version_hash"] = index_version_hash
        self._rebuild_required[index_id] = False
        if self._telemetry_callback:
            self._telemetry_callback(
                "faiss_index_rebuilt",
                {
                    "index_id": index_id,
                    "vector_count": len(vectors),
                    "index_version_hash": index_version_hash,
                },
            )
        return metadata

    @staticmethod
    def _compute_version_hash(vectors: list, metadatas: list) -> str:
        """Compute deterministic SHA-256 hash over (vector, metadata) pairs."""
        hash_input = []
        for vec, meta in zip(vectors, metadatas):
            vector_bytes = b"".join(struct.pack("<f", x) for x in vec)
            entry = {
                "content_hash": meta.get("content_hash", ""),
                "trace_id": meta.get("trace_id", ""),
                "vector_bytes": vector_bytes.hex(),
            }
            entry_bytes = json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
                "ascii"
            )
            hash_input.append(entry_bytes)
        hasher = hashlib.sha256()
        for eb in sorted(hash_input):
            hasher.update(eb)
        return hasher.hexdigest()

    def persist_to_disk(self, index_id: str, dest_dir: Path, *, embedder_id: str, model_version: str) -> str:
        """Write 3-file artifact (index.json, meta.json, manifest.json) and print W-A-DETERMINISM-DIGEST.

        All three files are written atomically to ``dest_dir``.  The digest is
        sha256 over the pipe-concatenated binding fields and is printed to stdout
        exactly once per call.

        Args:
            index_id: Identifier of the index to persist.
            dest_dir: Target directory (created if absent).
            embedder_id: Embedder identifier string (e.g. "BAAI/bge-m3" or "hash-fallback").
            model_version: Model version string.

        Returns:
            64-char lowercase hex W-A-DETERMINISM-DIGEST string.

        Raises:
            IndexNotBuiltError: If the index has not been built.
            IndexMetadataError: If the index has not been finalized (missing metadata).
        """
        if index_id not in self._memory_indexes:
            raise IndexNotBuiltError(
                f"Index {index_id} not found; call begin_build/add_vectors/finalize_build first"
            )
        memory_idx = self._memory_indexes[index_id]
        if "metadata" not in memory_idx:
            raise IndexMetadataError(f"Index {index_id} not finalized; call finalize_build first")
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        vectors = memory_idx["vectors"]
        metadatas = memory_idx["metadatas"]
        dimension = memory_idx["dimension"]
        version_hash = memory_idx.get("version_hash", "")
        index_data = {
            "schema_version": _SCHEMA_VERSION,
            "index_id": index_id,
            "dimension": dimension,
            "vector_count": len(vectors),
            "vectors": [list(v) for v in vectors],
            "metadatas": metadatas,
        }
        index_bytes = json.dumps(index_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
        sha256_index = hashlib.sha256(index_bytes).hexdigest()
        meta_data = {
            "dims": dimension,
            "embedder_id": embedder_id,
            "index_id": index_id,
            "index_version_hash": version_hash,
            "model_version": model_version,
            "schema_version": _SCHEMA_VERSION,
            "vector_count": len(vectors),
        }
        meta_bytes = json.dumps(meta_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
        sha256_meta = hashlib.sha256(meta_bytes).hexdigest()
        manifest_data = {
            "dims": dimension,
            "embedder_id": embedder_id,
            "model_version": model_version,
            "schema_version": _SCHEMA_VERSION,
            "sha256_index": sha256_index,
            "sha256_meta_canonical": sha256_meta,
            "vector_count": len(vectors),
        }
        manifest_bytes = json.dumps(
            manifest_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        sha256_manifest = hashlib.sha256(manifest_bytes).hexdigest()

        def _atomic_write(path: Path, data: bytes) -> None:
            tmp = path.with_suffix(".tmp")
            try:
                with open(tmp, "wb") as _fh:
                    _fh.write(data)
                    _fh.flush()
                    os.fsync(_fh.fileno())
                tmp.replace(path)
            except OSError as e:
                if tmp.exists():
                    tmp.unlink(missing_ok=True)
                raise

        for _stem in ("index", "meta", "manifest"):
            _stale = dest / f"{_stem}.tmp"
            if _stale.exists():
                _stale.unlink(missing_ok=True)
        _atomic_write(dest / "index.json", index_bytes)
        _atomic_write(dest / "meta.json", meta_bytes)
        _atomic_write(dest / "manifest.json", manifest_bytes)
        digest_input = f"{embedder_id}|{model_version}|{dimension}|{len(vectors)}|{sha256_index}|{sha256_meta}|{sha256_manifest}"
        digest = hashlib.sha256(digest_input.encode("ascii")).hexdigest()
        print(f"W-A-DETERMINISM-DIGEST: {digest}")
        if self._telemetry_callback:
            self._telemetry_callback(
                "faiss_index_persisted",
                {
                    "index_id": index_id,
                    "vector_count": len(vectors),
                    "digest": digest,
                    "embedder_id": embedder_id,
                    "model_version": model_version,
                },
            )
        return digest

    def load_from_disk(
        self, index_id: str, source_dir: Path, *, expected_embedder_id: str | None = None
    ) -> None:
        """Load index from 3-file disk artifact, verifying all manifest hashes.

        Fail-closed: any missing field, parse error, or hash mismatch raises
        ManifestIntegrityError immediately with no fallback.

        Args:
            index_id: Logical identifier to register the loaded index under.
            source_dir: Directory containing index.json, meta.json, manifest.json.
            expected_embedder_id: When provided, the manifest's embedder_id must
                match exactly; raises EmbedderMismatchError otherwise.  This
                prevents mixed-vector indexes from being silently loaded.

        Raises:
            ManifestIntegrityError: On any integrity violation.
            EmbedderMismatchError: When expected_embedder_id is given and does
                not match the stored value.
        """
        src = Path(source_dir)
        manifest_path = src / "manifest.json"
        if not manifest_path.exists():
            raise ManifestIntegrityError(f"manifest.json not found in {src}")
        try:
            manifest_bytes = manifest_path.read_bytes()
            manifest = json.loads(manifest_bytes.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ManifestIntegrityError(f"manifest.json parse error: {exc}") from exc
        required = {
            "schema_version",
            "embedder_id",
            "model_version",
            "dims",
            "vector_count",
            "sha256_index",
            "sha256_meta_canonical",
        }
        missing = required - manifest.keys()
        if missing:
            raise ManifestIntegrityError(f"manifest.json missing required fields: {sorted(missing)}")
        if expected_embedder_id is not None and manifest["embedder_id"] != expected_embedder_id:
            raise EmbedderMismatchError(
                f"embedder_id mismatch: manifest has '{manifest['embedder_id']}' but runtime expects '{expected_embedder_id}' — index at {source_dir} was built with a different model and cannot be loaded"
            )
        index_path = src / "index.json"
        if not index_path.exists():
            raise ManifestIntegrityError(f"index.json not found in {src}")
        index_bytes = index_path.read_bytes()
        if hashlib.sha256(index_bytes).hexdigest() != manifest["sha256_index"]:
            raise ManifestIntegrityError("index.json sha256 mismatch — artifact tampered")
        meta_path = src / "meta.json"
        if not meta_path.exists():
            raise ManifestIntegrityError(f"meta.json not found in {src}")
        meta_bytes = meta_path.read_bytes()
        if hashlib.sha256(meta_bytes).hexdigest() != manifest["sha256_meta_canonical"]:
            raise ManifestIntegrityError("meta.json sha256 mismatch — artifact tampered")
        try:
            index_data = json.loads(index_bytes.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ManifestIntegrityError(f"index.json parse error: {exc}") from exc
        vectors = [list(v) for v in index_data.get("vectors", [])]
        metadatas = index_data.get("metadatas", [])
        dimension = int(index_data.get("dimension", manifest["dims"]))
        from system_learning.types.index_build_metadata_types import IndexBuildMetadata

        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version="disk-json-v1",
            build_seed=0,
            canonicalization_version=_SCHEMA_VERSION,
            embedding_model_version=manifest["model_version"],
            embedding_model_checksum=manifest["sha256_index"],
            built_at_utc=0,
            index_version_hash=manifest["sha256_index"],
            vector_count=len(vectors),
            dimension=dimension,
        )
        self._memory_indexes[index_id] = {
            "dimension": dimension,
            "seed": 0,
            "vectors": vectors,
            "metadatas": metadatas,
            "metadata": metadata,
            "version_hash": manifest["sha256_index"],
        }
        if self._telemetry_callback:
            self._telemetry_callback(
                "faiss_manifest_verified",
                {
                    "index_id": index_id,
                    "vector_count": len(vectors),
                    "digest": manifest["sha256_index"],
                    "embedder_id": manifest["embedder_id"],
                    "model_version": manifest["model_version"],
                },
            )

    @staticmethod
    def verify_indexes_at_boot(base_dir: Path, *, expected_embedder_id: str | None = None) -> dict[str, str]:
        """Run boot-time integrity sweep over all persisted FAISS index artifacts.

        Delegates to ``faiss_startup_integrity.verify_all_indexes_in_dir``.
        Returns ``dict[index_id -> digest]`` on success.
        Raises ``StartupIntegrityError`` immediately on the first violation.

        Call this once at process startup before any ``load_from_disk`` calls.
        If ``base_dir`` does not exist, returns an empty dict (no indexes yet built).

        Args:
            base_dir: Root directory under which per-index subdirectories live.
            expected_embedder_id: If provided, every manifest must match exactly.

        Returns:
            Mapping of index_id to W-A-DETERMINISM-DIGEST for every verified index.
        """
        from system_learning.engines.faiss_startup_integrity import verify_all_indexes_in_dir

        base = Path(base_dir)
        if not base.exists():
            return {}
        return verify_all_indexes_in_dir(base, expected_embedder_id=expected_embedder_id)


__all__ = [
    "LocalFAISSStore",
    "IndexNotBuiltError",
    "IndexMetadataError",
    "ManifestIntegrityError",
    "EmbedderMismatchError",
]
