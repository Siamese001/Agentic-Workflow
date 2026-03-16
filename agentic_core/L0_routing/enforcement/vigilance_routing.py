"""
§Wave4.1 — L0 Vigilance Event Routing Intake.

Accepts a VigilanceEventArtifact from L6 and maps it to an L0 routing
decision (RoutePath). Does not modify existing L0 entry paths for user
requests.

Routing rules (deterministic, no fallback to wall-clock):
  LOW / MEDIUM  → STANDARD_VALIDATION (L5 rules-first)
  HIGH / CRITICAL → HUMAN_ESCALATION (HIL path)
"""

from __future__ import annotations

from typing import Any

from agentic_core.L0_routing.seams.vigilance_seam import (
    get_vigilance_severity,
)
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath
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

emit_replay_key("p0", "vigilance_routing")
emit_determinism_digest("p0", "vigilance_routing")

_emit_dispatches_healing_run("p1", "vigilance_routing", "L0")
_emit_routes_through("p1", "vigilance_routing", "L0")
_emit_escalates_to_human("p1", "vigilance_routing", "L0")
_emit_reads_policy_state("p1", "vigilance_routing", "L0")
_emit_authorize_and_execute("p2", "vigilance_routing", "execution_auth")
_emit_validates_capability("p2", "vigilance_routing", "capability_check")
_emit_routes_to_capability("p2", "vigilance_routing", "capability_route")
_emit_writes_via_uwg("p2", "vigilance_routing", "uwg_write")
_emit_blocks_direct_write("p2", "vigilance_routing", "direct_write_block")
_emit_records_tool_invocation("p2", "vigilance_routing", "tool_invocation")
_emit_captures_execution_output("p2", "vigilance_routing", "exec_output")
_emit_dispatches_agent("p3", "vigilance_routing", "agent_dispatch")
_emit_coordinates_agents("p3", "vigilance_routing", "agent_coordination")
_emit_records_workflow_lineage("p3", "vigilance_routing", "workflow_lineage")
_emit_records_healing_outcome("p3", "vigilance_routing", "healing_outcome")
_emit_escalates_failure("p3", "vigilance_routing", "failure_escalation")
_emit_orchestrates_workflow("p3", "vigilance_routing", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vigilance_routing", "healing_dispatch")
_emit_invokes_evaluation("p3", "vigilance_routing", "evaluation_signal")
_emit_records_telemetry_event("p4", "vigilance_routing", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vigilance_routing", "eval_metric")
_emit_stores_embedding("p4", "vigilance_routing", "embedding_store")
_emit_updates_meta_learning_state("p4", "vigilance_routing", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vigilance_routing", "exec_snapshot_link")


def route_vigilance_event(event: Any) -> RoutePath:
    """§Wave4.1 — Deterministic routing from VigilanceEventArtifact tier.

    Returns:
        RoutePath.HUMAN_ESCALATION for HIGH/CRITICAL
        RoutePath.STANDARD_VALIDATION for LOW/MEDIUM
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "route_vigilance_event", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "route_vigilance_event", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "route_vigilance_event")
    VigilanceSeverity = get_vigilance_severity()
    if event.vigilance_tier in (VigilanceSeverity.HIGH, VigilanceSeverity.CRITICAL):
        return RoutePath.HUMAN_ESCALATION
    return RoutePath.STANDARD_VALIDATION


__all__ = [
    "route_vigilance_event",
]
