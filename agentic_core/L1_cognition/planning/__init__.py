"""L1 Multi-Step Reasoning Planning module.

Provides explicit, staged, and checkpointed multi-step reasoning plans
rather than reactive and opaque reasoning.
"""

# P3/L1 Multi-Step Reasoning Planning exports
from agentic_core.L1_cognition.planning.plan_creator import (
    PlanningPolicy,
    ReasoningPlanContext,
    create_reasoning_plan,
    enforce_plan_checkpoint,
    execute_plan_step,
    get_plan_registry,
    query_reasoning_plans,
    record_plan_revision,
    reset_plan_registry,
)
from agentic_core.L1_cognition.planning.reasoning_plan import (
    CheckpointResult,
    PlanCheckpoint,
    PlanRevision,
    PlanStatus,
    PlanStep,
    ReasoningPlan,
    ReasoningPlanError,
    StepStatus,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "__init__", "L1")
_emit_routes_through("p1", "__init__", "L1")
_emit_escalates_to_human("p1", "__init__", "L1")
_emit_reads_policy_state("p1", "__init__", "L1")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Plan Records
    "ReasoningPlan",
    "PlanStep",
    "PlanCheckpoint",
    "PlanRevision",
    # Enums
    "PlanStatus",
    "StepStatus",
    "CheckpointResult",
    # Exception Classes
    "ReasoningPlanError",
    # Context Classes
    "ReasoningPlanContext",
    "PlanningPolicy",
    # Emission Functions
    "create_reasoning_plan",
    "execute_plan_step",
    "enforce_plan_checkpoint",
    "record_plan_revision",
    "query_reasoning_plans",
    # Registry Access
    "get_plan_registry",
    "reset_plan_registry",
]
