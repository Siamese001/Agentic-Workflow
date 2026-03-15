"""L6 Performance Observability module.

Provides structured runtime performance metrics across routing, reasoning, orchestration, execution, and mutation.
All major lifecycle stages emit measurable latency and throughput signals.
"""

# P2/L6 Performance Observability exports
from agentic_core.L6_observability.performance.performance_emitter import (
    LatencyBudget,
    PerformanceContext,
    StageOwner,
    measure_stage_timing,
    query_performance_records,
    record_stage_performance,
)
from agentic_core.L6_observability.performance.performance_registry import (
    BudgetViolationError,
    PerformanceMissingError,
    PerformanceRecord,
    PerformanceRegistry,
    get_performance_registry,
    reset_performance_registry,
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
    # Performance Records
    "PerformanceRecord",
    "PerformanceRegistry",
    # Exception Classes
    "PerformanceMissingError",
    "BudgetViolationError",
    # Registry Access
    "get_performance_registry",
    "reset_performance_registry",
    # Context Classes
    "PerformanceContext",
    "StageOwner",
    "LatencyBudget",
    # Emission Functions
    "record_stage_performance",
    "query_performance_records",
    "measure_stage_timing",
]
