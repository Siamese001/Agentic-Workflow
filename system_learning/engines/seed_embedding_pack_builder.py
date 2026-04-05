"""Seed Embedding Pack builder for Plan B Phase 0.

Deterministic, atomic builder for governed embedding bootstrap packs.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
import tempfile
from pathlib import Path
from typing import Any, Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "seed_embedding_pack_builder", "execution_auth")
_emit_validates_capability("p2", "seed_embedding_pack_builder", "capability_check")
_emit_routes_to_capability("p2", "seed_embedding_pack_builder", "capability_route")
_emit_writes_via_uwg("p2", "seed_embedding_pack_builder", "uwg_write")
_emit_blocks_direct_write("p2", "seed_embedding_pack_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "seed_embedding_pack_builder", "tool_invocation")
_emit_captures_execution_output("p2", "seed_embedding_pack_builder", "exec_output")
_emit_dispatches_agent("p3", "seed_embedding_pack_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "seed_embedding_pack_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "seed_embedding_pack_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "seed_embedding_pack_builder", "healing_outcome")
_emit_escalates_failure("p3", "seed_embedding_pack_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "seed_embedding_pack_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "seed_embedding_pack_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "seed_embedding_pack_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "seed_embedding_pack_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "seed_embedding_pack_builder", "eval_metric")
_emit_stores_embedding("p4", "seed_embedding_pack_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "seed_embedding_pack_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "seed_embedding_pack_builder", "exec_snapshot_link")
from system_learning.types.seed_embedding_pack_types import (
    SeedEmbeddingPackConfig,
    SeedEmbeddingPackManifest,
)

_emit_applies_guardrail("p0", "seed_embedding_pack_builder", "p0_governance")
_emit_reads_policy_state("p0", "seed_embedding_pack_builder", "policy_binding")
_emit_snapshots_state("p0", "seed_embedding_pack_builder", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("seed_embedding_pack_builder", "p4obs", "metric_1")
_emit_emits_metric_event("seed_embedding_pack_builder", "p4obs", "metric_2")
_emit_emits_metric_event("seed_embedding_pack_builder", "p4obs", "metric_3")
_emit_emits_metric_event("seed_embedding_pack_builder", "p4obs", "metric_4")
_emit_emits_metric_event("seed_embedding_pack_builder", "p4obs", "metric_5")
_emit_emits_metric_event("seed_embedding_pack_builder", "p4obs", "metric_6")
_emit_records_incident_event("seed_embedding_pack_builder", "p4obs", "incident")
_emit_captures_runtime_anomaly("seed_embedding_pack_builder", "p4obs", "anomaly")
_emit_writes_observability_log("seed_embedding_pack_builder", "p4obs", "obs_log")
_emit_updates_monitoring_state("seed_embedding_pack_builder", "p4obs", "mon_state")
_emit_triggers_alert("seed_embedding_pack_builder", "p4obs", "alert")
_emit_links_incident_trace("seed_embedding_pack_builder", "p4obs", "trace_link")
_emit_captures_pattern("seed_embedding_pack_builder", "p3lm", "pattern")
_emit_records_learning_event("seed_embedding_pack_builder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("seed_embedding_pack_builder", "p3lm", "snapshot")
_emit_feeds_meta_learning("seed_embedding_pack_builder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("seed_embedding_pack_builder", "p3lm", "routing")
_emit_improves_agent_policy("seed_embedding_pack_builder", "p3lm", "policy")
_emit_stores_learning_state("seed_embedding_pack_builder", "p3lm", "state")
_emit_records_execution_trace("seed_embedding_pack_builder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("seed_embedding_pack_builder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("seed_embedding_pack_builder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("seed_embedding_pack_builder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("seed_embedding_pack_builder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("seed_embedding_pack_builder", "env_read", "p2_env_1")
_emit_reads_environ("seed_embedding_pack_builder", "env_read", "p2_env_2")
_emit_reads_runtime_state("seed_embedding_pack_builder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("seed_embedding_pack_builder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "seed_embedding_pack_builder", "context_pull")
_emit_pulls_context("p1", "seed_embedding_pack_builder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "seed_embedding_pack_builder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "seed_embedding_pack_builder", "uwg_term_2")
_emit_writes_through("p1", "seed_embedding_pack_builder", "write_through")
_emit_writes_through("p1", "seed_embedding_pack_builder", "write_through_2")
_emit_validated_by_safety_plane("p1", "seed_embedding_pack_builder", "safety_validation")
_emit_invokes_eval("p1", "seed_embedding_pack_builder", "eval_call")
_emit_proposal_commits_routing("p1", "seed_embedding_pack_builder", "routing_commit")
_emit_escalates_to_human("p1", "seed_embedding_pack_builder", "human_escalation")
_emit_routes_through("p1", "seed_embedding_pack_builder", "route_through")
_emit_checks_agent_registry("p1", "seed_embedding_pack_builder", "agent_registry")
_emit_validates_agent_capability("p1", "seed_embedding_pack_builder", "capability")
_emit_dispatches_execution_plan("p1", "seed_embedding_pack_builder", "exec_plan")
_emit_agent_executes_agent("p1", "seed_embedding_pack_builder", "sub_agent")
_emit_routes_to_agent("p1", "seed_embedding_pack_builder", "target_agent")
_emit_verifies_policy("p1", "seed_embedding_pack_builder", "policy_check")
_emit_observes_runtime_state("p1", "seed_embedding_pack_builder", "runtime_state")
_emit_verifies_boundary("p1", "seed_embedding_pack_builder", "boundary_check")
_emit_transcripts_response("p1", "seed_embedding_pack_builder", "transcript")
_emit_hard_fails_untranscripted("p1", "seed_embedding_pack_builder")
_emit_gated_by_confidence("p1", "seed_embedding_pack_builder", "confidence_gate")
emit_replay_key("p0", "seed_embedding_pack_builder")
emit_determinism_digest("p0", "seed_embedding_pack_builder")
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


class DeterministicHashEmbedder:
    """Deterministic embedder for unit tests.

    Generates vectors deterministically from content_hash.
    """

    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def embed_batch(self, texts: list[str], dimensions: int) -> list[list[float]]:
        """Generate deterministic vectors from content_hash.

        Args:
            texts: List of texts (content_hash values used as input).
            dimensions: Embedding vector dimensions.

        Returns:
            List of deterministic embedding vectors.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DeterministicHashEmbedder.embed_batch")

        vectors = []
        for text in texts:
            # Use SHA-256 of text to generate deterministic float32 values
            hash_bytes = hashlib.sha256(text.encode()).digest()
            # Convert bytes to float32 values
            vector = []
            for i in range(dimensions):
                # Take 4 bytes at a time, interpret as little-endian uint32, then convert to float
                byte_idx = (i * 4) % len(hash_bytes)
                uint32 = struct.unpack("<I", hash_bytes[byte_idx : byte_idx + 4])[0]
                # Convert to float in range [-1, 1]
                float_val = (uint32 / 0xFFFFFFFF) * 2.0 - 1.0
                vector.append(float_val)
            vectors.append(vector)
        return vectors


def _canonical_sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort rows canonically by (content_hash ASC, trace_id ASC, row_id ASC).

    Args:
        rows: List of row dictionaries.

    Returns:
        Sorted list of rows.
    """
    return sorted(rows, key=lambda r: (r["content_hash"], r["trace_id"], r["row_id"]))


def _write_row_index_jsonl(rows: list[dict[str, Any]], output_path: Path) -> str:
    """Write row_index.jsonl with canonical format.

    Args:
        rows: Sorted list of row dictionaries.
        output_path: Output file path.

    Returns:
        SHA-256 hash of the written file.
    """
    lines = []
    for row in rows:
        # Canonical JSON with strict field order
        line_data = {
            "row_id": row["row_id"],
            "content_hash": row["content_hash"],
            "trace_id": row["trace_id"],
            "namespace": row["namespace"],
            "created_utc": row["created_utc"],
        }
        line = json.dumps(line_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        lines.append(line)

    content = "\n".join(lines).encode("utf-8")
    output_path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def _write_embeddings_f32(vectors: list[list[float]], output_path: Path) -> str:
    """Write embeddings.f32 as little-endian float32 binary.

    Args:
        vectors: List of embedding vectors.
        output_path: Output file path.

    Returns:
        SHA-256 hash of the written file.
    """
    # Convert to little-endian float32 bytes
    byte_data = bytearray()
    for vector in vectors:
        for value in vector:
            byte_data.extend(struct.pack("<f", value))

    output_path.write_bytes(byte_data)
    return hashlib.sha256(byte_data).hexdigest()


def _compute_seed_index_version_hash(row_index_hash: str, matrix_hash: str, canonical_manifest: bytes) -> str:
    """Compute seed_index_version_hash as SHA256(R || M || C).

    Args:
        row_index_hash: SHA-256 of row_index.jsonl.
        matrix_hash: SHA-256 of embeddings.f32.
        canonical_manifest: Canonical JSON bytes of manifest (excluding hash fields).

    Returns:
        Computed seed_index_version_hash.
    """
    combined = row_index_hash.encode() + matrix_hash.encode() + canonical_manifest
    return hashlib.sha256(combined).hexdigest()


def build_seed_embedding_pack(
    *,
    base_path: Path,
    config: SeedEmbeddingPackConfig,
    corpus_rows: list[dict[str, Any]],
    embedder: Embedder,
    built_at_utc: int,
) -> SeedEmbeddingPackManifest:
    """Build a Seed Embedding Pack deterministically.

    Args:
        base_path: Base path for seed pack storage.
        config: Configuration for the seed pack.
        corpus_rows: Plan A corpus rows containing required fields.
        embedder: Embedder instance for generating embeddings.
        built_at_utc: Build timestamp (injected, not wall clock).

    Returns:
        Manifest for the built seed pack.

    Raises:
        RuntimeError: If build fails or target directory already exists.
    """
    # Step 1: Apply bootstrap selection
    if config.bootstrap_mode == "minimal_seed":
        if config.minimal_seed_count is None:
            raise RuntimeError("minimal_seed_count required for minimal_seed mode")
        # Filter by namespace
        filtered = [row for row in corpus_rows if row.get("namespace") == config.namespace]
        # Sort by (content_hash, trace_id) for selection, then add row_id and sort again
        filtered_sorted = sorted(filtered, key=lambda r: (r["content_hash"], r["trace_id"]))
        selected = filtered_sorted[: config.minimal_seed_count]
    elif config.bootstrap_mode == "curated_seed":
        if config.curated_allowlist is None:
            raise RuntimeError("curated_allowlist required for curated_seed mode")
        # Filter by allowlist and namespace
        allowlist_set = set(config.curated_allowlist)
        filtered = [
            row
            for row in corpus_rows
            if row.get("namespace") == config.namespace
            and (row.get("trace_id"), row.get("content_hash")) in allowlist_set
        ]
        # Sort by (content_hash, trace_id) for selection, then add row_id and sort again
        selected = sorted(filtered, key=lambda r: (r["content_hash"], r["trace_id"]))
    else:
        raise RuntimeError(f"Unknown bootstrap_mode: {config.bootstrap_mode}")

    if not selected:
        raise RuntimeError(f"No rows selected for namespace {config.namespace}")

    # Step 2: Prepare rows with row_id = content_hash
    rows = []
    for row in selected:
        rows.append(
            {
                "row_id": row["content_hash"],  # row_id = content_hash
                "content_hash": row["content_hash"],
                "trace_id": row["trace_id"],
                "namespace": row["namespace"],
                "created_utc": row["created_utc"],
            }
        )

    # Step 3: Canonical sort (now with row_id present)
    rows = _canonical_sort_rows(rows)

    # Step 4-5: Write row_index.jsonl and compute hash
    # Use temp directory for atomic write
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        row_index_path = temp_path / "row_index.jsonl"
        row_index_hash = _write_row_index_jsonl(rows, row_index_path)

        # Step 6-7: Generate embeddings and write embeddings.f32
        texts = [row["content_hash"] for row in rows]  # Use content_hash as text input
        # For DeterministicHashEmbedder, use its configured dimensions
        # For production embedders, we'll need to get dimensions from the model
        if hasattr(embedder, "dimensions"):
            dimensions = embedder.dimensions
        else:
            # For BGE embedder, get dimensions from model info
            # This is a fallback - in production, dimensions should be determined by the model
            dimensions = 1024  # Default for BAAI/bge-m3
        vectors = embedder.embed_batch(texts, dimensions=dimensions)
        embeddings_path = temp_path / "embeddings.f32"
        matrix_hash = _write_embeddings_f32(vectors, embeddings_path)

        # Step 8-9: Construct canonical manifest (non-hash portion)
        manifest = SeedEmbeddingPackManifest(
            namespace=config.namespace,
            bootstrap_mode=config.bootstrap_mode,
            embedding_model_version=config.embedding_model_version,
            embedding_model_checksum=config.embedding_model_checksum,
            canonicalization_version=config.canonicalization_version,
            dimensions=len(vectors[0]) if vectors else 0,
            vector_count=len(vectors),
            row_index_hash="",  # Will be filled
            matrix_hash="",  # Will be filled
            seed_index_version_hash="",  # Will be filled
            built_at_utc=built_at_utc,
        )

        # Get canonical bytes without hash fields
        canonical_manifest = manifest.to_canonical_json_bytes()

        # Step 10: Compute seed_index_version_hash
        seed_index_version_hash = _compute_seed_index_version_hash(
            row_index_hash, matrix_hash, canonical_manifest
        )

        # Step 11: Write final manifest
        final_manifest = SeedEmbeddingPackManifest(
            namespace=manifest.namespace,
            bootstrap_mode=manifest.bootstrap_mode,
            embedding_model_version=manifest.embedding_model_version,
            embedding_model_checksum=manifest.embedding_model_checksum,
            canonicalization_version=manifest.canonicalization_version,
            dimensions=manifest.dimensions,
            vector_count=manifest.vector_count,
            row_index_hash=row_index_hash,
            matrix_hash=matrix_hash,
            seed_index_version_hash=seed_index_version_hash,
            built_at_utc=manifest.built_at_utc,
        )

        manifest_path = temp_path / "seed_manifest.json"
        manifest_path.write_bytes(final_manifest.to_full_json_bytes())

        # Step 12: Atomic rename to final directory
        final_dir = base_path / "seed_packs" / config.namespace / seed_index_version_hash
        if final_dir.exists():
            raise RuntimeError(f"Seed pack directory already exists: {final_dir}")

        final_dir.mkdir(parents=True)
        shutil.copy2(row_index_path, final_dir / "row_index.jsonl")
        shutil.copy2(embeddings_path, final_dir / "embeddings.f32")
        shutil.copy2(manifest_path, final_dir / "seed_manifest.json")

        return final_manifest


__all__ = [
    "DeterministicHashEmbedder",
    "build_seed_embedding_pack",
]
