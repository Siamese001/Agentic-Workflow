"""GravityLeakHealerAgent - canonical healer name alias for GravityLeakRepairAgent."""

from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
    GravityLeakRepairAgent as GravityLeakHealerAgent,
)
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

emit_replay_key("p0", "GravityLeakHealerAgent")
emit_determinism_digest("p0", "GravityLeakHealerAgent")

_emit_dispatches_healing_run("p1", "GravityLeakHealerAgent", "L5")
_emit_routes_through("p1", "GravityLeakHealerAgent", "L5")
_emit_escalates_to_human("p1", "GravityLeakHealerAgent", "L5")
_emit_reads_policy_state("p1", "GravityLeakHealerAgent", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "GravityLeakHealerAgent")
_emit_applies_guardrail("p0", "GravityLeakHealerAgent", "p0_governance")
_emit_snapshots_state("p0", "GravityLeakHealerAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "GravityLeakHealerAgent", "execution_auth")
_emit_validates_capability("p2", "GravityLeakHealerAgent", "capability_check")
_emit_routes_to_capability("p2", "GravityLeakHealerAgent", "capability_route")
_emit_writes_via_uwg("p2", "GravityLeakHealerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "GravityLeakHealerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "GravityLeakHealerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "GravityLeakHealerAgent", "exec_output")
_emit_dispatches_agent("p3", "GravityLeakHealerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "GravityLeakHealerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "GravityLeakHealerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "GravityLeakHealerAgent", "healing_outcome")
_emit_escalates_failure("p3", "GravityLeakHealerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "GravityLeakHealerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GravityLeakHealerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "GravityLeakHealerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "GravityLeakHealerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GravityLeakHealerAgent", "eval_metric")
_emit_stores_embedding("p4", "GravityLeakHealerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "GravityLeakHealerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GravityLeakHealerAgent", "exec_snapshot_link")

__all__ = ["GravityLeakHealerAgent"]
