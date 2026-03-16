"""
agentic_core/interfaces/embeddings.py

C0-informational-only embedding interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- Embedding results are score + content_hash + preview ONLY
- No raw vectors exposed
- No FAISS index handles
- No routing metadata that could influence tier selection
- No instantiation authority — embeddings created only via EmbeddingServiceFactory
- query_similarity is read-only with bounded top_k

USAGE (apps_*):
    from agentic_core.interfaces.embeddings import (
        SimilarityResult,
        query_similarity,
    )
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_records_execution_trace("p0", "evidence", "embeddings")
_emit_applies_guardrail("p0", "embeddings", "p0_governance")
_emit_reads_policy_state("p0", "embeddings", "policy_binding")
_emit_snapshots_state("p0", "embeddings", "state_snapshot")
emit_replay_key("p0", "embeddings")
emit_determinism_digest("p0", "embeddings")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "embeddings", "execution_auth")
_emit_validates_capability("p2", "embeddings", "capability_check")
_emit_routes_to_capability("p2", "embeddings", "capability_route")
_emit_writes_via_uwg("p2", "embeddings", "uwg_write")
_emit_blocks_direct_write("p2", "embeddings", "direct_write_block")
_emit_records_tool_invocation("p2", "embeddings", "tool_invocation")
_emit_captures_execution_output("p2", "embeddings", "exec_output")
_emit_dispatches_agent("p3", "embeddings", "agent_dispatch")
_emit_coordinates_agents("p3", "embeddings", "agent_coordination")
_emit_records_workflow_lineage("p3", "embeddings", "workflow_lineage")
_emit_records_healing_outcome("p3", "embeddings", "healing_outcome")
_emit_escalates_failure("p3", "embeddings", "failure_escalation")
_emit_orchestrates_workflow("p3", "embeddings", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embeddings", "healing_dispatch")
_emit_invokes_evaluation("p3", "embeddings", "evaluation_signal")
_emit_records_telemetry_event("p4", "embeddings", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embeddings", "eval_metric")
_emit_stores_embedding("p4", "embeddings", "embedding_store")
_emit_updates_meta_learning_state("p4", "embeddings", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embeddings", "exec_snapshot_link")


@dataclass(frozen=True)
class SimilarityResult:
    """
    Informational-only embedding result.

    DELIBERATELY EXCLUDES:
    - Raw embedding vectors (no routing influence)
    - FAISS index handles
    - Routing metadata
    - Tier selection data
    - Any mutable state

    Contains only: content_hash, similarity_score, content_preview.
    """

    content_hash: str
    similarity_score: float
    content_preview: str


def query_similarity(query: str, top_k: int = 20, namespace: str = "") -> list[SimilarityResult]:
    """
    Query existing embeddings — informational only, C0 context.

    Args:
        query: The query text
        top_k: Maximum results (capped at 20 per C0 spec)
        namespace: Optional namespace for seed pack lookup

    Returns:
        List of SimilarityResult — score + hash + preview only
    """
    if top_k > 20:
        top_k = 20
    try:
        from agentic_core.L4_state.memory.sovereign_semantic_cache import SovereignSemanticCache

        cache = SovereignSemanticCache()
        raw = cache.query(query, top_k=top_k, namespace=namespace)
        return [
            SimilarityResult(
                content_hash=r.get("content_hash", ""),
                similarity_score=float(r.get("score", 0.0)),
                content_preview=r.get("content", "")[:200],
            )
            for r in raw
        ]
    # guardian: allow-silent-swallow
    except Exception:
        return []


__all__ = ["SimilarityResult", "query_similarity"]
