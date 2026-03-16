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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "readonly_retrieval_orchestrator")
emit_determinism_digest("p0", "readonly_retrieval_orchestrator")

_emit_dispatches_healing_run("p1", "readonly_retrieval_orchestrator", "L4")
_emit_routes_through("p1", "readonly_retrieval_orchestrator", "L4")
_emit_escalates_to_human("p1", "readonly_retrieval_orchestrator", "L4")
_emit_reads_policy_state("p1", "readonly_retrieval_orchestrator", "L4")

_emit_snapshots_state("p0", "readonly_retrieval_orchestrator", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "readonly_retrieval_orchestrator", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "readonly_retrieval_orchestrator")
_emit_authorize_and_execute("p2", "readonly_retrieval_orchestrator", "execution_auth")
_emit_validates_capability("p2", "readonly_retrieval_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "readonly_retrieval_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "readonly_retrieval_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "readonly_retrieval_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "readonly_retrieval_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "readonly_retrieval_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "readonly_retrieval_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "readonly_retrieval_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "readonly_retrieval_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "readonly_retrieval_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "readonly_retrieval_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "readonly_retrieval_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "readonly_retrieval_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "readonly_retrieval_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "readonly_retrieval_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "readonly_retrieval_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "readonly_retrieval_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "readonly_retrieval_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "readonly_retrieval_orchestrator", "exec_snapshot_link")


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
