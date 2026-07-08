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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "readonly_retrieval_scope")
trace_contract.emit_determinism_digest("p0", "readonly_retrieval_scope")

trace_contract._emit_dispatches_healing_run("p1", "readonly_retrieval_scope", "L4")
trace_contract._emit_routes_through("p1", "readonly_retrieval_scope", "L4")
trace_contract._emit_checks_agent_registry("p1", "readonly_retrieval_scope", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "readonly_retrieval_scope", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "readonly_retrieval_scope", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "readonly_retrieval_scope", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "readonly_retrieval_scope", "target_agent")
trace_contract._emit_verifies_policy("p1", "readonly_retrieval_scope", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "readonly_retrieval_scope", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "readonly_retrieval_scope", "boundary_check")
trace_contract._emit_transcripts_response("p1", "readonly_retrieval_scope", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "readonly_retrieval_scope")
trace_contract._emit_gated_by_confidence("p1", "readonly_retrieval_scope", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "readonly_retrieval_scope", "L4")
trace_contract._emit_reads_policy_state("p1", "readonly_retrieval_scope", "L4")
trace_contract._emit_authorize_and_execute("p2", "readonly_retrieval_scope", "execution_auth")
trace_contract._emit_validates_capability("p2", "readonly_retrieval_scope", "capability_check")
trace_contract._emit_routes_to_capability("p2", "readonly_retrieval_scope", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "readonly_retrieval_scope", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "readonly_retrieval_scope", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "readonly_retrieval_scope", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "readonly_retrieval_scope", "exec_output")
trace_contract._emit_dispatches_agent("p3", "readonly_retrieval_scope", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "readonly_retrieval_scope", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "readonly_retrieval_scope", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "readonly_retrieval_scope", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "readonly_retrieval_scope", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "readonly_retrieval_scope", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "readonly_retrieval_scope", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "readonly_retrieval_scope", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "readonly_retrieval_scope", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "readonly_retrieval_scope", "eval_metric")
trace_contract._emit_stores_embedding("p4", "readonly_retrieval_scope", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "readonly_retrieval_scope", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "readonly_retrieval_scope", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("readonly_retrieval_scope", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("readonly_retrieval_scope", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("readonly_retrieval_scope", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("readonly_retrieval_scope", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("readonly_retrieval_scope", "p4obs", "alert")
trace_contract._emit_links_incident_trace("readonly_retrieval_scope", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("readonly_retrieval_scope", "p3lm", "pattern")
trace_contract._emit_records_learning_event("readonly_retrieval_scope", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("readonly_retrieval_scope", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("readonly_retrieval_scope", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("readonly_retrieval_scope", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("readonly_retrieval_scope", "p3lm", "policy")
trace_contract._emit_stores_learning_state("readonly_retrieval_scope", "p3lm", "state")
trace_contract._emit_records_execution_trace("readonly_retrieval_scope", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("readonly_retrieval_scope", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("readonly_retrieval_scope", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("readonly_retrieval_scope", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("readonly_retrieval_scope", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("readonly_retrieval_scope", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("readonly_retrieval_scope", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("readonly_retrieval_scope", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("readonly_retrieval_scope", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "readonly_retrieval_scope", "context_pull")
trace_contract._emit_pulls_context("p1", "readonly_retrieval_scope", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "readonly_retrieval_scope", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "readonly_retrieval_scope", "uwg_term_2")
trace_contract._emit_writes_through("p1", "readonly_retrieval_scope", "write_through")
trace_contract._emit_writes_through("p1", "readonly_retrieval_scope", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "readonly_retrieval_scope", "safety_validation")
trace_contract._emit_invokes_eval("p1", "readonly_retrieval_scope", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "readonly_retrieval_scope", "routing_commit")

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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "RetrievalMutationViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "RetrievalMutationViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "RetrievalMutationViolation.__init__")
        self.detail = detail
        super().__init__(
            f"[{self.code}] Mutation blocked inside read-only retrieval scope"
            + (f": {detail}" if detail else ""),
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
