"""IndexBuildMetadata type for Plan A deterministic index builds.

This type is consumed by Plan B as part of the EmbeddingSearchProvider protocol.
All fields are frozen and ASCII-only for deterministic serialization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

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

_emit_applies_guardrail("p0", "index_build_metadata_types", "p0_governance")
_emit_reads_policy_state("p0", "index_build_metadata_types", "policy_binding")
_emit_snapshots_state("p0", "index_build_metadata_types", "state_snapshot")
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

_emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_1")
_emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_2")
_emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_3")
_emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_4")
_emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_5")
_emit_emits_metric_event("index_build_metadata_types", "p4obs", "metric_6")
_emit_records_incident_event("index_build_metadata_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("index_build_metadata_types", "p4obs", "anomaly")
_emit_writes_observability_log("index_build_metadata_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("index_build_metadata_types", "p4obs", "mon_state")
_emit_triggers_alert("index_build_metadata_types", "p4obs", "alert")
_emit_links_incident_trace("index_build_metadata_types", "p4obs", "trace_link")
_emit_captures_pattern("index_build_metadata_types", "p3lm", "pattern")
_emit_records_learning_event("index_build_metadata_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("index_build_metadata_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("index_build_metadata_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("index_build_metadata_types", "p3lm", "routing")
_emit_improves_agent_policy("index_build_metadata_types", "p3lm", "policy")
_emit_stores_learning_state("index_build_metadata_types", "p3lm", "state")
_emit_records_execution_trace("index_build_metadata_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("index_build_metadata_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("index_build_metadata_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("index_build_metadata_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("index_build_metadata_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("index_build_metadata_types", "env_read", "p2_env_1")
_emit_reads_environ("index_build_metadata_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("index_build_metadata_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("index_build_metadata_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "index_build_metadata_types", "context_pull")
_emit_pulls_context("p1", "index_build_metadata_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "index_build_metadata_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "index_build_metadata_types", "uwg_term_2")
_emit_writes_through("p1", "index_build_metadata_types", "write_through")
_emit_writes_through("p1", "index_build_metadata_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "index_build_metadata_types", "safety_validation")
_emit_invokes_eval("p1", "index_build_metadata_types", "eval_call")
_emit_proposal_commits_routing("p1", "index_build_metadata_types", "routing_commit")
_emit_escalates_to_human("p1", "index_build_metadata_types", "human_escalation")
_emit_routes_through("p1", "index_build_metadata_types", "route_through")
_emit_checks_agent_registry("p1", "index_build_metadata_types", "agent_registry")
_emit_validates_agent_capability("p1", "index_build_metadata_types", "capability")
_emit_dispatches_execution_plan("p1", "index_build_metadata_types", "exec_plan")
_emit_agent_executes_agent("p1", "index_build_metadata_types", "sub_agent")
_emit_routes_to_agent("p1", "index_build_metadata_types", "target_agent")
_emit_verifies_policy("p1", "index_build_metadata_types", "policy_check")
_emit_observes_runtime_state("p1", "index_build_metadata_types", "runtime_state")
_emit_verifies_boundary("p1", "index_build_metadata_types", "boundary_check")
_emit_transcripts_response("p1", "index_build_metadata_types", "transcript")
_emit_hard_fails_untranscripted("p1", "index_build_metadata_types")
_emit_gated_by_confidence("p1", "index_build_metadata_types", "confidence_gate")
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
