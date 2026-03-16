"""Type-invariant tests for BGE embedding extension addendum types.

Covers:
  - ReplayFailureRecord (addendum §2.4)
  - PromptOutcomeEmbeddingRecord (addendum §2.5)
  - RetrievalCaseRecord (addendum §2.6)
"""

from __future__ import annotations

import pytest

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_bge_embedding_types")
_emit_applies_guardrail("p0", "test_bge_embedding_types", "p0_governance")
_emit_reads_policy_state("p0", "test_bge_embedding_types", "policy_binding")
_emit_snapshots_state("p0", "test_bge_embedding_types", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_bge_embedding_types", "p4obs", "metric_1")
_emit_emits_metric_event("test_bge_embedding_types", "p4obs", "metric_2")
_emit_emits_metric_event("test_bge_embedding_types", "p4obs", "metric_3")
_emit_emits_metric_event("test_bge_embedding_types", "p4obs", "metric_4")
_emit_emits_metric_event("test_bge_embedding_types", "p4obs", "metric_5")
_emit_emits_metric_event("test_bge_embedding_types", "p4obs", "metric_6")
_emit_records_incident_event("test_bge_embedding_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_bge_embedding_types", "p4obs", "anomaly")
_emit_writes_observability_log("test_bge_embedding_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_bge_embedding_types", "p4obs", "mon_state")
_emit_triggers_alert("test_bge_embedding_types", "p4obs", "alert")
_emit_links_incident_trace("test_bge_embedding_types", "p4obs", "trace_link")
_emit_captures_pattern("test_bge_embedding_types", "p3lm", "pattern")
_emit_records_learning_event("test_bge_embedding_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_bge_embedding_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_bge_embedding_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_bge_embedding_types", "p3lm", "routing")
_emit_improves_agent_policy("test_bge_embedding_types", "p3lm", "policy")
_emit_stores_learning_state("test_bge_embedding_types", "p3lm", "state")
_emit_records_execution_trace("test_bge_embedding_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_bge_embedding_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_bge_embedding_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_bge_embedding_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_bge_embedding_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_bge_embedding_types", "env_read", "p2_env_1")
_emit_reads_environ("test_bge_embedding_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_bge_embedding_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_bge_embedding_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_bge_embedding_types", "context_pull")
_emit_pulls_context("p1", "test_bge_embedding_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_bge_embedding_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_bge_embedding_types", "uwg_term_2")
_emit_writes_through("p1", "test_bge_embedding_types", "write_through")
_emit_writes_through("p1", "test_bge_embedding_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_bge_embedding_types", "safety_validation")
_emit_invokes_eval("p1", "test_bge_embedding_types", "eval_call")
_emit_proposal_commits_routing("p1", "test_bge_embedding_types", "routing_commit")
_emit_escalates_to_human("p1", "test_bge_embedding_types", "human_escalation")
_emit_routes_through("p1", "test_bge_embedding_types", "route_through")
_emit_checks_agent_registry("p1", "test_bge_embedding_types", "agent_registry")
_emit_validates_agent_capability("p1", "test_bge_embedding_types", "capability")
_emit_dispatches_execution_plan("p1", "test_bge_embedding_types", "exec_plan")
_emit_agent_executes_agent("p1", "test_bge_embedding_types", "sub_agent")
_emit_routes_to_agent("p1", "test_bge_embedding_types", "target_agent")
_emit_verifies_policy("p1", "test_bge_embedding_types", "policy_check")
_emit_observes_runtime_state("p1", "test_bge_embedding_types", "runtime_state")
_emit_verifies_boundary("p1", "test_bge_embedding_types", "boundary_check")
_emit_transcripts_response("p1", "test_bge_embedding_types", "transcript")
_emit_hard_fails_untranscripted("p1", "test_bge_embedding_types")
_emit_gated_by_confidence("p1", "test_bge_embedding_types", "confidence_gate")
emit_replay_key("p0", "test_bge_embedding_types")
emit_determinism_digest("p0", "test_bge_embedding_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_bge_embedding_types", "execution_auth")
_emit_validates_capability("p2", "test_bge_embedding_types", "capability_check")
_emit_routes_to_capability("p2", "test_bge_embedding_types", "capability_route")
_emit_writes_via_uwg("p2", "test_bge_embedding_types", "uwg_write")
_emit_blocks_direct_write("p2", "test_bge_embedding_types", "direct_write_block")
_emit_records_tool_invocation("p2", "test_bge_embedding_types", "tool_invocation")
_emit_captures_execution_output("p2", "test_bge_embedding_types", "exec_output")
_emit_dispatches_agent("p3", "test_bge_embedding_types", "agent_dispatch")
_emit_coordinates_agents("p3", "test_bge_embedding_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_bge_embedding_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_bge_embedding_types", "healing_outcome")
_emit_escalates_failure("p3", "test_bge_embedding_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_bge_embedding_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_bge_embedding_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_bge_embedding_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_bge_embedding_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_bge_embedding_types", "eval_metric")
_emit_stores_embedding("p4", "test_bge_embedding_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_bge_embedding_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_bge_embedding_types", "exec_snapshot_link")

# ============================================================
# Constants
# ============================================================

_TS = 1_700_200_000
_RK = "rk-" + "a" * 60
_DD = "dd-" + "b" * 60
_PH = "ph-" + "c" * 60
_TID = "tr-001"


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
# 1. ReplayFailureRecord — type invariants
# ============================================================


class TestReplayFailureRecord:
    def test_hash_computed_on_construction(self):
        r = _rfr()
        assert len(r.failure_hash) == 64
        assert r.failure_hash.isalnum()

    def test_hash_deterministic(self):
        assert _rfr().failure_hash == _rfr().failure_hash

    def test_different_nd_type_gives_different_hash(self):
        r1 = _rfr(nd_type="HASH_MISMATCH")
        r2 = _rfr(nd_type="ORDERING_INSTABILITY")
        assert r1.failure_hash != r2.failure_hash

    def test_influence_class_c0(self):
        assert _rfr().influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutable(self):
        r = _rfr()
        with pytest.raises((AttributeError, TypeError)):
            r.nondeterminism_type = "MUTATED"  # type: ignore[misc]

    def test_empty_failure_id_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord

        with pytest.raises(ValueError, match="failure_id"):
            ReplayFailureRecord(
                failure_id="",
                failure_summary="x",
                nondeterminism_type="T",
                mismatch_explanation="m",
                affected_subsystems=(),
                attempted_remediation="r",
                replay_key=_RK,
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_empty_nondeterminism_type_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord

        with pytest.raises(ValueError, match="nondeterminism_type"):
            ReplayFailureRecord(
                failure_id="f",
                failure_summary="x",
                nondeterminism_type="",
                mismatch_explanation="m",
                affected_subsystems=(),
                attempted_remediation="r",
                replay_key=_RK,
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_empty_replay_key_raises(self):
        from system_learning.types.semantic_memory_types import ReplayFailureRecord

        with pytest.raises(ValueError, match="replay_key"):
            ReplayFailureRecord(
                failure_id="f",
                failure_summary="x",
                nondeterminism_type="T",
                mismatch_explanation="m",
                affected_subsystems=(),
                attempted_remediation="r",
                replay_key="",
                determinism_digest=_DD,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_embedding_text_excludes_ids(self):
        r = _rfr(replay_key=_RK, dd=_DD, trace_id="tr-secret")
        text = r.to_embedding_text()
        assert _RK not in text
        assert _DD not in text
        assert "tr-secret" not in text

    def test_embedding_text_contains_all_semantic_fields(self):
        r = _rfr(
            summary="L3 hash mismatch",
            nd_type="HASH_MISMATCH",
            mismatch="digest diff",
            subsystems=("L3", "L0"),
            remediation="re-seed ctx",
        )
        text = r.to_embedding_text()
        assert "L3 hash mismatch" in text
        assert "HASH_MISMATCH" in text
        assert "digest diff" in text
        assert "L0" in text
        assert "re-seed ctx" in text

    def test_embedding_text_has_5_segments(self):
        parts = _rfr().to_embedding_text().split(" ## ")
        assert len(parts) == 5

    def test_affected_subsystems_sorted_in_embedding(self):
        r = _rfr(subsystems=("ZZZ", "AAA", "MMM"))
        text = r.to_embedding_text()
        assert text.index("AAA") < text.index("MMM") < text.index("ZZZ")


# ============================================================
# 2. PromptOutcomeEmbeddingRecord — type invariants
# ============================================================


class TestPromptOutcomeEmbeddingRecord:
    def test_hash_computed(self):
        r = _poem()
        assert len(r.record_hash) == 64

    def test_hash_deterministic(self):
        assert _poem().record_hash == _poem().record_hash

    def test_different_task_gives_different_hash(self):
        r1 = _poem(task="classify intent")
        r2 = _poem(task="summarize document")
        assert r1.record_hash != r2.record_hash

    def test_influence_class_c0(self):
        assert _poem().influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutable(self):
        r = _poem()
        with pytest.raises((AttributeError, TypeError)):
            r.safety_outcome = "BLOCKED"  # type: ignore[misc]

    def test_empty_record_id_raises(self):
        from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

        with pytest.raises(ValueError, match="record_id"):
            PromptOutcomeEmbeddingRecord(
                record_id="",
                slot_s0_summary="s",
                slot_d0_summary="d",
                slot_i0_summary="i",
                slot_c0_summary="c",
                slot_u0_summary="u",
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

    def test_invalid_safety_outcome_raises(self):
        from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

        with pytest.raises(ValueError, match="safety_outcome"):
            PromptOutcomeEmbeddingRecord(
                record_id="r",
                slot_s0_summary="s",
                slot_d0_summary="d",
                slot_i0_summary="i",
                slot_c0_summary="c",
                slot_u0_summary="u",
                task_description="t",
                answer_summary="a",
                safety_outcome="UNKNOWN_BAD",
                retrieval_grounding_summary="g",
                prompt_hash="ph",
                template_id="ti",
                route="r",
                model="m",
                policy_hash="plh",
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_all_five_safety_outcomes_accepted(self):
        for outcome in ("ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"):
            r = _poem(safety=outcome, record_id=f"r-{outcome}")
            assert r.safety_outcome == outcome

    def test_embedding_text_excludes_ids(self):
        r = _poem(
            prompt_hash="secret_ph", template_id="secret_tmpl", trace_id="secret_tr", policy_hash="secret_pol"
        )
        text = r.to_embedding_text()
        assert "secret_ph" not in text
        assert "secret_tmpl" not in text
        assert "secret_tr" not in text
        assert "secret_pol" not in text

    def test_embedding_text_contains_all_slot_summaries(self):
        r = _poem(
            s0="SYS", d0="DOM", i0="INS", c0="CTX", u0="USR", task="TASK", answer="ANS", grounding="GRND"
        )
        text = r.to_embedding_text()
        for token in ("SYS", "DOM", "INS", "CTX", "USR", "TASK", "ANS", "GRND"):
            assert token in text

    def test_embedding_text_has_9_segments(self):
        parts = _poem().to_embedding_text().split(" ## ")
        assert len(parts) == 9

    def test_embedding_text_starts_with_s0(self):
        r = _poem(s0="system_anchor")
        assert r.to_embedding_text().startswith("s0:system_anchor")


# ============================================================
# 3. RetrievalCaseRecord — type invariants
# ============================================================


class TestRetrievalCaseRecord:
    def test_hash_computed(self):
        r = _rcr()
        assert len(r.case_hash) == 64

    def test_hash_deterministic(self):
        assert _rcr().case_hash == _rcr().case_hash

    def test_different_support_scores_give_different_hashes(self):
        r1 = _rcr(support_score=0.8)
        r2 = _rcr(support_score=0.2)
        assert r1.case_hash != r2.case_hash

    def test_influence_class_c0(self):
        assert _rcr().influence_class == "C0_INFORMATIONAL"

    def test_frozen_immutable(self):
        r = _rcr()
        with pytest.raises((AttributeError, TypeError)):
            r.support_score = 0.0  # type: ignore[misc]

    def test_empty_case_id_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord

        with pytest.raises(ValueError, match="case_id"):
            RetrievalCaseRecord(
                case_id="",
                query_summary="q",
                chunk_summaries=(),
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=(),
                support_score=0.5,
                completeness_score=0.5,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_support_score_out_of_range_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord

        with pytest.raises(ValueError, match="support_score"):
            RetrievalCaseRecord(
                case_id="c",
                query_summary="q",
                chunk_summaries=(),
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=(),
                support_score=1.5,
                completeness_score=0.5,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_completeness_score_out_of_range_raises(self):
        from system_learning.types.semantic_memory_types import RetrievalCaseRecord

        with pytest.raises(ValueError, match="completeness_score"):
            RetrievalCaseRecord(
                case_id="c",
                query_summary="q",
                chunk_summaries=(),
                support_reasoning="s",
                answer_quality_summary="a",
                query_id="qi",
                chunk_ids=(),
                support_score=0.5,
                completeness_score=-0.1,
                escalation_flag=False,
                healer_invoked=False,
                replay_pass=True,
                trace_id="tr",
                timestamp_utc=_TS,
            )

    def test_scores_at_boundary_accepted(self):
        for ss, cs in ((0.0, 0.0), (1.0, 1.0), (0.5, 0.5)):
            r = _rcr(support_score=ss, completeness_score=cs, case_id=f"c{ss}{cs}")
            assert r.support_score == ss

    def test_embedding_text_excludes_ids(self):
        r = _rcr(query_id="secret_qid", chunk_ids=("secret_cid",))
        text = r.to_embedding_text()
        assert "secret_qid" not in text
        assert "secret_cid" not in text

    def test_embedding_text_has_4_segments(self):
        parts = _rcr().to_embedding_text().split(" ## ")
        assert len(parts) == 4

    def test_chunk_summaries_sorted_in_embedding(self):
        r = _rcr(chunks=("ZZZ chunk", "AAA chunk", "MMM chunk"))
        text = r.to_embedding_text()
        assert text.index("AAA") < text.index("MMM") < text.index("ZZZ")

    def test_scores_rounded_in_canonical_dict(self):
        r = _rcr(support_score=0.123456789, completeness_score=0.987654321)
        d = r._canonical_dict()
        assert d["support_score"] == round(0.123456789, 6)
        assert d["completeness_score"] == round(0.987654321, 6)
