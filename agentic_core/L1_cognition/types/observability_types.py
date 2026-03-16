"""
agentic_core/L1_cognition/reasoning/types/observability_types.py

Passive data structures for MetaLearningObservability.
Extracted from engine/meta_observability.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "observability_types")
emit_determinism_digest("p0", "observability_types")

_emit_dispatches_healing_run("p1", "observability_types", "L1")
_emit_routes_through("p1", "observability_types", "L1")
_emit_escalates_to_human("p1", "observability_types", "L1")
_emit_reads_policy_state("p1", "observability_types", "L1")

_emit_snapshots_state("p0", "observability_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "observability_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "observability_types")
_emit_authorize_and_execute("p2", "observability_types", "execution_auth")
_emit_validates_capability("p2", "observability_types", "capability_check")
_emit_routes_to_capability("p2", "observability_types", "capability_route")
_emit_writes_via_uwg("p2", "observability_types", "uwg_write")
_emit_blocks_direct_write("p2", "observability_types", "direct_write_block")
_emit_records_tool_invocation("p2", "observability_types", "tool_invocation")
_emit_captures_execution_output("p2", "observability_types", "exec_output")
_emit_dispatches_agent("p3", "observability_types", "agent_dispatch")
_emit_coordinates_agents("p3", "observability_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "observability_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "observability_types", "healing_outcome")
_emit_escalates_failure("p3", "observability_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "observability_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "observability_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "observability_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "observability_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "observability_types", "eval_metric")
_emit_stores_embedding("p4", "observability_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "observability_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "observability_types", "exec_snapshot_link")


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    healthy: bool
    message: str
    last_check: str = field(default_factory=lambda: datetime.now().isoformat())
    details: dict[str, Any] = field(default_factory=dict)
