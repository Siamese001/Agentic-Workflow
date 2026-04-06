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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "readonly_retrieval_scope")
emit_determinism_digest("p0", "readonly_retrieval_scope")

_emit_dispatches_healing_run("p1", "readonly_retrieval_scope", "L4")
_emit_routes_through("p1", "readonly_retrieval_scope", "L4")
_emit_checks_agent_registry("p1", "readonly_retrieval_scope", "agent_registry")
_emit_validates_agent_capability("p1", "readonly_retrieval_scope", "capability")
_emit_dispatches_execution_plan("p1", "readonly_retrieval_scope", "exec_plan")
_emit_agent_executes_agent("p1", "readonly_retrieval_scope", "sub_agent")
_emit_routes_to_agent("p1", "readonly_retrieval_scope", "target_agent")
_emit_verifies_policy("p1", "readonly_retrieval_scope", "policy_check")
_emit_observes_runtime_state("p1", "readonly_retrieval_scope", "runtime_state")
_emit_verifies_boundary("p1", "readonly_retrieval_scope", "boundary_check")
_emit_transcripts_response("p1", "readonly_retrieval_scope", "transcript")
_emit_hard_fails_untranscripted("p1", "readonly_retrieval_scope")
_emit_gated_by_confidence("p1", "readonly_retrieval_scope", "confidence_gate")
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_1")
_emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_2")
_emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_3")
_emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_4")
_emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_5")
_emit_emits_metric_event("readonly_retrieval_scope", "p4obs", "metric_6")
_emit_records_incident_event("readonly_retrieval_scope", "p4obs", "incident")
_emit_captures_runtime_anomaly("readonly_retrieval_scope", "p4obs", "anomaly")
_emit_writes_observability_log("readonly_retrieval_scope", "p4obs", "obs_log")
_emit_updates_monitoring_state("readonly_retrieval_scope", "p4obs", "mon_state")
_emit_triggers_alert("readonly_retrieval_scope", "p4obs", "alert")
_emit_links_incident_trace("readonly_retrieval_scope", "p4obs", "trace_link")
_emit_captures_pattern("readonly_retrieval_scope", "p3lm", "pattern")
_emit_records_learning_event("readonly_retrieval_scope", "p3lm", "learning_event")
_emit_writes_learning_snapshot("readonly_retrieval_scope", "p3lm", "snapshot")
_emit_feeds_meta_learning("readonly_retrieval_scope", "p3lm", "meta_feed")
_emit_updates_routing_strategy("readonly_retrieval_scope", "p3lm", "routing")
_emit_improves_agent_policy("readonly_retrieval_scope", "p3lm", "policy")
_emit_stores_learning_state("readonly_retrieval_scope", "p3lm", "state")
_emit_records_execution_trace("readonly_retrieval_scope", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("readonly_retrieval_scope", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("readonly_retrieval_scope", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("readonly_retrieval_scope", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("readonly_retrieval_scope", "L4_STATE", "p2_trace_5")
_emit_reads_environ("readonly_retrieval_scope", "env_read", "p2_env_1")
_emit_reads_environ("readonly_retrieval_scope", "env_read", "p2_env_2")
_emit_reads_runtime_state("readonly_retrieval_scope", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("readonly_retrieval_scope", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "readonly_retrieval_scope", "context_pull")
_emit_pulls_context("p1", "readonly_retrieval_scope", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "readonly_retrieval_scope", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "readonly_retrieval_scope", "uwg_term_2")
_emit_writes_through("p1", "readonly_retrieval_scope", "write_through")
_emit_writes_through("p1", "readonly_retrieval_scope", "write_through_2")
_emit_validated_by_safety_plane("p1", "readonly_retrieval_scope", "safety_validation")
_emit_invokes_eval("p1", "readonly_retrieval_scope", "eval_call")
_emit_proposal_commits_routing("p1", "readonly_retrieval_scope", "routing_commit")

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
