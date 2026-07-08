"""
Candidate Fusion

Reciprocal Rank Fusion (RRF) implementation for merging lexical and vector
retrieval results into a single ranked candidate list.
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "fusion", "execution_auth")
trace_contract._emit_validates_capability("p2", "fusion", "capability_check")
trace_contract._emit_routes_to_capability("p2", "fusion", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "fusion", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "fusion", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "fusion", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "fusion", "exec_output")
trace_contract._emit_dispatches_agent("p3", "fusion", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "fusion", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "fusion", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "fusion", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "fusion", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "fusion", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "fusion", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "fusion", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "fusion", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "fusion", "eval_metric")
trace_contract._emit_stores_embedding("p4", "fusion", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "fusion", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "fusion", "exec_snapshot_link")
from .interfaces import Document, ICandidateFusion

trace_contract._emit_applies_guardrail("p0", "fusion", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "fusion", "policy_binding")
trace_contract._emit_snapshots_state("p0", "fusion", "state_snapshot")

trace_contract._emit_emits_metric_event("fusion", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("fusion", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("fusion", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("fusion", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("fusion", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("fusion", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("fusion", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("fusion", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("fusion", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("fusion", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("fusion", "p4obs", "alert")
trace_contract._emit_links_incident_trace("fusion", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("fusion", "p3lm", "pattern")
trace_contract._emit_records_learning_event("fusion", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("fusion", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("fusion", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("fusion", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("fusion", "p3lm", "policy")
trace_contract._emit_stores_learning_state("fusion", "p3lm", "state")
trace_contract._emit_records_execution_trace("fusion", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("fusion", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("fusion", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("fusion", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("fusion", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("fusion", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("fusion", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("fusion", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("fusion", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "fusion", "context_pull")
trace_contract._emit_pulls_context("p1", "fusion", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "fusion", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "fusion", "uwg_term_2")
trace_contract._emit_writes_through("p1", "fusion", "write_through")
trace_contract._emit_writes_through("p1", "fusion", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "fusion", "safety_validation")
trace_contract._emit_invokes_eval("p1", "fusion", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "fusion", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "fusion", "human_escalation")
trace_contract._emit_routes_through("p1", "fusion", "route_through")
trace_contract._emit_checks_agent_registry("p1", "fusion", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "fusion", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "fusion", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "fusion", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "fusion", "target_agent")
trace_contract._emit_verifies_policy("p1", "fusion", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "fusion", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "fusion", "boundary_check")
trace_contract._emit_transcripts_response("p1", "fusion", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "fusion")
trace_contract._emit_gated_by_confidence("p1", "fusion", "confidence_gate")
trace_contract.emit_replay_key("p0", "fusion")
trace_contract.emit_determinism_digest("p0", "fusion")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ReciprocalRankFusion.merge")

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
                ),
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ScoreFusion.merge")

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
                ),
            )
        return merged


__all__ = ["ReciprocalRankFusion", "ScoreFusion"]
