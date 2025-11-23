from __future__ import annotations

from typing import Any, Dict, List

from runtime.observability.collectors import get_events


def get_routing_trace() -> List[Dict[str, Any]]:
    """Return a structured trace of routing decisions from telemetry.

    This mirrors the real runtime.trace.trace_reconstruction helper but lives
    inside the Agentic-Workflow-10_10 snapshot so that
    ``from runtime.trace.trace_reconstruction import get_routing_trace`` works
    when tests are run with rootdir=Agentic-Workflow-10_10.
    """

    trace: List[Dict[str, Any]] = []
    try:
        for evt in get_events():
            if getattr(evt, "name", "") != "routing_decision":
                continue
            attrs = getattr(evt, "attributes", {}) or {}
            trace.append(
                {
                    "task": attrs.get("task"),
                    "agent_role": attrs.get("agent_role"),
                    "reason": attrs.get("reason"),
                    "has_council": attrs.get("has_council"),
                    "council_selected_id": attrs.get("council_selected_id"),
                    "council_aggregated_decision": attrs.get("council_aggregated_decision"),
                    "council_vote_count": attrs.get("council_vote_count"),
                }
            )
    except Exception:
        # Evaluation helpers must never break runtime code.
        pass

    return trace
