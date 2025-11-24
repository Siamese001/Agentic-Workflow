from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.models.models import (
    TelemetryEvent,
    RetrievalAttemptEvent,
    RetrievalSuccessEvent,
    RetrievalFailureEvent,
    RankingEvent,
    CostSnapshot,
)
from runtime.observability.collectors import append_event
from runtime.observability.spans import _now_ms


def emit_node_event(node: str, status: str, details: Optional[str] = None) -> None:
    """Node-level events for L3 orchestration visibility."""

    append_event(
        TelemetryEvent(
            name=node,
            ts_ms=_now_ms(),
            attributes={
                "event_type": "node",
                "status": status,
                "details": details,
            },
        )
    )


def emit_telemetry_event(name: str, attributes: Dict[str, Any]) -> None:
    """General-purpose event emission for arbitrary telemetry use cases."""

    append_event(
        TelemetryEvent(
            name=name,
            ts_ms=_now_ms(),
            attributes=attributes,
        )
    )


def log_exception(name: str, exc: Exception) -> None:
    """Emit an error-level telemetry event for exceptions."""

    append_event(
        TelemetryEvent(
            name=name,
            ts_ms=_now_ms(),
            attributes={
                "event_type": "exception",
                "error": str(exc),
            },
        )
    )


def record_event(name: str, attributes: Dict[str, Any]) -> None:
    """Convenience wrapper so infra code can emit generic events."""

    emit_telemetry_event(name, attributes)


def record_exception(name: str, exc: Exception) -> None:
    """Convenience wrapper mirroring log_exception for infra code."""

    log_exception(name, exc)


def emit_retrieval_attempt(evt: RetrievalAttemptEvent) -> None:
    append_event(evt)


def emit_retrieval_success(evt: RetrievalSuccessEvent) -> None:
    append_event(evt)


def emit_retrieval_failure(evt: RetrievalFailureEvent) -> None:
    append_event(evt)


def emit_ranking_event(evt: RankingEvent) -> None:
    append_event(evt)


def emit_cost_snapshot(snapshot: CostSnapshot) -> None:
    """Emit a cost snapshot event used by L2 after completion."""

    append_event(
        TelemetryEvent(
            name="costs",
            ts_ms=_now_ms(),
            attributes={
                "event_type": "cost_snapshot",
                **snapshot.model_dump(),
            },
        )
    )


def emit_resilience_event(name: str, attributes: Dict[str, Any]) -> None:
    """Generic entrypoint for resilience-related telemetry events."""

    emit_telemetry_event(name, attributes)


def emit_golden_eval_event(
    *,
    workflow_id: str,
    scenario_id: str,
    passed: bool,
    score: float,
    summary: Dict[str, Any],
    routing_trace: Optional[List[Dict[str, Any]]] = None,
    council_summary: Optional[Dict[str, Any]] = None,
    resilience_summary: Optional[Dict[str, Any]] = None,
    cost_snapshot: Optional[CostSnapshot] = None,
) -> None:
    attrs: Dict[str, Any] = {
        "event_type": "golden_eval",
        "workflow_id": workflow_id,
        "scenario_id": scenario_id,
        "passed": passed,
        "score": score,
        "summary": summary,
    }
    if routing_trace is not None:
        attrs["routing_trace"] = routing_trace
    if council_summary is not None:
        attrs["council_summary"] = council_summary
    if resilience_summary is not None:
        attrs["resilience_summary"] = resilience_summary
    if cost_snapshot is not None:
        attrs["cost_snapshot"] = cost_snapshot.model_dump()

    emit_telemetry_event("golden_eval", attrs)


def emit_scenario_simulation_event(
    *,
    workflow_id: Optional[str],
    scenario_id: str,
    outcome: Dict[str, Any],
    telemetry: Dict[str, Any],
    error_taxonomy: Optional[Dict[str, Any]] = None,
) -> None:
    attrs: Dict[str, Any] = {
        "event_type": "scenario_simulation",
        "workflow_id": workflow_id,
        "scenario_id": scenario_id,
        "outcome": outcome,
        "telemetry": telemetry,
    }
    if error_taxonomy is not None:
        attrs["error_taxonomy"] = error_taxonomy

    emit_telemetry_event("scenario_simulation", attrs)


def emit_scenario_start_event(
    *,
    workflow_id: Optional[str],
    scenario_id: str,
    description: Optional[str] = None,
) -> None:
    emit_telemetry_event(
        "scenario_start",
        {
            "event_type": "scenario_start",
            "workflow_id": workflow_id,
            "scenario_id": scenario_id,
            "description": description,
        },
    )


def emit_scenario_end_event(
    *,
    workflow_id: Optional[str],
    scenario_id: str,
    passed: Optional[bool] = None,
    score: Optional[float] = None,
) -> None:
    emit_telemetry_event(
        "scenario_end",
        {
            "event_type": "scenario_end",
            "workflow_id": workflow_id,
            "scenario_id": scenario_id,
            "passed": passed,
            "score": score,
        },
    )


def emit_council_arbitration_event(
    *,
    workflow_id: Optional[str],
    scenario_id: Optional[str],
    role: str,
    arbitration: Dict[str, Any],
) -> None:
    attrs: Dict[str, Any] = {
        "event_type": "council_arbitration",
        "workflow_id": workflow_id,
        "scenario_id": scenario_id,
        "role": role,
        **arbitration,
    }
    emit_telemetry_event("council_arbitration", attrs)


def emit_resilience_trace_event(
    *,
    workflow_id: Optional[str],
    scenario_id: Optional[str],
    name: str,
    attributes: Dict[str, Any],
) -> None:
    attrs = dict(attributes)
    attrs.setdefault("event_type", "resilience_trace")
    attrs["workflow_id"] = workflow_id
    attrs["scenario_id"] = scenario_id
    emit_resilience_event(name, attrs)
