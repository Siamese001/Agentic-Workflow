"""Tests for SemanticIndexRegistry and integration pipelines.

Covers:
  - SemanticIndexRegistry — all 8 indexes, buffer snapshot, export,
    delegation methods, custom buffer sizes
  - Creative registry methods: total_buffer_utilization,
    cross_index_health_report, bulk_evict_by_trace_id,
    index_namespace_map
  - Integration: full addendum pipeline, multi-method pipelines,
    registry health transitions
"""

from __future__ import annotations

import threading

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_bge_embedding_registry")
# REMOVED: _emit_applies_guardrail("p0", "test_bge_embedding_registry", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_bge_embedding_registry", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_bge_embedding_registry", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_registry", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_registry", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_registry", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_registry", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_registry", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_bge_embedding_registry", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_bge_embedding_registry", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_bge_embedding_registry", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_bge_embedding_registry", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_bge_embedding_registry", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_bge_embedding_registry", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_bge_embedding_registry", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_bge_embedding_registry", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_bge_embedding_registry", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_bge_embedding_registry", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_bge_embedding_registry", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_bge_embedding_registry", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_bge_embedding_registry", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_registry", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_registry", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_registry", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_registry", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_registry", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_bge_embedding_registry", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_bge_embedding_registry", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_bge_embedding_registry", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_bge_embedding_registry", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_bge_embedding_registry", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_bge_embedding_registry", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_bge_embedding_registry", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_bge_embedding_registry", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_bge_embedding_registry", "write_through")
# REMOVED: _emit_writes_through("p1", "test_bge_embedding_registry", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_bge_embedding_registry", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_bge_embedding_registry", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_bge_embedding_registry", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_bge_embedding_registry", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_bge_embedding_registry", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_bge_embedding_registry", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_bge_embedding_registry", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_bge_embedding_registry", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_bge_embedding_registry", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_bge_embedding_registry", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_bge_embedding_registry", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_bge_embedding_registry", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_bge_embedding_registry", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_bge_embedding_registry", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_bge_embedding_registry")
# REMOVED: _emit_gated_by_confidence("p1", "test_bge_embedding_registry", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_bge_embedding_registry")
# REMOVED: emit_determinism_digest("p0", "test_bge_embedding_registry")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_bge_embedding_registry", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_bge_embedding_registry", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_bge_embedding_registry", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_bge_embedding_registry", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_bge_embedding_registry", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_bge_embedding_registry", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_bge_embedding_registry", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_bge_embedding_registry", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_bge_embedding_registry", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_bge_embedding_registry", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_bge_embedding_registry", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_bge_embedding_registry", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_bge_embedding_registry", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_bge_embedding_registry", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_bge_embedding_registry", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_bge_embedding_registry", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_bge_embedding_registry", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_bge_embedding_registry", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_bge_embedding_registry", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_bge_embedding_registry", "exec_snapshot_link")

# ============================================================
# Constants
# ============================================================

_TS = 1_700_200_000
_TS2 = 1_700_300_000
_RK = "rk-" + "a" * 60
_DD = "dd-" + "b" * 60
_PH = "ph-" + "c" * 60
_TID = "tr-001"

_RK_A = "rka-" + "a" * 59
_RK_B = "rkb-" + "b" * 59


# ============================================================
# Builder helpers
# ============================================================


def _rfr(
    failure_id: str = "fail-001",
    summary: str = "L3 hash mismatch on replay",
    nd_type: str = "HASH_MISMATCH",
    mismatch: str = "determinism digest differed between runs",
    subsystems: tuple = ("L3_orchestration", "L0_routing"),
    remediation: str = "re-seed determinism context",
    replay_key: str = _RK,
    dd: str = _DD,
    trace_id: str = _TID,
    ts: int = _TS,
):
#  # MOVED: from system_learning.types.semantic_memory_types import ReplayFailureRecord

    return ReplayFailureRecord(
        failure_id=failure_id,
        failure_summary=summary,
        nondeterminism_type=nd_type,
        mismatch_explanation=mismatch,
        affected_subsystems=subsystems,
        attempted_remediation=remediation,
        replay_key=replay_key,
        determinism_digest=dd,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _poem(
    record_id: str = "poem-001",
    s0: str = "system prompt: govern routing",
    d0: str = "domain knowledge: enterprise SaaS",
    i0: str = "instruction: classify intent",
    c0: str = "context: retrieved 5 chunks",
    u0: str = "user: find my order status",
    task: str = "classify customer intent",
    answer: str = "ORDER_STATUS with confidence 0.92",
    safety: str = "ALLOWED",
    grounding: str = "3 of 5 chunks matched",
    prompt_hash: str = "prh-" + "d" * 59,
    template_id: str = "tmpl-v3",
    route: str = "L2_STANDARD",
    model: str = "gpt-4o-mini",
    policy_hash: str = _PH,
    trace_id: str = _TID,
    ts: int = _TS,
):
#  # MOVED: from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

    return PromptOutcomeEmbeddingRecord(
        record_id=record_id,
        slot_s0_summary=s0,
        slot_d0_summary=d0,
        slot_i0_summary=i0,
        slot_c0_summary=c0,
        slot_u0_summary=u0,
        task_description=task,
        answer_summary=answer,
        safety_outcome=safety,
        retrieval_grounding_summary=grounding,
        prompt_hash=prompt_hash,
        template_id=template_id,
        route=route,
        model=model,
        policy_hash=policy_hash,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _rcr(
    case_id: str = "rc-001",
    query: str = "what is the refund policy?",
    chunks: tuple = ("refund policy text", "return window details"),
    support_reasoning: str = "both chunks directly answer the query",
    quality: str = "high quality, complete answer",
    query_id: str = "qid-001",
    chunk_ids: tuple = ("cid-001", "cid-002"),
    support_score: float = 0.85,
    completeness_score: float = 0.90,
    escalation_flag: bool = False,
    healer_invoked: bool = False,
    replay_pass: bool = True,
    trace_id: str = _TID,
    ts: int = _TS,
):
#  # MOVED: from system_learning.types.semantic_memory_types import RetrievalCaseRecord

    return RetrievalCaseRecord(
        case_id=case_id,
        query_summary=query,
        chunk_summaries=chunks,
        support_reasoning=support_reasoning,
        answer_quality_summary=quality,
        query_id=query_id,
        chunk_ids=chunk_ids,
        support_score=support_score,
        completeness_score=completeness_score,
        escalation_flag=escalation_flag,
        healer_invoked=healer_invoked,
        replay_pass=replay_pass,
        trace_id=trace_id,
        timestamp_utc=ts,
    )


def _registry(**kwargs):
#  # MOVED: from system_learning.engines.semantic_index_registry import SemanticIndexRegistry

    return SemanticIndexRegistry(**kwargs)


# ============================================================
# 7. SemanticIndexRegistry — core ingest/export/delegation
# ============================================================


class TestSemanticIndexRegistry:
    def test_construction_with_defaults(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.types.semantic_memory_types import ReplayFailureRecord
        from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord
        from system_learning.engines.semantic_index_registry import SemanticIndexRegistry
        from system_learning.types.semantic_memory_types import IncidentBundle
        from system_learning.engines.semantic_index_registry import INDEX_INCIDENT
        from system_learning.engines.semantic_index_registry import INDEX_GRAPH
        from system_learning.types.semantic_memory_types import GraphNeighborhood
        from system_learning.engines.semantic_index_registry import INDEX_MUTATION
        from system_learning.types.semantic_memory_types import MutationDiffRecord
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        from system_learning.engines.semantic_index_registry import INDEX_RETRIEVAL
        from system_learning.engines.semantic_index_registry import INDEX_REPLAY
        from system_learning.engines.semantic_index_registry import INDEX_PREFERENCE
        from system_learning.types.semantic_memory_types import PathDPreferencePair
        from system_learning.engines.semantic_index_registry import INDEX_GUARDRAIL
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase
        from system_learning.types.semantic_memory_types import IncidentBundle
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        from system_learning.engines.semantic_index_registry import (
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        from system_learning.engines.semantic_index_registry import ALL_INDEXES
        from system_learning.engines.semantic_index_registry import (
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
        from system_learning.types.semantic_memory_types import (
        from system_learning.engines.semantic_index_registry import INDEX_PROMPT
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder
        r = _registry()
        snap = r.buffer_snapshot()
        assert snap.total == 0

    def test_ingest_incident(self):
#  # MOVED: from system_learning.types.semantic_memory_types import IncidentBundle

        r = _registry()
        bundle = IncidentBundle(
            trace_id="tr-i",
            trace_summary="L3 routing failure",
            violations=("V1", "V2"),
            route_path="L0->L2->L3",
            tool_capability="route",
            state_diff_summary="threshold changed",
            healer_id="h1",
            outcome="failure",
            policy_hash=_PH,
            timestamp_utc=_TS,
        )
        result = r.ingest_incident(bundle)
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_INCIDENT

        assert result.index_name == INDEX_INCIDENT
        assert r.buffer_snapshot().incident_index == 1

    def test_ingest_graph_neighborhood(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_GRAPH
#  # MOVED: from system_learning.types.semantic_memory_types import GraphNeighborhood

        r = _registry()
        n = GraphNeighborhood(
            node_id="n1",
            node_type="Engine",
            layer="L3",
            inbound_relations=("GOVERNS",),
            outbound_relations=("ROUTES_TO",),
            governance_edges=("POLICY_EDGE",),
            mutation_edges=("MUT_1",),
            ownership_territory="apps_rg",
            risk_label="HIGH",
        )
        res = r.ingest_graph_neighborhood(n)
        assert res.index_name == INDEX_GRAPH
        assert r.buffer_snapshot().graph_index == 1

    def test_ingest_mutation(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_MUTATION
#  # MOVED: from system_learning.types.semantic_memory_types import MutationDiffRecord

        r = _registry()
        m = MutationDiffRecord(
            mutation_id="m1",
            target_resource="config/thresholds.json",
            operations=("op:add:/threshold",),
            state_diff_summary="threshold 0.8->0.9",
            rollback_context="revert to 0.8",
            commit_outcome="committed",
            trace_id="tr-m",
            policy_hash=_PH,
            timestamp_utc=_TS,
        )
        res = r.ingest_mutation(m)
        assert res.index_name == INDEX_MUTATION
        assert r.buffer_snapshot().mutation_index == 1

    def test_ingest_prompt_outcome(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_PROMPT

        r = _registry()
        res = r.ingest_prompt_outcome(_poem())
        assert res.index_name == INDEX_PROMPT
        assert r.buffer_snapshot().prompt_index == 1

    def test_ingest_retrieval_case(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_RETRIEVAL

        r = _registry()
        res = r.ingest_retrieval_case(_rcr())
        assert res.index_name == INDEX_RETRIEVAL
        assert r.buffer_snapshot().retrieval_index == 1

    def test_ingest_replay_failure(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_REPLAY

        r = _registry()
        res = r.ingest_replay_failure(_rfr())
        assert res.index_name == INDEX_REPLAY
        assert r.buffer_snapshot().replay_index == 1

    def test_ingest_preference(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_PREFERENCE
#  # MOVED: from system_learning.types.semantic_memory_types import PathDPreferencePair

        r = _registry()
        p = PathDPreferencePair(
            decision_id="d1",
            original_plan="do X",
            human_patch="do Y instead",
            decision="modified",
            reason="X was risky",
            resulting_outcome="success",
            agent="PlannerAgent",
            trace_id="tr-p",
            timestamp_utc=_TS,
        )
        res = r.ingest_preference(p)
        assert res.index_name == INDEX_PREFERENCE
        assert r.buffer_snapshot().preference_index == 1

    def test_ingest_guardrail_case(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_GUARDRAIL
#  # MOVED: from system_learning.types.semantic_memory_types import PolicyGuardrailCase

        r = _registry()
        c = PolicyGuardrailCase(
            case_id="gc-001",
            blocked_payload_summary="SQL inject",
            remediation_text="sanitize",
            policy_hash=_PH,
            policy_root="root_sql",
            verdict="true_positive",
            strictness_level="HIGH",
            trace_id="tr-gc",
            timestamp_utc=_TS,
        )
        res = r.ingest_guardrail_case(c)
        assert res.index_name == INDEX_GUARDRAIL
        assert r.buffer_snapshot().guardrail_index == 1

    def test_buffer_snapshot_total_tracks_all_indexes(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        r.ingest_retrieval_case(_rcr())
        snap = r.buffer_snapshot()
        assert snap.total == 3

    def test_export_all_corpus_records_returns_all_index_keys(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import ALL_INDEXES

        r = _registry()
        r.ingest_prompt_outcome(_poem())
        dump = r.export_all_corpus_records()
        assert set(dump.keys()) == ALL_INDEXES

    def test_export_records_are_sorted(self):
        r = _registry()
        for i in range(5):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}", trace_id=f"t{i}", task=f"task{i}"))
        dump = r.export_all_corpus_records()
        records = dump["prompt_index"]
        keys = [(rec.content_hash, rec.trace_id) for rec in records]
        assert keys == sorted(keys)

    def test_retrieval_quality_summary_delegates_to_retrieval_embedder(self):
        r = _registry()
        r.ingest_retrieval_case(
            _rcr(support_score=0.6, completeness_score=0.7, case_id="c0", query="q0", chunk_ids=("x0",))
        )
        s = r.retrieval_quality_summary()
        assert s["count"] == 1
        assert abs(s["avg_support_score"] - 0.6) < 1e-4

    def test_prompt_safety_outcome_stats_delegates(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem(safety="BLOCKED", record_id="b1", trace_id="tb1", task="task-b"))
        stats = r.prompt_safety_outcome_stats()
        assert stats["BLOCKED"] == 1
        assert stats["ALLOWED"] == 0

    def test_replay_nondeterminism_stats_delegates(self):
        r = _registry()
        r.ingest_replay_failure(_rfr(nd_type="TIMING_DEPENDENCY"))
        stats = r.replay_nondeterminism_stats()
        assert stats.get("TIMING_DEPENDENCY", 0) == 1

    def test_guardrail_verdict_stats_delegates(self):
#  # MOVED: from system_learning.types.semantic_memory_types import PolicyGuardrailCase

        r = _registry()
        r.ingest_guardrail_case(
            PolicyGuardrailCase(
                case_id="gv1",
                blocked_payload_summary="p",
                remediation_text="r",
                policy_hash=_PH,
                policy_root="root",
                verdict="false_positive",
                strictness_level="LOW",
                trace_id="tr-gv1",
                timestamp_utc=_TS,
            )
        )
        stats = r.guardrail_verdict_stats()
        assert stats["false_positive"] == 1

    def test_custom_buffer_sizes_respected(self):
        r = _registry(incident_buffer=5, prompt_buffer=3)
        for i in range(6):
#  # MOVED: from system_learning.types.semantic_memory_types import IncidentBundle

            b = IncidentBundle(
                trace_id=f"tr{i}",
                trace_summary=f"s{i}",
                violations=(f"V{i}",),
                route_path=f"L0->L{i}",
                tool_capability="route",
                state_diff_summary=f"diff{i}",
                healer_id=f"h{i}",
                outcome="failure",
                policy_hash=_PH,
                timestamp_utc=_TS + i,
            )
            r.ingest_incident(b)
        assert r.buffer_snapshot().incident_index == 5  # capped at 5

    def test_indexes_independent_no_cross_contamination(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        snap = r.buffer_snapshot()
        assert snap.prompt_index == 1
        assert snap.replay_index == 1
        assert snap.incident_index == 0
        assert snap.retrieval_index == 0


# ============================================================
# Creative: registry — total_buffer_utilization
# ============================================================


class TestTotalBufferUtilization:
    def test_all_indexes_present(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import ALL_INDEXES

        r = _registry()
        util = r.total_buffer_utilization()
        for idx in ALL_INDEXES:
            assert idx in util

    def test_total_used_and_capacity_present(self):
        r = _registry()
        util = r.total_buffer_utilization()
        assert "total_used" in util
        assert "total_capacity" in util

    def test_utilization_zero_on_empty(self):
        r = _registry()
        util = r.total_buffer_utilization()
#  # MOVED: from system_learning.engines.semantic_index_registry import ALL_INDEXES

        for idx in ALL_INDEXES:
            assert util[idx]["used"] == 0
            assert util[idx]["utilization"] == 0.0

    def test_utilization_correct_after_ingest(self):
        r = _registry(prompt_buffer=100)
        for i in range(10):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}", trace_id=f"t{i}", task=f"task{i}"))
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_PROMPT

        util = r.total_buffer_utilization()
        assert util[INDEX_PROMPT]["used"] == 10
        assert util[INDEX_PROMPT]["capacity"] == 100
        assert abs(util[INDEX_PROMPT]["utilization"] - 0.1) < 1e-4

    def test_total_used_is_sum_of_all_used(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        r.ingest_retrieval_case(_rcr())
        util = r.total_buffer_utilization()
#  # MOVED: from system_learning.engines.semantic_index_registry import ALL_INDEXES

        manual_sum = sum(util[idx]["used"] for idx in ALL_INDEXES)
        assert util["total_used"] == manual_sum == 3


# ============================================================
# Creative: registry — cross_index_health_report
# ============================================================


class TestCrossIndexHealthReport:
    def test_empty_registry_is_ok(self):
        r = _registry()
        report = r.cross_index_health_report()
        assert report["health"] == "OK"
        assert report["total_records"] == 0

    def test_required_keys_present(self):
        r = _registry()
        report = r.cross_index_health_report()
        for key in (
            "health",
            "total_records",
            "total_capacity",
            "retrieval_avg_support_score",
            "retrieval_avg_completeness_score",
            "retrieval_escalation_rate",
            "retrieval_quality_tier",
            "prompt_blocked_count",
            "prompt_escalated_count",
            "replay_top3_nondeterminism",
            "guardrail_false_positive_count",
            "guardrail_true_positive_count",
        ):
            assert key in report, f"missing key: {key}"

    def test_health_critical_when_retrieval_tier_critical(self):
        r = _registry()
        for i in range(6):
            r.ingest_retrieval_case(
                _rcr(
                    case_id=f"w{i}",
                    query=f"q{i}",
                    chunk_ids=(f"x{i}",),
                    support_score=0.1,
                    replay_pass=False,
                )
            )
        for i in range(4):
            r.ingest_retrieval_case(
                _rcr(
                    case_id=f"s{i}",
                    query=f"qs{i}",
                    chunk_ids=(f"xs{i}",),
                    support_score=0.9,
                )
            )
        report = r.cross_index_health_report()
        assert report["health"] == "CRITICAL"

    def test_health_warn_when_any_index_over_90pct(self):
        r = _registry(prompt_buffer=10)
        for i in range(10):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}", trace_id=f"t{i}", task=f"task{i}"))
        report = r.cross_index_health_report()
        assert report["health"] in ("WARN", "CRITICAL")

    def test_prompt_blocked_count_correct(self):
        r = _registry()
        for i in range(3):
            r.ingest_prompt_outcome(
                _poem(record_id=f"b{i}", trace_id=f"tb{i}", task=f"t-b{i}", safety="BLOCKED")
            )
        report = r.cross_index_health_report()
        assert report["prompt_blocked_count"] == 3

    def test_guardrail_false_positive_count_correct(self):
#  # MOVED: from system_learning.types.semantic_memory_types import PolicyGuardrailCase

        r = _registry()
        r.ingest_guardrail_case(
            PolicyGuardrailCase(
                case_id="fp0",
                blocked_payload_summary="payload A - SQL inject attempt",
                remediation_text="sanitize input",
                policy_hash=_PH,
                policy_root="root_sql",
                verdict="false_positive",
                strictness_level="LOW",
                trace_id="tr-fp0",
                timestamp_utc=_TS,
            )
        )
        r.ingest_guardrail_case(
            PolicyGuardrailCase(
                case_id="fp1",
                blocked_payload_summary="payload B - XSS attempt",
                remediation_text="escape output",
                policy_hash=_PH,
                policy_root="root_xss",
                verdict="false_positive",
                strictness_level="MEDIUM",
                trace_id="tr-fp1",
                timestamp_utc=_TS + 1,
            )
        )
        report = r.cross_index_health_report()
        assert report["guardrail_false_positive_count"] == 2

    def test_replay_top3_nondeterminism_correct(self):
        r = _registry()
        for i in range(5):
            r.ingest_replay_failure(
                _rfr(failure_id=f"fh{i}", trace_id=f"th{i}", summary=f"sh{i}", nd_type="HASH_MISMATCH")
            )
        for i in range(3):
            r.ingest_replay_failure(
                _rfr(failure_id=f"fo{i}", trace_id=f"to{i}", summary=f"so{i}", nd_type="ORDERING_INSTABILITY")
            )
        report = r.cross_index_health_report()
        top3 = dict(report["replay_top3_nondeterminism"])
        assert top3.get("HASH_MISMATCH", 0) == 5

    def test_total_records_matches_snapshot_total(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem())
        r.ingest_replay_failure(_rfr())
        r.ingest_retrieval_case(_rcr())
        report = r.cross_index_health_report()
        assert report["total_records"] == r.buffer_snapshot().total


# ============================================================
# Creative: registry — bulk_evict_by_trace_id
# ============================================================


class TestBulkEvictByTraceId:
    def test_empty_trace_id_raises(self):
        r = _registry()
        with pytest.raises(ValueError, match="trace_id"):
            r.bulk_evict_by_trace_id("")

    def test_returns_dict_with_all_8_indexes(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import ALL_INDEXES

        r = _registry()
        result = r.bulk_evict_by_trace_id("tr-nobody")
        assert set(result.keys()) == ALL_INDEXES

    def test_all_zeros_when_trace_not_found(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem(trace_id="tr-real"))
        result = r.bulk_evict_by_trace_id("tr-ghost")
        assert all(v == 0 for v in result.values())
        assert r.buffer_snapshot().total == 1

    def test_evicts_from_correct_index(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_PROMPT

        r = _registry()
        r.ingest_prompt_outcome(_poem(trace_id="tr-target"))
        r.ingest_prompt_outcome(_poem(record_id="r-keep", trace_id="tr-keep", task="keep-task"))
        result = r.bulk_evict_by_trace_id("tr-target")
        assert result[INDEX_PROMPT] == 1
        assert r.buffer_snapshot().prompt_index == 1

    def test_evicts_across_multiple_indexes(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import (
            INDEX_PROMPT,
            INDEX_REPLAY,
            INDEX_RETRIEVAL,
        )

        r = _registry()
        shared_trace = "tr-shared"
        r.ingest_prompt_outcome(_poem(trace_id=shared_trace))
        r.ingest_replay_failure(_rfr(trace_id=shared_trace))
        r.ingest_retrieval_case(_rcr(trace_id=shared_trace))
        result = r.bulk_evict_by_trace_id(shared_trace)
        assert result[INDEX_PROMPT] == 1
        assert result[INDEX_REPLAY] == 1
        assert result[INDEX_RETRIEVAL] == 1
        assert r.buffer_snapshot().total == 0

    def test_does_not_evict_different_trace(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem(trace_id="tr-safe"))
        r.ingest_prompt_outcome(_poem(record_id="r-target", trace_id="tr-target", task="target-task"))
        r.bulk_evict_by_trace_id("tr-target")
        assert r.buffer_snapshot().prompt_index == 1

    def test_idempotent(self):
        r = _registry()
        r.ingest_prompt_outcome(_poem(trace_id="tr-once"))
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_PROMPT

        r1 = r.bulk_evict_by_trace_id("tr-once")
        r2 = r.bulk_evict_by_trace_id("tr-once")
        assert r1[INDEX_PROMPT] == 1
        assert r2[INDEX_PROMPT] == 0

    def test_concurrent_bulk_evict_thread_safe(self):
        r = _registry(prompt_buffer=10_000)
        for i in range(100):
            r.ingest_prompt_outcome(_poem(record_id=f"r{i}", trace_id=f"tr-{i}", task=f"task{i}"))
        errors = []

        def worker(i):
            try:
                r.bulk_evict_by_trace_id(f"tr-{i}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert r.buffer_snapshot().prompt_index == 0


# ============================================================
# Creative: registry — index_namespace_map
# ============================================================


class TestIndexNamespaceMap:
    def test_returns_all_8_indexes(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import ALL_INDEXES

        nm = _registry().index_namespace_map()
        assert set(nm.keys()) == ALL_INDEXES

    def test_namespaces_are_nonempty_strings(self):
        nm = _registry().index_namespace_map()
        for k, v in nm.items():
            assert isinstance(v, str) and len(v) > 0, f"empty namespace for {k}"

    def test_namespace_values_unique(self):
        nm = _registry().index_namespace_map()
        namespaces = list(nm.values())
        assert len(namespaces) == len(set(namespaces))

    def test_known_namespaces_correct(self):
#  # MOVED: from system_learning.engines.semantic_index_registry import (
            INDEX_PROMPT,
            INDEX_REPLAY,
            INDEX_RETRIEVAL,
        )

        nm = _registry().index_namespace_map()
        assert nm[INDEX_REPLAY] == "replay_failures"
        assert nm[INDEX_PROMPT] == "prompt_outcomes"
        assert nm[INDEX_RETRIEVAL] == "retrieval_cases"

    def test_static_method_callable_without_instance(self):
    """Test static_method_callable_without_instance runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute static_method_callable_without_instance
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
#  # MOVED: from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder()
        rk2 = "rk2-" + "y" * 59
        for i in range(5):
            e.ingest(
                _rfr(
                    nd_type="HASH_MISMATCH",
                    failure_id=f"f-hm{i}",
                    trace_id=f"t-hm{i}",
                    summary=f"s-hm{i}",
                    replay_key=_RK,
                )
            )
        for i in range(3):
            e.ingest(
                _rfr(
                    nd_type="ORDERING_INSTABILITY",
                    failure_id=f"f-oi{i}",
                    trace_id=f"t-oi{i}",
                    summary=f"s-oi{i}",
                    replay_key=rk2,
                )
            )
        assert e.nondeterminism_type_stats()["HASH_MISMATCH"] == 5
        e.evict_by_replay_key(_RK)
        assert e.nondeterminism_type_stats().get("HASH_MISMATCH", 0) == 0
        assert e.nondeterminism_type_stats()["ORDERING_INSTABILITY"] == 3

    def test_prompt_ingest_evict_stats_consistent(self):
#  # MOVED: from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        e = PromptOutcomeEmbedder()
        for i in range(4):
            e.ingest(
                _poem(
                    safety="BLOCKED",
                    record_id=f"b{i}",
                    trace_id=f"tb{i}",
                    task=f"t-b{i}",
                    template_id="tmpl-old",
                )
            )
        for i in range(2):
            e.ingest(
                _poem(
                    safety="ALLOWED",
                    record_id=f"a{i}",
                    trace_id=f"ta{i}",
                    task=f"t-a{i}",
                    template_id="tmpl-new",
                )
            )
        assert e.safety_outcome_stats()["BLOCKED"] == 4
        e.evict_by_template_id("tmpl-old")
        assert e.safety_outcome_stats()["BLOCKED"] == 0
        assert e.safety_outcome_stats()["ALLOWED"] == 2

    def test_retrieval_weak_case_pipeline(self):
    """Test retrieval_weak_case_pipeline runtime behavior."""
    # Arrange
    # TODO: Set up workflow context
    workflow_input = {}  # Replace with actual workflow input

    # Act
    # TODO: Execute workflow retrieval_weak_case_pipeline
    workflow_result = None  # Replace with actual workflow execution

    # Assert
    assert workflow_result is not None, "Workflow should produce a result"
    assert isinstance(workflow_result, dict), "Workflow result should be structured"
    # TODO: Add workflow step assertions
        for i in range(5):
            e.ingest(
                _rcr(
                    case_id=f"strong-{i}",
                    support_score=0.9,
                    completeness_score=0.95,
                    query=f"q-s{i}",
                    chunk_ids=(f"xs{i}",),
                )
            )
        weak = e.retrieve_weak_cases(support_threshold=0.5, completeness_threshold=0.5)
        assert all(m["case_id"].startswith("weak") for m in weak)
        sig = e.quality_signal_summary()
        assert sig["count"] == 10

    def test_registry_all_indexes_ingest_export_round_trip(self):
#  # MOVED: from system_learning.types.semantic_memory_types import (
            GraphNeighborhood,
            IncidentBundle,
            MutationDiffRecord,
            PathDPreferencePair,
            PolicyGuardrailCase,
        )

        r = _registry()
        r.ingest_incident(
            IncidentBundle(
                trace_id="tr-int",
                trace_summary="s",
                violations=("V1",),
                route_path="L0->L3",
                tool_capability="route",
                state_diff_summary="d",
                healer_id="h1",
                outcome="success",
                policy_hash=_PH,
                timestamp_utc=_TS,
            )
        )
        r.ingest_graph_neighborhood(
            GraphNeighborhood(
                node_id="n1",
                node_type="Engine",
                layer="L3",
                inbound_relations=("A",),
                outbound_relations=("B",),
                governance_edges=("G",),
                mutation_edges=("M",),
                ownership_territory="apps_rg",
                risk_label="LOW",
            )
        )
        r.ingest_mutation(
            MutationDiffRecord(
                mutation_id="m1",
                target_resource="cfg",
                operations=("op:add",),
                state_diff_summary="diff",
                rollback_context="rb",
                commit_outcome="committed",
                trace_id="tr-m",
                policy_hash=_PH,
                timestamp_utc=_TS,
            )
        )
        r.ingest_prompt_outcome(_poem())
        r.ingest_retrieval_case(_rcr())
        r.ingest_replay_failure(_rfr())
        r.ingest_preference(
            PathDPreferencePair(
                decision_id="d1",
                original_plan="plan A",
                human_patch="plan B",
                decision="modified",
                reason="safer",
                resulting_outcome="ok",
                agent="A",
                trace_id="tr-pref",
                timestamp_utc=_TS,
            )
        )
        r.ingest_guardrail_case(
            PolicyGuardrailCase(
                case_id="gc1",
                blocked_payload_summary="p",
                remediation_text="fix",
                policy_hash=_PH,
                policy_root="root",
                verdict="true_positive",
                strictness_level="HIGH",
                trace_id="tr-gc",
                timestamp_utc=_TS,
            )
        )
        snap = r.buffer_snapshot()
        assert snap.total == 8
        dump = r.export_all_corpus_records()
        assert all(len(v) == 1 for v in dump.values())

    def test_multiindex_ingest_result_fields(self):
        r = _registry()
        res = r.ingest_prompt_outcome(_poem(trace_id="tr-field-test"))
#  # MOVED: from system_learning.engines.semantic_index_registry import INDEX_PROMPT

        assert res.index_name == INDEX_PROMPT
        assert len(res.content_hash) == 64
        assert res.trace_id == "tr-field-test"


# ============================================================
# Creative integration — multi-method pipelines
# ============================================================


class TestCreativeIntegration:
    def test_replay_full_pipeline_top_subsystems_then_evict_type(self):
    """Test replay_full_pipeline_top_subsystems_then_evict_type runtime behavior."""
    # Arrange
    # TODO: Set up workflow context
    workflow_input = {}  # Replace with actual workflow input

    # Act
    # TODO: Execute workflow replay_full_pipeline_top_subsystems_then_evict_type
    workflow_result = None  # Replace with actual workflow execution

    # Assert
    assert workflow_result is not None, "Workflow should produce a result"
    assert isinstance(workflow_result, dict), "Workflow result should be structured"
    # TODO: Add workflow step assertions
        for i in range(2):
            e.ingest(
                _rfr(
                    failure_id=f"o{i}",
                    trace_id=f"to{i}",
                    summary=f"so{i}",
                    nd_type="ORDERING_INSTABILITY",
                    subsystems=("L1",),
                )
            )
        top = e.top_affected_subsystems(top_n=3)
        names = [n for n, _ in top]
        assert "L3" in names and "L2" in names
        e.evict_by_nondeterminism_type("HASH_MISMATCH")
        stats = e.nondeterminism_type_stats()
        assert stats.get("HASH_MISMATCH", 0) == 0
        top_after = e.top_affected_subsystems()
        assert dict(top_after).get("L1", 0) == 2

    def test_prompt_model_stats_then_evict_before_ts(self):
#  # MOVED: from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        e = PromptOutcomeEmbedder(max_buffer=10_000)
        e.ingest(
            _poem(record_id="old1", safety="BLOCKED", model="gpt-4o", trace_id="@TS:500", task="old-task-1")
        )
        e.ingest(
            _poem(record_id="old2", safety="ALLOWED", model="gpt-4o", trace_id="@TS:800", task="old-task-2")
        )
        e.ingest(
            _poem(record_id="new1", safety="BLOCKED", model="gpt-4o", trace_id="@TS:2000", task="new-task")
        )
        stats_before = e.model_stats()
        assert stats_before["gpt-4o"]["BLOCKED"] == 2
        e.evict_before_timestamp(1000)
        stats_after = e.model_stats()
        assert stats_after["gpt-4o"]["BLOCKED"] == 1
        assert stats_after["gpt-4o"].get("ALLOWED", 0) == 0

    def test_retrieval_expansion_report_then_evict_bad_queries(self):
#  # MOVED: from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        e = RetrievalCaseEmbedder(max_buffer=10_000)
        for i in range(6):
            e.ingest(
                _rcr(
                    case_id=f"bad{i}",
                    query=f"q-bad{i}",
                    chunk_ids=(f"xb{i}",),
                    support_score=0.1,
                    replay_pass=False,
                    query_id="qid-bad",
                )
            )
        for i in range(4):
            e.ingest(
                _rcr(
                    case_id=f"good{i}",
                    query=f"q-good{i}",
                    chunk_ids=(f"xg{i}",),
                    support_score=0.9,
                    replay_pass=True,
                    query_id="qid-good",
                )
            )
        report = e.corpus_expansion_report()
        assert report["quality_tier"] == "CRITICAL"
        e.evict_by_query_id("qid-bad")
        report_after = e.corpus_expansion_report()
        assert report_after["quality_tier"] == "HEALTHY"

    def test_registry_health_transitions_ok_to_critical(self):
        r = _registry()
        report_empty = r.cross_index_health_report()
        assert report_empty["health"] == "OK"
        for i in range(8):
            r.ingest_retrieval_case(
                _rcr(
                    case_id=f"w{i}",
                    query=f"q{i}",
                    chunk_ids=(f"x{i}",),
                    support_score=0.05,
                    replay_pass=False,
                )
            )
        for i in range(2):
            r.ingest_retrieval_case(
                _rcr(
                    case_id=f"ok{i}",
                    query=f"qok{i}",
                    chunk_ids=(f"xok{i}",),
                    support_score=0.9,
                )
            )
        report_critical = r.cross_index_health_report()
        assert report_critical["health"] == "CRITICAL"

    def test_registry_bulk_evict_then_health_ok(self):
        r = _registry()
        bad_trace = "tr-bad-trace"
        for i in range(8):
            r.ingest_retrieval_case(
                _rcr(
                    case_id=f"w{i}",
                    query=f"q{i}",
                    chunk_ids=(f"x{i}",),
                    support_score=0.05,
                    replay_pass=False,
                    trace_id=bad_trace,
                )
            )
        r.bulk_evict_by_trace_id(bad_trace)
        assert r.buffer_snapshot().total == 0
        report = r.cross_index_health_report()
        assert report["health"] == "OK"

    def test_score_buckets_plus_quality_summary_consistent(self):
#  # MOVED: from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        e = RetrievalCaseEmbedder(max_buffer=10_000)
        for i in range(4):
            e.ingest(_rcr(case_id=f"q1-{i}", query=f"q{i}", chunk_ids=(f"x{i}",), support_score=0.1))
        for i in range(4):
            e.ingest(_rcr(case_id=f"q4-{i}", query=f"qq{i}", chunk_ids=(f"y{i}",), support_score=0.9))
        buckets = e.score_percentile_buckets()
        sig = e.quality_signal_summary()
        assert buckets["support_score"]["Q1"] == 4
        assert buckets["support_score"]["Q4"] == 4
        assert abs(sig["avg_support_score"] - 0.5) < 0.1
