"""
Phase 5 — Escalation Router: policy-coded L0 mode decision from prior violations.

GUARANTEE: reads ONLY events with commit_tick < execution_start_tick.
Same-cycle violations are structurally invisible to the routing decision.

decide_mode_from_prior_violations(execution_start_tick, routing_config, store) -> str
  Returns escalation_mode from config if prior violations trigger escalation,
  otherwise returns "normal" (legacy default preserved).
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


def _get_routing_config_class():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_config_class", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_config_class", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_routing_config_class")
    from agentic_core.L4_state.config.versioned_configs import RoutingConfig

    return RoutingConfig


def _get_violation_event_store_class():
    from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore

    return ViolationEventStore


def decide_mode_from_prior_violations(
    execution_start_tick: int, routing_config: object, violation_store: object,
) -> str:
    """
    Determine L0 routing mode based solely on prior violations.

    Algorithm
    ---------
    1. Fetch events in window [execution_start_tick - window_ticks, execution_start_tick).
       Same-cycle events (commit_tick == execution_start_tick) are excluded by the store.
    2. For each prior event, check:
       a. severity_score >= escalation_severity_threshold (from config — no hardcoded literal)
       b. OR any violation_code in event.violation_codes is in denylist (if denylist non-empty)
    3. If any event triggers escalation → return routing_config.escalation_mode.
    4. Otherwise → return "normal".

    Parameters
    ----------
    execution_start_tick : int
        The commit_tick at which the current execution begins.
    routing_config : RoutingConfig
        Versioned config supplying all thresholds (no hardcoded literals).
    violation_store : ViolationEventStore
        L4 store to query prior violations from.

    Returns
    -------
    str
        Routing mode string ("normal" or routing_config.escalation_mode).
    """
    prior_events = violation_store.fetch_window(
        before_tick=execution_start_tick, window_ticks=routing_config.escalation_window_ticks,
    )
    denylist = set(routing_config.escalation_violation_code_denylist)
    for event in prior_events:
        severity_triggered = event.severity_score >= routing_config.escalation_severity_threshold
        code_triggered = bool(denylist and denylist.intersection(event.violation_codes))
        if severity_triggered or code_triggered:
            return routing_config.escalation_mode
    return "normal"
