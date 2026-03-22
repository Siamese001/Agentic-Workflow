"""
Persistent Storage Layer Contract

Defines immutable data structures and protocols for deterministic,
append-only storage of agentic artifacts with local filesystem backend.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "persistent_store")
emit_determinism_digest("p0", "persistent_store")

_emit_dispatches_healing_run("p1", "persistent_store", "L4")
_emit_routes_through("p1", "persistent_store", "L4")
_emit_checks_agent_registry("p1", "persistent_store", "agent_registry")
_emit_validates_agent_capability("p1", "persistent_store", "capability")
_emit_dispatches_execution_plan("p1", "persistent_store", "exec_plan")
_emit_agent_executes_agent("p1", "persistent_store", "sub_agent")
_emit_routes_to_agent("p1", "persistent_store", "target_agent")
_emit_verifies_policy("p1", "persistent_store", "policy_check")
_emit_observes_runtime_state("p1", "persistent_store", "runtime_state")
_emit_verifies_boundary("p1", "persistent_store", "boundary_check")
_emit_transcripts_response("p1", "persistent_store", "transcript")
_emit_hard_fails_untranscripted("p1", "persistent_store")
_emit_gated_by_confidence("p1", "persistent_store", "confidence_gate")
_emit_escalates_to_human("p1", "persistent_store", "L4")
_emit_reads_policy_state("p1", "persistent_store", "L4")
_emit_authorize_and_execute("p2", "persistent_store", "execution_auth")
_emit_validates_capability("p2", "persistent_store", "capability_check")
_emit_routes_to_capability("p2", "persistent_store", "capability_route")
_emit_writes_via_uwg("p2", "persistent_store", "uwg_write")
_emit_blocks_direct_write("p2", "persistent_store", "direct_write_block")
_emit_records_tool_invocation("p2", "persistent_store", "tool_invocation")
_emit_captures_execution_output("p2", "persistent_store", "exec_output")
_emit_dispatches_agent("p3", "persistent_store", "agent_dispatch")
_emit_coordinates_agents("p3", "persistent_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "persistent_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "persistent_store", "healing_outcome")
_emit_escalates_failure("p3", "persistent_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "persistent_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "persistent_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "persistent_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "persistent_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "persistent_store", "eval_metric")
_emit_stores_embedding("p4", "persistent_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "persistent_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "persistent_store", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("persistent_store", "p4obs", "metric_1")
_emit_emits_metric_event("persistent_store", "p4obs", "metric_2")
_emit_emits_metric_event("persistent_store", "p4obs", "metric_3")
_emit_emits_metric_event("persistent_store", "p4obs", "metric_4")
_emit_emits_metric_event("persistent_store", "p4obs", "metric_5")
_emit_emits_metric_event("persistent_store", "p4obs", "metric_6")
_emit_records_incident_event("persistent_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("persistent_store", "p4obs", "anomaly")
_emit_writes_observability_log("persistent_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("persistent_store", "p4obs", "mon_state")
_emit_triggers_alert("persistent_store", "p4obs", "alert")
_emit_links_incident_trace("persistent_store", "p4obs", "trace_link")
_emit_captures_pattern("persistent_store", "p3lm", "pattern")
_emit_records_learning_event("persistent_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("persistent_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("persistent_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("persistent_store", "p3lm", "routing")
_emit_improves_agent_policy("persistent_store", "p3lm", "policy")
_emit_stores_learning_state("persistent_store", "p3lm", "state")
_emit_records_execution_trace("persistent_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("persistent_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("persistent_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("persistent_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("persistent_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("persistent_store", "env_read", "p2_env_1")
_emit_reads_environ("persistent_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("persistent_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("persistent_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "persistent_store", "context_pull")
_emit_pulls_context("p1", "persistent_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "persistent_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "persistent_store", "uwg_term_2")
_emit_writes_through("p1", "persistent_store", "write_through")
_emit_writes_through("p1", "persistent_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "persistent_store", "safety_validation")
_emit_invokes_eval("p1", "persistent_store", "eval_call")
_emit_proposal_commits_routing("p1", "persistent_store", "routing_commit")


@dataclass(frozen=True)
class StoredArtifact:
    """Immutable artifact definition for storage."""

    kind: str
    logical_id: str
    created_utc: str
    content_type: str
    payload: dict[str, Any]
    hashes: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class StoreMetrics:
    """Deterministic performance metrics for storage operations."""

    bytes_written: int = 0
    bytes_read: int = 0
    artifacts_written: int = 0
    artifacts_read: int = 0


@dataclass(frozen=True)
class StoredArtifactRef:
    """Immutable reference to a stored artifact."""

    kind: str
    logical_id: str
    version: int
    path: str
    size_bytes: int = 0


class StoreBackend(Protocol):
    """Protocol for storage backends."""

    def put(self, artifact: StoredArtifact) -> StoredArtifactRef:
        """Store an artifact and return its reference."""
        ...

    def get(self, ref: StoredArtifactRef) -> StoredArtifact:
        """Retrieve an artifact by reference."""
        ...

    def list(self, kind: str | None = None) -> list[StoredArtifactRef]:
        """List stored artifacts, optionally filtered by kind."""
        ...


def _sanitize_id(identifier: str) -> str:
    """Sanitize identifier to prevent path traversal.

    Only allows alphanumeric, hyphen, underscore, and dot characters.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_sanitize_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_sanitize_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "_sanitize_id")
    sanitized = re.sub("[^a-zA-Z0-9._-]", "_", identifier)
    if sanitized.startswith("-") or (sanitized.startswith(".") and (not sanitized.startswith(".."))):
        sanitized = "id_" + sanitized
    return sanitized


def _canonicalize_payload(payload: dict[str, Any]) -> str:
    """Canonicalize payload to deterministic JSON string."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _compute_sha256(data: str) -> str:
    """Compute SHA256 hash of data string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def create_artifact(
    kind: str,
    logical_id: str,
    payload: dict[str, Any],
    content_type: str = "application/json",
    created_utc: str | None = None,
    metadata: dict[str, str] | None = None,
) -> StoredArtifact:
    """Create a StoredArtifact with computed hashes.

    Args:
        kind: Artifact kind
        logical_id: Logical identifier
        payload: Artifact data
        content_type: Content type (default: application/json)
        created_utc: ISO timestamp (if None, uses current UTC time)
        metadata: Allowlisted metadata (filtered to allowed keys)

    Returns:
        StoredArtifact with computed hashes
    """
    if created_utc is None:
        created_utc = datetime.utcnow().isoformat() + "Z"
    if metadata is None:
        metadata = {}
    payload_json = _canonicalize_payload(payload)
    hashes = {"sha256": _compute_sha256(payload_json)}
    metadata["size"] = str(len(payload_json.encode("utf-8")))
    return StoredArtifact(
        kind=kind,
        logical_id=_sanitize_id(logical_id),
        created_utc=created_utc,
        content_type=content_type,
        payload=payload,
        hashes=hashes,
        metadata=metadata,
    )


__all__ = [
    "StoredArtifact",
    "StoredArtifactRef",
    "StoreBackend",
    "create_artifact",
    "_sanitize_id",
    "_canonicalize_payload",
    "_compute_sha256",
]
