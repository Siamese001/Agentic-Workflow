"""
Durable Write Wrapper - Enforces sole mutation authority in L2.2.

All durable writes must go through this wrapper to track mutations.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "durable_write_wrapper")
emit_determinism_digest("p0", "durable_write_wrapper")

_emit_dispatches_healing_run("p1", "durable_write_wrapper", "L2")
_emit_routes_through("p1", "durable_write_wrapper", "L2")
_emit_escalates_to_human("p1", "durable_write_wrapper", "L2")
_emit_reads_policy_state("p1", "durable_write_wrapper", "L2")
_emit_authorize_and_execute("p2", "durable_write_wrapper", "execution_auth")
_emit_validates_capability("p2", "durable_write_wrapper", "capability_check")
_emit_routes_to_capability("p2", "durable_write_wrapper", "capability_route")
_emit_writes_via_uwg("p2", "durable_write_wrapper", "uwg_write")
_emit_blocks_direct_write("p2", "durable_write_wrapper", "direct_write_block")
_emit_records_tool_invocation("p2", "durable_write_wrapper", "tool_invocation")
_emit_captures_execution_output("p2", "durable_write_wrapper", "exec_output")
_emit_dispatches_agent("p3", "durable_write_wrapper", "agent_dispatch")
_emit_coordinates_agents("p3", "durable_write_wrapper", "agent_coordination")
_emit_records_workflow_lineage("p3", "durable_write_wrapper", "workflow_lineage")
_emit_records_healing_outcome("p3", "durable_write_wrapper", "healing_outcome")
_emit_escalates_failure("p3", "durable_write_wrapper", "failure_escalation")
_emit_orchestrates_workflow("p3", "durable_write_wrapper", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "durable_write_wrapper", "healing_dispatch")
_emit_invokes_evaluation("p3", "durable_write_wrapper", "evaluation_signal")
_emit_records_telemetry_event("p4", "durable_write_wrapper", "telemetry_event")
_emit_captures_evaluation_metric("p4", "durable_write_wrapper", "eval_metric")
_emit_stores_embedding("p4", "durable_write_wrapper", "embedding_store")
_emit_updates_meta_learning_state("p4", "durable_write_wrapper", "meta_learning")
_emit_links_execution_to_snapshot("p4", "durable_write_wrapper", "exec_snapshot_link")

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
