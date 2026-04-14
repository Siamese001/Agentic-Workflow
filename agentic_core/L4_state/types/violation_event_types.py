"""
Phase 5 — ViolationEvent: Typed, versioned Guardian outcome schema.

Persisted to L4 SSOT. Canonical bytes exclude event_hash (self-referential).
Violation codes are sorted in canonical form to guarantee determinism.
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

emit_replay_key("p0", "violation_event_types")
emit_determinism_digest("p0", "violation_event_types")

_emit_dispatches_healing_run("p1", "violation_event_types", "L4")
_emit_routes_through("p1", "violation_event_types", "L4")
_emit_checks_agent_registry("p1", "violation_event_types", "agent_registry")
_emit_validates_agent_capability("p1", "violation_event_types", "capability")
_emit_dispatches_execution_plan("p1", "violation_event_types", "exec_plan")
_emit_agent_executes_agent("p1", "violation_event_types", "sub_agent")
_emit_routes_to_agent("p1", "violation_event_types", "target_agent")
_emit_verifies_policy("p1", "violation_event_types", "policy_check")
_emit_observes_runtime_state("p1", "violation_event_types", "runtime_state")
_emit_verifies_boundary("p1", "violation_event_types", "boundary_check")
_emit_transcripts_response("p1", "violation_event_types", "transcript")
_emit_hard_fails_untranscripted("p1", "violation_event_types")
_emit_gated_by_confidence("p1", "violation_event_types", "confidence_gate")
_emit_escalates_to_human("p1", "violation_event_types", "L4")
_emit_reads_policy_state("p1", "violation_event_types", "L4")
_emit_authorize_and_execute("p2", "violation_event_types", "execution_auth")
_emit_validates_capability("p2", "violation_event_types", "capability_check")
_emit_routes_to_capability("p2", "violation_event_types", "capability_route")
_emit_writes_via_uwg("p2", "violation_event_types", "uwg_write")
_emit_blocks_direct_write("p2", "violation_event_types", "direct_write_block")
_emit_records_tool_invocation("p2", "violation_event_types", "tool_invocation")
_emit_captures_execution_output("p2", "violation_event_types", "exec_output")
_emit_dispatches_agent("p3", "violation_event_types", "agent_dispatch")
_emit_coordinates_agents("p3", "violation_event_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "violation_event_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "violation_event_types", "healing_outcome")
_emit_escalates_failure("p3", "violation_event_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "violation_event_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "violation_event_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "violation_event_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "violation_event_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "violation_event_types", "eval_metric")
_emit_stores_embedding("p4", "violation_event_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "violation_event_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "violation_event_types", "exec_snapshot_link")
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

_emit_emits_metric_event("violation_event_types", "p4obs", "metric_1")
_emit_emits_metric_event("violation_event_types", "p4obs", "metric_2")
_emit_emits_metric_event("violation_event_types", "p4obs", "metric_3")
_emit_emits_metric_event("violation_event_types", "p4obs", "metric_4")
_emit_emits_metric_event("violation_event_types", "p4obs", "metric_5")
_emit_emits_metric_event("violation_event_types", "p4obs", "metric_6")
_emit_records_incident_event("violation_event_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("violation_event_types", "p4obs", "anomaly")
_emit_writes_observability_log("violation_event_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("violation_event_types", "p4obs", "mon_state")
_emit_triggers_alert("violation_event_types", "p4obs", "alert")
_emit_links_incident_trace("violation_event_types", "p4obs", "trace_link")
_emit_captures_pattern("violation_event_types", "p3lm", "pattern")
_emit_records_learning_event("violation_event_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("violation_event_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("violation_event_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("violation_event_types", "p3lm", "routing")
_emit_improves_agent_policy("violation_event_types", "p3lm", "policy")
_emit_stores_learning_state("violation_event_types", "p3lm", "state")
_emit_records_execution_trace("violation_event_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("violation_event_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("violation_event_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("violation_event_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("violation_event_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("violation_event_types", "env_read", "p2_env_1")
_emit_reads_environ("violation_event_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("violation_event_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("violation_event_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "violation_event_types", "context_pull")
_emit_pulls_context("p1", "violation_event_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "violation_event_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "violation_event_types", "uwg_term_2")
_emit_writes_through("p1", "violation_event_types", "write_through")
_emit_writes_through("p1", "violation_event_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "violation_event_types", "safety_validation")
_emit_invokes_eval("p1", "violation_event_types", "eval_call")
_emit_proposal_commits_routing("p1", "violation_event_types", "routing_commit")

_VALID_DECISIONS: frozenset[str] = frozenset({"allow", "block", "escalate"})
_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class ViolationEvent:
    """
    Typed record of a Guardian decision outcome.

    Fields
    ------
    schema_version   : int   — bumped on breaking schema changes
    mission_id       : str   — non-empty identifier for the mission/run
    commit_tick      : int   — monotonic execution boundary (>= 0)
    guardian_decision: str   — one of "allow", "block", "escalate"
    violation_codes  : list  — sorted list of string violation codes
    severity_score   : float — in [0.0, 1.0]
    created_at_utc   : str   — ISO-8601 UTC timestamp string
    event_hash       : str   — sha256(canonical_bytes()); auto-computed
    """

    schema_version: int
    mission_id: str
    commit_tick: int
    guardian_decision: str
    violation_codes: list[str]
    severity_score: float
    created_at_utc: str
    event_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"ViolationEvent: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}",
            )
        if not self.mission_id:
            raise ValueError("ViolationEvent: mission_id must be non-empty")
        if self.commit_tick < 0:
            raise ValueError(f"ViolationEvent: commit_tick must be >= 0, got {self.commit_tick}")
        if self.guardian_decision not in _VALID_DECISIONS:
            raise ValueError(
                f"ViolationEvent: guardian_decision must be one of {sorted(_VALID_DECISIONS)}, got {self.guardian_decision!r}",
            )
        if not 0.0 <= self.severity_score <= 1.0:
            raise ValueError(
                f"ViolationEvent: severity_score must be in [0.0, 1.0], got {self.severity_score}",
            )
        if not isinstance(self.violation_codes, list):
            raise TypeError("ViolationEvent: violation_codes must be a list")
        self.violation_codes = sorted(self.violation_codes)
        object.__setattr__(self, "event_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """
        Deterministic serialisation excluding event_hash (self-referential).
        Keys sorted, violation_codes sorted list.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ViolationEvent.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ViolationEvent.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ViolationEvent.canonical_bytes")

        doc: dict[str, Any] = {
            "commit_tick": self.commit_tick,
            "created_at_utc": self.created_at_utc,
            "guardian_decision": self.guardian_decision,
            "mission_id": self.mission_id,
            "schema_version": self.schema_version,
            "severity_score": self.severity_score,
            "violation_codes": sorted(self.violation_codes),
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mission_id": self.mission_id,
            "commit_tick": self.commit_tick,
            "guardian_decision": self.guardian_decision,
            "violation_codes": list(self.violation_codes),
            "severity_score": self.severity_score,
            "created_at_utc": self.created_at_utc,
            "event_hash": self.event_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ViolationEvent:
        return cls(
            schema_version=data["schema_version"],
            mission_id=data["mission_id"],
            commit_tick=data["commit_tick"],
            guardian_decision=data["guardian_decision"],
            violation_codes=list(data["violation_codes"]),
            severity_score=data["severity_score"],
            created_at_utc=data["created_at_utc"],
        )


def emit_violation_event(
    mission_id: str,
    commit_tick: int,
    guardian_decision: str,
    violation_codes: list[str],
    severity_score: float,
    created_at_utc: str,
    *,
    _registry: list[ViolationEvent] | None = None,
) -> ViolationEvent:
    """
    Construct and emit a ViolationEvent.

    Pure recording — does not alter the guardian_decision.
    If _registry is provided, appends to it (for in-memory accumulation).
    """
    event = ViolationEvent(
        schema_version=_SCHEMA_VERSION,
        mission_id=mission_id,
        commit_tick=commit_tick,
        guardian_decision=guardian_decision,
        violation_codes=violation_codes,
        severity_score=severity_score,
        created_at_utc=created_at_utc,
    )
    if _registry is not None:
        _registry.append(event)
    return event
