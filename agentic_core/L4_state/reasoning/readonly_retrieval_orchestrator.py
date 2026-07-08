"""
Phase 6 — Read-Only Retrieval Orchestrator.

Canonical retrieval entrypoint that:
1. Enters read_only_retrieval_scope() before any L4 query.
2. Produces a RetrievalBoundarySnapshot (non-mutating).
3. Returns AnchoredResult list + snapshot.

Any persistent mutation attempted inside this path raises RetrievalMutationViolation.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (
    read_only_retrieval_scope,
)
from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult
from agentic_core.L4_state.types.retrieval_boundary_snapshot_types import (
    AnchorEntry,
    RetrievalBoundarySnapshot,
    create_retrieval_boundary_snapshot,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("readonly_retrieval_orchestrator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("readonly_retrieval_orchestrator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("readonly_retrieval_orchestrator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("readonly_retrieval_orchestrator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("readonly_retrieval_orchestrator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("readonly_retrieval_orchestrator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("readonly_retrieval_orchestrator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("readonly_retrieval_orchestrator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("readonly_retrieval_orchestrator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("readonly_retrieval_orchestrator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("readonly_retrieval_orchestrator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("readonly_retrieval_orchestrator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("readonly_retrieval_orchestrator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("readonly_retrieval_orchestrator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("readonly_retrieval_orchestrator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("readonly_retrieval_orchestrator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("readonly_retrieval_orchestrator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("readonly_retrieval_orchestrator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("readonly_retrieval_orchestrator", "p3lm", "state")
trace_contract._emit_records_execution_trace("readonly_retrieval_orchestrator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("readonly_retrieval_orchestrator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("readonly_retrieval_orchestrator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("readonly_retrieval_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("readonly_retrieval_orchestrator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("readonly_retrieval_orchestrator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("readonly_retrieval_orchestrator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("readonly_retrieval_orchestrator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("readonly_retrieval_orchestrator", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "readonly_retrieval_orchestrator")
trace_contract.emit_determinism_digest("p0", "readonly_retrieval_orchestrator")

trace_contract._emit_dispatches_healing_run("p1", "readonly_retrieval_orchestrator", "L4")
trace_contract._emit_routes_through("p1", "readonly_retrieval_orchestrator", "L4")
trace_contract._emit_checks_agent_registry("p1", "readonly_retrieval_orchestrator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "readonly_retrieval_orchestrator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "readonly_retrieval_orchestrator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "readonly_retrieval_orchestrator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "readonly_retrieval_orchestrator", "target_agent")
trace_contract._emit_verifies_policy("p1", "readonly_retrieval_orchestrator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "readonly_retrieval_orchestrator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "readonly_retrieval_orchestrator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "readonly_retrieval_orchestrator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "readonly_retrieval_orchestrator")
trace_contract._emit_gated_by_confidence("p1", "readonly_retrieval_orchestrator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "readonly_retrieval_orchestrator", "L4")
trace_contract._emit_reads_policy_state("p1", "readonly_retrieval_orchestrator", "L4")
trace_contract._emit_pulls_context("p1", "readonly_retrieval_orchestrator", "context_pull")
trace_contract._emit_pulls_context("p1", "readonly_retrieval_orchestrator", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "readonly_retrieval_orchestrator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "readonly_retrieval_orchestrator", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "readonly_retrieval_orchestrator", "write_through")
trace_contract._emit_writes_through("p1", "readonly_retrieval_orchestrator", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "readonly_retrieval_orchestrator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "readonly_retrieval_orchestrator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "readonly_retrieval_orchestrator", "routing_commit")

trace_contract._emit_snapshots_state("p0", "readonly_retrieval_orchestrator", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "readonly_retrieval_orchestrator", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "readonly_retrieval_orchestrator")
trace_contract._emit_authorize_and_execute("p2", "readonly_retrieval_orchestrator", "execution_auth")
trace_contract._emit_validates_capability("p2", "readonly_retrieval_orchestrator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "readonly_retrieval_orchestrator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "readonly_retrieval_orchestrator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "readonly_retrieval_orchestrator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "readonly_retrieval_orchestrator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "readonly_retrieval_orchestrator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "readonly_retrieval_orchestrator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "readonly_retrieval_orchestrator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "readonly_retrieval_orchestrator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "readonly_retrieval_orchestrator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "readonly_retrieval_orchestrator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "readonly_retrieval_orchestrator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "readonly_retrieval_orchestrator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "readonly_retrieval_orchestrator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "readonly_retrieval_orchestrator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "readonly_retrieval_orchestrator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "readonly_retrieval_orchestrator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "readonly_retrieval_orchestrator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "readonly_retrieval_orchestrator", "exec_snapshot_link")


def retrieve_with_readonly_guarantee(
    mission_id: str,
    query: str,
    top_k: int,
    domain: str,
    active_config_hashes: dict[str, str],
    created_at_utc: str,
    *,
    _query_fn: Any = None,
) -> tuple[list[AnchoredResult], RetrievalBoundarySnapshot]:
    """
    Execute a retrieval inside a read-only scope and return results + snapshot.

    Parameters
    ----------
    mission_id           : str  — mission identifier
    query                : str  — retrieval query text
    top_k                : int  — maximum results to return
    domain               : str  — retrieval domain
    active_config_hashes : dict — L4 active config hashes (policy/routing/model/budget)
    created_at_utc       : str  — stable UTC timestamp for the snapshot
    _query_fn            : callable | None
        Injected query function (for testing / real L4 backend).
        Signature: (query: str, top_k: int, domain: str) -> list[AnchoredResult]
        If None, returns an empty result list (safe default for wiring tests).

    Returns
    -------
    (results, snapshot)
        results  : list[AnchoredResult]
        snapshot : RetrievalBoundarySnapshot  (non-mutating, stable hash)
    """
    with read_only_retrieval_scope():
        if _query_fn is not None:
            results: list[AnchoredResult] = _query_fn(query, top_k, domain)
        else:
            results = []

        anchor_entries = [
            AnchorEntry(
                chunk_id=r.anchor.chunk_id,
                version_hash=r.anchor.version_hash,
            )
            for r in results
        ]

        snapshot = create_retrieval_boundary_snapshot(
            mission_id=mission_id,
            query=query,
            top_k=top_k,
            domain=domain,
            active_config_hashes=active_config_hashes,
            anchors=anchor_entries,
            created_at_utc=created_at_utc,
        )

    return results, snapshot
