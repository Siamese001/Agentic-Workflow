"""Seed Embedding Pack types for Plan B Phase 0.

Immutable, deterministic types for governed embedding bootstrap.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

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

_emit_applies_guardrail("p0", "seed_embedding_pack_types", "p0_governance")
_emit_reads_policy_state("p0", "seed_embedding_pack_types", "policy_binding")
_emit_snapshots_state("p0", "seed_embedding_pack_types", "state_snapshot")
emit_replay_key("p0", "seed_embedding_pack_types")
emit_determinism_digest("p0", "seed_embedding_pack_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "seed_embedding_pack_types", "execution_auth")
_emit_validates_capability("p2", "seed_embedding_pack_types", "capability_check")
_emit_routes_to_capability("p2", "seed_embedding_pack_types", "capability_route")
_emit_writes_via_uwg("p2", "seed_embedding_pack_types", "uwg_write")
_emit_blocks_direct_write("p2", "seed_embedding_pack_types", "direct_write_block")
_emit_records_tool_invocation("p2", "seed_embedding_pack_types", "tool_invocation")
_emit_captures_execution_output("p2", "seed_embedding_pack_types", "exec_output")
_emit_dispatches_agent("p3", "seed_embedding_pack_types", "agent_dispatch")
_emit_coordinates_agents("p3", "seed_embedding_pack_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "seed_embedding_pack_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "seed_embedding_pack_types", "healing_outcome")
_emit_escalates_failure("p3", "seed_embedding_pack_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "seed_embedding_pack_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "seed_embedding_pack_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "seed_embedding_pack_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "seed_embedding_pack_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "seed_embedding_pack_types", "eval_metric")
_emit_stores_embedding("p4", "seed_embedding_pack_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "seed_embedding_pack_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "seed_embedding_pack_types", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackManifest:
    """Immutable manifest for a Seed Embedding Pack.

    All hash fields are computed AFTER canonical serialization of non-hash material.
    built_at_utc is metadata-only and excluded from hash computation.
    """

    namespace: str
    bootstrap_mode: Literal["minimal_seed", "curated_seed"]
    embedding_model_version: str
    embedding_model_checksum: str
    canonicalization_version: str
    dimensions: int
    vector_count: int
    row_index_hash: str
    matrix_hash: str
    seed_index_version_hash: str
    built_at_utc: int

    def to_canonical_json_bytes(self) -> bytes:
        """Serialize manifest to canonical JSON bytes.

        Returns:
            ASCII-only canonical JSON bytes.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SeedEmbeddingPackManifest.to_canonical_json_bytes")

        canonical_data = {
            "namespace": self.namespace,
            "bootstrap_mode": self.bootstrap_mode,
            "embedding_model_version": self.embedding_model_version,
            "embedding_model_checksum": self.embedding_model_checksum,
            "canonicalization_version": self.canonicalization_version,
            "dimensions": self.dimensions,
            "vector_count": self.vector_count,
        }
        return json.dumps(canonical_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )

    def to_full_json_bytes(self) -> bytes:
        """Serialize full manifest including hash fields and metadata.

        Returns:
            ASCII-only JSON bytes with all fields.
        """
        data = {
            "namespace": self.namespace,
            "bootstrap_mode": self.bootstrap_mode,
            "embedding_model_version": self.embedding_model_version,
            "embedding_model_checksum": self.embedding_model_checksum,
            "canonicalization_version": self.canonicalization_version,
            "dimensions": self.dimensions,
            "vector_count": self.vector_count,
            "row_index_hash": self.row_index_hash,
            "matrix_hash": self.matrix_hash,
            "seed_index_version_hash": self.seed_index_version_hash,
            "built_at_utc": self.built_at_utc,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackConfig:
    """Configuration for building a Seed Embedding Pack."""

    namespace: str
    bootstrap_mode: Literal["minimal_seed", "curated_seed"]
    minimal_seed_count: int | None = None
    curated_allowlist: list[tuple[str, str]] | None = None
    embedding_model_version: str = "v1"
    embedding_model_checksum: str = "0" * 64
    canonicalization_version: str = "v1"


__all__ = ["SeedEmbeddingPackManifest", "SeedEmbeddingPackConfig"]
