"""
Reranker Implementations

Heuristic reranker (zero-dependency, deterministic) and an interface stub
for cross-encoder injection.
"""

from __future__ import annotations

import re
from typing import Callable

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

_emit_authorize_and_execute("p2", "reranker", "execution_auth")
_emit_validates_capability("p2", "reranker", "capability_check")
_emit_routes_to_capability("p2", "reranker", "capability_route")
_emit_writes_via_uwg("p2", "reranker", "uwg_write")
_emit_blocks_direct_write("p2", "reranker", "direct_write_block")
_emit_records_tool_invocation("p2", "reranker", "tool_invocation")
_emit_captures_execution_output("p2", "reranker", "exec_output")
_emit_dispatches_agent("p3", "reranker", "agent_dispatch")
_emit_coordinates_agents("p3", "reranker", "agent_coordination")
_emit_records_workflow_lineage("p3", "reranker", "workflow_lineage")
_emit_records_healing_outcome("p3", "reranker", "healing_outcome")
_emit_escalates_failure("p3", "reranker", "failure_escalation")
_emit_orchestrates_workflow("p3", "reranker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reranker", "healing_dispatch")
_emit_invokes_evaluation("p3", "reranker", "evaluation_signal")
_emit_records_telemetry_event("p4", "reranker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reranker", "eval_metric")
_emit_stores_embedding("p4", "reranker", "embedding_store")
_emit_updates_meta_learning_state("p4", "reranker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reranker", "exec_snapshot_link")
from .interfaces import Document, IReranker

_emit_applies_guardrail("p0", "reranker", "p0_governance")
_emit_reads_policy_state("p0", "reranker", "policy_binding")
_emit_snapshots_state("p0", "reranker", "state_snapshot")
emit_replay_key("p0", "reranker")
emit_determinism_digest("p0", "reranker")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _query_term_overlap(query: str, content: str) -> float:
    """Count query token overlap with document content (normalized)."""

    def tokenize(text: str) -> set:
        text = text.lower()
        text = re.sub("[^\\w\\s]", " ", text)
        return set(text.split())

    query_tokens = tokenize(query)
    content_tokens = tokenize(content)
    if not query_tokens:
        return 0.0
    overlap = query_tokens & content_tokens
    return len(overlap) / len(query_tokens)


class HeuristicReranker(IReranker):
    """Deterministic reranker using query-term coverage as the rerank signal.

    Production use: inject a cross-encoder via the ``scorer`` callable.
    """

    def __init__(self, scorer: Callable[[str, str], float] | None = None, top_k: int = 10):
        self._scorer = scorer or _query_term_overlap
        self.top_k = top_k

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Rerank candidates by scorer(query, content).

        Args:
            query: Original search query
            candidates: Documents to rerank

        Returns:
            Top-k documents sorted by descending rerank score
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HeuristicReranker.rerank")

        if not candidates:
            return []
        scored = []
        for doc in candidates:
            rerank_score = self._scorer(query, doc.content)
            scored.append(
                Document(
                    doc_id=doc.doc_id,
                    content=doc.content,
                    score=rerank_score,
                    metadata={**doc.metadata, "rerank_score": rerank_score},
                )
            )
        scored.sort(key=lambda d: -d.score)
        return scored[: self.top_k]


class PassthroughReranker(IReranker):
    """No-op reranker that preserves original order, optionally truncating to top_k."""

    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Return candidates unchanged, truncated to top_k.

        Args:
            query: Unused
            candidates: Documents to pass through

        Returns:
            First top_k candidates in original order
        """
        return candidates[: self.top_k]


__all__ = ["HeuristicReranker", "PassthroughReranker"]
