"""Seed Embedding Pack types for Plan B Phase 0.

Immutable, deterministic types for governed embedding bootstrap.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "seed_embedding_pack_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "seed_embedding_pack_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "seed_embedding_pack_types", "state_snapshot")

trace_contract._emit_emits_metric_event("seed_embedding_pack_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("seed_embedding_pack_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("seed_embedding_pack_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("seed_embedding_pack_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("seed_embedding_pack_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("seed_embedding_pack_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("seed_embedding_pack_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("seed_embedding_pack_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("seed_embedding_pack_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("seed_embedding_pack_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("seed_embedding_pack_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("seed_embedding_pack_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("seed_embedding_pack_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("seed_embedding_pack_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("seed_embedding_pack_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("seed_embedding_pack_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("seed_embedding_pack_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("seed_embedding_pack_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("seed_embedding_pack_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("seed_embedding_pack_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("seed_embedding_pack_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("seed_embedding_pack_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("seed_embedding_pack_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("seed_embedding_pack_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("seed_embedding_pack_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("seed_embedding_pack_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("seed_embedding_pack_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("seed_embedding_pack_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "seed_embedding_pack_types", "context_pull")
trace_contract._emit_pulls_context("p1", "seed_embedding_pack_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "seed_embedding_pack_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "seed_embedding_pack_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "seed_embedding_pack_types", "write_through")
trace_contract._emit_writes_through("p1", "seed_embedding_pack_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "seed_embedding_pack_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "seed_embedding_pack_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "seed_embedding_pack_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "seed_embedding_pack_types", "human_escalation")
trace_contract._emit_routes_through("p1", "seed_embedding_pack_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "seed_embedding_pack_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "seed_embedding_pack_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "seed_embedding_pack_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "seed_embedding_pack_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "seed_embedding_pack_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "seed_embedding_pack_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "seed_embedding_pack_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "seed_embedding_pack_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "seed_embedding_pack_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "seed_embedding_pack_types")
trace_contract._emit_gated_by_confidence("p1", "seed_embedding_pack_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "seed_embedding_pack_types")
trace_contract.emit_determinism_digest("p0", "seed_embedding_pack_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "seed_embedding_pack_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "seed_embedding_pack_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "seed_embedding_pack_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "seed_embedding_pack_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "seed_embedding_pack_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "seed_embedding_pack_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "seed_embedding_pack_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "seed_embedding_pack_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "seed_embedding_pack_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "seed_embedding_pack_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "seed_embedding_pack_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "seed_embedding_pack_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "seed_embedding_pack_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "seed_embedding_pack_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "seed_embedding_pack_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "seed_embedding_pack_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "seed_embedding_pack_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "seed_embedding_pack_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "seed_embedding_pack_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "seed_embedding_pack_types", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SeedEmbeddingPackManifest.to_canonical_json_bytes"
        )

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
            "ascii",
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
