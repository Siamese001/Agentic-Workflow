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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execution_intent_types")
emit_determinism_digest("p0", "execution_intent_types")

_emit_dispatches_healing_run("p1", "execution_intent_types", "L1")
_emit_routes_through("p1", "execution_intent_types", "L1")
_emit_escalates_to_human("p1", "execution_intent_types", "L1")
_emit_reads_policy_state("p1", "execution_intent_types", "L1")


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
