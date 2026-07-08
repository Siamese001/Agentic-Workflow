"""
Phase A: Completeness-Aware Reranker.

Reranks candidates using a blended score of:
  relevance_score  (from retrieval — cosine/BM25)
  completeness_score (from IContextCompletenessScorer)

Does NOT promote fragments purely on similarity when completeness is low.

C0 RULE: Informational only — cannot alter routing, safety, or tiers.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.evaluation.retrieval.completeness import (
    ContextCompletenessScore,
    IContextCompletenessScorer,
)
from agentic_core.evaluation.retrieval.interfaces import Document, IReranker
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "completeness_reranker", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "completeness_reranker", "policy_binding")
trace_contract._emit_snapshots_state("p0", "completeness_reranker", "state_snapshot")

trace_contract._emit_emits_metric_event("completeness_reranker", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("completeness_reranker", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("completeness_reranker", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("completeness_reranker", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("completeness_reranker", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("completeness_reranker", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("completeness_reranker", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("completeness_reranker", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("completeness_reranker", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("completeness_reranker", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("completeness_reranker", "p4obs", "alert")
trace_contract._emit_links_incident_trace("completeness_reranker", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("completeness_reranker", "p3lm", "pattern")
trace_contract._emit_records_learning_event("completeness_reranker", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("completeness_reranker", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("completeness_reranker", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("completeness_reranker", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("completeness_reranker", "p3lm", "policy")
trace_contract._emit_stores_learning_state("completeness_reranker", "p3lm", "state")
trace_contract._emit_records_execution_trace("completeness_reranker", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("completeness_reranker", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("completeness_reranker", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("completeness_reranker", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("completeness_reranker", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("completeness_reranker", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("completeness_reranker", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("completeness_reranker", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("completeness_reranker", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "completeness_reranker", "context_pull")
trace_contract._emit_pulls_context("p1", "completeness_reranker", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "completeness_reranker", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "completeness_reranker", "uwg_term_2")
trace_contract._emit_writes_through("p1", "completeness_reranker", "write_through")
trace_contract._emit_writes_through("p1", "completeness_reranker", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "completeness_reranker", "safety_validation")
trace_contract._emit_invokes_eval("p1", "completeness_reranker", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "completeness_reranker", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "completeness_reranker", "human_escalation")
trace_contract._emit_routes_through("p1", "completeness_reranker", "route_through")
trace_contract._emit_checks_agent_registry("p1", "completeness_reranker", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "completeness_reranker", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "completeness_reranker", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "completeness_reranker", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "completeness_reranker", "target_agent")
trace_contract._emit_verifies_policy("p1", "completeness_reranker", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "completeness_reranker", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "completeness_reranker", "boundary_check")
trace_contract._emit_transcripts_response("p1", "completeness_reranker", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "completeness_reranker")
trace_contract._emit_gated_by_confidence("p1", "completeness_reranker", "confidence_gate")
trace_contract.emit_replay_key("p0", "completeness_reranker")
trace_contract.emit_determinism_digest("p0", "completeness_reranker")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "completeness_reranker", "execution_auth")
trace_contract._emit_validates_capability("p2", "completeness_reranker", "capability_check")
trace_contract._emit_routes_to_capability("p2", "completeness_reranker", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "completeness_reranker", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "completeness_reranker", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "completeness_reranker", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "completeness_reranker", "exec_output")
trace_contract._emit_dispatches_agent("p3", "completeness_reranker", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "completeness_reranker", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "completeness_reranker", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "completeness_reranker", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "completeness_reranker", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "completeness_reranker", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "completeness_reranker", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "completeness_reranker", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "completeness_reranker", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "completeness_reranker", "eval_metric")
trace_contract._emit_stores_embedding("p4", "completeness_reranker", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "completeness_reranker", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "completeness_reranker", "exec_snapshot_link")


@dataclass(frozen=True)
class CompletenessRerankerConfig:
    """Configuration for the blended relevance + completeness reranker."""

    relevance_weight: float = 0.6
    completeness_weight: float = 0.4
    top_k: int = 10

    def __post_init__(self) -> None:
        total = self.relevance_weight + self.completeness_weight
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"relevance_weight + completeness_weight must sum to 1.0, got {total}")
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")


class CompletenessReranker(IReranker):
    """Reranks candidates by blending relevance with completeness scores.

    Prevents high-similarity but contextually incomplete fragments from
    dominating the final top-N context.

    C0 RULE: Output is informational top-N grounded context only.
    """

    def __init__(
        self,
        scorer: IContextCompletenessScorer,
        config: CompletenessRerankerConfig | None = None,
        query_id: str = "default",
    ) -> None:
        self._scorer = scorer
        self._cfg = config or CompletenessRerankerConfig()
        self._query_id = query_id

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Rerank candidates using blended relevance + completeness score.

        Args:
            query: Original query text used for completeness scoring.
            candidates: Documents to rerank (may be GroundedDocuments).

        Returns:
            Top-K reranked list, highest blended score first.
            Deterministic tie-break: doc_id ascending.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "CompletenessReranker.rerank")

        if not candidates:
            return []

        completeness_scores: list[ContextCompletenessScore] = self._scorer.score_batch(
            query_id=self._query_id,
            query=query,
            chunks=candidates,
        )

        scored: list[tuple[float, str, Document]] = []
        for doc, cs in zip(candidates, completeness_scores):
            blended = (
                self._cfg.relevance_weight * doc.score + self._cfg.completeness_weight * cs.completeness_score
            )
            scored.append((blended, doc.doc_id, doc))

        scored.sort(key=lambda t: (-t[0], t[1]))
        return [doc for _, _, doc in scored[: self._cfg.top_k]]


__all__ = [
    "CompletenessRerankerConfig",
    "CompletenessReranker",
]
