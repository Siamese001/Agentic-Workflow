"""L2 Execution Observability module.

Provides operational telemetry for runtime execution with structured
start, finish, failure, retry, and duration telemetry.
"""

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
    get_observability_registry,
    policy_block_recorded,
    query_execution_observability,
    record_execution_failure,
    record_execution_observability,
    record_execution_retry,
    record_policy_block,
)

__all__ = [
    # Observability Records
    "ExecutionObservabilityRecord",
    # Enums
    "ExecutionStatus",
    "FailureClassification",
    # Exception Classes
    "ExecutionObservabilityError",
    # Context Classes
    "ExecutionObservabilityContext",
    # Emission Functions
    "record_execution_observability",
    "record_execution_retry",
    "record_execution_failure",
    "record_policy_block",
    "query_execution_observability",
    # Registry Access
    "get_observability_registry",
    "reset_observability_registry",
    # ADG Edge Emitters
    "execution_observability_emitted",
    "execution_retry_recorded",
    "execution_failure_classified",
    "policy_block_recorded",
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
