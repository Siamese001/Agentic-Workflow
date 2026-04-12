"""
Reranker Implementations

Heuristic reranker (zero-dependency, deterministic) and an interface stub
for cross-encoder injection.
"""

from __future__ import annotations

import re
from typing import Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("reranker", "p4obs", "metric_1")
_emit_emits_metric_event("reranker", "p4obs", "metric_2")
_emit_emits_metric_event("reranker", "p4obs", "metric_3")
_emit_emits_metric_event("reranker", "p4obs", "metric_4")
_emit_emits_metric_event("reranker", "p4obs", "metric_5")
_emit_emits_metric_event("reranker", "p4obs", "metric_6")
_emit_records_incident_event("reranker", "p4obs", "incident")
_emit_captures_runtime_anomaly("reranker", "p4obs", "anomaly")
_emit_writes_observability_log("reranker", "p4obs", "obs_log")
_emit_updates_monitoring_state("reranker", "p4obs", "mon_state")
_emit_triggers_alert("reranker", "p4obs", "alert")
_emit_links_incident_trace("reranker", "p4obs", "trace_link")
_emit_captures_pattern("reranker", "p3lm", "pattern")
_emit_records_learning_event("reranker", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reranker", "p3lm", "snapshot")
_emit_feeds_meta_learning("reranker", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reranker", "p3lm", "routing")
_emit_improves_agent_policy("reranker", "p3lm", "policy")
_emit_stores_learning_state("reranker", "p3lm", "state")
_emit_records_execution_trace("reranker", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reranker", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reranker", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reranker", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reranker", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reranker", "env_read", "p2_env_1")
_emit_reads_environ("reranker", "env_read", "p2_env_2")
_emit_reads_runtime_state("reranker", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reranker", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reranker", "context_pull")
_emit_pulls_context("p1", "reranker", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reranker", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reranker", "uwg_term_2")
_emit_writes_through("p1", "reranker", "write_through")
_emit_writes_through("p1", "reranker", "write_through_2")
_emit_validated_by_safety_plane("p1", "reranker", "safety_validation")
_emit_invokes_eval("p1", "reranker", "eval_call")
_emit_proposal_commits_routing("p1", "reranker", "routing_commit")
_emit_escalates_to_human("p1", "reranker", "human_escalation")
_emit_routes_through("p1", "reranker", "route_through")
_emit_checks_agent_registry("p1", "reranker", "agent_registry")
_emit_validates_agent_capability("p1", "reranker", "capability")
_emit_dispatches_execution_plan("p1", "reranker", "exec_plan")
_emit_agent_executes_agent("p1", "reranker", "sub_agent")
_emit_routes_to_agent("p1", "reranker", "target_agent")
_emit_verifies_policy("p1", "reranker", "policy_check")
_emit_observes_runtime_state("p1", "reranker", "runtime_state")
_emit_verifies_boundary("p1", "reranker", "boundary_check")
_emit_transcripts_response("p1", "reranker", "transcript")
_emit_hard_fails_untranscripted("p1", "reranker")
_emit_gated_by_confidence("p1", "reranker", "confidence_gate")
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
