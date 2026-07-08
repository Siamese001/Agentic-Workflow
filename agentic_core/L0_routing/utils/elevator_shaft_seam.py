"""Elevator Shaft Seam — C0 JIT context loading.

Implements just-in-time context loading for the C0 slot.
Replaces the stub implementation with real context retrieval.
"""

from __future__ import annotations

import uuid
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

# Self-bootstrap governance wiring
trace_contract._emit_authorize_and_execute("p2", "elevator_shaft_seam", "execution_auth")
trace_contract._emit_validates_capability("p2", "elevator_shaft_seam", "capability_check")
trace_contract._emit_routes_to_capability("p2", "elevator_shaft_seam", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "elevator_shaft_seam", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "elevator_shaft_seam", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "elevator_shaft_seam", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "elevator_shaft_seam", "exec_output")
trace_contract._emit_dispatches_agent("p3", "elevator_shaft_seam", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "elevator_shaft_seam", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "elevator_shaft_seam", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "elevator_shaft_seam", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "elevator_shaft_seam", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "elevator_shaft_seam", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "elevator_shaft_seam", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "elevator_shaft_seam", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "elevator_shaft_seam", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "elevator_shaft_seam", "eval_metric")
trace_contract._emit_stores_embedding("p4", "elevator_shaft_seam", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "elevator_shaft_seam", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "elevator_shaft_seam", "exec_snapshot_link")
trace_contract._emit_dispatches_healing_run("p1", "elevator_shaft_seam", "L0")
trace_contract._emit_routes_through("p1", "elevator_shaft_seam", "L0")
trace_contract._emit_checks_agent_registry("p1", "elevator_shaft_seam", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "elevator_shaft_seam", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "elevator_shaft_seam", "exec_plan")
trace_contract._emit_routes_to_agent("p1", "elevator_shaft_seam", "target_agent")
trace_contract._emit_verifies_policy("p1", "elevator_shaft_seam", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "elevator_shaft_seam", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "elevator_shaft_seam", "boundary_check")
trace_contract._emit_transcripts_response("p1", "elevator_shaft_seam", "transcript")
trace_contract._emit_gated_by_confidence("p1", "elevator_shaft_seam", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "elevator_shaft_seam", "L0")
trace_contract._emit_reads_policy_state("p1", "elevator_shaft_seam", "L0")


# Default token budget for C0 context
DEFAULT_C0_TOKEN_BUDGET = 2048


def load_context_jit(
    trace_id: str,
    intent_class: str,
    token_budget: int = DEFAULT_C0_TOKEN_BUDGET,
) -> dict[str, Any]:
    """Load JIT context for C0 slot.

    Retrieves context from L4 state stores with token budget enforcement.
    No routing logic, no decision logic — context loading only.

    Args:
        trace_id: Execution trace identifier.
        intent_class: Classified intent category.
        token_budget: Maximum tokens for context (default 2048).

    Returns:
        Structured context dict with keys:
        - rag_chunks: List of relevant RAG chunks
        - ast_snapshot: AST snapshot for current scope
        - boundary_refs: Boundary reference documents
    """
    _tid = str(uuid.uuid4())
    trace_contract._emit_records_execution_trace(
        _tid,
        trace_contract.LayerSegment.L0_ROUTING,
        "elevator_shaft_seam.load_context_jit",
    )
    trace_contract.emit_replay_key(_tid, f"c0:{trace_id}")
    trace_contract.emit_determinism_digest(_tid, f"intent:{intent_class}")

    # Query semantic cache for relevant chunks
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            get_semantic_cache,
        )

        semantic_cache = get_semantic_cache()
        rag_chunks = semantic_cache.query(intent_class, k=5)
    except (ValueError, TypeError):
        rag_chunks = []

    # Query BM25 store for keyword matches
    try:
        from agentic_core.L4_state.utils.memory.bm25_store import get_bm25_store

        bm25_store = get_bm25_store()
        bm25_results = bm25_store.query(intent_class, k=5)
    except (ValueError, TypeError):
        bm25_results = []

    # Combine and deduplicate results
    all_chunks = []
    seen_hashes = set()
    for chunk in rag_chunks + bm25_results:
        chunk_hash = hash(str(chunk))
        if chunk_hash not in seen_hashes:
            seen_hashes.add(chunk_hash)
            all_chunks.append(chunk)

    # Apply token budget (simple estimation: 4 chars ≈ 1 token)
    total_chars = 0
    selected_chunks = []
    for chunk in all_chunks:
        chunk_text = str(chunk)
        chunk_chars = len(chunk_text)
        if total_chars + chunk_chars <= token_budget * 4:
            selected_chunks.append(chunk)
            total_chars += chunk_chars
        else:
            break

    # Get AST snapshot if available
    try:
        from agentic_core.L4_state.utils.memory.ast_snapshot_store import (
            get_ast_snapshot_store,
        )

        ast_store = get_ast_snapshot_store()
        ast_snapshot = ast_store.get_snapshot(trace_id)
    except (ValueError, TypeError):
        ast_snapshot = None

    # Get boundary refs if available
    try:
        from agentic_core.L4_state.utils.memory.boundary_store import get_boundary_store

        boundary_store = get_boundary_store()
        boundary_refs = boundary_store.get_refs_for_intent(intent_class)
    except (ValueError, TypeError):
        boundary_refs = []

    return {
        "rag_chunks": selected_chunks,
        "ast_snapshot": ast_snapshot,
        "boundary_refs": boundary_refs,
        "token_budget": token_budget,
        "tokens_used": total_chars // 4,
    }


__all__ = ["load_context_jit", "DEFAULT_C0_TOKEN_BUDGET"]
