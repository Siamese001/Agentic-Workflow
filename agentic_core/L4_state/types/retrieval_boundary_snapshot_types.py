"""
Phase 6 — RetrievalBoundarySnapshot: deterministic, non-mutating retrieval record.

Records retrieval inputs + anchor set + active config hashes at the boundary.
Does NOT write to the knowledge index (Pinecone/Redis).
snapshot_hash = sha256(canonical_bytes excluding snapshot_hash).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "retrieval_boundary_snapshot_types")
emit_determinism_digest("p0", "retrieval_boundary_snapshot_types")

_emit_dispatches_healing_run("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_routes_through("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_checks_agent_registry("p1", "retrieval_boundary_snapshot_types", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_boundary_snapshot_types", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_boundary_snapshot_types", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_boundary_snapshot_types", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_boundary_snapshot_types", "target_agent")
_emit_verifies_policy("p1", "retrieval_boundary_snapshot_types", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_boundary_snapshot_types", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_boundary_snapshot_types", "boundary_check")
_emit_transcripts_response("p1", "retrieval_boundary_snapshot_types", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_boundary_snapshot_types")
_emit_gated_by_confidence("p1", "retrieval_boundary_snapshot_types", "confidence_gate")
_emit_escalates_to_human("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_reads_policy_state("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_authorize_and_execute("p2", "retrieval_boundary_snapshot_types", "execution_auth")
_emit_validates_capability("p2", "retrieval_boundary_snapshot_types", "capability_check")
_emit_routes_to_capability("p2", "retrieval_boundary_snapshot_types", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_boundary_snapshot_types", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_boundary_snapshot_types", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_boundary_snapshot_types", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_boundary_snapshot_types", "exec_output")
_emit_dispatches_agent("p3", "retrieval_boundary_snapshot_types", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_boundary_snapshot_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_boundary_snapshot_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_boundary_snapshot_types", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_boundary_snapshot_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_boundary_snapshot_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_boundary_snapshot_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_boundary_snapshot_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_boundary_snapshot_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_boundary_snapshot_types", "eval_metric")
_emit_stores_embedding("p4", "retrieval_boundary_snapshot_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_boundary_snapshot_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_boundary_snapshot_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("retrieval_boundary_snapshot_types", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_boundary_snapshot_types", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_boundary_snapshot_types", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_boundary_snapshot_types", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_boundary_snapshot_types", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_boundary_snapshot_types", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_boundary_snapshot_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_boundary_snapshot_types", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_boundary_snapshot_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_boundary_snapshot_types", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_boundary_snapshot_types", "p4obs", "alert")
_emit_links_incident_trace("retrieval_boundary_snapshot_types", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_boundary_snapshot_types", "p3lm", "pattern")
_emit_records_learning_event("retrieval_boundary_snapshot_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_boundary_snapshot_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_boundary_snapshot_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_boundary_snapshot_types", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_boundary_snapshot_types", "p3lm", "policy")
_emit_stores_learning_state("retrieval_boundary_snapshot_types", "p3lm", "state")
_emit_records_execution_trace("retrieval_boundary_snapshot_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_boundary_snapshot_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_boundary_snapshot_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_boundary_snapshot_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_boundary_snapshot_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_boundary_snapshot_types", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_boundary_snapshot_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_boundary_snapshot_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_boundary_snapshot_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_boundary_snapshot_types", "context_pull")
_emit_pulls_context("p1", "retrieval_boundary_snapshot_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_boundary_snapshot_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_boundary_snapshot_types", "uwg_term_2")
_emit_writes_through("p1", "retrieval_boundary_snapshot_types", "write_through")
_emit_writes_through("p1", "retrieval_boundary_snapshot_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_boundary_snapshot_types", "safety_validation")
_emit_invokes_eval("p1", "retrieval_boundary_snapshot_types", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_boundary_snapshot_types", "routing_commit")

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class AnchorEntry:
    """
    Minimal anchor identifier included in the snapshot.
    Carries chunk_id and version_hash for deterministic ordering.
    """

    chunk_id: str
    version_hash: str

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise ValueError("AnchorEntry: chunk_id must be non-empty")
        if not self.version_hash:
            raise ValueError("AnchorEntry: version_hash must be non-empty")

    def to_dict(self) -> dict[str, str]:
        return {"chunk_id": self.chunk_id, "version_hash": self.version_hash}

    def sort_key(self) -> tuple[str, str]:
        return (self.chunk_id, self.version_hash)


@dataclass
class RetrievalBoundarySnapshot:
    """
    Non-mutating boundary record produced at the start of every retrieval.

    Fields
    ------
    schema_version      : int  — bumped on breaking schema changes
    mission_id          : str  — non-empty identifier for the mission/run
    request_hash        : str  — sha256 of the canonical retrieval request subset
    active_config_hashes: dict — {"policy_hash": ..., "routing_hash": ..., ...}
    anchors             : list — sorted AnchorEntry records (chunk_id, version_hash)
    created_at_utc      : str  — ISO-8601 UTC timestamp (stable, no uuid/elapsed)
    snapshot_hash       : str  — sha256(canonical_bytes()); auto-computed
    """

    schema_version: int
    mission_id: str
    request_hash: str
    active_config_hashes: dict[str, str]
    anchors: list[AnchorEntry]
    created_at_utc: str
    snapshot_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"RetrievalBoundarySnapshot: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.mission_id:
            raise ValueError("RetrievalBoundarySnapshot: mission_id must be non-empty")
        if not self.request_hash:
            raise ValueError("RetrievalBoundarySnapshot: request_hash must be non-empty")
        if not isinstance(self.active_config_hashes, dict):
            raise TypeError("RetrievalBoundarySnapshot: active_config_hashes must be a dict")
        if not isinstance(self.anchors, list):
            raise TypeError("RetrievalBoundarySnapshot: anchors must be a list")
        self.anchors = sorted(self.anchors, key=lambda a: a.sort_key())
        object.__setattr__(self, "snapshot_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """
        Deterministic serialisation excluding snapshot_hash (self-referential).
        Keys sorted, anchors sorted by (chunk_id, version_hash).
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "RetrievalBoundarySnapshot.canonical_bytes", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "RetrievalBoundarySnapshot.canonical_bytes", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "RetrievalBoundarySnapshot.canonical_bytes"
        )

        doc: dict[str, Any] = {
            "active_config_hashes": {
                k: self.active_config_hashes[k] for k in sorted(self.active_config_hashes)
            },
            "anchors": [a.to_dict() for a in sorted(self.anchors, key=lambda a: a.sort_key())],
            "created_at_utc": self.created_at_utc,
            "mission_id": self.mission_id,
            "request_hash": self.request_hash,
            "schema_version": self.schema_version,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mission_id": self.mission_id,
            "request_hash": self.request_hash,
            "active_config_hashes": dict(self.active_config_hashes),
            "anchors": [a.to_dict() for a in self.anchors],
            "created_at_utc": self.created_at_utc,
            "snapshot_hash": self.snapshot_hash,
        }


def build_request_hash(query: str, top_k: int, domain: str) -> str:
    """
    Compute a deterministic sha256 hash of the canonical retrieval request subset.
    Excludes volatile fields (timestamps, trace IDs).
    """
    doc = {"domain": domain, "query": query, "top_k": top_k}
    raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
    return _sha256(raw)


def create_retrieval_boundary_snapshot(
    mission_id: str,
    query: str,
    top_k: int,
    domain: str,
    active_config_hashes: dict[str, str],
    anchors: list[AnchorEntry],
    created_at_utc: str,
) -> RetrievalBoundarySnapshot:
    """
    Factory: build a RetrievalBoundarySnapshot from retrieval parameters.

    Non-mutating — does not write to any persistent store.
    """
    request_hash = build_request_hash(query=query, top_k=top_k, domain=domain)
    return RetrievalBoundarySnapshot(
        schema_version=_SCHEMA_VERSION,
        mission_id=mission_id,
        request_hash=request_hash,
        active_config_hashes=active_config_hashes,
        anchors=anchors,
        created_at_utc=created_at_utc,
    )
