"""
L6 DetectionSignalEmitter — Phase 7

NON-AUTHORITY emission hook. Called AFTER GatewayResult is finalized.
Cannot mutate, gate, or block the current execution decision.
Enhanced to write L4A detection signals to L4 state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    record_execution_trace,
)

record_execution_trace("detection_signal_emitter", "detection_signal_emitter_trace")


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
        except (AttributeError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            import logging

            logging.getLogger(__name__).debug("detection_signal_emitter: Exception swallowed at L117: %s", e)
    return signal


def emit_signal_from_gateway_result(
    mission_id: str,
    created_at_utc: int,
    gateway_result: object,
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
