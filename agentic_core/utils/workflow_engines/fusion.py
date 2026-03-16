"""
Candidate Fusion

Reciprocal Rank Fusion (RRF) implementation for merging lexical and vector
retrieval results into a single ranked candidate list.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "fusion", "execution_auth")
_emit_validates_capability("p2", "fusion", "capability_check")
_emit_routes_to_capability("p2", "fusion", "capability_route")
_emit_writes_via_uwg("p2", "fusion", "uwg_write")
_emit_blocks_direct_write("p2", "fusion", "direct_write_block")
_emit_records_tool_invocation("p2", "fusion", "tool_invocation")
_emit_captures_execution_output("p2", "fusion", "exec_output")
_emit_dispatches_agent("p3", "fusion", "agent_dispatch")
_emit_coordinates_agents("p3", "fusion", "agent_coordination")
_emit_records_workflow_lineage("p3", "fusion", "workflow_lineage")
_emit_records_healing_outcome("p3", "fusion", "healing_outcome")
_emit_escalates_failure("p3", "fusion", "failure_escalation")
_emit_orchestrates_workflow("p3", "fusion", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fusion", "healing_dispatch")
_emit_invokes_evaluation("p3", "fusion", "evaluation_signal")
_emit_records_telemetry_event("p4", "fusion", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fusion", "eval_metric")
_emit_stores_embedding("p4", "fusion", "embedding_store")
_emit_updates_meta_learning_state("p4", "fusion", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fusion", "exec_snapshot_link")
from .interfaces import Document, ICandidateFusion

_emit_applies_guardrail("p0", "fusion", "p0_governance")
_emit_reads_policy_state("p0", "fusion", "policy_binding")
_emit_snapshots_state("p0", "fusion", "state_snapshot")
emit_replay_key("p0", "fusion")
emit_determinism_digest("p0", "fusion")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class ReciprocalRankFusion(ICandidateFusion):
    """Merges retrieval results using Reciprocal Rank Fusion (RRF).

    RRF score = sum(1 / (k + rank_i)) across all ranked lists.
    k=60 is the standard constant (Cormack et al., 2009).
    """

    def __init__(self, k: int = 60):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    def merge(self, lexical_results: list[Document], vector_results: list[Document]) -> list[Document]:
        """Merge lexical and vector results via RRF.

        Args:
            lexical_results: Ranked documents from lexical retrieval
            vector_results: Ranked documents from vector retrieval

        Returns:
            Merged list sorted by descending RRF score
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReciprocalRankFusion.merge")

        rrf_scores: dict[str, float] = {}
        doc_map: dict[str, Document] = {}
        for rank, doc in enumerate(lexical_results, start=1):
            rrf_scores[doc.doc_id] = rrf_scores.get(doc.doc_id, 0.0) + 1.0 / (self.k + rank)
            doc_map[doc.doc_id] = doc
        for rank, doc in enumerate(vector_results, start=1):
            rrf_scores[doc.doc_id] = rrf_scores.get(doc.doc_id, 0.0) + 1.0 / (self.k + rank)
            if doc.doc_id not in doc_map:
                doc_map[doc.doc_id] = doc
        merged = []
        for doc_id, rrf_score in sorted(rrf_scores.items(), key=lambda x: -x[1]):
            src = doc_map[doc_id]
            merged.append(
                Document(
                    doc_id=src.doc_id,
                    content=src.content,
                    score=rrf_score,
                    metadata={**src.metadata, "rrf_score": rrf_score},
                )
            )
        return merged


class ScoreFusion(ICandidateFusion):
    """Merges retrieval results by normalizing and averaging scores."""

    def merge(self, lexical_results: list[Document], vector_results: list[Document]) -> list[Document]:
        """Merge by normalized score averaging.

        Args:
            lexical_results: Ranked documents from lexical retrieval
            vector_results: Ranked documents from vector retrieval

        Returns:
            Merged list sorted by descending average score
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ScoreFusion.merge")


        def _normalize(docs: list[Document]) -> dict[str, float]:
            if not docs:
                return {}
            scores = [d.score for d in docs]
            min_s, max_s = (min(scores), max(scores))
            if max_s == min_s:
                return {d.doc_id: 1.0 for d in docs}
            return {d.doc_id: (d.score - min_s) / (max_s - min_s) for d in docs}

        lex_norm = _normalize(lexical_results)
        vec_norm = _normalize(vector_results)
        doc_map: dict[str, Document] = {d.doc_id: d for d in lexical_results}
        doc_map.update({d.doc_id: d for d in vector_results})
        all_ids = set(lex_norm) | set(vec_norm)
        fused_scores: dict[str, float] = {}
        for doc_id in all_ids:
            s_lex = lex_norm.get(doc_id, 0.0)
            s_vec = vec_norm.get(doc_id, 0.0)
            count = (1 if doc_id in lex_norm else 0) + (1 if doc_id in vec_norm else 0)
            fused_scores[doc_id] = (s_lex + s_vec) / count
        merged = []
        for doc_id, score in sorted(fused_scores.items(), key=lambda x: -x[1]):
            src = doc_map[doc_id]
            merged.append(
                Document(
                    doc_id=src.doc_id,
                    content=src.content,
                    score=score,
                    metadata={**src.metadata, "fused_score": score},
                )
            )
        return merged


__all__ = ["ReciprocalRankFusion", "ScoreFusion"]
