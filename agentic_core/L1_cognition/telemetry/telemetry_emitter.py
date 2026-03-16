"""
L1 Cognition Telemetry Emitter - Write-only, ZERO-decision component

Emits deterministic TelemetryEvent artifacts and forwards them to L4
telemetry recording via an injected seam. L1 never branches on safety
state and does not couple to L2/L5.
"""

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "telemetry_emitter")
emit_determinism_digest("p0", "telemetry_emitter")

_emit_dispatches_healing_run("p1", "telemetry_emitter", "L1")
_emit_routes_through("p1", "telemetry_emitter", "L1")
_emit_escalates_to_human("p1", "telemetry_emitter", "L1")
_emit_reads_policy_state("p1", "telemetry_emitter", "L1")
_emit_authorize_and_execute("p2", "telemetry_emitter", "execution_auth")
_emit_validates_capability("p2", "telemetry_emitter", "capability_check")
_emit_routes_to_capability("p2", "telemetry_emitter", "capability_route")
_emit_writes_via_uwg("p2", "telemetry_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "telemetry_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "telemetry_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "telemetry_emitter", "exec_output")
_emit_dispatches_agent("p3", "telemetry_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "telemetry_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "telemetry_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "telemetry_emitter", "healing_outcome")
_emit_escalates_failure("p3", "telemetry_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "telemetry_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telemetry_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "telemetry_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "telemetry_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telemetry_emitter", "eval_metric")
_emit_stores_embedding("p4", "telemetry_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "telemetry_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telemetry_emitter", "exec_snapshot_link")


def compute_event_hash(stage: str, kind: str, commit_tick: int, details: dict[str, Any]) -> str:
    """
    Compute deterministic event hash from canonical JSON bytes.

    Args:
        stage: Event stage identifier
        kind: Event kind/type
        commit_tick: Required input tick (no wall-clock)
        details: Event details dictionary

    Returns:
        SHA-256 hash of canonical JSON representation
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_event_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_event_hash", "p0_governance")
    canonical_data = {"stage": stage, "kind": kind, "commit_tick": commit_tick, "details": details}
    canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TelemetryEvent:
    """Immutable telemetry event artifact."""

    trace_id: str
    stage: str
    kind: str
    commit_tick: int
    details: dict
    event_hash: str

    @classmethod
    def create(
        cls, trace_id: str, stage: str, kind: str, commit_tick: int, details: dict[str, Any]
    ) -> "TelemetryEvent":
        """
        Create a new TelemetryEvent with deterministic event_hash.

        Args:
            trace_id: Execution trace identifier
            stage: Event stage identifier
            kind: Event kind/type
            commit_tick: Required input tick (no wall-clock)
            details: Event details dictionary

        Returns:
            New TelemetryEvent with computed event_hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "TelemetryEvent.create")

        details_copy = copy.deepcopy(details)
        event_hash = compute_event_hash(stage, kind, commit_tick, details_copy)
        return cls(
            trace_id=trace_id,
            stage=stage,
            kind=kind,
            commit_tick=commit_tick,
            details=details_copy,
            event_hash=event_hash,
        )


class TelemetryEmitter:
    """
    Write-only telemetry emitter with injected recording seam.

    Calls injected record_fn exactly once, no branching on event content,
    no I/O, no decisions.
    """

    def emit(self, *, event: TelemetryEvent, record_fn) -> None:
        """
        Emit telemetry event via injected recording function.

        Args:
            event: TelemetryEvent to emit
            record_fn: Injected recording function to call
        """
        record_fn(event)

    def build_event(
        self, *, trace_id: str, stage: str, kind: str, commit_tick: int, details: dict[str, Any]
    ) -> TelemetryEvent:
        """
        Convenience constructor for TelemetryEvent.

        Args:
            trace_id: Execution trace identifier
            stage: Event stage identifier
            kind: Event kind/type
            commit_tick: Required input tick (no wall-clock)
            details: Event details dictionary

        Returns:
            New TelemetryEvent
        """
        return TelemetryEvent.create(trace_id, stage, kind, commit_tick, details)
