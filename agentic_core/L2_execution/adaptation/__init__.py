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
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

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
