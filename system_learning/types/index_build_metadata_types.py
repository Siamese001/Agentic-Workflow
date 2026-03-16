"""IndexBuildMetadata type for Plan A deterministic index builds.

This type is consumed by Plan B as part of the EmbeddingSearchProvider protocol.
All fields are frozen and ASCII-only for deterministic serialization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

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

_emit_applies_guardrail("p0", "index_build_metadata_types", "p0_governance")
_emit_reads_policy_state("p0", "index_build_metadata_types", "policy_binding")
_emit_snapshots_state("p0", "index_build_metadata_types", "state_snapshot")
emit_replay_key("p0", "index_build_metadata_types")
emit_determinism_digest("p0", "index_build_metadata_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "index_build_metadata_types", "execution_auth")
_emit_validates_capability("p2", "index_build_metadata_types", "capability_check")
_emit_routes_to_capability("p2", "index_build_metadata_types", "capability_route")
_emit_writes_via_uwg("p2", "index_build_metadata_types", "uwg_write")
_emit_blocks_direct_write("p2", "index_build_metadata_types", "direct_write_block")
_emit_records_tool_invocation("p2", "index_build_metadata_types", "tool_invocation")
_emit_captures_execution_output("p2", "index_build_metadata_types", "exec_output")
_emit_dispatches_agent("p3", "index_build_metadata_types", "agent_dispatch")
_emit_coordinates_agents("p3", "index_build_metadata_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "index_build_metadata_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "index_build_metadata_types", "healing_outcome")
_emit_escalates_failure("p3", "index_build_metadata_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "index_build_metadata_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "index_build_metadata_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "index_build_metadata_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "index_build_metadata_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "index_build_metadata_types", "eval_metric")
_emit_stores_embedding("p4", "index_build_metadata_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "index_build_metadata_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "index_build_metadata_types", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class IndexBuildMetadata:
    """Stable contract consumed by Plan B.

    INVARIANT: If embedding_model_version or embedding_model_checksum changes,
    the index is invalid and must be fully rebuilt before reads are permitted.
    """

    index_id: str
    faiss_version: str
    build_seed: int
    canonicalization_version: str
    embedding_model_version: str
    embedding_model_checksum: str
    built_at_utc: int
    index_version_hash: str
    vector_count: int
    dimension: int

    def to_canonical_json_bytes(self) -> bytes:
        """Return deterministic ASCII-only JSON bytes.

        Uses canonical JSON: keys sorted ASC, no whitespace, ASCII encoding.
        Result is suitable for hashing and replay determinism.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "IndexBuildMetadata.to_canonical_json_bytes")

        data = {
            "index_id": self.index_id,
            "faiss_version": self.faiss_version,
            "build_seed": self.build_seed,
            "canonicalization_version": self.canonicalization_version,
            "embedding_model_version": self.embedding_model_version,
            "embedding_model_checksum": self.embedding_model_checksum,
            "built_at_utc": self.built_at_utc,
            "index_version_hash": self.index_version_hash,
            "vector_count": self.vector_count,
            "dimension": self.dimension,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


__all__ = ["IndexBuildMetadata"]
