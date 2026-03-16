from __future__ import annotations

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

emit_replay_key("p0", "budget_types")
emit_determinism_digest("p0", "budget_types")

_emit_dispatches_healing_run("p1", "budget_types", "L1")
_emit_routes_through("p1", "budget_types", "L1")
_emit_escalates_to_human("p1", "budget_types", "L1")
_emit_reads_policy_state("p1", "budget_types", "L1")

_emit_snapshots_state("p0", "budget_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "budget_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "budget_types")
_emit_authorize_and_execute("p2", "budget_types", "execution_auth")
_emit_validates_capability("p2", "budget_types", "capability_check")
_emit_routes_to_capability("p2", "budget_types", "capability_route")
_emit_writes_via_uwg("p2", "budget_types", "uwg_write")
_emit_blocks_direct_write("p2", "budget_types", "direct_write_block")
_emit_records_tool_invocation("p2", "budget_types", "tool_invocation")
_emit_captures_execution_output("p2", "budget_types", "exec_output")
_emit_dispatches_agent("p3", "budget_types", "agent_dispatch")
_emit_coordinates_agents("p3", "budget_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "budget_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "budget_types", "healing_outcome")
_emit_escalates_failure("p3", "budget_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "budget_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "budget_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "budget_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "budget_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "budget_types", "eval_metric")
_emit_stores_embedding("p4", "budget_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "budget_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "budget_types", "exec_snapshot_link")

"Dataclass models for lic_routing_rules."
import logging
from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: dict[str, str] = field(default_factory=dict)
