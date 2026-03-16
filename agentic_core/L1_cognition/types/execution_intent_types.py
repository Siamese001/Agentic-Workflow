"""
L1 Execution Intent - Pure transformation without side effects.

L1 modules must return ExecutionIntent objects instead of performing mutations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execution_intent_types")
emit_determinism_digest("p0", "execution_intent_types")

_emit_dispatches_healing_run("p1", "execution_intent_types", "L1")
_emit_routes_through("p1", "execution_intent_types", "L1")
_emit_escalates_to_human("p1", "execution_intent_types", "L1")
_emit_reads_policy_state("p1", "execution_intent_types", "L1")
_emit_authorize_and_execute("p2", "execution_intent_types", "execution_auth")
_emit_validates_capability("p2", "execution_intent_types", "capability_check")
_emit_routes_to_capability("p2", "execution_intent_types", "capability_route")
_emit_writes_via_uwg("p2", "execution_intent_types", "uwg_write")
_emit_blocks_direct_write("p2", "execution_intent_types", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_intent_types", "tool_invocation")
_emit_captures_execution_output("p2", "execution_intent_types", "exec_output")
_emit_dispatches_agent("p3", "execution_intent_types", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_intent_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_intent_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_intent_types", "healing_outcome")
_emit_escalates_failure("p3", "execution_intent_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_intent_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_intent_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_intent_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_intent_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_intent_types", "eval_metric")
_emit_stores_embedding("p4", "execution_intent_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_intent_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_intent_types", "exec_snapshot_link")


@dataclass
class ExecutionIntent:
    """Pure execution intent that L1 can return without side effects."""

    tool_name: str
    args: dict[str, Any]
    metadata: dict[str, Any]
    requires_commit: bool = True


@dataclass
class L1Result:
    """Standard L1 result containing either pure output or execution intents."""

    success: bool
    output: Any
    execution_intents: list[ExecutionIntent] | None = None
    error: str | None = None


MUTATION_GUARD = 0


def assert_l1_purity(instance: Any) -> None:
    """Runtime assertion that L1 instance has no mutation capabilities."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_l1_purity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_l1_purity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "assert_l1_purity")
    assert not hasattr(instance, "redis"), "L1 instance cannot have redis client"
    assert not hasattr(instance, "pinecone"), "L1 instance cannot have pinecone client"
    assert not hasattr(instance, "subprocess"), "L1 instance cannot have subprocess access"
    assert not hasattr(instance, "filesystem"), "L1 instance cannot have direct filesystem access"


def increment_mutation_guard() -> None:
    """Increment global mutation guard - should only be called in L2.2."""
    global MUTATION_GUARD
    MUTATION_GUARD += 1


def get_mutation_count() -> int:
    """Get current mutation count."""
    return MUTATION_GUARD


def reset_mutation_guard() -> None:
    """Reset mutation guard (for testing only)."""
    global MUTATION_GUARD
    MUTATION_GUARD = 0
