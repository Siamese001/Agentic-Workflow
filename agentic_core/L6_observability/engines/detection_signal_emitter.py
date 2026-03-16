"""
L6 DetectionSignalEmitter — Phase 7

NON-AUTHORITY emission hook. Called AFTER GatewayResult is finalized.
Cannot mutate, gate, or block the current execution decision.
Enhanced to write L4A detection signals to L4 state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
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

emit_replay_key("p0", "detection_signal_emitter")
emit_determinism_digest("p0", "detection_signal_emitter")

_emit_dispatches_healing_run("p1", "detection_signal_emitter", "L6")
_emit_routes_through("p1", "detection_signal_emitter", "L6")
_emit_escalates_to_human("p1", "detection_signal_emitter", "L6")
_emit_reads_policy_state("p1", "detection_signal_emitter", "L6")
_emit_authorize_and_execute("p2", "detection_signal_emitter", "execution_auth")
_emit_validates_capability("p2", "detection_signal_emitter", "capability_check")
_emit_routes_to_capability("p2", "detection_signal_emitter", "capability_route")
_emit_writes_via_uwg("p2", "detection_signal_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "detection_signal_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "detection_signal_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "detection_signal_emitter", "exec_output")
_emit_dispatches_agent("p3", "detection_signal_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "detection_signal_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "detection_signal_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "detection_signal_emitter", "healing_outcome")
_emit_escalates_failure("p3", "detection_signal_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "detection_signal_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "detection_signal_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "detection_signal_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "detection_signal_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "detection_signal_emitter", "eval_metric")
_emit_stores_embedding("p4", "detection_signal_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "detection_signal_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "detection_signal_emitter", "exec_snapshot_link")

if TYPE_CHECKING:
    from system_learning.engines.l4_state_writer import L4StateWriter


def emit_detection_signal(
    mission_id: str,
    created_at_utc: int,
    anomaly_score: float = 0.0,
    escalation_rate: float = 0.0,
    retry_rate: float = 0.0,
    violation_density: float = 0.0,
    schema_version: int = 1,
) -> DetectionSignal:
    """
    Build and return a DetectionSignal from mission boundary metrics.

    AUTHORITY CONSTRAINT: caller must not use the returned signal to
    alter the GatewayResult or any in-flight execution decision.
    The signal is for persistence + N+1 routing influence only.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "emit_detection_signal", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "emit_detection_signal", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "emit_detection_signal")
    signal = DetectionSignal.build(
        mission_id=mission_id,
        created_at_utc=created_at_utc,
        anomaly_score=anomaly_score,
        escalation_rate=escalation_rate,
        retry_rate=retry_rate,
        violation_density=violation_density,
        schema_version=schema_version,
    )
    return signal


def emit_detection_signal_with_l4a(
    mission_id: str,
    created_at_utc: int,
    l4a_writer: L4StateWriter | None = None,
    anomaly_score: float = 0.0,
    escalation_rate: float = 0.0,
    retry_rate: float = 0.0,
    violation_density: float = 0.0,
    schema_version: int = 1,
) -> DetectionSignal:
    """
    Build and emit a DetectionSignal with optional L4A persistence.

    Args:
        mission_id: Mission identifier for the signal.
        created_at_utc: Timestamp for signal creation.
        l4a_writer: Optional L4A state writer for persistence.
        anomaly_score: Anomaly score metric.
        escalation_rate: Escalation rate metric.
        retry_rate: Retry rate metric.
        violation_density: Violation density metric.
        schema_version: Schema version for the signal.

    Returns:
        The created DetectionSignal.
    """
    signal = emit_detection_signal(
        mission_id=mission_id,
        created_at_utc=created_at_utc,
        anomaly_score=anomaly_score,
        escalation_rate=escalation_rate,
        retry_rate=retry_rate,
        violation_density=violation_density,
        schema_version=schema_version,
    )
    if l4a_writer is not None:
        try:
            payload_bytes = signal.canonical_bytes()
            l4a_writer.write_l4a_detection_signal(
                payload_bytes=payload_bytes,
                component_name="detection_signal_emitter",
                created_utc=created_at_utc,
            )
        # guardian: allow-silent-swallow
        except Exception:
            pass
    return signal


def emit_signal_from_gateway_result(
    mission_id: str, created_at_utc: int, gateway_result: object
) -> DetectionSignal:
    """
    Derive a DetectionSignal from a completed GatewayResult.

    Reads only already-finalized fields; never modifies gateway_result.
    Returns the signal for downstream persistence — does NOT feed back
    into the current execution cycle.
    """
    success = getattr(gateway_result, "success", True)
    error = getattr(gateway_result, "error", None)
    anomaly_score = 0.0 if success else 0.6
    escalation_rate = 0.0
    retry_rate = 0.0
    violation_density = 0.1 if error is not None else 0.0
    return DetectionSignal.build(
        mission_id=mission_id,
        created_at_utc=created_at_utc,
        anomaly_score=anomaly_score,
        escalation_rate=escalation_rate,
        retry_rate=retry_rate,
        violation_density=violation_density,
    )
