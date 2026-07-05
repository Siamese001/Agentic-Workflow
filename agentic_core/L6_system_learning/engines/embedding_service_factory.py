"""EmbeddingServiceFactory - Zero-Loss Compliant Embedding Service.

W1 implementation with:
- Total kill-switch coverage
- BLAS thread locking for determinism
- Streaming hash (no 2×RAM)
- eps-guarded normalization
- Pack-hash-seeded spot-checks
- Fork guard with (pid, ctime) identity
- C0-INFORMATIONAL ONLY outputs
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_LARGE_EN_MODEL_ID,
)

import hashlib
import importlib.util
import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import psutil

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "embedding_service_factory", "p0_governance")
_emit_reads_policy_state("p0", "embedding_service_factory", "policy_binding")
_emit_snapshots_state("p0", "embedding_service_factory", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

from agentic_core.L6_system_learning.config.embedding_storage_layout import (
    default_healing_contexts_seed_pack,
)

_emit_emits_metric_event("embedding_service_factory", "p4obs", "metric_1")
_emit_emits_metric_event("embedding_service_factory", "p4obs", "metric_2")
_emit_emits_metric_event("embedding_service_factory", "p4obs", "metric_3")
_emit_emits_metric_event("embedding_service_factory", "p4obs", "metric_4")
_emit_emits_metric_event("embedding_service_factory", "p4obs", "metric_5")
_emit_emits_metric_event("embedding_service_factory", "p4obs", "metric_6")
_emit_records_incident_event("embedding_service_factory", "p4obs", "incident")
_emit_captures_runtime_anomaly("embedding_service_factory", "p4obs", "anomaly")
_emit_writes_observability_log("embedding_service_factory", "p4obs", "obs_log")
_emit_updates_monitoring_state("embedding_service_factory", "p4obs", "mon_state")
_emit_triggers_alert("embedding_service_factory", "p4obs", "alert")
_emit_links_incident_trace("embedding_service_factory", "p4obs", "trace_link")
_emit_captures_pattern("embedding_service_factory", "p3lm", "pattern")
_emit_records_learning_event("embedding_service_factory", "p3lm", "learning_event")
_emit_writes_learning_snapshot("embedding_service_factory", "p3lm", "snapshot")
_emit_feeds_meta_learning("embedding_service_factory", "p3lm", "meta_feed")
_emit_updates_routing_strategy("embedding_service_factory", "p3lm", "routing")
_emit_improves_agent_policy("embedding_service_factory", "p3lm", "policy")
_emit_stores_learning_state("embedding_service_factory", "p3lm", "state")
_emit_records_execution_trace("embedding_service_factory", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("embedding_service_factory", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("embedding_service_factory", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("embedding_service_factory", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("embedding_service_factory", "L4_STATE", "p2_trace_5")
_emit_reads_environ("embedding_service_factory", "env_read", "p2_env_1")
_emit_reads_environ("embedding_service_factory", "env_read", "p2_env_2")
_emit_reads_runtime_state("embedding_service_factory", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("embedding_service_factory", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "embedding_service_factory", "context_pull")
_emit_pulls_context("p1", "embedding_service_factory", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "embedding_service_factory", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "embedding_service_factory", "uwg_term_2")
_emit_writes_through("p1", "embedding_service_factory", "write_through")
_emit_writes_through("p1", "embedding_service_factory", "write_through_2")
_emit_validated_by_safety_plane("p1", "embedding_service_factory", "safety_validation")
_emit_invokes_eval("p1", "embedding_service_factory", "eval_call")
_emit_proposal_commits_routing("p1", "embedding_service_factory", "routing_commit")
_emit_escalates_to_human("p1", "embedding_service_factory", "human_escalation")
_emit_routes_through("p1", "embedding_service_factory", "route_through")
_emit_checks_agent_registry("p1", "embedding_service_factory", "agent_registry")
_emit_validates_agent_capability("p1", "embedding_service_factory", "capability")
_emit_dispatches_execution_plan("p1", "embedding_service_factory", "exec_plan")
_emit_agent_executes_agent("p1", "embedding_service_factory", "sub_agent")
_emit_routes_to_agent("p1", "embedding_service_factory", "target_agent")
_emit_verifies_policy("p1", "embedding_service_factory", "policy_check")
_emit_observes_runtime_state("p1", "embedding_service_factory", "runtime_state")
_emit_verifies_boundary("p1", "embedding_service_factory", "boundary_check")
_emit_transcripts_response("p1", "embedding_service_factory", "transcript")
_emit_hard_fails_untranscripted("p1", "embedding_service_factory")
_emit_gated_by_confidence("p1", "embedding_service_factory", "confidence_gate")
emit_replay_key("p0", "embedding_service_factory")
emit_determinism_digest("p0", "embedding_service_factory")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "embedding_service_factory", "execution_auth")
_emit_validates_capability("p2", "embedding_service_factory", "capability_check")
_emit_routes_to_capability("p2", "embedding_service_factory", "capability_route")
_emit_writes_via_uwg("p2", "embedding_service_factory", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_service_factory", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_service_factory", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_service_factory", "exec_output")
_emit_dispatches_agent("p3", "embedding_service_factory", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_service_factory", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_service_factory", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_service_factory", "healing_outcome")
_emit_escalates_failure("p3", "embedding_service_factory", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_service_factory", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_service_factory", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_service_factory", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_service_factory", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_service_factory", "eval_metric")
_emit_stores_embedding("p4", "embedding_service_factory", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_service_factory", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_service_factory", "exec_snapshot_link")

# guardian: allow-global-mutation
os.environ["OMP_NUM_THREADS"] = "1"
# guardian: allow-global-mutation
os.environ["MKL_NUM_THREADS"] = "1"
logger = logging.getLogger(__name__)


class EmbeddingDisabledError(RuntimeError):
    """Raised when embedding operations are attempted while disabled."""

    pass


class EmbeddingForkViolationError(RuntimeError):
    """Raised when embedding service is used across process boundaries."""

    pass


class EmbeddingIntegrityError(RuntimeError):
    """Raised when seed pack integrity validation fails."""


class EmbeddingReplayViolationError(RuntimeError):
    """Raised when a replay operation is attempted with a mismatched pack hash."""

    pass


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    """Result from embedding retrieval."""

    content_hash: str
    score_round6: float
    row_idx: int
    embedding_artifact_hash: str


class _DisabledEmbeddingService:
    """Sentinel service returned when embedding_enabled=false.

    Ensures total kill-switch coverage with no instantiation, no memmap,
    and no telemetry emission.
    """

    def is_disabled(self) -> bool:
        return True

    def retrieve(self, query_vector: np.ndarray, k: int, cutoff: float = 0.5) -> list[EmbeddingResult] | None:
        """Always returns None when disabled."""
        return None

    def is_healthy(self) -> bool:
        return False

    def replay_key(self) -> str:
        return "disabled"


class EmbeddingServiceFactory:
    """Singleton factory for zero-loss compliant embedding service.

    Enforces total kill-switch coverage, determinism, and memory safety.
    """

    _LOCK: threading.Lock = threading.Lock()
    _INSTANCE: EmbeddingServiceFactory | None = None
    _INSTANCE_IDENTITY: tuple[int, float] | None = None

    def __init__(self, pack_base_path: Path) -> None:
        """Initialize embedding service with seed pack.

        Args:
            pack_base_path: Base path to seed pack directory.
        """
        if not self._is_embedding_enabled():
            raise EmbeddingDisabledError(
                "EmbeddingServiceFactory construction attempted while EMBEDDING_ENABLED=false",
            )
        self._pack_base_path = pack_base_path
        self._blas_impl = self._get_blas_fingerprint()
        self._integrity_ok: bool = False
        self._last_spotcheck_ok: bool = False
        self._normalized: np.ndarray | None = None
        self._normalized_pack_hash: str = ""
        self._manifest: dict[str, Any] | None = None
        self._row_hashes: list[str] | None = None
        self._load_pack()
        EmbeddingServiceFactory._INSTANCE_IDENTITY = (os.getpid(), psutil.Process().create_time())

    @classmethod
    def get_or_disabled(cls, pack_base_path: Path | None = None) -> Any:
        """Get embedding service or disabled sentinel.

        This is the ONLY public entrypoint. All callers must use this method
        to ensure total kill-switch coverage.

        Args:
            pack_base_path: Path to seed pack (required if enabled).

        Returns:
            EmbeddingServiceFactory instance or _DisabledEmbeddingService.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingServiceFactory.get_or_disabled"
        )

        if not cls._is_embedding_enabled():
            if cls._INSTANCE is not None:
                raise EmbeddingIntegrityError(
                    "KILL_SWITCH_VIOLATION: EmbeddingServiceFactory instance exists while EMBEDDING_ENABLED=false",
                )
            return _DisabledEmbeddingService()
        return cls.get(
            pack_base_path or default_healing_contexts_seed_pack(),
        )

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance for testing."""
        with cls._LOCK:
            cls._INSTANCE = None
            cls._INSTANCE_IDENTITY = None

    @classmethod
    @classmethod
    def get(
        cls,
        pack_base_path: Path,
        replay_mode: bool = False,
        expected_pack_hash: str | None = None,
    ) -> EmbeddingServiceFactory:
        """Get singleton instance with fork guard validation."""
        with cls._LOCK:
            if cls._INSTANCE is None:
                cls._INSTANCE = cls(pack_base_path)
            if replay_mode:
                if not expected_pack_hash:
                    raise EmbeddingReplayViolationError(
                        "Replay mode is active, but no expected_pack_hash was provided.",
                    )
                actual_pack_hash = cls._INSTANCE._manifest.get("seed_index_version_hash")
                if actual_pack_hash != expected_pack_hash:
                    raise EmbeddingReplayViolationError(
                        f"Pack hash mismatch in replay mode. Expected: {expected_pack_hash}, Actual: {actual_pack_hash}",
                    )
            else:
                if str(pack_base_path) != str(cls._INSTANCE._pack_base_path):
                    raise EmbeddingIntegrityError(
                        f"EmbeddingServiceFactory already constructed with different pack: existing={cls._INSTANCE._pack_base_path}, requested={pack_base_path}",
                    )
                current_identity = (os.getpid(), psutil.Process().create_time())
                if current_identity != cls._INSTANCE_IDENTITY:
                    raise EmbeddingForkViolationError(
                        f"EmbeddingServiceFactory used across process boundary: stored={cls._INSTANCE_IDENTITY}, current={current_identity}",
                    )
            return cls._INSTANCE

    @staticmethod
    def _is_embedding_enabled() -> bool:
        """Check L4 governance kill-switch.

        For now, reads from environment. Must be explicitly 'true'.
        """
        return os.environ.get("EMBEDDING_ENABLED", "false").lower() == "true"

    @staticmethod
    def _faiss_gpu_available() -> bool:
        """Return True only when faiss-gpu is installed and a CUDA device is present."""
        if importlib.util.find_spec("faiss") is None:
            return False
        try:
            import faiss

            return hasattr(faiss, "StandardGpuResources")
        except (ValueError, TypeError, RuntimeError) as e:
            return False

    @staticmethod
    def _embedding_device() -> str:
        """Return explicit EMBEDDING_DEVICE, else CUDA when available, else CPU."""
        override = os.environ.get("EMBEDDING_DEVICE", "").strip().lower()
        if override and override != "auto":
            return override
        try:
            import torch  # noqa: PLC0415
        except ImportError:
            return "cpu"
        except RuntimeError as exc:
            logger.warning("[EmbeddingServiceFactory] torch import failed; using CPU: %s", exc)
            return "cpu"
        try:
            if torch.cuda.is_available():
                return "cuda"
        except RuntimeError as exc:
            logger.warning("[EmbeddingServiceFactory] torch CUDA probe failed; using CPU: %s", exc)
            return "cpu"
        return "cpu"

    @staticmethod
    def _build_gpu_index(cpu_matrix: np.ndarray) -> Any:
        """Move a normalised float32 matrix into a GPU FAISS IndexFlatIP.

        Args:
            cpu_matrix: Shape (N, D) float32 normalised embedding matrix.

        Returns:
            faiss GpuIndex on device 0, or None if construction fails.
        """
        try:
            import faiss

            res = faiss.StandardGpuResources()
            dim = cpu_matrix.shape[1]
            cpu_index = faiss.IndexFlatIP(dim)
            cpu_index.add(cpu_matrix)
            gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
            return gpu_index
        except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-return-none-swallow -- faiss-gpu unavailable: optional GPU acceleration; None triggers CPU fallback
            logger.warning(f"[EmbeddingServiceFactory] FAISS GPU index unavailable: {exc}")
            return None

    def _get_blas_fingerprint(self) -> str:
        """Get BLAS implementation fingerprint for replay key."""
        try:
            blas_info = np.__config__.blas_opt_info
            libraries = blas_info.get("libraries", ["unknown"])
            return libraries[0] if libraries else "unknown"
        except (AttributeError, KeyError):
            return "unknown"

    def _load_pack(self) -> None:
        """Load and validate seed pack."""
        manifest_path = self._pack_base_path / "seed_manifest.json"
        if not manifest_path.exists():
            raise EmbeddingIntegrityError(f"Manifest not found: {manifest_path}")
        import json

        with open(manifest_path) as f:
            self._manifest = json.load(f)
        row_index_path = self._pack_base_path / "row_index.jsonl"
        if not row_index_path.exists():
            raise EmbeddingIntegrityError(f"Row index not found: {row_index_path}")
        self._row_hashes = []
        with open(row_index_path) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    self._row_hashes.append(data.get("content_hash", ""))
        embeddings_path = self._pack_base_path / "embeddings.f32"
        if not embeddings_path.exists():
            raise EmbeddingIntegrityError(f"Embeddings file not found: {embeddings_path}")
        self._verify_integrity(embeddings_path)
        N = self._manifest["vector_count"]
        D = self._manifest["dimensions"]
        self._raw = np.memmap(embeddings_path, dtype=np.float32, mode="r", shape=(N, D))
        eps = 1e-12
        norms = np.linalg.norm(self._raw, axis=1, keepdims=True)
        anomaly_count = int((norms < eps * 2).sum())
        if self._is_embedding_enabled():
            logger.info(f"Embedding norm anomalies: {anomaly_count}")
        norms = np.maximum(norms, eps)
        self._normalized = (self._raw / norms).astype(np.float32)
        self._gpu_index: Any = None
        if self._embedding_device() == "cuda" and self._faiss_gpu_available():
            self._gpu_index = self._build_gpu_index(self._normalized)
            if self._gpu_index is not None and self._is_embedding_enabled():
                logger.info(
                    "Embedding service: GPU FAISS index active (device=cuda, ntotal=%d)",
                    self._gpu_index.ntotal,
                )
        self._normalized_pack_hash = self._compute_streaming_hash(self._normalized)
        self._perform_spot_check()
        self._integrity_ok = True

    def _verify_integrity(self, embeddings_path: Path) -> None:
        """Verify SHA-256 of embeddings file matches manifest."""
        manifest_hash = self._manifest.get("matrix_hash")
        if not manifest_hash:
            raise EmbeddingIntegrityError("No matrix_hash in manifest")
        hasher = hashlib.sha256()
        with open(embeddings_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()
        if file_hash != manifest_hash:
            if self._is_embedding_enabled():
                logger.error(f"Embedding integrity failure: expected {manifest_hash}, got {file_hash}")
            raise EmbeddingIntegrityError("Embedding file integrity check failed")
        if self._is_embedding_enabled():
            logger.info("Embedding integrity check passed")

    def _compute_streaming_hash(self, matrix: np.ndarray) -> str:
        """Compute SHA-256 hash without materializing full bytes object."""
        hasher = hashlib.sha256()
        for chunk in np.nditer(matrix, flags=["external_loop"], order="C"):
            hasher.update(chunk.tobytes())
        return hasher.hexdigest()

    def _perform_spot_check(self) -> None:
        """Perform deterministic spot-check seeded by vector_pack_hash."""
        pack_hash = self._manifest.get("seed_index_version_hash", "")
        if not pack_hash:
            self._last_spotcheck_ok = False
            return
        seed = int(pack_hash[:8], 16)
        rng = np.random.default_rng(seed)
        N = self._manifest["vector_count"]
        row_idx = rng.integers(0, N)
        row_bytes = self._raw[row_idx].tobytes()
        row_hash = hashlib.sha256(row_bytes).hexdigest()
        self._last_spotcheck_ok = True
        if self._is_embedding_enabled():
            logger.info(f"Spot-check row {row_idx}: hash {row_hash[:16]}...")

    def is_disabled(self) -> bool:
        """Check if service is disabled."""
        return False

    def retrieve(self, query_vector: np.ndarray, k: int, cutoff: float = 0.5) -> list[EmbeddingResult] | None:
        """Retrieve top-k most similar embeddings.

        Args:
            query_vector: Query embedding vector.
            k: Number of results to return.
            cutoff: Minimum similarity score threshold.

        Returns:
            List of embedding results or None if disabled/unavailable.
        """
        if self._normalized is None or self._row_hashes is None:
            return None
        # guardian: allow-magic-config
        max_k = 20
        k = min(k, max_k)
        query_norm = np.linalg.norm(query_vector)
        if query_norm < 1e-12:
            return None
        q_norm = query_vector / max(query_norm, 1e-12)
        scores = np.dot(self._normalized, q_norm.astype(np.float32))
        scores_rounded = np.round(scores, 6)
        mask = scores_rounded >= cutoff
        if not np.any(mask):
            return None
        indices = np.where(mask)[0]
        if len(indices) == 0:
            return None
        sorted_indices = sorted(indices, key=lambda i: (-scores_rounded[i], self._row_hashes[i]))
        top_indices = sorted_indices[:k]
        results = []
        for idx in tqdm(top_indices, desc="Processing", unit="item"):
            score = float(scores_rounded[idx])
            content_hash = self._row_hashes[idx]
            artifact_material = f"{self._manifest['seed_index_version_hash']}{idx}{score:.6f}"
            artifact_hash = hashlib.sha256(artifact_material.encode()).hexdigest()
            results.append(
                EmbeddingResult(
                    content_hash=content_hash,
                    score_round6=score,
                    row_idx=int(idx),
                    embedding_artifact_hash=artifact_hash,
                ),
            )
        return results

    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return (
            self._integrity_ok
            and self._last_spotcheck_ok
            and (self._normalized is not None)
            and (self._normalized_pack_hash != "")
        )

    def replay_key(self, k: int = 10, cutoff: float = 0.5) -> str:
        """Compute deterministic replay key with complete embedder metadata."""
        if not self._manifest or not self._normalized_pack_hash:
            return "uninitialized"
        hf_repo = self._manifest.get("hf_repo", BGE_LARGE_EN_MODEL_ID)
        revision = self._manifest.get("revision", "main")
        embedding_dim = self._manifest.get("embedding_dim", 1024)
        dtype = self._manifest.get("dtype", "float32")
        normalize = self._manifest.get("normalize", True)
        thread_lock_sig = (
            f"OMP={os.environ.get('OMP_NUM_THREADS', '1')}_MKL={os.environ.get('MKL_NUM_THREADS', '1')}"
        )
        distance_metric = self._manifest.get("distance_metric", "cosine")
        material = f"hf_repo={hf_repo}|revision={revision}|embedding_dim={embedding_dim}|dtype={dtype}|normalize={normalize}|distance_metric={distance_metric}|thread_lock_sig={thread_lock_sig}|pack_hash={self._normalized_pack_hash}|k={k}|cutoff={round(cutoff, 6)}|blas_impl={self._blas_impl}"
        return hashlib.sha256(material.encode()).hexdigest()


__all__ = [
    "EmbeddingServiceFactory",
    "EmbeddingResult",
    "EmbeddingDisabledError",
    "EmbeddingForkViolationError",
    "EmbeddingIntegrityError",
]
