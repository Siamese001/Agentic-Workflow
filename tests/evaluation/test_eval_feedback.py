"""
Tests: Phase 5 — Human Feedback and Alignment

Branch coverage:
- ReviewRubric: is_positive (all combos), quality_score, to_dict, from_dict
- FeedbackExample: to_dict, from_dict roundtrip
- DPOPair: to_dict, from_dict, frozen
- DPOBatch: to_dict
- DPOBatchBuilder: empty input, no cross-query pairs, positive+negative pairing,
                   min_score_delta filter, invalid delta raises, L4 persist
- ImprovementSignal: to_dict
- ImprovementProposal: to_dict, from_dict, requires_intervention
- EvaluatorProposerBridge: no inputs, with eval report, with drift, with dpo,
                            health score, recommend_actions, L4 persist
"""

import pytest

from agentic_core.evaluation.feedback.dpo_batch_builder import DPOBatchBuilder
from agentic_core.evaluation.feedback.proposer_bridge import (
    EvaluatorProposerBridge,
    ImprovementProposal,
    ImprovementSignal,
)
from agentic_core.evaluation.feedback.schemas import (
    DPOBatch,
    DPOPair,
    FeedbackExample,
    ReviewRubric,
)
from agentic_core.evaluation.monitoring.snapshots import (
    AnswerQualitySnapshot,
    RetrievalDriftSnapshot,
)
from agentic_core.evaluation.schemas.evaluation_result_schema import EvaluationReport
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_eval_feedback")
# REMOVED: _emit_applies_guardrail("p0", "test_eval_feedback", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_eval_feedback", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_eval_feedback", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_eval_feedback", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_eval_feedback", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_eval_feedback", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_eval_feedback", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_eval_feedback", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_eval_feedback", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_eval_feedback", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_eval_feedback", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_eval_feedback", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_eval_feedback", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_eval_feedback", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_eval_feedback", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_eval_feedback", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_eval_feedback", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_eval_feedback", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_eval_feedback", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_eval_feedback", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_eval_feedback", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_eval_feedback", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_eval_feedback", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_eval_feedback", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_eval_feedback", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_eval_feedback", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_eval_feedback", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_eval_feedback", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_eval_feedback", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_eval_feedback", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_eval_feedback", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_eval_feedback", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_eval_feedback", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_eval_feedback", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_eval_feedback", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_eval_feedback", "write_through")
# REMOVED: _emit_writes_through("p1", "test_eval_feedback", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_eval_feedback", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_eval_feedback", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_eval_feedback", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_eval_feedback", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_eval_feedback", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_eval_feedback", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_eval_feedback", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_eval_feedback", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_eval_feedback", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_eval_feedback", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_eval_feedback", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_eval_feedback", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_eval_feedback", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_eval_feedback", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_eval_feedback")
# REMOVED: _emit_gated_by_confidence("p1", "test_eval_feedback", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_eval_feedback")
# REMOVED: emit_determinism_digest("p0", "test_eval_feedback")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_eval_feedback", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_eval_feedback", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_eval_feedback", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_eval_feedback", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_eval_feedback", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_eval_feedback", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_eval_feedback", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_eval_feedback", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_eval_feedback", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_eval_feedback", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_eval_feedback", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_eval_feedback", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_eval_feedback", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_eval_feedback", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_eval_feedback", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_eval_feedback", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_eval_feedback", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_eval_feedback", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_eval_feedback", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_eval_feedback", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_rubric(grounded=True, useful=True, correct=True, safe=True, missing=False):
    return ReviewRubric(
        grounded=grounded,
        useful=useful,
        correct=correct,
        safe=safe,
        missing_context=missing,
    )


def _make_feedback(
    example_id="ex_0",
    query="q",
    answer="model answer",
    rubric=None,
    ctx=None,
):
    return FeedbackExample(
        example_id=example_id,
        query=query,
        model_answer=answer,
        human_annotation=rubric or _make_rubric(),
        context_documents=ctx or ["doc_1"],
        timestamp="2025-01-01T00:00:00Z",
    )


def _make_report(scores=None):
    return EvaluationReport(
        run_id="run_001",
        dataset_name="test",
        dataset_version="1.0",
        system_version="v1",
        timestamp="2025-01-01T00:00:00Z",
        aggregate_scores=scores
        or {
            "precision@5": 0.75,
            "recall@10": 0.80,
            "MRR": 0.70,
            "NDCG@10": 0.72,
            "groundedness": 0.85,
            "answer_correctness": 0.78,
        },
        per_example_results=[],
    )


# ---------------------------------------------------------------------------
# ReviewRubric
# ---------------------------------------------------------------------------


class TestReviewRubric:
    def test_all_positive_is_positive(self):
        assert _make_rubric().is_positive is True

    def test_not_grounded_is_negative(self):
        assert _make_rubric(grounded=False).is_positive is False

    def test_not_useful_is_negative(self):
        assert _make_rubric(useful=False).is_positive is False

    def test_not_correct_is_negative(self):
        assert _make_rubric(correct=False).is_positive is False

    def test_not_safe_is_negative(self):
        assert _make_rubric(safe=False).is_positive is False

    def test_quality_score_perfect(self):
        assert _make_rubric(missing=False).quality_score == pytest.approx(1.0)

    def test_quality_score_penalized_by_missing_context(self):
        score_no_missing = _make_rubric(missing=False).quality_score
        score_with_missing = _make_rubric(missing=True).quality_score
        assert score_with_missing < score_no_missing

    def test_quality_score_zero_floor(self):
        # All negative + missing context → must not go below 0
        r = ReviewRubric(grounded=False, useful=False, correct=False, safe=False, missing_context=True)
        assert r.quality_score >= 0.0

    def test_quality_score_range(self):
        for g in [True, False]:
            for u in [True, False]:
                for c in [True, False]:
                    for s in [True, False]:
                        score = _make_rubric(g, u, c, s).quality_score
                        assert 0.0 <= score <= 1.0

    def test_to_dict_roundtrip(self):
        r = _make_rubric(grounded=True, missing=True)
        d = r.to_dict()
        restored = ReviewRubric.from_dict(d)
        assert restored.grounded is True
        assert restored.missing_context is True

    def test_from_dict_optional_fields(self):
        d = {
            "grounded": True,
            "useful": True,
            "correct": True,
            "safe": True,
            "missing_context": False,
        }
        r = ReviewRubric.from_dict(d)
        assert r.reviewer_id == ""
        assert r.notes == ""


# ---------------------------------------------------------------------------
# FeedbackExample
# ---------------------------------------------------------------------------


class TestFeedbackExample:
    def test_to_dict_roundtrip(self):
        ex = _make_feedback()
        d = ex.to_dict()
        restored = FeedbackExample.from_dict(d)
        assert restored.example_id == ex.example_id
        assert restored.query == ex.query
        assert restored.model_answer == ex.model_answer
        assert restored.human_annotation.grounded == ex.human_annotation.grounded

    def test_context_documents_preserved(self):
        ex = _make_feedback(ctx=["doc_1", "doc_2", "doc_3"])
        d = ex.to_dict()
        restored = FeedbackExample.from_dict(d)
        assert restored.context_documents == ["doc_1", "doc_2", "doc_3"]

    def test_metadata_defaults_empty(self):
        d = _make_feedback().to_dict()
        d.pop("metadata", None)
        restored = FeedbackExample.from_dict({**d, "metadata": {}})
        assert restored.metadata == {}


# ---------------------------------------------------------------------------
# DPOPair
# ---------------------------------------------------------------------------


class TestDPOPair:
    def _make(self):
        return DPOPair(
            pair_id="pair_001",
            query="what is governance?",
            chosen_response="The governance validator enforces rules.",
            rejected_response="I don't know.",
            context_documents=["doc_1", "doc_2"],
            chosen_score=0.9,
            rejected_score=0.2,
            source_example_ids=["ex_0", "ex_1"],
        )

    def test_to_dict_roundtrip(self):
        p = self._make()
        d = p.to_dict()
        restored = DPOPair.from_dict(d)
        assert restored.pair_id == p.pair_id
        assert restored.chosen_score == pytest.approx(p.chosen_score)
        assert restored.rejected_score == pytest.approx(p.rejected_score)

    def test_frozen(self):
        p = self._make()
        with pytest.raises((AttributeError, TypeError)):
            p.pair_id = "changed"

    def test_context_documents_preserved(self):
        p = self._make()
        d = p.to_dict()
        assert d["context_documents"] == ["doc_1", "doc_2"]

    def test_source_example_ids_preserved(self):
        p = self._make()
        assert p.source_example_ids == ("ex_0", "ex_1") or p.source_example_ids == ["ex_0", "ex_1"]


# ---------------------------------------------------------------------------
# DPOBatch
# ---------------------------------------------------------------------------


class TestDPOBatch:
    def _make_pair(self, n):
        return DPOPair(
            pair_id=f"pair_{n}",
            query="q",
            chosen_response="chosen",
            rejected_response="rejected",
            context_documents=[],
            chosen_score=0.9,
            rejected_score=0.1,
            source_example_ids=[],
        )

    def test_to_dict_keys(self):
        batch = DPOBatch(
            batch_id="batch_001",
            timestamp="2025-01-01T00:00:00Z",
            pair_count=2,
            pairs=[self._make_pair(0), self._make_pair(1)],
            source_feedback_count=4,
        )
        d = batch.to_dict()
        assert d["pair_count"] == 2
        assert len(d["pairs"]) == 2
        assert d["source_feedback_count"] == 4


# ---------------------------------------------------------------------------
# DPOBatchBuilder
# ---------------------------------------------------------------------------


class TestDPOBatchBuilder:
    def test_invalid_min_score_delta_raises(self):
        with pytest.raises(ValueError):
            DPOBatchBuilder(min_score_delta=-0.1)

    def test_empty_input_returns_empty_batch(self):
        builder = DPOBatchBuilder()
        batch = builder.generate_pairs([])
        assert batch.pair_count == 0
        assert len(batch.pairs) == 0

    def test_only_positives_no_pairs(self):
        decisions = [
            _make_feedback("ex_0", "q", rubric=_make_rubric()),
            _make_feedback("ex_1", "q", rubric=_make_rubric()),
        ]
        batch = DPOBatchBuilder().generate_pairs(decisions)
        assert batch.pair_count == 0

    def test_only_negatives_no_pairs(self):
        decisions = [
            _make_feedback("ex_0", "q", rubric=_make_rubric(grounded=False)),
            _make_feedback("ex_1", "q", rubric=_make_rubric(correct=False)),
        ]
        batch = DPOBatchBuilder().generate_pairs(decisions)
        assert batch.pair_count == 0

    def test_one_positive_one_negative_produces_pair(self):
        decisions = [
            _make_feedback("ex_0", "q", answer="good answer", rubric=_make_rubric()),
            _make_feedback("ex_1", "q", answer="bad answer", rubric=_make_rubric(correct=False)),
        ]
        batch = DPOBatchBuilder(min_score_delta=0.0).generate_pairs(decisions)
        assert batch.pair_count == 1
        assert batch.pairs[0].chosen_response == "good answer"
        assert batch.pairs[0].rejected_response == "bad answer"

    def test_min_score_delta_filters_pairs(self):
        # positive score = 0.75, negative score = 0.75 - epsilon → delta = epsilon < threshold
        pos_rubric = ReviewRubric(grounded=True, useful=True, correct=True, safe=True, missing_context=False)
        neg_rubric = ReviewRubric(grounded=False, useful=True, correct=True, safe=True, missing_context=False)
        decisions = [
            _make_feedback("ex_0", "q", answer="good", rubric=pos_rubric),
            _make_feedback("ex_1", "q", answer="bad", rubric=neg_rubric),
        ]
        # With a very high threshold, the pair should be filtered out
        batch = DPOBatchBuilder(min_score_delta=0.99).generate_pairs(decisions)
        assert batch.pair_count == 0

    def test_multiple_queries_produce_independent_pairs(self):
        decisions = [
            _make_feedback("ex_0", "q1", answer="good", rubric=_make_rubric()),
            _make_feedback("ex_1", "q1", answer="bad", rubric=_make_rubric(correct=False)),
            _make_feedback("ex_2", "q2", answer="good", rubric=_make_rubric()),
            _make_feedback("ex_3", "q2", answer="bad", rubric=_make_rubric(grounded=False)),
        ]
        batch = DPOBatchBuilder(min_score_delta=0.0).generate_pairs(decisions)
        assert batch.pair_count == 2

    def test_source_feedback_count_matches_input(self):
        decisions = [_make_feedback(f"ex_{i}", "q") for i in range(5)]
        batch = DPOBatchBuilder().generate_pairs(decisions)
        assert batch.source_feedback_count == 5

    def test_pair_ids_are_unique(self):
        decisions = [
            _make_feedback("ex_0", "q", answer="good", rubric=_make_rubric()),
            _make_feedback("ex_1", "q", answer="bad", rubric=_make_rubric(correct=False)),
            _make_feedback("ex_2", "q", answer="worse", rubric=_make_rubric(grounded=False, correct=False)),
        ]
        batch = DPOBatchBuilder(min_score_delta=0.0).generate_pairs(decisions)
        pair_ids = [p.pair_id for p in batch.pairs]
        assert len(pair_ids) == len(set(pair_ids))

    def test_deterministic_output_order(self):
        decisions = [
            _make_feedback("ex_b", "query_b", answer="good_b", rubric=_make_rubric()),
            _make_feedback("ex_a", "query_a", answer="good_a", rubric=_make_rubric()),
            _make_feedback("ex_c", "query_b", answer="bad_b", rubric=_make_rubric(correct=False)),
            _make_feedback("ex_d", "query_a", answer="bad_a", rubric=_make_rubric(grounded=False)),
        ]
        # Queries sorted alphabetically: query_a first, then query_b
        batch = DPOBatchBuilder(min_score_delta=0.0).generate_pairs(decisions)
        if len(batch.pairs) >= 2:
            assert batch.pairs[0].query == "query_a"
            assert batch.pairs[1].query == "query_b"

    def test_l4_persist_called(self):
        stored = []

        class FakeStore:
            def put(self, a):
                stored.append(a)

        decisions = [
            _make_feedback("ex_0", "q", answer="good", rubric=_make_rubric()),
            _make_feedback("ex_1", "q", answer="bad", rubric=_make_rubric(correct=False)),
        ]
        batch = DPOBatchBuilder(min_score_delta=0.0, l4_store=FakeStore()).generate_pairs(decisions)
        assert len(stored) == 1

    def test_l4_persist_graceful_on_exception(self):
        class BrokenStore:
            def put(self, a):
                raise OSError("disk full")

        decisions = [
            _make_feedback("ex_0", "q", answer="good", rubric=_make_rubric()),
            _make_feedback("ex_1", "q", answer="bad", rubric=_make_rubric(correct=False)),
        ]
        batch = DPOBatchBuilder(min_score_delta=0.0, l4_store=BrokenStore()).generate_pairs(decisions)
        assert batch is not None


# ---------------------------------------------------------------------------
# ImprovementSignal
# ---------------------------------------------------------------------------


class TestImprovementSignal:
    def test_to_dict_keys(self):
        s = ImprovementSignal(
            signal_type="eval_metric",
            metric_name="precision@5",
            current_value=0.7,
            target_value=0.8,
            delta=-0.1,
            priority="warning",
            source="run_001",
            message="below target",
        )
        d = s.to_dict()
        assert d["signal_type"] == "eval_metric"
        assert d["delta"] == pytest.approx(-0.1)


# ---------------------------------------------------------------------------
# ImprovementProposal
# ---------------------------------------------------------------------------


class TestImprovementProposal:
    def _make(self, health=0.80, requires=False):
        return ImprovementProposal(
            proposal_id="prop_001",
            timestamp="2025-01-01T00:00:00Z",
            signals=[],
            dpo_pair_count=5,
            recommended_actions=["tune_reranker"],
            overall_health_score=health,
            requires_intervention=requires,
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert "proposal_id" in d
        assert "overall_health_score" in d
        assert "requires_intervention" in d

    def test_from_dict_roundtrip(self):
        p = self._make()
        d = p.to_dict()
        restored = ImprovementProposal.from_dict(d)
        assert restored.proposal_id == p.proposal_id
        assert restored.overall_health_score == pytest.approx(p.overall_health_score)
        assert restored.requires_intervention == p.requires_intervention

    def test_requires_intervention_true(self):
        p = self._make(requires=True)
        assert p.requires_intervention is True

    def test_requires_intervention_false(self):
        p = self._make(requires=False)
        assert p.requires_intervention is False


# ---------------------------------------------------------------------------
# EvaluatorProposerBridge
# ---------------------------------------------------------------------------


class TestEvaluatorProposerBridge:
    def test_empty_inputs_produces_proposal(self):
        bridge = EvaluatorProposerBridge()
        proposal = bridge.propose()
        assert proposal is not None
        assert proposal.signals == []
        assert proposal.overall_health_score == pytest.approx(1.0)

    def test_eval_report_signals_extracted(self):
        bridge = EvaluatorProposerBridge()
        report = _make_report(scores={"precision@5": 0.5, "recall@10": 0.6, "MRR": 0.5})
        proposal = bridge.propose(eval_report=report)
        assert len(proposal.signals) > 0
        metric_names = {s.metric_name for s in proposal.signals}
        assert "precision@5" in metric_names

    def test_below_target_scores_generate_warning_signals(self):
        bridge = EvaluatorProposerBridge()
        report = _make_report(scores={"precision@5": 0.50})
        proposal = bridge.propose(eval_report=report)
        warning_signals = [s for s in proposal.signals if s.priority in ("warning", "critical")]
        assert len(warning_signals) > 0

    def test_above_target_scores_generate_ok_signals(self):
        bridge = EvaluatorProposerBridge()
        report = _make_report(
            scores={
                "precision@5": 0.90,
                "recall@10": 0.95,
                "MRR": 0.90,
                "NDCG@10": 0.88,
                "groundedness": 0.90,
                "answer_correctness": 0.85,
            }
        )
        proposal = bridge.propose(eval_report=report)
        ok_signals = [s for s in proposal.signals if s.priority == "ok"]
        assert len(ok_signals) == len(proposal.signals)

    def test_retrieval_snapshot_signal_added(self):
        bridge = EvaluatorProposerBridge()
        snapshot = RetrievalDriftSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            retrieval_hit_rate=0.50,
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=0.8,
            sample_size=10,
        )
        proposal = bridge.propose(retrieval_snapshot=snapshot)
        assert any(s.signal_type == "retrieval_drift" for s in proposal.signals)

    def test_answer_snapshot_signals_added(self):
        bridge = EvaluatorProposerBridge()
        snapshot = AnswerQualitySnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            groundedness_rate=0.50,
            hallucination_rate=0.30,
            human_override_rate=0.10,
            answer_correctness_mean=0.70,
            sample_size=10,
        )
        proposal = bridge.propose(answer_snapshot=snapshot)
        types = {s.signal_type for s in proposal.signals}
        assert "answer_quality_drift" in types

    def test_dpo_count_above_ten_triggers_finetuning(self):
        bridge = EvaluatorProposerBridge()
        from agentic_core.evaluation.feedback.schemas import DPOBatch, DPOPair

        pairs = [
            DPOPair(
                pair_id=f"p_{i}",
                query="q",
                chosen_response="c",
                rejected_response="r",
                context_documents=[],
                chosen_score=0.9,
                rejected_score=0.1,
                source_example_ids=[],
            )
            for i in range(11)
        ]
        batch = DPOBatch(
            batch_id="b",
            timestamp="2025-01-01T00:00:00Z",
            pair_count=11,
            pairs=pairs,
            source_feedback_count=20,
        )
        proposal = bridge.propose(dpo_batch=batch)
        assert "trigger_dpo_finetuning" in proposal.recommended_actions

    def test_dpo_count_low_suggests_accumulate(self):
        bridge = EvaluatorProposerBridge()
        from agentic_core.evaluation.feedback.schemas import DPOBatch, DPOPair

        pairs = [
            DPOPair(
                pair_id=f"p_{i}",
                query="q",
                chosen_response="c",
                rejected_response="r",
                context_documents=[],
                chosen_score=0.9,
                rejected_score=0.1,
                source_example_ids=[],
            )
            for i in range(3)
        ]
        batch = DPOBatch(
            batch_id="b",
            timestamp="2025-01-01T00:00:00Z",
            pair_count=3,
            pairs=pairs,
            source_feedback_count=5,
        )
        proposal = bridge.propose(dpo_batch=batch)
        assert "accumulate_more_dpo_pairs" in proposal.recommended_actions

    def test_critical_signal_triggers_intervention(self):
        bridge = EvaluatorProposerBridge()
        report = _make_report(scores={"precision@5": 0.20})  # far below target → critical
        proposal = bridge.propose(eval_report=report)
        assert proposal.requires_intervention is True

    def test_health_score_one_when_all_ok(self):
        bridge = EvaluatorProposerBridge()
        proposal = bridge.propose()
        assert proposal.overall_health_score == pytest.approx(1.0)

    def test_health_score_zero_when_all_critical(self):
        bridge = EvaluatorProposerBridge()
        report = _make_report(
            scores={
                "precision@5": 0.10,
                "recall@10": 0.10,
                "MRR": 0.10,
                "NDCG@10": 0.10,
                "groundedness": 0.10,
                "answer_correctness": 0.10,
            }
        )
        proposal = bridge.propose(eval_report=report)
        assert proposal.overall_health_score == pytest.approx(0.0)

    def test_l4_persist_called(self):
        stored = []

        class FakeStore:
            def put(self, a):
                stored.append(a)

        bridge = EvaluatorProposerBridge(l4_store=FakeStore())
        bridge.propose()
        assert len(stored) == 1

    def test_l4_persist_graceful_on_exception(self):
        class BrokenStore:
            def put(self, a):
                raise RuntimeError("disk full")

        bridge = EvaluatorProposerBridge(l4_store=BrokenStore())
        proposal = bridge.propose()  # must not raise
        assert proposal is not None

    def test_proposal_has_timestamp_ending_z(self):
        bridge = EvaluatorProposerBridge()
        proposal = bridge.propose()
        assert proposal.timestamp.endswith("Z")

    def test_proposal_id_is_non_empty(self):
        bridge = EvaluatorProposerBridge()
        proposal = bridge.propose()
        assert len(proposal.proposal_id) > 0
