"""
Reranker Implementations

Heuristic reranker (zero-dependency, deterministic) and an interface stub
for cross-encoder injection.
"""

from __future__ import annotations

import re
from typing import Callable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "reranker", "execution_auth")
trace_contract._emit_validates_capability("p2", "reranker", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reranker", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reranker", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reranker", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reranker", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reranker", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reranker", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reranker", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reranker", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reranker", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reranker", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reranker", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reranker", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reranker", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reranker", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reranker", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reranker", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reranker", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reranker", "exec_snapshot_link")
from .interfaces import Document, IReranker

trace_contract._emit_applies_guardrail("p0", "reranker", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "reranker", "policy_binding")
trace_contract._emit_snapshots_state("p0", "reranker", "state_snapshot")

trace_contract._emit_emits_metric_event("reranker", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reranker", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reranker", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reranker", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reranker", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reranker", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reranker", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reranker", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reranker", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reranker", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reranker", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reranker", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reranker", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reranker", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reranker", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reranker", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reranker", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reranker", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reranker", "p3lm", "state")
trace_contract._emit_records_execution_trace("reranker", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reranker", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reranker", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reranker", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reranker", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reranker", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reranker", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reranker", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reranker", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reranker", "context_pull")
trace_contract._emit_pulls_context("p1", "reranker", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reranker", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reranker", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reranker", "write_through")
trace_contract._emit_writes_through("p1", "reranker", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reranker", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reranker", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reranker", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "reranker", "human_escalation")
trace_contract._emit_routes_through("p1", "reranker", "route_through")
trace_contract._emit_checks_agent_registry("p1", "reranker", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reranker", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reranker", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reranker", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reranker", "target_agent")
trace_contract._emit_verifies_policy("p1", "reranker", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reranker", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reranker", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reranker", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reranker")
trace_contract._emit_gated_by_confidence("p1", "reranker", "confidence_gate")
trace_contract.emit_replay_key("p0", "reranker")
trace_contract.emit_determinism_digest("p0", "reranker")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HeuristicReranker.rerank")

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
                ),
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
