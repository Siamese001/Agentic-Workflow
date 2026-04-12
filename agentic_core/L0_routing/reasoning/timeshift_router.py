"""
L0 Time-Shifted Router — Phase 3

Routing decisions driven ONLY by prior committed DetectionSignals (N+1 influence).
Same-cycle signals (emitted during execution N) CANNOT influence routing of N.

Architecture:
    1. At execution start, record execution_start_tick.
    2. Call get_prior_detection_signal(execution_start_tick) — strictly prior only.
    3. If prior signal anomaly_score >= threshold → route to compliance_mode.
    4. Emit new signal AFTER routing decision is finalized (no feedback loop).
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


def _get_routing_config_and_active():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_config_and_active", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_config_and_active", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_routing_config_and_active")
    from agentic_core.L4_state.config.versioned_configs import RoutingConfig, get_active_configs

    return (RoutingConfig, get_active_configs)


def _get_prior_detection_signal():
    from agentic_core.L4_state.types.detection_signal_store_types import get_prior_detection_signal

    return get_prior_detection_signal


class RoutingMode:
    STANDARD = "standard"
    COMPLIANCE = "compliance_mode"


@dataclass
class TimeshiftRoutingDecision:
    """Result of a time-shifted routing evaluation."""

    mode: str
    prior_signal_hash: str | None
    prior_anomaly_score: float | None
    threshold_used: float
    same_cycle_influence: bool = False


def evaluate_timeshift_routing(
    execution_start_tick: int,
    routing_config: object | None = None,
) -> TimeshiftRoutingDecision:
    """
    Evaluate routing mode using ONLY prior committed signals.

    Args:
        execution_start_tick: The tick at which this execution started.
            Only signals committed BEFORE this tick are considered.
        routing_config: Optional override; defaults to L4 SSOT RoutingConfig.

    Returns:
        TimeshiftRoutingDecision with mode and audit fields.

    GUARANTEE: same_cycle_influence is always False — signals emitted
    during this execution cycle cannot affect this decision.
    """
    if routing_config is None:
        _, get_active_configs = _get_routing_config_and_active()
        routing_config = get_active_configs().routing
    threshold = routing_config.anomaly_routing_threshold
    prior = _get_prior_detection_signal()(execution_start_tick)
    if prior is not None and prior.anomaly_score >= threshold:
        mode = RoutingMode.COMPLIANCE
    else:
        mode = RoutingMode.STANDARD
    return TimeshiftRoutingDecision(
        mode=mode,
        prior_signal_hash=prior.signal_hash if prior else None,
        prior_anomaly_score=prior.anomaly_score if prior else None,
        threshold_used=threshold,
        same_cycle_influence=False,
    )
