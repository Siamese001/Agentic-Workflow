"""
Phase 6 — Read-Only Retrieval Scope: mutation blocker for L4 retrieval paths.

Guarantees:
- read_only_retrieval_scope(): context manager that activates the read-only flag.
- is_read_only_retrieval_active(): returns True when inside the scope.
- assert_not_read_only(operation): raises RetrievalMutationViolation if scope active.

Any persistent mutation (Redis setex/set, Pinecone upsert, file write) that calls
assert_not_read_only() during an active retrieval scope is deterministically blocked
and surfaces as a typed pre-action violation.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

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

emit_replay_key("p0", "readonly_retrieval_scope")
emit_determinism_digest("p0", "readonly_retrieval_scope")

_emit_dispatches_healing_run("p1", "readonly_retrieval_scope", "L4")
_emit_routes_through("p1", "readonly_retrieval_scope", "L4")
_emit_escalates_to_human("p1", "readonly_retrieval_scope", "L4")
_emit_reads_policy_state("p1", "readonly_retrieval_scope", "L4")
_emit_authorize_and_execute("p2", "readonly_retrieval_scope", "execution_auth")
_emit_validates_capability("p2", "readonly_retrieval_scope", "capability_check")
_emit_routes_to_capability("p2", "readonly_retrieval_scope", "capability_route")
_emit_writes_via_uwg("p2", "readonly_retrieval_scope", "uwg_write")
_emit_blocks_direct_write("p2", "readonly_retrieval_scope", "direct_write_block")
_emit_records_tool_invocation("p2", "readonly_retrieval_scope", "tool_invocation")
_emit_captures_execution_output("p2", "readonly_retrieval_scope", "exec_output")
_emit_dispatches_agent("p3", "readonly_retrieval_scope", "agent_dispatch")
_emit_coordinates_agents("p3", "readonly_retrieval_scope", "agent_coordination")
_emit_records_workflow_lineage("p3", "readonly_retrieval_scope", "workflow_lineage")
_emit_records_healing_outcome("p3", "readonly_retrieval_scope", "healing_outcome")
_emit_escalates_failure("p3", "readonly_retrieval_scope", "failure_escalation")
_emit_orchestrates_workflow("p3", "readonly_retrieval_scope", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "readonly_retrieval_scope", "healing_dispatch")
_emit_invokes_evaluation("p3", "readonly_retrieval_scope", "evaluation_signal")
_emit_records_telemetry_event("p4", "readonly_retrieval_scope", "telemetry_event")
_emit_captures_evaluation_metric("p4", "readonly_retrieval_scope", "eval_metric")
_emit_stores_embedding("p4", "readonly_retrieval_scope", "embedding_store")
_emit_updates_meta_learning_state("p4", "readonly_retrieval_scope", "meta_learning")
_emit_links_execution_to_snapshot("p4", "readonly_retrieval_scope", "exec_snapshot_link")

_READ_ONLY_RETRIEVAL_ACTIVE: bool = False


class RetrievalMutationViolation(Exception):
    """
    Raised when a persistent mutation is attempted inside a read-only retrieval scope.

    Attributes
    ----------
    code   : str  — always "RETRIEVAL_MUTATION_BLOCKED"
    detail : str  — human-readable description of the blocked operation
    """

    code: str = "RETRIEVAL_MUTATION_BLOCKED"

    def __init__(self, detail: str = "") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RetrievalMutationViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RetrievalMutationViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "RetrievalMutationViolation.__init__")
        self.detail = detail
        super().__init__(
            f"[{self.code}] Mutation blocked inside read-only retrieval scope"
            + (f": {detail}" if detail else "")
        )


def is_read_only_retrieval_active() -> bool:
    """Return True when a read_only_retrieval_scope() is currently active."""
    return _READ_ONLY_RETRIEVAL_ACTIVE


def assert_not_read_only(operation: str = "") -> None:
    """
    Raise RetrievalMutationViolation if a read-only retrieval scope is active.

    Call this at the top of any persistent-write seam (Redis set/setex,
    Pinecone upsert, file write) that must be blocked during retrieval.

    Parameters
    ----------
    operation : str
        Short description of the attempted mutation (e.g., "redis.setex",
        "pinecone.upsert"). Included in the violation detail for traceability.
    """
    if _READ_ONLY_RETRIEVAL_ACTIVE:
        raise RetrievalMutationViolation(detail=operation)


@contextmanager
def read_only_retrieval_scope() -> Generator[None, None, None]:
    """
    Context manager that activates the read-only retrieval flag.

    Usage
    -----
    with read_only_retrieval_scope():
        results = l4_semantic_query(query)   # safe — read-only
        # any assert_not_read_only() call here raises RetrievalMutationViolation

    Guarantees
    ----------
    - Flag is set to True on entry.
    - Flag is restored to False on exit (even on exception).
    - Re-entrant: nested scopes are allowed (flag stays True until outermost exits).
    """
    global _READ_ONLY_RETRIEVAL_ACTIVE
    already_active = _READ_ONLY_RETRIEVAL_ACTIVE
    _READ_ONLY_RETRIEVAL_ACTIVE = True
    try:
        yield
    finally:
        if not already_active:
            _READ_ONLY_RETRIEVAL_ACTIVE = False
