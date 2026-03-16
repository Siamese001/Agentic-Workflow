"""L2 Execution Adaptation module.

Provides adaptive execution where execution paths adapt dynamically based on
historical success or failure of tools and execution strategies.
"""

# P4/L2 Execution Adaptation exports
from agentic_core.L2_execution.adaptation.adaptation_orchestrator import (
    ExecutionContext,
    ExecutionStrategy,
    HistoricalMetrics,
    check_policy_compliance,
    choose_execution_strategy,
    evaluate_strategy_safety,
    execution_strategy_chosen,
    get_execution_adaptation_registry,
    policy_compliance_checked,
    query_execution_adaptations,
    strategy_evaluated,
    unsafe_strategy_rejected,
)
from agentic_core.L2_execution.adaptation.execution_adaptation import (
    ExecutionAdaptationError,
    ExecutionAdaptationRecord,
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

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L2")
_emit_routes_through("p1", "__init__", "L2")
_emit_escalates_to_human("p1", "__init__", "L2")
_emit_reads_policy_state("p1", "__init__", "L2")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")
_emit_authorize_and_execute("p2", "__init__", "execution_auth")
_emit_validates_capability("p2", "__init__", "capability_check")
_emit_routes_to_capability("p2", "__init__", "capability_route")
_emit_writes_via_uwg("p2", "__init__", "uwg_write")
_emit_blocks_direct_write("p2", "__init__", "direct_write_block")
_emit_records_tool_invocation("p2", "__init__", "tool_invocation")
_emit_captures_execution_output("p2", "__init__", "exec_output")
_emit_dispatches_agent("p3", "__init__", "agent_dispatch")
_emit_coordinates_agents("p3", "__init__", "agent_coordination")
_emit_records_workflow_lineage("p3", "__init__", "workflow_lineage")
_emit_records_healing_outcome("p3", "__init__", "healing_outcome")
_emit_escalates_failure("p3", "__init__", "failure_escalation")
_emit_orchestrates_workflow("p3", "__init__", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "__init__", "healing_dispatch")
_emit_invokes_evaluation("p3", "__init__", "evaluation_signal")
_emit_records_telemetry_event("p4", "__init__", "telemetry_event")
_emit_captures_evaluation_metric("p4", "__init__", "eval_metric")
_emit_stores_embedding("p4", "__init__", "embedding_store")
_emit_updates_meta_learning_state("p4", "__init__", "meta_learning")
_emit_links_execution_to_snapshot("p4", "__init__", "exec_snapshot_link")

__all__ = [
    # Execution Adaptation Records
    "ExecutionAdaptationRecord",
    # Exception Classes
    "ExecutionAdaptationError",
    # Context Classes
    "ExecutionContext",
    "ExecutionStrategy",
    "HistoricalMetrics",
    # Adaptation Functions
    "choose_execution_strategy",
    "query_execution_adaptations",
    "get_execution_adaptation_registry",
    # Safety Functions
    "evaluate_strategy_safety",
    "check_policy_compliance",
]
