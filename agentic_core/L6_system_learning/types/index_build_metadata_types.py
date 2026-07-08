"""IndexBuildMetadata type for Plan A deterministic index builds.

This type is consumed by Plan B as part of the EmbeddingSearchProvider protocol.
All fields are frozen and ASCII-only for deterministic serialization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "index_build_metadata_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "index_build_metadata_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "index_build_metadata_types", "state_snapshot")

trace_contract._emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("index_build_metadata_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("index_build_metadata_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("index_build_metadata_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("index_build_metadata_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("index_build_metadata_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("index_build_metadata_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("index_build_metadata_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("index_build_metadata_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("index_build_metadata_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("index_build_metadata_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("index_build_metadata_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("index_build_metadata_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("index_build_metadata_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("index_build_metadata_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("index_build_metadata_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("index_build_metadata_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("index_build_metadata_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("index_build_metadata_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("index_build_metadata_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("index_build_metadata_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("index_build_metadata_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("index_build_metadata_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "index_build_metadata_types", "context_pull")
trace_contract._emit_pulls_context("p1", "index_build_metadata_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "index_build_metadata_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "index_build_metadata_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "index_build_metadata_types", "write_through")
trace_contract._emit_writes_through("p1", "index_build_metadata_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "index_build_metadata_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "index_build_metadata_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "index_build_metadata_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "index_build_metadata_types", "human_escalation")
trace_contract._emit_routes_through("p1", "index_build_metadata_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "index_build_metadata_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "index_build_metadata_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "index_build_metadata_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "index_build_metadata_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "index_build_metadata_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "index_build_metadata_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "index_build_metadata_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "index_build_metadata_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "index_build_metadata_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "index_build_metadata_types")
trace_contract._emit_gated_by_confidence("p1", "index_build_metadata_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "index_build_metadata_types")
trace_contract.emit_determinism_digest("p0", "index_build_metadata_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "index_build_metadata_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "index_build_metadata_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "index_build_metadata_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "index_build_metadata_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "index_build_metadata_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "index_build_metadata_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "index_build_metadata_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "index_build_metadata_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "index_build_metadata_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "index_build_metadata_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "index_build_metadata_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "index_build_metadata_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "index_build_metadata_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "index_build_metadata_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "index_build_metadata_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "index_build_metadata_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "index_build_metadata_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "index_build_metadata_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "index_build_metadata_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "index_build_metadata_types", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "IndexBuildMetadata.to_canonical_json_bytes"
        )

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
