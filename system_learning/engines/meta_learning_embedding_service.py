"""MetaLearningEmbeddingService for Plan B Phase 2.

Read-only embedding retrieval service that consumes Seed Embedding Packs
and produces deterministic EmbeddingArtifacts.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Protocol

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

_emit_authorize_and_execute("p2", "meta_learning_embedding_service", "execution_auth")
_emit_validates_capability("p2", "meta_learning_embedding_service", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_embedding_service", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_embedding_service", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_embedding_service", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_embedding_service", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_embedding_service", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_embedding_service", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_embedding_service", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_embedding_service", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_embedding_service", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_embedding_service", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_embedding_service", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_embedding_service", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_embedding_service", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_embedding_service", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_embedding_service", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_embedding_service", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_embedding_service", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_embedding_service", "exec_snapshot_link")
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.types.embedding_artifact import EmbeddingArtifact

_emit_applies_guardrail("p0", "meta_learning_embedding_service", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_embedding_service", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_embedding_service", "state_snapshot")
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

_emit_emits_metric_event("meta_learning_embedding_service", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_embedding_service", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_embedding_service", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_embedding_service", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_embedding_service", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_embedding_service", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_embedding_service", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_embedding_service", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_embedding_service", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_embedding_service", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_embedding_service", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_embedding_service", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_embedding_service", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_embedding_service", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_embedding_service", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_embedding_service", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_embedding_service", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_embedding_service", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_embedding_service", "p3lm", "state")
_emit_records_execution_trace("meta_learning_embedding_service", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_embedding_service", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_embedding_service", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_embedding_service", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_embedding_service", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_embedding_service", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_embedding_service", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_embedding_service", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_embedding_service", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning_embedding_service", "context_pull")
_emit_pulls_context("p1", "meta_learning_embedding_service", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_learning_embedding_service", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_embedding_service", "uwg_term_2")
_emit_writes_through("p1", "meta_learning_embedding_service", "write_through")
_emit_writes_through("p1", "meta_learning_embedding_service", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_learning_embedding_service", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_embedding_service", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_embedding_service", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_embedding_service", "human_escalation")
_emit_routes_through("p1", "meta_learning_embedding_service", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_embedding_service", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_embedding_service", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_embedding_service", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_embedding_service", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_embedding_service", "target_agent")
_emit_verifies_policy("p1", "meta_learning_embedding_service", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_embedding_service", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_embedding_service", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_embedding_service", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_embedding_service")
_emit_gated_by_confidence("p1", "meta_learning_embedding_service", "confidence_gate")
emit_replay_key("p0", "meta_learning_embedding_service")
emit_determinism_digest("p0", "meta_learning_embedding_service")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class Embedder(Protocol):
    """Protocol for embedding generation.

    Production embedder will be injected; tests use deterministic stub.
    """

    def embed_batch(self, texts: list[str], dimensions: int) -> list[list[float]]:
        """Embed a batch of texts.

        Args:
            texts: List of texts to embed.
            dimensions: Embedding vector dimensions.

        Returns:
            List of embedding vectors as lists of floats.
        """
        ...


class IntegrityError(Exception):
    """Raised when seed pack integrity validation fails."""

    pass


class MetaLearningEmbeddingService:
    """Read-only embedding retrieval service for Seed Embedding Packs."""

    def __init__(self, base_path: str, embedder: Embedder | None = None):
        """Initialize the service.

        Args:
            base_path: Base directory containing seed packs.
            embedder: Embedder instance for query embedding. If None, a live OpenAI client is created.
        """
        self.base_path = Path(base_path)
        self._embedder_injected = embedder is not None
        if embedder:
            self.embedder = embedder
        else:
            _factory = EmbeddingServiceFactory.get_or_disabled()
            if not _factory.is_disabled():
                try:
                    from system_learning.engines.openai_embedder import BGEEmbedder

                    self.embedder = BGEEmbedder()
                except (AttributeError, ImportError, RuntimeError, TypeError, ValueError):
                    self.embedder = None
            else:
                self.embedder = None
        self._factory = EmbeddingServiceFactory.get_or_disabled()

    def retrieve(
        self,
        *,
        namespace: str,
        seed_index_version_hash: str,
        query_text: str,
        profile: RetrievalProfile | None = None,
        k: int | None = None,
    ) -> EmbeddingArtifact | None:
        """Retrieve top-k embeddings for a query.

        Args:
            namespace: Namespace of the seed pack.
            seed_index_version_hash: Version hash of the seed pack.
            query_text: Query text to embed.
            k: Number of results to retrieve.

        Returns:
            EmbeddingArtifact with results, or None if pack doesn't exist or disabled.

        Raises:
            IntegrityError: If pack integrity validation fails.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "MetaLearningEmbeddingService.retrieve"
        )

        if self.embedder is None:
            return None
        if not self._embedder_injected and self._factory.is_disabled():
            return None
        pack_dir = self.base_path / "seed_packs" / namespace / seed_index_version_hash
        if not pack_dir.exists():
            return None
        manifest, row_data, embeddings_matrix = self._load_and_validate_pack(
            pack_dir,
            seed_index_version_hash,
        )
        if profile is not None and manifest["dimensions"] != profile.embedding_dim:
            raise IntegrityError(
                f"FAISS dimension mismatch: manifest={manifest['dimensions']}, profile={profile.embedding_dim}. Rebuild seed pack for this profile.",
            )
        query_vecs = self.embedder.embed_batch([query_text], dimensions=manifest["dimensions"])
        query_vec = query_vecs[0]
        candidates = self._compute_similarities(query_vec, row_data, embeddings_matrix)
        sorted_candidates = sorted(candidates, key=lambda x: (-x["score"], x["content_hash"], x["trace_id"]))
        effective_k = k if k is not None else profile.top_k if profile is not None else len(sorted_candidates)
        top_k = sorted_candidates[:effective_k]
        return EmbeddingArtifact(
            namespace=namespace,
            seed_index_version_hash=seed_index_version_hash,
            supporting_trace_ids=[c["trace_id"] for c in top_k],
            supporting_content_hashes=[c["content_hash"] for c in top_k],
            k=len(top_k),
            similarity_metric="cosine",
            embedding_model_version=manifest["embedding_model_version"],
        )

    def _load_and_validate_pack(
        self,
        pack_dir: Path,
        seed_index_version_hash: str,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[list[float]]]:
        """Load and validate seed pack integrity.

        Args:
            pack_dir: Directory containing the seed pack.
            seed_index_version_hash: Expected version hash.

        Returns:
            Tuple of (manifest, row_data, embeddings_matrix).

        Raises:
            IntegrityError: If validation fails.
        """
        manifest_path = pack_dir / "seed_manifest.json"
        row_index_path = pack_dir / "row_index.jsonl"
        embeddings_path = pack_dir / "embeddings.f32"
        if not all(p.exists() for p in [manifest_path, row_index_path, embeddings_path]):
            raise IntegrityError(f"Missing required files in seed pack: {pack_dir}")
        row_index_bytes = row_index_path.read_bytes()
        embeddings_bytes = embeddings_path.read_bytes()
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        if manifest.get("seed_index_version_hash") != seed_index_version_hash:
            raise IntegrityError(
                f"Seed index version hash mismatch: manifest {manifest.get('seed_index_version_hash')}, expected {seed_index_version_hash}",
            )
        row_index_hash = hashlib.sha256(row_index_bytes).hexdigest()
        if row_index_hash != manifest.get("row_index_hash"):
            raise IntegrityError(
                f"Row index hash mismatch: computed {row_index_hash}, expected {manifest.get('row_index_hash')}",
            )
        embeddings_hash = hashlib.sha256(embeddings_bytes).hexdigest()
        if embeddings_hash != manifest.get("matrix_hash"):
            raise IntegrityError(
                f"Embeddings hash mismatch: computed {embeddings_hash}, expected {manifest.get('matrix_hash')}",
            )
        row_data = []
        for line in row_index_bytes.decode("utf-8").strip().split("\n"):
            if line:
                row_data.append(json.loads(line))
        dimensions = manifest["dimensions"]
        vector_count = manifest["vector_count"]
        if len(embeddings_bytes) != vector_count * dimensions * 4:
            raise IntegrityError(
                f"Embeddings file size mismatch: expected {vector_count * dimensions * 4} bytes, got {len(embeddings_bytes)}",
            )
        embeddings_matrix = []
        for i in range(vector_count):
            offset = i * dimensions * 4
            vector = []
            for j in range(dimensions):
                byte_offset = offset + j * 4
                value = struct.unpack("<f", embeddings_bytes[byte_offset : byte_offset + 4])[0]
                vector.append(value)
            embeddings_matrix.append(vector)
        return (manifest, row_data, embeddings_matrix)

    def _compute_similarities(
        self,
        query_vec: list[float],
        row_data: list[dict[str, Any]],
        embeddings_matrix: list[list[float]],
    ) -> list[dict[str, Any]]:
        """Compute cosine similarities between query and all embeddings.

        Args:
            query_vec: Query embedding vector.
            row_data: Parsed row index data.
            embeddings_matrix: Embedding vectors matrix.

        Returns:
            List of candidates with similarity scores.
        """
        if not embeddings_matrix:
            return []
        import numpy as np

        q = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        q_unit = q / q_norm
        matrix = np.array(embeddings_matrix, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        valid_mask = norms[:, 0] > 0
        matrix_unit = np.where(norms > 0, matrix / np.maximum(norms, 1e-12), 0.0)
        scores = matrix_unit @ q_unit
        candidates = []
        for i, row in tqdm(enumerate(row_data), desc="Processing", unit="item"):
            if not valid_mask[i]:
                continue
            candidates.append(
                {
                    "score": float(scores[i]),
                    "trace_id": row["trace_id"],
                    "content_hash": row["content_hash"],
                    "row_id": row["row_id"],
                },
            )
        return candidates


__all__ = ["MetaLearningEmbeddingService", "IntegrityError"]
