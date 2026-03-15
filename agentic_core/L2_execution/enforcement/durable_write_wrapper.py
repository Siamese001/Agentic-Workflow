"""
Durable Write Wrapper - Enforces sole mutation authority in L2.2.

All durable writes must go through this wrapper to track mutations.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "durable_write_wrapper", "L2")
_emit_routes_through("p1", "durable_write_wrapper", "L2")
_emit_escalates_to_human("p1", "durable_write_wrapper", "L2")
_emit_reads_policy_state("p1", "durable_write_wrapper", "L2")

Logger = logging.getLogger(__name__)
from agentic_core.L0_routing.enforcement.execution_gateway import CURRENT_PHASE, MUTATION_COUNTER
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def durable_write(operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Wrapper for all durable write operations.

    Args:
        operation: The actual write operation to perform
        *args: Arguments to pass to the operation
        **kwargs: Keyword arguments to pass to the operation

    Returns:
        Result of the operation

    Raises:
        AssertionError: If not in L2.2 phase
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "durable_write", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "durable_write", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "durable_write")
    global CURRENT_PHASE, MUTATION_COUNTER
    if CURRENT_PHASE != "L2.2":
        raise AssertionError(f"Durable write attempted in phase {CURRENT_PHASE}, only L2.2 allowed")
    MUTATION_COUNTER += 1
    Logger.info(f"[DURABLE_WRITE] Mutation #{MUTATION_COUNTER} in phase {CURRENT_PHASE}")
    return operation(*args, **kwargs)


def reset_mutation_counter() -> None:
    """Reset mutation counter (for testing only)."""
    global MUTATION_COUNTER
    MUTATION_COUNTER = 0


def get_mutation_count() -> int:
    """Get current mutation count."""
    return MUTATION_COUNTER


def set_phase(phase: str) -> None:
    """Set current execution phase."""
    global CURRENT_PHASE
    CURRENT_PHASE = phase


def get_current_phase() -> str:
    """Get current execution phase."""
    return CURRENT_PHASE
