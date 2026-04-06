"""
L2 Execution Layer — Governed runtime execution.

This layer provides execution, tool invocation, and operational contracts.
No cognition, routing, or persistence logic belongs in this layer.
Only execution contracts and tool contracts are exported.
"""
from enum import Enum

# Execution contracts and tool contracts
from agentic_core.L2_execution.reasoning.adaptation_orchestrator import (
    ExecutionContext,
    ExecutionStrategy,
    HistoricalMetrics,
    check_policy_compliance,
    choose_execution_strategy,
    evaluate_strategy_safety,
    execution_strategy_chosen,
    policy_compliance_checked,
    query_execution_adaptations,
    strategy_evaluated,
    unsafe_strategy_rejected,
)

# P4/L2 Execution Adaptation exports
from agentic_core.L2_execution.reasoning.execution_adaptation import (
    ExecutionAdaptationError,
    ExecutionAdaptationRecord,
    adaptation_reason_hash,
    chosen_strategy_hash,
    # Dataclass field exports for ADG scanner detection
    execution_adaptation_id,
    execution_strategy_hash,
    get_execution_adaptation_registry,
    historical_failure_rate,
    historical_success_rate,
    latency_profile_hash,
    run_id,
    trace_id,
)

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from .types.typed_tool_contract import (  # noqa: F401
    ToolContract,
    ToolContractStore,
    ToolSchema,
    TypedToolRegistry,
    invoke_typed_tool,
)

_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Tool Contracts
    "ToolContract",
    "TypedToolRegistry",
    "ToolSchema",
    "ToolContractStore",
    "invoke_typed_tool",
    # Execution Adaptation Records
    "ExecutionAdaptationRecord",
    # Execution Adaptation Exception Classes
    "ExecutionAdaptationError",
    # Execution Adaptation Registry Access
    "get_execution_adaptation_registry",
    # Execution Adaptation Context Classes
    "ExecutionContext",
    "ExecutionStrategy",
    "HistoricalMetrics",
    # Execution Adaptation Functions
    "choose_execution_strategy",
    "query_execution_adaptations",
    # Execution Adaptation Safety Functions
    "evaluate_strategy_safety",
    "check_policy_compliance",
    # Execution Adaptation ADG Edge Emitters
    "execution_strategy_chosen",
    "strategy_evaluated",
    "unsafe_strategy_rejected",
    "policy_compliance_checked",
    # Execution Adaptation Dataclass field exports for ADG scanner detection
    "execution_adaptation_id",
    "run_id",
    "trace_id",
    "execution_strategy_hash",
    "historical_success_rate",
    "historical_failure_rate",
    "latency_profile_hash",
    "chosen_strategy_hash",
    "adaptation_reason_hash",
]

# Sovereignty assertion: This layer contains NO cognition or routing logic
# L2 may only execute governed actions; cognition belongs to L1, routing to L3
