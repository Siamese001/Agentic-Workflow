from __future__ import annotations

"""Snapshot-local observability façade for v10_10.

This makes ``from runtime.observability import ...`` work inside the
Agentic-Workflow-10_10 test snapshot by re-exporting symbols from the
nested observability modules.
"""

from .spans import start_span, end_span
from .events import TelemetryEvent  # type: ignore[F401]
from .emitters import (
    emit_node_event,
    emit_telemetry_event,
    emit_ranking_event,
    emit_cost_snapshot,
    emit_golden_eval_event,
    emit_scenario_start_event,
    emit_scenario_end_event,
    emit_scenario_simulation_event,
    emit_council_arbitration_event,
    emit_resilience_event,
    emit_resilience_trace_event,
    log_exception,
    record_event,
    record_exception,
)
from .collectors import get_events, clear_events  # noqa: F401


def get_all_events():
    """Backward-compatible alias used by routing.

    Historically, callers imported get_all_events from observability; in the
    new layout, collectors exposes get_events. This adapter preserves the
    older name.
    """

    return list(get_events())


__all__ = [
    "start_span",
    "end_span",
    "emit_node_event",
    "emit_telemetry_event",
    "emit_ranking_event",
    "emit_cost_snapshot",
    "emit_golden_eval_event",
    "emit_scenario_start_event",
    "emit_scenario_end_event",
    "emit_scenario_simulation_event",
    "emit_council_arbitration_event",
    "emit_resilience_event",
    "emit_resilience_trace_event",
    "log_exception",
    "record_event",
    "record_exception",
    "get_events",
    "get_all_events",
    "clear_events",
]



