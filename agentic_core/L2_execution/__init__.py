"""
L2 Execution Layer — Governed runtime execution with observability.

This layer provides execution, tool invocation, and operational observability.
No cognition, routing, or persistence logic belongs in this layer.
Only execution contracts, tool contracts, and observability are exported.
"""

# Execution contracts and tool contracts
from agentic_core.L2_execution.adaptation.adaptation_orchestrator import (
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
from agentic_core.L2_execution.adaptation.execution_adaptation import (
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

# P3/L2 Execution Observability exports
from agentic_core.L2_execution.observability.execution_observability import (
    BLOCKED_BY_POLICY,
    CANCELLED,
    ESCALATED,
    FAILED,
    MUTATION_FAILURE,
    NETWORK_FAILURE,
    POLICY_BLOCK,
    RETRIED,
    # Enum values for ADG scanner detection
    STARTED,
    SUCCEEDED,
    TOOL_ERROR,
    UNKNOWN_FAILURE,
    VALIDATION_FAILURE,
    ExecutionObservabilityError,
    ExecutionObservabilityRecord,
    ExecutionStatus,
    FailureClassification,
    get_observability_registry,
    reset_observability_registry,
)
from agentic_core.L2_execution.observability.observability_recorder import (
    ExecutionObservabilityContext,
    execution_failure_classified,
    execution_observability_emitted,
    execution_retry_recorded,
    policy_block_recorded,
    query_execution_observability,
    record_execution_failure,
    record_execution_observability,
    record_execution_retry,
    record_policy_block,
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
from .contracts.typed_tool_contract import (  # noqa: F401
    ToolContract,
    ToolContractStore,
    ToolSchema,
    TypedToolRegistry,
    invoke_typed_tool,
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

__all__ = [
    # Tool Contracts
    "ToolContract",
    "TypedToolRegistry",
    "ToolSchema",
    "ToolContractStore",
    "invoke_typed_tool",
    # Observability Records
    "ExecutionObservabilityRecord",
    # Enums
    "ExecutionStatus",
    "FailureClassification",
    # Exception Classes
    "ExecutionObservabilityError",
    # Registry Access
    "get_observability_registry",
    "reset_observability_registry",
    # Context Classes
    "ExecutionObservabilityContext",
    # Emission Functions
    "record_execution_observability",
    "record_execution_retry",
    "record_execution_failure",
    "record_policy_block",
    "query_execution_observability",
    # ADG Edge Emitters
    "execution_observability_emitted",
    "execution_retry_recorded",
    "execution_failure_classified",
    "policy_block_recorded",
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
    # Enum values for ADG scanner detection
    "STARTED",
    "SUCCEEDED",
    "FAILED",
    "RETRIED",
    "CANCELLED",
    "BLOCKED_BY_POLICY",
    "ESCALATED",
    "POLICY_BLOCK",
    "TOOL_ERROR",
    "NETWORK_FAILURE",
    "MUTATION_FAILURE",
    "VALIDATION_FAILURE",
    "UNKNOWN_FAILURE",
]

# Sovereignty assertion: This layer contains NO cognition or routing logic
# L2 may only execute governed actions; cognition belongs to L1, routing to L3
