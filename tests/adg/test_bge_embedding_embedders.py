"""Tests for BGE embedding engine components.

Covers extension embedder behaviour + creative analytical methods:
  - ReplayFailureEmbedder  (ingest, evict, stats, top_affected_subsystems,
                            evict_by_nondeterminism_type, replay_key_summary)
  - PromptOutcomeEmbedder  (ingest, evict, stats, top_templates_by_outcome,
                            model_stats, evict_before_timestamp,
                            route_distribution)
  - RetrievalCaseEmbedder  (ingest, evict, quality_signal_summary,
                            retrieve_weak_cases, escalation_candidates,
                            corpus_expansion_report, evict_by_query_id,
                            score_percentile_buckets)
"""

from __future__ import annotations

import threading

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_bge_embedding_embedders")
# REMOVED: _emit_applies_guardrail("p0", "test_bge_embedding_embedders", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_bge_embedding_embedders", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_bge_embedding_embedders", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_bge_embedding_embedders", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_embedders", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_embedders", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_embedders", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_embedders", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_bge_embedding_embedders", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_bge_embedding_embedders", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_bge_embedding_embedders", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_bge_embedding_embedders", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_bge_embedding_embedders", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_bge_embedding_embedders", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_bge_embedding_embedders", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_bge_embedding_embedders", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_bge_embedding_embedders", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_bge_embedding_embedders", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_bge_embedding_embedders", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_bge_embedding_embedders", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_bge_embedding_embedders", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_bge_embedding_embedders", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_embedders", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_embedders", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_embedders", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_embedders", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_bge_embedding_embedders", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_bge_embedding_embedders", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_bge_embedding_embedders", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_bge_embedding_embedders", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_bge_embedding_embedders", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_bge_embedding_embedders", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_bge_embedding_embedders", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_bge_embedding_embedders", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_bge_embedding_embedders", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_bge_embedding_embedders", "write_through")
# REMOVED: _emit_writes_through("p1", "test_bge_embedding_embedders", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_bge_embedding_embedders", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_bge_embedding_embedders", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_bge_embedding_embedders", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_bge_embedding_embedders", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_bge_embedding_embedders", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_bge_embedding_embedders", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_bge_embedding_embedders", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_bge_embedding_embedders", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_bge_embedding_embedders", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_bge_embedding_embedders", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_bge_embedding_embedders", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_bge_embedding_embedders", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_bge_embedding_embedders", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_bge_embedding_embedders", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_bge_embedding_embedders")
# REMOVED: _emit_gated_by_confidence("p1", "test_bge_embedding_embedders", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_bge_embedding_embedders")
# REMOVED: emit_determinism_digest("p0", "test_bge_embedding_embedders")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_bge_embedding_embedders", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_bge_embedding_embedders", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_bge_embedding_embedders", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_bge_embedding_embedders", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_bge_embedding_embedders", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_bge_embedding_embedders", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_bge_embedding_embedders", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_bge_embedding_embedders", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_bge_embedding_embedders", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_bge_embedding_embedders", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_bge_embedding_embedders", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_bge_embedding_embedders", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_bge_embedding_embedders", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_bge_embedding_embedders", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_bge_embedding_embedders", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_bge_embedding_embedders", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_bge_embedding_embedders", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_bge_embedding_embedders", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_bge_embedding_embedders", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_bge_embedding_embedders", "exec_snapshot_link")

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
    from system_learning.types.semantic_memory_types import ReplayFailureRecord

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
    from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

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
    from system_learning.types.semantic_memory_types import RetrievalCaseRecord

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


# ============================================================
# 4. ReplayFailureEmbedder — core ingest/evict/stats
# ============================================================


class TestReplayFailureEmbedder:
    def _e(self, max_buffer=100):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        return ReplayFailureEmbedder(max_buffer=max_buffer)

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord

        e = self._e()
        r = e.ingest(_rfr())
        assert isinstance(r, CorpusRecord)

    def test_namespace_is_replay_failures(self):
        e = self._e()
        r = e.ingest(_rfr())
        assert r.namespace == "replay_failures"

    def test_buffer_increments(self):
        e = self._e()
        e.ingest(_rfr())
        assert e.buffer_size() == 1

    def test_buffer_evicts_oldest_at_capacity(self):
        e = self._e(max_buffer=2)
        e.ingest(_rfr(failure_id="f0", trace_id="t0", summary="s0"))
        e.ingest(_rfr(failure_id="f1", trace_id="t1", summary="s1"))
        e.ingest(_rfr(failure_id="f2", trace_id="t2", summary="s2"))
        assert e.buffer_size() == 2
        tids = {r.trace_id for r in e.export_corpus_records()}
        assert "t0" not in tids

    def test_nondeterminism_type_stats_correct(self):
        e = self._e()
        for _ in range(3):
            e.ingest(
                _rfr(
                    nd_type="HASH_MISMATCH", failure_id=f"f-hm-{_}", trace_id=f"t-hm-{_}", summary=f"s-hm-{_}"
                )
            )
        for _ in range(2):
            e.ingest(
                _rfr(
                    nd_type="ORDERING_INSTABILITY",
                    failure_id=f"f-oi-{_}",
                    trace_id=f"t-oi-{_}",
                    summary=f"s-oi-{_}",
                )
            )
        stats = e.nondeterminism_type_stats()
        assert stats["HASH_MISMATCH"] == 3
        assert stats["ORDERING_INSTABILITY"] == 2

    def test_nondeterminism_stats_empty_buffer(self):
        e = self._e()
        assert e.nondeterminism_type_stats() == {}

    def test_nondeterminism_stats_sorted_alphabetically(self):
        e = self._e()
        for nd, fid, tid, sm in [
            ("ZZZ", "fz", "tz", "sz"),
            ("AAA", "fa", "ta", "sa"),
            ("MMM", "fm", "tm", "sm"),
        ]:
            e.ingest(_rfr(nd_type=nd, failure_id=fid, trace_id=tid, summary=sm))
        keys = list(e.nondeterminism_type_stats().keys())
        assert keys == sorted(keys)

    def test_evict_by_replay_key_removes_correct_records(self):
        e = self._e()
        rk2 = "rk2-" + "x" * 59
        for i in range(3):
            e.ingest(_rfr(failure_id=f"f-a{i}", trace_id=f"ta{i}", summary=f"sa{i}", replay_key=_RK))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"f-b{i}", trace_id=f"tb{i}", summary=f"sb{i}", replay_key=rk2))
        n = e.evict_by_replay_key(_RK)
        assert n == 3
        assert e.buffer_size() == 2

    def test_evict_empty_replay_key_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="replay_key"):
            e.evict_by_replay_key("")

    def test_evict_idempotent(self):
        e = self._e()
        e.ingest(_rfr())
        n1 = e.evict_by_replay_key(_RK)
        n2 = e.evict_by_replay_key(_RK)
        assert n1 == 1
        assert n2 == 0

    def test_record_from_replay_event_convenience_constructor(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        r = ReplayFailureEmbedder.record_from_replay_event(
            failure_id="fe-001",
            failure_summary="hash mismatch",
            nondeterminism_type="HASH_MISMATCH",
            mismatch_explanation="digest differed",
            affected_subsystems=["L3", "L0"],
            attempted_remediation="reseed",
            replay_key=_RK,
            determinism_digest=_DD,
            trace_id="tr-x",
            timestamp_utc=_TS,
        )
        assert r.nondeterminism_type == "HASH_MISMATCH"
        assert r.affected_subsystems == ("L0", "L3")  # sorted

    def test_record_from_replay_event_empty_failure_id_raises(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        with pytest.raises(ValueError, match="failure_id"):
            ReplayFailureEmbedder.record_from_replay_event(
                failure_id="",
                failure_summary="x",
                nondeterminism_type="T",
                mismatch_explanation="m",
                affected_subsystems=[],
                attempted_remediation="r",
                replay_key=_RK,
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_export_sorted_by_content_hash(self):
        e = self._e()
        for i in range(5):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"tr{i}", summary=f"s{i}"))
        records = e.export_corpus_records()
        keys = [(r.content_hash, r.trace_id) for r in records]
        assert keys == sorted(keys)

    def test_concurrent_ingest_thread_safe(self):
        e = self._e(max_buffer=10_000)
        errors = []

        def worker(tid):
            try:
                for j in range(20):
                    e.ingest(_rfr(failure_id=f"f-{tid}-{j}", trace_id=f"t-{tid}-{j}", summary=f"s-{tid}-{j}"))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert e.buffer_size() == 100


# ============================================================
# 5. PromptOutcomeEmbedder — core ingest/evict/stats
# ============================================================


class TestPromptOutcomeEmbedder:
    def _e(self, max_buffer=100):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        return PromptOutcomeEmbedder(max_buffer=max_buffer)

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord

        e = self._e()
        assert isinstance(e.ingest(_poem()), CorpusRecord)

    def test_namespace_is_prompt_outcomes(self):
        e = self._e()
        r = e.ingest(_poem())
        assert r.namespace == "prompt_outcomes"

    def test_buffer_increments(self):
        e = self._e()
        e.ingest(_poem())
        assert e.buffer_size() == 1

    def test_safety_outcome_stats_all_keys_present(self):
        e = self._e()
        e.ingest(_poem(safety="ALLOWED", record_id="r1"))
        stats = e.safety_outcome_stats()
        for key in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            assert key in stats

    def test_safety_outcome_stats_counts_correct(self):
        e = self._e()
        for i in range(4):
            e.ingest(_poem(safety="ALLOWED", record_id=f"a{i}", trace_id=f"ta{i}", task=f"task-a{i}"))
        for i in range(2):
            e.ingest(_poem(safety="BLOCKED", record_id=f"b{i}", trace_id=f"tb{i}", task=f"task-b{i}"))
        stats = e.safety_outcome_stats()
        assert stats["ALLOWED"] == 4
        assert stats["BLOCKED"] == 2
        assert stats["ESCALATED"] == 0

    def test_safety_outcome_stats_sum_equals_buffer(self):
        e = self._e()
        for i, s in enumerate(["ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"]):
            e.ingest(_poem(safety=s, record_id=f"r{i}", trace_id=f"t{i}", task=f"task{i}"))
        assert sum(e.safety_outcome_stats().values()) == e.buffer_size()

    def test_evict_by_template_id_removes_records(self):
        e = self._e()
        for i in range(5):
            e.ingest(
                _poem(record_id=f"r-v3-{i}", trace_id=f"t-v3-{i}", task=f"task-v3-{i}", template_id="tmpl-v3")
            )
        for i in range(3):
            e.ingest(
                _poem(record_id=f"r-v4-{i}", trace_id=f"t-v4-{i}", task=f"task-v4-{i}", template_id="tmpl-v4")
            )
        n = e.evict_by_template_id("tmpl-v3")
        assert n == 5
        assert e.buffer_size() == 3

    def test_evict_empty_template_id_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="template_id"):
            e.evict_by_template_id("")

    def test_evict_updates_safety_outcome_stats(self):
        e = self._e()
        e.ingest(_poem(safety="BLOCKED", record_id="b1", trace_id="tb1", task="t-b", template_id="tmpl-old"))
        e.ingest(_poem(safety="ALLOWED", record_id="a1", trace_id="ta1", task="t-a", template_id="tmpl-new"))
        e.evict_by_template_id("tmpl-old")
        stats = e.safety_outcome_stats()
        assert stats["BLOCKED"] == 0
        assert stats["ALLOWED"] == 1

    def test_record_from_execution_convenience_constructor(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        r = PromptOutcomeEmbedder.record_from_execution(
            record_id="exec-001",
            slot_s0_summary="sys",
            slot_d0_summary="dom",
            slot_i0_summary="ins",
            slot_c0_summary="ctx",
            slot_u0_summary="usr",
            task_description="t",
            answer_summary="a",
            safety_outcome="ALLOWED",
            retrieval_grounding_summary="g",
            prompt_hash="ph",
            template_id="ti",
            route="r",
            model="m",
            policy_hash="plh",
            trace_id="tr",
            timestamp_utc=_TS,
        )
        assert r.record_id == "exec-001"
        assert r.safety_outcome == "ALLOWED"

    def test_record_from_execution_invalid_safety_raises(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        with pytest.raises(ValueError, match="safety_outcome"):
            PromptOutcomeEmbedder.record_from_execution(
                record_id="x",
                slot_s0_summary="s",
                slot_d0_summary="d",
                slot_i0_summary="i",
                slot_c0_summary="c",
                slot_u0_summary="u",
                task_description="t",
                answer_summary="a",
                safety_outcome="INVALID",
                retrieval_grounding_summary="g",
                prompt_hash="ph",
                template_id="ti",
                route="r",
                model="m",
                policy_hash="plh",
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_buffer_evicts_oldest_at_capacity(self):
        e = self._e(max_buffer=2)
        e.ingest(_poem(record_id="r0", trace_id="t0", task="task0"))
        e.ingest(_poem(record_id="r1", trace_id="t1", task="task1"))
        e.ingest(_poem(record_id="r2", trace_id="t2", task="task2"))
        assert e.buffer_size() == 2
        tids = {r.trace_id for r in e.export_corpus_records()}
        assert "t0" not in tids

    def test_concurrent_ingest_thread_safe(self):
        e = self._e(max_buffer=10_000)
        errors = []

        def worker(tid):
            try:
                for j in range(25):
                    e.ingest(_poem(record_id=f"r-{tid}-{j}", trace_id=f"t-{tid}-{j}", task=f"task-{tid}-{j}"))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert e.buffer_size() == 100


# ============================================================
# 6. RetrievalCaseEmbedder — core ingest/evict/quality
# ============================================================


class TestRetrievalCaseEmbedder:
    def _e(self, max_buffer=100):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        return RetrievalCaseEmbedder(max_buffer=max_buffer)

    def test_ingest_returns_corpus_record(self):
        from system_learning.engines.embedding_corpus_extraction import CorpusRecord

        e = self._e()
        assert isinstance(e.ingest(_rcr()), CorpusRecord)

    def test_namespace_is_retrieval_cases(self):
        e = self._e()
        assert e.ingest(_rcr()).namespace == "retrieval_cases"

    def test_buffer_increments(self):
        e = self._e()
        e.ingest(_rcr())
        assert e.buffer_size() == 1

    def test_quality_signal_summary_empty_buffer(self):
        e = self._e()
        summary = e.quality_signal_summary()
        assert summary["count"] == 0
        assert summary["avg_support_score"] == 0.0

    def test_quality_signal_summary_correct_averages(self):
        e = self._e()
        e.ingest(_rcr(case_id="c0", support_score=0.8, completeness_score=0.9, query="q0", chunk_ids=("c0",)))
        e.ingest(_rcr(case_id="c1", support_score=0.4, completeness_score=0.6, query="q1", chunk_ids=("c1",)))
        s = e.quality_signal_summary()
        assert s["count"] == 2
        assert abs(s["avg_support_score"] - 0.6) < 1e-5
        assert abs(s["avg_completeness_score"] - 0.75) < 1e-5

    def test_quality_signal_escalation_rate(self):
        e = self._e()
        e.ingest(_rcr(case_id="c0", escalation_flag=True, query="q0", chunk_ids=("x0",)))
        e.ingest(_rcr(case_id="c1", escalation_flag=False, query="q1", chunk_ids=("x1",)))
        s = e.quality_signal_summary()
        assert abs(s["escalation_rate"] - 0.5) < 1e-5

    def test_quality_signal_replay_pass_rate(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rcr(case_id=f"c{i}", replay_pass=True, query=f"q{i}", chunk_ids=(f"x{i}",)))
        e.ingest(_rcr(case_id="c-fail", replay_pass=False, query="q-f", chunk_ids=("x-f",)))
        s = e.quality_signal_summary()
        assert abs(s["replay_pass_rate"] - 0.75) < 1e-5

    def test_retrieve_weak_cases_below_support_threshold(self):
        e = self._e()
        e.ingest(
            _rcr(case_id="weak", support_score=0.2, completeness_score=0.9, query="qw", chunk_ids=("cw",))
        )
        e.ingest(
            _rcr(case_id="strong", support_score=0.9, completeness_score=0.9, query="qs", chunk_ids=("cs",))
        )
        weak = e.retrieve_weak_cases(support_threshold=0.5)
        assert len(weak) == 1
        assert weak[0]["case_id"] == "weak"

    def test_retrieve_weak_cases_below_completeness_threshold(self):
        e = self._e()
        e.ingest(
            _rcr(case_id="w-comp", support_score=0.9, completeness_score=0.3, query="qwc", chunk_ids=("cwc",))
        )
        e.ingest(
            _rcr(case_id="s-comp", support_score=0.9, completeness_score=0.9, query="qsc", chunk_ids=("csc",))
        )
        weak = e.retrieve_weak_cases(completeness_threshold=0.5)
        assert len(weak) == 1
        assert weak[0]["case_id"] == "w-comp"

    def test_retrieve_weak_cases_limit_respected(self):
        e = self._e(max_buffer=200)
        for i in range(20):
            e.ingest(_rcr(case_id=f"w{i}", support_score=0.1, query=f"q{i}", chunk_ids=(f"x{i}",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5, limit=5)
        assert len(weak) == 5

    def test_retrieve_weak_cases_limit_capped_at_100(self):
        e = self._e(max_buffer=200)
        for i in range(150):
            e.ingest(_rcr(case_id=f"w{i}", support_score=0.1, query=f"q{i}", chunk_ids=(f"x{i}",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5, limit=999)
        assert len(weak) <= 100

    def test_retrieve_weak_cases_invalid_threshold_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="support_threshold"):
            e.retrieve_weak_cases(support_threshold=1.5)
        with pytest.raises(ValueError, match="completeness_threshold"):
            e.retrieve_weak_cases(completeness_threshold=-0.1)

    def test_retrieve_weak_cases_sorted_by_support_score(self):
        e = self._e()
        for i, ss in enumerate([0.4, 0.1, 0.3]):
            e.ingest(
                _rcr(
                    case_id=f"w{i}",
                    support_score=ss,
                    completeness_score=0.9,
                    query=f"q{i}",
                    chunk_ids=(f"x{i}",),
                )
            )
        weak = e.retrieve_weak_cases(support_threshold=0.5)
        scores = [m["support_score"] for m in weak]
        assert scores == sorted(scores)

    def test_retrieve_weak_cases_returns_copies_not_refs(self):
        e = self._e()
        e.ingest(_rcr(case_id="c0", support_score=0.2, query="q0", chunk_ids=("x0",)))
        weak = e.retrieve_weak_cases(support_threshold=0.5)
        weak[0]["case_id"] = "MUTATED"
        weak2 = e.retrieve_weak_cases(support_threshold=0.5)
        assert weak2[0]["case_id"] == "c0"

    def test_record_from_rag_evaluation_convenience(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        r = RetrievalCaseEmbedder.record_from_rag_evaluation(
            case_id="eval-001",
            query_summary="what is X?",
            chunk_summaries=["B chunk", "A chunk"],
            support_reasoning="both match",
            answer_quality_summary="complete",
            query_id="qid-x",
            chunk_ids=["cid-b", "cid-a"],
            support_score=0.85,
            completeness_score=0.9,
            escalation_flag=False,
            healer_invoked=False,
            replay_pass=True,
            trace_id="tr-e",
            timestamp_utc=_TS,
        )
        assert r.case_id == "eval-001"
        assert r.chunk_summaries == ("A chunk", "B chunk")  # sorted
        assert r.chunk_ids == ("cid-a", "cid-b")  # sorted

    def test_record_from_rag_evaluation_invalid_score_raises(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        with pytest.raises(ValueError, match="support_score"):
            RetrievalCaseEmbedder.record_from_rag_evaluation(
                case_id="e",
                query_summary="q",
                chunk_summaries=[],
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=[],
                support_score=2.0,
                completeness_score=0.5,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_buffer_evicts_oldest_at_capacity(self):
        e = self._e(max_buffer=2)
        e.ingest(_rcr(case_id="c0", query="q0", chunk_ids=("x0",)))
        e.ingest(_rcr(case_id="c1", query="q1", chunk_ids=("x1",)))
        e.ingest(_rcr(case_id="c2", query="q2", chunk_ids=("x2",)))
        assert e.buffer_size() == 2

    def test_concurrent_ingest_thread_safe(self):
        e = self._e(max_buffer=10_000)
        errors = []

        def worker(tid):
            try:
                for j in range(30):
                    e.ingest(
                        _rcr(
                            case_id=f"c-{tid}-{j}",
                            trace_id=f"t-{tid}-{j}",
                            query=f"q-{tid}-{j}",
                            chunk_ids=(f"x-{tid}-{j}",),
                        )
                    )
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert e.buffer_size() == 120


# ============================================================
# Creative: RFE — top_affected_subsystems
# ============================================================


class TestTopAffectedSubsystems:
    def test_empty_buffer_returns_empty(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        assert e.top_affected_subsystems() == []

    def test_single_record_counts_each_subsystem(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        e.ingest(_rfr(subsystems=("L3", "L0", "L1")))
        result = e.top_affected_subsystems()
        names = [r[0] for r in result]
        assert "L3" in names and "L0" in names and "L1" in names
        assert all(c == 1 for _, c in result)

    def test_most_frequent_subsystem_ranks_first(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        for i in range(5):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}", summary=f"sa{i}", subsystems=("L3", "L2")))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}", summary=f"sb{i}", subsystems=("L0",)))
        result = e.top_affected_subsystems()
        assert result[0][0] in ("L3", "L2")
        assert result[0][1] == 5

    def test_tie_broken_alphabetically(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        e.ingest(_rfr(failure_id="f1", trace_id="t1", summary="s1", subsystems=("ZZZ", "AAA")))
        e.ingest(_rfr(failure_id="f2", trace_id="t2", summary="s2", subsystems=("ZZZ", "AAA")))
        result = e.top_affected_subsystems()
        counts = dict(result)
        assert counts["AAA"] == counts["ZZZ"] == 2
        first_names = [n for n, _ in result[:2]]
        assert first_names == sorted(first_names)

    def test_top_n_capped_at_50(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        for i in range(60):
            e.ingest(
                _rfr(failure_id=f"f{i}", trace_id=f"t{i}", summary=f"s{i}", subsystems=(f"SYS_{i:03d}",))
            )
        assert len(e.top_affected_subsystems(top_n=999)) <= 50

    def test_top_n_limits_output(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        for i in range(10):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"t{i}", summary=f"s{i}", subsystems=(f"SYS_{i}",)))
        assert len(e.top_affected_subsystems(top_n=3)) == 3

    def test_eviction_updates_subsystem_counts(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        for i in range(4):
            e.ingest(
                _rfr(
                    failure_id=f"fa{i}",
                    trace_id=f"ta{i}",
                    summary=f"sa{i}",
                    subsystems=("L3",),
                    replay_key=_RK_A,
                )
            )
        for i in range(2):
            e.ingest(
                _rfr(
                    failure_id=f"fb{i}",
                    trace_id=f"tb{i}",
                    summary=f"sb{i}",
                    subsystems=("L0",),
                    replay_key=_RK_B,
                )
            )
        e.evict_by_replay_key(_RK_A)
        result = e.top_affected_subsystems()
        counts = dict(result)
        assert counts.get("L3", 0) == 0
        assert counts.get("L0", 0) == 2

    def test_multiple_subsystems_per_record_all_counted(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        e.ingest(_rfr(subsystems=("A", "B", "C", "D", "E")))
        result = e.top_affected_subsystems()
        assert len(result) == 5
        assert all(c == 1 for _, c in result)

    def test_concurrent_read_does_not_crash(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        e = ReplayFailureEmbedder(max_buffer=10_000)
        for i in range(50):
            e.ingest(_rfr(failure_id=f"f{i}", trace_id=f"t{i}", summary=f"s{i}", subsystems=(f"S{i % 5}",)))
        errors = []

        def reader():
            try:
                for _ in range(10):
                    e.top_affected_subsystems()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=reader) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


# ============================================================
# Creative: RFE — evict_by_nondeterminism_type
# ============================================================


class TestEvictByNondeterminismType:
    def _e(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        return ReplayFailureEmbedder(max_buffer=10_000)

    def test_evicts_correct_records(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rfr(failure_id=f"fh{i}", trace_id=f"th{i}", summary=f"sh{i}", nd_type="HASH_MISMATCH"))
        for i in range(2):
            e.ingest(
                _rfr(failure_id=f"fo{i}", trace_id=f"to{i}", summary=f"so{i}", nd_type="ORDERING_INSTABILITY")
            )
        n = e.evict_by_nondeterminism_type("HASH_MISMATCH")
        assert n == 3
        assert e.buffer_size() == 2

    def test_stats_updated_after_eviction(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rfr(failure_id=f"fh{i}", trace_id=f"th{i}", summary=f"sh{i}", nd_type="HASH_MISMATCH"))
        e.evict_by_nondeterminism_type("HASH_MISMATCH")
        assert e.nondeterminism_type_stats().get("HASH_MISMATCH", 0) == 0

    def test_meta_cleaned_after_eviction(self):
        e = self._e()
        e.ingest(_rfr(nd_type="TIMING_DEPENDENCY"))
        e.evict_by_nondeterminism_type("TIMING_DEPENDENCY")
        assert e.buffer_size() == 0
        assert len(e._meta) == 0  # noqa: SLF001

    def test_idempotent(self):
        e = self._e()
        e.ingest(_rfr(nd_type="HASH_MISMATCH"))
        n1 = e.evict_by_nondeterminism_type("HASH_MISMATCH")
        n2 = e.evict_by_nondeterminism_type("HASH_MISMATCH")
        assert n1 == 1
        assert n2 == 0

    def test_empty_type_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="nondeterminism_type"):
            e.evict_by_nondeterminism_type("")

    def test_nonexistent_type_returns_zero(self):
        e = self._e()
        e.ingest(_rfr(nd_type="HASH_MISMATCH"))
        assert e.evict_by_nondeterminism_type("UNICORN_TYPE") == 0
        assert e.buffer_size() == 1

    def test_does_not_evict_different_type(self):
        e = self._e()
        e.ingest(_rfr(failure_id="f1", trace_id="t1", summary="s1", nd_type="HASH_MISMATCH"))
        e.ingest(_rfr(failure_id="f2", trace_id="t2", summary="s2", nd_type="ORDERING_INSTABILITY"))
        e.evict_by_nondeterminism_type("HASH_MISMATCH")
        stats = e.nondeterminism_type_stats()
        assert stats.get("ORDERING_INSTABILITY", 0) == 1


# ============================================================
# Creative: RFE — replay_key_summary
# ============================================================


class TestReplayKeySummary:
    def _e(self):
        from system_learning.engines.replay_failure_embedder import ReplayFailureEmbedder

        return ReplayFailureEmbedder(max_buffer=10_000)

    def test_empty_buffer_returns_empty(self):
        e = self._e()
        assert e.replay_key_summary() == []

    def test_highest_count_first(self):
        e = self._e()
        for i in range(5):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}", summary=f"sa{i}", replay_key=_RK_A))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}", summary=f"sb{i}", replay_key=_RK_B))
        summary = e.replay_key_summary()
        assert summary[0] == (_RK_A, 5)
        assert summary[1] == (_RK_B, 2)

    def test_tie_broken_alphabetically_by_key(self):
        e = self._e()
        rk_z = "zzz-" + "z" * 59
        rk_a = "aaa-" + "a" * 59
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fz{i}", trace_id=f"tz{i}", summary=f"sz{i}", replay_key=rk_z))
        for i in range(2):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}", summary=f"sa{i}", replay_key=rk_a))
        summary = e.replay_key_summary()
        assert summary[0][0] == rk_a
        assert summary[1][0] == rk_z

    def test_sum_of_counts_equals_buffer_size(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rfr(failure_id=f"fa{i}", trace_id=f"ta{i}", summary=f"sa{i}", replay_key=_RK_A))
        for i in range(4):
            e.ingest(_rfr(failure_id=f"fb{i}", trace_id=f"tb{i}", summary=f"sb{i}", replay_key=_RK_B))
        total = sum(c for _, c in e.replay_key_summary())
        assert total == e.buffer_size()

    def test_after_eviction_key_disappears(self):
        e = self._e()
        e.ingest(_rfr(replay_key=_RK_A))
        e.evict_by_replay_key(_RK_A)
        keys = [k for k, _ in e.replay_key_summary()]
        assert _RK_A not in keys

    def test_returns_list_of_tuples(self):
        e = self._e()
        e.ingest(_rfr())
        summary = e.replay_key_summary()
        assert isinstance(summary, list)
        assert isinstance(summary[0], tuple)
        assert len(summary[0]) == 2


# ============================================================
# Creative: POE — top_templates_by_outcome
# ============================================================


class TestTopTemplatesByOutcome:
    def _e(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        return PromptOutcomeEmbedder(max_buffer=10_000)

    def test_empty_buffer_returns_empty(self):
        e = self._e()
        assert e.top_templates_by_outcome("ALLOWED") == []

    def test_invalid_outcome_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="outcome"):
            e.top_templates_by_outcome("INVALID_OUTCOME")

    def test_filters_by_outcome(self):
        e = self._e()
        for i in range(3):
            e.ingest(
                _poem(
                    record_id=f"a{i}",
                    trace_id=f"ta{i}",
                    task=f"t-a{i}",
                    safety="ALLOWED",
                    template_id="tmpl-allow",
                )
            )
        for i in range(2):
            e.ingest(
                _poem(
                    record_id=f"b{i}",
                    trace_id=f"tb{i}",
                    task=f"t-b{i}",
                    safety="BLOCKED",
                    template_id="tmpl-block",
                )
            )
        allowed = e.top_templates_by_outcome("ALLOWED")
        blocked = e.top_templates_by_outcome("BLOCKED")
        assert dict(allowed).get("tmpl-allow") == 3
        assert dict(allowed).get("tmpl-block", 0) == 0
        assert dict(blocked).get("tmpl-block") == 2

    def test_highest_count_first(self):
        e = self._e()
        for i in range(5):
            e.ingest(
                _poem(
                    record_id=f"r-v3-{i}",
                    trace_id=f"t-v3-{i}",
                    task=f"tv3{i}",
                    safety="BLOCKED",
                    template_id="tmpl-v3",
                )
            )
        for i in range(2):
            e.ingest(
                _poem(
                    record_id=f"r-v4-{i}",
                    trace_id=f"t-v4-{i}",
                    task=f"tv4{i}",
                    safety="BLOCKED",
                    template_id="tmpl-v4",
                )
            )
        result = e.top_templates_by_outcome("BLOCKED")
        assert result[0] == ("tmpl-v3", 5)

    def test_tie_broken_alphabetically(self):
        e = self._e()
        for tid in ("tmpl-zzz", "tmpl-aaa"):
            for i in range(2):
                e.ingest(
                    _poem(
                        record_id=f"r-{tid}-{i}",
                        trace_id=f"t-{tid}-{i}",
                        task=f"task-{tid}-{i}",
                        safety="ESCALATED",
                        template_id=tid,
                    )
                )
        result = e.top_templates_by_outcome("ESCALATED")
        assert result[0][0] == "tmpl-aaa"

    def test_top_n_capped_at_50(self):
        e = self._e()
        for i in range(55):
            e.ingest(
                _poem(
                    record_id=f"r{i}",
                    trace_id=f"t{i}",
                    task=f"task{i}",
                    safety="ALLOWED",
                    template_id=f"tmpl-{i:03d}",
                )
            )
        assert len(e.top_templates_by_outcome("ALLOWED", top_n=999)) <= 50

    def test_top_n_limits_output(self):
        e = self._e()
        for i in range(10):
            e.ingest(
                _poem(
                    record_id=f"r{i}",
                    trace_id=f"t{i}",
                    task=f"task{i}",
                    safety="ALLOWED",
                    template_id=f"tmpl-{i}",
                )
            )
        assert len(e.top_templates_by_outcome("ALLOWED", top_n=3)) == 3

    def test_after_eviction_counts_updated(self):
        e = self._e()
        for i in range(3):
            e.ingest(
                _poem(
                    record_id=f"rv3{i}",
                    trace_id=f"tv3{i}",
                    task=f"tv3task{i}",
                    safety="BLOCKED",
                    template_id="tmpl-v3",
                )
            )
        e.evict_by_template_id("tmpl-v3")
        assert e.top_templates_by_outcome("BLOCKED") == []


# ============================================================
# Creative: POE — model_stats
# ============================================================


class TestModelStats:
    def _e(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        return PromptOutcomeEmbedder(max_buffer=10_000)

    def test_empty_buffer_returns_empty_dict(self):
        e = self._e()
        assert e.model_stats() == {}

    def test_correct_breakdown_per_model(self):
        e = self._e()
        for i in range(3):
            e.ingest(
                _poem(record_id=f"ra{i}", trace_id=f"ta{i}", task=f"ta{i}", safety="ALLOWED", model="gpt-4o")
            )
        for i in range(2):
            e.ingest(
                _poem(record_id=f"rb{i}", trace_id=f"tb{i}", task=f"tb{i}", safety="BLOCKED", model="gpt-4o")
            )
        e.ingest(_poem(record_id="rc0", trace_id="tc0", task="tc0", safety="ALLOWED", model="gpt-3.5-turbo"))
        stats = e.model_stats()
        assert stats["gpt-4o"]["ALLOWED"] == 3
        assert stats["gpt-4o"]["BLOCKED"] == 2
        assert stats["gpt-3.5-turbo"]["ALLOWED"] == 1

    def test_sorted_by_model_name(self):
        e = self._e()
        for model in ("zzz-model", "aaa-model", "mmm-model"):
            e.ingest(_poem(record_id=f"r-{model}", trace_id=f"t-{model}", task=f"task-{model}", model=model))
        keys = list(e.model_stats().keys())
        assert keys == sorted(keys)

    def test_multiple_outcomes_same_model(self):
        e = self._e()
        for outcome in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            e.ingest(
                _poem(
                    record_id=f"r-{outcome}",
                    trace_id=f"t-{outcome}",
                    task=f"task-{outcome}",
                    safety=outcome,
                    model="uni-model",
                )
            )
        stats = e.model_stats()
        assert len(stats["uni-model"]) == 5

    def test_returns_only_observed_outcomes(self):
        e = self._e()
        e.ingest(_poem(record_id="r1", trace_id="t1", task="t1", safety="ALLOWED", model="sparse-model"))
        stats = e.model_stats()
        assert "ALLOWED" in stats["sparse-model"]
        assert "BLOCKED" not in stats["sparse-model"]

    def test_after_eviction_model_disappears(self):
        e = self._e()
        e.ingest(
            _poem(
                record_id="rv",
                trace_id="tv",
                task="tv",
                safety="ALLOWED",
                model="old-model",
                template_id="tmpl-old",
            )
        )
        e.evict_by_template_id("tmpl-old")
        assert "old-model" not in e.model_stats()


# ============================================================
# Creative: POE — evict_before_timestamp
# ============================================================


class TestEvictBeforeTimestamp:
    def _e(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        return PromptOutcomeEmbedder(max_buffer=10_000)

    def test_evicts_records_with_ts_prefix_below_cutoff(self):
        e = self._e()
        e.ingest(_poem(record_id="r-old", task="old", trace_id="@TS:1000"))
        e.ingest(_poem(record_id="r-new", task="new", trace_id="@TS:2000"))
        n = e.evict_before_timestamp(1500)
        assert n == 1
        assert e.buffer_size() == 1

    def test_keeps_records_at_or_above_cutoff(self):
        e = self._e()
        e.ingest(_poem(record_id="r-exact", task="exact", trace_id="@TS:1500"))
        n = e.evict_before_timestamp(1500)
        assert n == 0
        assert e.buffer_size() == 1

    def test_records_without_ts_prefix_kept(self):
        e = self._e()
        e.ingest(_poem(record_id="r-notimestamp", task="no-ts", trace_id="plain-trace-id"))
        n = e.evict_before_timestamp(9_999_999)
        assert n == 0
        assert e.buffer_size() == 1

    def test_zero_cutoff_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="cutoff_utc"):
            e.evict_before_timestamp(0)

    def test_negative_cutoff_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="cutoff_utc"):
            e.evict_before_timestamp(-1)

    def test_malformed_ts_prefix_kept(self):
        e = self._e()
        e.ingest(_poem(record_id="r-bad", task="bad", trace_id="@TS:not_an_int"))
        n = e.evict_before_timestamp(999_999)
        assert n == 0

    def test_meta_cleaned_after_eviction(self):
        e = self._e()
        e.ingest(_poem(record_id="r-old", task="old", trace_id="@TS:100"))
        e.evict_before_timestamp(500)
        assert e.buffer_size() == 0
        assert len(e._meta) == 0  # noqa: SLF001

    def test_idempotent(self):
        e = self._e()
        e.ingest(_poem(record_id="r-old", task="old", trace_id="@TS:100"))
        n1 = e.evict_before_timestamp(500)
        n2 = e.evict_before_timestamp(500)
        assert n1 == 1
        assert n2 == 0


# ============================================================
# Creative: POE — route_distribution
# ============================================================


class TestRouteDistribution:
    def _e(self):
        from system_learning.engines.prompt_outcome_embedder import PromptOutcomeEmbedder

        return PromptOutcomeEmbedder(max_buffer=10_000)

    def test_empty_buffer_returns_empty(self):
        e = self._e()
        assert e.route_distribution() == {}

    def test_counts_by_route(self):
        e = self._e()
        for i in range(3):
            e.ingest(_poem(record_id=f"rs{i}", trace_id=f"ts{i}", task=f"ts{i}", route="L2_STANDARD"))
        for i in range(2):
            e.ingest(_poem(record_id=f"rp{i}", trace_id=f"tp{i}", task=f"tp{i}", route="L2_PREMIUM"))
        dist = e.route_distribution()
        assert dist["L2_STANDARD"] == 3
        assert dist["L2_PREMIUM"] == 2

    def test_sorted_alphabetically(self):
        e = self._e()
        for route in ("ZZZ", "AAA", "MMM"):
            e.ingest(_poem(record_id=f"r-{route}", trace_id=f"t-{route}", task=f"task-{route}", route=route))
        keys = list(e.route_distribution().keys())
        assert keys == sorted(keys)

    def test_sum_equals_buffer_size(self):
        e = self._e()
        for i, route in enumerate(["R1", "R2", "R1", "R3"]):
            e.ingest(_poem(record_id=f"r{i}", trace_id=f"t{i}", task=f"t{i}", route=route))
        dist = e.route_distribution()
        assert sum(dist.values()) == e.buffer_size()

    def test_after_eviction_route_removed(self):
        e = self._e()
        e.ingest(
            _poem(
                record_id="r-stale",
                trace_id="t-stale",
                task="stale",
                route="STALE_ROUTE",
                template_id="tmpl-stale",
            )
        )
        e.evict_by_template_id("tmpl-stale")
        assert "STALE_ROUTE" not in e.route_distribution()


# ============================================================
# Creative: RCE — escalation_candidates
# ============================================================


class TestEscalationCandidates:
    def _e(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        return RetrievalCaseEmbedder(max_buffer=10_000)

    def test_empty_buffer_returns_empty(self):
        e = self._e()
        assert e.escalation_candidates() == []

    def test_only_escalated_cases_returned(self):
        e = self._e()
        e.ingest(_rcr(case_id="esc", query="q-esc", chunk_ids=("x0",), escalation_flag=True))
        e.ingest(_rcr(case_id="non", query="q-non", chunk_ids=("x1",), escalation_flag=False))
        cands = e.escalation_candidates()
        assert len(cands) == 1
        assert cands[0]["case_id"] == "esc"

    def test_sorted_by_completeness_score_asc(self):
        e = self._e()
        for i, cs in enumerate([0.9, 0.3, 0.6]):
            e.ingest(
                _rcr(
                    case_id=f"esc-{i}",
                    query=f"q{i}",
                    chunk_ids=(f"x{i}",),
                    escalation_flag=True,
                    completeness_score=cs,
                )
            )
        cands = e.escalation_candidates()
        scores = [m["completeness_score"] for m in cands]
        assert scores == sorted(scores)

    def test_limit_respected(self):
        e = self._e()
        for i in range(20):
            e.ingest(_rcr(case_id=f"e{i}", query=f"q{i}", chunk_ids=(f"x{i}",), escalation_flag=True))
        assert len(e.escalation_candidates(limit=5)) == 5

    def test_limit_capped_at_100(self):
        e = self._e()
        for i in range(120):
            e.ingest(_rcr(case_id=f"e{i}", query=f"q{i}", chunk_ids=(f"x{i}",), escalation_flag=True))
        assert len(e.escalation_candidates(limit=9999)) <= 100

    def test_returns_copies_not_references(self):
        e = self._e()
        e.ingest(_rcr(case_id="esc-ref", query="q-ref", chunk_ids=("x0",), escalation_flag=True))
        cands = e.escalation_candidates()
        cands[0]["case_id"] = "MUTATED"
        cands2 = e.escalation_candidates()
        assert cands2[0]["case_id"] == "esc-ref"

    def test_tie_broken_by_case_id(self):
        e = self._e()
        for cid in ("zzz-esc", "aaa-esc"):
            e.ingest(
                _rcr(
                    case_id=cid,
                    query=f"q-{cid}",
                    chunk_ids=(f"x-{cid}",),
                    escalation_flag=True,
                    completeness_score=0.5,
                )
            )
        cands = e.escalation_candidates()
        assert cands[0]["case_id"] == "aaa-esc"


# ============================================================
# Creative: RCE — corpus_expansion_report
# ============================================================


class TestCorpusExpansionReport:
    def _e(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        return RetrievalCaseEmbedder(max_buffer=10_000)

    def test_empty_buffer_healthy(self):
        e = self._e()
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "HEALTHY"
        assert r["total"] == 0
        assert r["pure_escalation_count"] == 0

    def test_pure_escalation_count_correct(self):
        e = self._e()
        e.ingest(
            _rcr(case_id="pe", query="q-pe", chunk_ids=("x0",), escalation_flag=True, healer_invoked=False)
        )
        e.ingest(
            _rcr(case_id="he", query="q-he", chunk_ids=("x1",), escalation_flag=True, healer_invoked=True)
        )
        e.ingest(
            _rcr(case_id="ne", query="q-ne", chunk_ids=("x2",), escalation_flag=False, healer_invoked=False)
        )
        r = e.corpus_expansion_report()
        assert r["pure_escalation_count"] == 1

    def test_weak_support_count_correct(self):
        e = self._e()
        for i in range(4):
            e.ingest(_rcr(case_id=f"w{i}", query=f"q{i}", chunk_ids=(f"x{i}",), support_score=0.3))
        for i in range(2):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}", chunk_ids=(f"xs{i}",), support_score=0.9))
        r = e.corpus_expansion_report()
        assert r["weak_support_count"] == 4

    def test_replay_failure_count_correct(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rcr(case_id=f"rf{i}", query=f"qr{i}", chunk_ids=(f"xr{i}",), replay_pass=False))
        r = e.corpus_expansion_report()
        assert r["replay_failure_count"] == 3

    def test_tier_healthy_when_degradation_rate_below_20pct(self):
        e = self._e()
        for i in range(9):
            e.ingest(
                _rcr(
                    case_id=f"s{i}",
                    query=f"qs{i}",
                    chunk_ids=(f"xs{i}",),
                    support_score=0.9,
                    replay_pass=True,
                )
            )
        e.ingest(_rcr(case_id="w0", query="qw0", chunk_ids=("xw0",), support_score=0.3))
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "HEALTHY"

    def test_tier_degraded_when_between_20_and_50pct(self):
        e = self._e()
        for i in range(7):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}", chunk_ids=(f"xs{i}",), support_score=0.9))
        for i in range(3):
            e.ingest(_rcr(case_id=f"w{i}", query=f"qw{i}", chunk_ids=(f"xw{i}",), support_score=0.2))
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "DEGRADED"

    def test_tier_critical_when_above_50pct(self):
        e = self._e()
        for i in range(4):
            e.ingest(_rcr(case_id=f"s{i}", query=f"qs{i}", chunk_ids=(f"xs{i}",), support_score=0.9))
        for i in range(6):
            e.ingest(
                _rcr(
                    case_id=f"w{i}",
                    query=f"qw{i}",
                    chunk_ids=(f"xw{i}",),
                    support_score=0.1,
                    replay_pass=False,
                )
            )
        r = e.corpus_expansion_report()
        assert r["quality_tier"] == "CRITICAL"

    def test_total_matches_buffer_size(self):
        e = self._e()
        for i in range(7):
            e.ingest(_rcr(case_id=f"c{i}", query=f"q{i}", chunk_ids=(f"x{i}",)))
        r = e.corpus_expansion_report()
        assert r["total"] == e.buffer_size()


# ============================================================
# Creative: RCE — evict_by_query_id
# ============================================================


class TestEvictByQueryId:
    def _e(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        return RetrievalCaseEmbedder(max_buffer=10_000)

    def test_evicts_correct_records(self):
        e = self._e()
        for i in range(3):
            e.ingest(_rcr(case_id=f"c-q1-{i}", query=f"q-q1-{i}", chunk_ids=(f"x{i}",), query_id="qid-001"))
        for i in range(2):
            e.ingest(_rcr(case_id=f"c-q2-{i}", query=f"q-q2-{i}", chunk_ids=(f"y{i}",), query_id="qid-002"))
        n = e.evict_by_query_id("qid-001")
        assert n == 3
        assert e.buffer_size() == 2

    def test_empty_query_id_raises(self):
        e = self._e()
        with pytest.raises(ValueError, match="query_id"):
            e.evict_by_query_id("")

    def test_idempotent(self):
        e = self._e()
        e.ingest(_rcr(query_id="qid-x"))
        n1 = e.evict_by_query_id("qid-x")
        n2 = e.evict_by_query_id("qid-x")
        assert n1 == 1
        assert n2 == 0

    def test_meta_cleaned(self):
        e = self._e()
        e.ingest(_rcr(query_id="qid-clean"))
        e.evict_by_query_id("qid-clean")
        assert len(e._meta) == 0  # noqa: SLF001

    def test_nonexistent_query_id_returns_zero(self):
        e = self._e()
        e.ingest(_rcr(query_id="qid-real"))
        assert e.evict_by_query_id("qid-nonexistent") == 0

    def test_does_not_evict_different_query_id(self):
        e = self._e()
        e.ingest(_rcr(case_id="keep", query_id="qid-keep"))
        e.ingest(_rcr(case_id="evict", query="q-evict", chunk_ids=("y0",), query_id="qid-evict"))
        e.evict_by_query_id("qid-evict")
        weak = e.retrieve_weak_cases(support_threshold=1.0)
        ids = [m["case_id"] for m in weak]
        assert "evict" not in ids


# ============================================================
# Creative: RCE — score_percentile_buckets
# ============================================================


class TestScorePercentileBuckets:
    def _e(self):
        from system_learning.engines.retrieval_case_embedder import RetrievalCaseEmbedder

        return RetrievalCaseEmbedder(max_buffer=10_000)

    def test_empty_buffer_all_zeros(self):
        e = self._e()
        buckets = e.score_percentile_buckets()
        for key in ("support_score", "completeness_score"):
            assert buckets[key] == {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

    def test_q1_bucket_for_low_scores(self):
        e = self._e()
        e.ingest(_rcr(support_score=0.1, completeness_score=0.15))
        b = e.score_percentile_buckets()
        assert b["support_score"]["Q1"] == 1
        assert b["completeness_score"]["Q1"] == 1

    def test_q4_bucket_for_high_scores(self):
        e = self._e()
        e.ingest(_rcr(support_score=0.9, completeness_score=0.8))
        b = e.score_percentile_buckets()
        assert b["support_score"]["Q4"] == 1
        assert b["completeness_score"]["Q4"] == 1

    def test_boundary_values_correct_bucket(self):
        e = self._e()
        e.ingest(
            _rcr(case_id="c025", query="q025", chunk_ids=("x0",), support_score=0.25, completeness_score=0.5)
        )
        b = e.score_percentile_buckets()
        assert b["support_score"]["Q2"] == 1
        assert b["completeness_score"]["Q3"] == 1

    def test_sum_of_buckets_equals_buffer_size(self):
        e = self._e()
        for i in range(12):
            e.ingest(
                _rcr(
                    case_id=f"c{i}",
                    query=f"q{i}",
                    chunk_ids=(f"x{i}",),
                    support_score=round((i % 4) * 0.25 + 0.01, 3),
                    completeness_score=round((i % 4) * 0.25 + 0.01, 3),
                )
            )
        b = e.score_percentile_buckets()
        assert sum(b["support_score"].values()) == e.buffer_size()
        assert sum(b["completeness_score"].values()) == e.buffer_size()

    def test_all_four_buckets_always_present(self):
        e = self._e()
        e.ingest(_rcr())
        b = e.score_percentile_buckets()
        for key in ("support_score", "completeness_score"):
            assert set(b[key].keys()) == {"Q1", "Q2", "Q3", "Q4"}

    def test_returns_independent_copies(self):
        e = self._e()
        e.ingest(_rcr())
        b1 = e.score_percentile_buckets()
        b1["support_score"]["Q1"] = 999
        b2 = e.score_percentile_buckets()
        assert b2["support_score"]["Q1"] != 999
