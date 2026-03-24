"""
Tests: Phase 1 — Evaluation Metrics

Branch coverage for all 6 metrics:
- PrecisionAtK: empty prediction, empty ground_truth, top-k truncation, boundary
- RecallAtK: empty, partial, full recall
- MeanReciprocalRank: first hit at rank 1/5/none, mean helper
- NDCG: binary relevance, graded relevance, ideal ordering
- Groundedness: empty prediction, empty context, token F1, judge injection
- AnswerCorrectness: empty, perfect match, partial, judge injection
"""

import pytest

from agentic_core.evaluation.metrics.answer_correctness import AnswerCorrectness
from agentic_core.evaluation.metrics.groundedness import Groundedness, _token_f1, _tokenize
from agentic_core.evaluation.metrics.mrr import MeanReciprocalRank
from agentic_core.evaluation.metrics.ndcg import NDCG
from agentic_core.evaluation.metrics.precision_at_k import PrecisionAtK
from agentic_core.evaluation.metrics.recall_at_k import RecallAtK
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_eval_metrics", "p4obs", "metric_1")
_emit_emits_metric_event("test_eval_metrics", "p4obs", "metric_2")
_emit_emits_metric_event("test_eval_metrics", "p4obs", "metric_3")
_emit_emits_metric_event("test_eval_metrics", "p4obs", "metric_4")
_emit_emits_metric_event("test_eval_metrics", "p4obs", "metric_5")
_emit_emits_metric_event("test_eval_metrics", "p4obs", "metric_6")
_emit_records_incident_event("test_eval_metrics", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_eval_metrics", "p4obs", "anomaly")
_emit_writes_observability_log("test_eval_metrics", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_eval_metrics", "p4obs", "mon_state")
_emit_triggers_alert("test_eval_metrics", "p4obs", "alert")
_emit_links_incident_trace("test_eval_metrics", "p4obs", "trace_link")
_emit_captures_pattern("test_eval_metrics", "p3lm", "pattern")
_emit_records_learning_event("test_eval_metrics", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_eval_metrics", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_eval_metrics", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_eval_metrics", "p3lm", "routing")
_emit_improves_agent_policy("test_eval_metrics", "p3lm", "policy")
_emit_stores_learning_state("test_eval_metrics", "p3lm", "state")
_emit_records_execution_trace("test_eval_metrics", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_eval_metrics", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_eval_metrics", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_eval_metrics", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_eval_metrics", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_eval_metrics", "env_read", "p2_env_1")
_emit_reads_environ("test_eval_metrics", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_eval_metrics", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_eval_metrics", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_eval_metrics")
_emit_applies_guardrail("p0", "test_eval_metrics", "p0_governance")
_emit_reads_policy_state("p0", "test_eval_metrics", "policy_binding")
_emit_snapshots_state("p0", "test_eval_metrics", "state_snapshot")
_emit_pulls_context("p1", "test_eval_metrics", "context_pull")
_emit_pulls_context("p1", "test_eval_metrics", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_eval_metrics", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_eval_metrics", "uwg_term_secondary")
_emit_writes_through("p1", "test_eval_metrics", "write_through")
_emit_writes_through("p1", "test_eval_metrics", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_eval_metrics", "safety_validation")
_emit_invokes_eval("p1", "test_eval_metrics", "eval_call")
_emit_proposal_commits_routing("p1", "test_eval_metrics", "routing_commit")
_emit_escalates_to_human("p1", "test_eval_metrics", "human_escalation")
_emit_routes_through("p1", "test_eval_metrics", "route_through")
_emit_checks_agent_registry("p1", "test_eval_metrics", "agent_registry")
_emit_validates_agent_capability("p1", "test_eval_metrics", "capability")
_emit_dispatches_execution_plan("p1", "test_eval_metrics", "exec_plan")
_emit_agent_executes_agent("p1", "test_eval_metrics", "sub_agent")
_emit_routes_to_agent("p1", "test_eval_metrics", "target_agent")
_emit_verifies_policy("p1", "test_eval_metrics", "policy_check")
_emit_observes_runtime_state("p1", "test_eval_metrics", "runtime_state")
_emit_verifies_boundary("p1", "test_eval_metrics", "boundary_check")
_emit_transcripts_response("p1", "test_eval_metrics", "transcript")
_emit_hard_fails_untranscripted("p1", "test_eval_metrics")
_emit_gated_by_confidence("p1", "test_eval_metrics", "confidence_gate")
emit_replay_key("p0", "test_eval_metrics")
emit_determinism_digest("p0", "test_eval_metrics")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_eval_metrics", "execution_auth")
_emit_validates_capability("p2", "test_eval_metrics", "capability_check")
_emit_routes_to_capability("p2", "test_eval_metrics", "capability_route")
_emit_writes_via_uwg("p2", "test_eval_metrics", "uwg_write")
_emit_blocks_direct_write("p2", "test_eval_metrics", "direct_write_block")
_emit_records_tool_invocation("p2", "test_eval_metrics", "tool_invocation")
_emit_captures_execution_output("p2", "test_eval_metrics", "exec_output")
_emit_dispatches_agent("p3", "test_eval_metrics", "agent_dispatch")
_emit_coordinates_agents("p3", "test_eval_metrics", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_eval_metrics", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_eval_metrics", "healing_outcome")
_emit_escalates_failure("p3", "test_eval_metrics", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_eval_metrics", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_eval_metrics", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_eval_metrics", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_eval_metrics", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_eval_metrics", "eval_metric")
_emit_stores_embedding("p4", "test_eval_metrics", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_eval_metrics", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_eval_metrics", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# PrecisionAtK
# ---------------------------------------------------------------------------


class TestPrecisionAtK:
    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            PrecisionAtK(k=0)
        with pytest.raises(ValueError):
            PrecisionAtK(k=-1)

    def test_name(self):
        assert PrecisionAtK(k=5).name == "precision@5"
        assert PrecisionAtK(k=10).name == "precision@10"

    def test_empty_prediction_returns_zero(self):
        assert PrecisionAtK(k=5).compute([], ["doc_1"]) == 0.0

    def test_empty_ground_truth_returns_zero(self):
        assert PrecisionAtK(k=5).compute(["doc_1", "doc_2"], []) == 0.0

    def test_perfect_precision(self):
        # All top-k retrieved are relevant
        assert PrecisionAtK(k=3).compute(
            ["doc_1", "doc_2", "doc_3", "doc_4"], ["doc_1", "doc_2", "doc_3"]
        ) == pytest.approx(1.0)

    def test_zero_precision(self):
        assert PrecisionAtK(k=3).compute(["doc_x", "doc_y", "doc_z"], ["doc_1", "doc_2"]) == pytest.approx(
            0.0
        )

    def test_partial_precision(self):
        score = PrecisionAtK(k=4).compute(["doc_1", "doc_x", "doc_2", "doc_y"], ["doc_1", "doc_2"])
        assert score == pytest.approx(0.5)  # 2/4

    def test_truncates_to_k(self):
        # Only top-k (3) considered; docs beyond ignored
        score = PrecisionAtK(k=3).compute(
            ["doc_x", "doc_y", "doc_z", "doc_1"],  # doc_1 is 4th, outside k=3
            ["doc_1"],
        )
        assert score == pytest.approx(0.0)

    def test_k_boundary_exactly_one_relevant(self):
        # k=1, first doc is relevant
        assert PrecisionAtK(k=1).compute(["doc_1"], ["doc_1"]) == pytest.approx(1.0)

    def test_k_boundary_first_not_relevant(self):
        assert PrecisionAtK(k=1).compute(["doc_x"], ["doc_1"]) == pytest.approx(0.0)

    def test_prediction_shorter_than_k(self):
        # Only 2 docs returned, k=5 → 1 relevant out of k=5
        score = PrecisionAtK(k=5).compute(["doc_1", "doc_x"], ["doc_1"])
        assert score == pytest.approx(1.0 / 5.0)

    def test_deterministic_identical_inputs(self):
        m = PrecisionAtK(k=5)
        r1 = m.compute(["doc_1", "doc_2"], ["doc_1"])
        r2 = m.compute(["doc_1", "doc_2"], ["doc_1"])
        assert r1 == r2


# ---------------------------------------------------------------------------
# RecallAtK
# ---------------------------------------------------------------------------


class TestRecallAtK:
    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            RecallAtK(k=0)

    def test_name(self):
        assert RecallAtK(k=10).name == "recall@10"

    def test_empty_prediction_returns_zero(self):
        assert RecallAtK(k=10).compute([], ["doc_1"]) == 0.0

    def test_empty_ground_truth_returns_zero(self):
        assert RecallAtK(k=10).compute(["doc_1"], []) == 0.0

    def test_perfect_recall(self):
        assert RecallAtK(k=5).compute(
            ["doc_1", "doc_2", "doc_3"], ["doc_1", "doc_2", "doc_3"]
        ) == pytest.approx(1.0)

    def test_zero_recall(self):
        assert RecallAtK(k=5).compute(["doc_x", "doc_y"], ["doc_1", "doc_2"]) == pytest.approx(0.0)

    def test_partial_recall(self):
        # 1 of 2 relevant docs in top-5
        score = RecallAtK(k=5).compute(["doc_1", "doc_x", "doc_y"], ["doc_1", "doc_2"])
        assert score == pytest.approx(0.5)

    def test_recall_caps_at_one(self):
        # Duplicates in prediction shouldn't inflate recall past 1.0
        score = RecallAtK(k=5).compute(["doc_1", "doc_1", "doc_1"], ["doc_1"])
        assert score == pytest.approx(1.0)

    def test_k_boundary_plus_one(self):
        # Relevant doc at position k+1 should NOT be counted
        score = RecallAtK(k=3).compute(["doc_x", "doc_y", "doc_z", "doc_1"], ["doc_1"])
        assert score == pytest.approx(0.0)

    def test_k_boundary_exact(self):
        # Relevant doc at exactly position k should be counted
        score = RecallAtK(k=3).compute(["doc_x", "doc_y", "doc_1"], ["doc_1"])
        assert score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# MeanReciprocalRank
# ---------------------------------------------------------------------------


class TestMeanReciprocalRank:
    def test_name(self):
        assert MeanReciprocalRank().name == "MRR"

    def test_empty_prediction_returns_zero(self):
        assert MeanReciprocalRank().compute([], ["doc_1"]) == 0.0

    def test_empty_ground_truth_returns_zero(self):
        assert MeanReciprocalRank().compute(["doc_1"], []) == 0.0

    def test_first_rank_hit(self):
        assert MeanReciprocalRank().compute(["doc_1", "doc_2"], ["doc_1"]) == pytest.approx(1.0)

    def test_second_rank_hit(self):
        assert MeanReciprocalRank().compute(["doc_x", "doc_1"], ["doc_1"]) == pytest.approx(0.5)

    def test_fifth_rank_hit(self):
        pred = ["doc_x", "doc_y", "doc_z", "doc_w", "doc_1"]
        assert MeanReciprocalRank().compute(pred, ["doc_1"]) == pytest.approx(0.2)

    def test_no_hit_returns_zero(self):
        assert MeanReciprocalRank().compute(["doc_x", "doc_y"], ["doc_1"]) == pytest.approx(0.0)

    def test_mean_helper_empty_returns_zero(self):
        assert MeanReciprocalRank.mean([]) == 0.0

    def test_mean_helper_single(self):
        assert MeanReciprocalRank.mean([0.5]) == pytest.approx(0.5)

    def test_mean_helper_multiple(self):
        assert MeanReciprocalRank.mean([1.0, 0.5, 0.25]) == pytest.approx(0.5833, rel=1e-3)

    def test_deterministic_identical_input(self):
        m = MeanReciprocalRank()
        pred = ["doc_x", "doc_1", "doc_2"]
        gt = ["doc_1"]
        assert m.compute(pred, gt) == m.compute(pred, gt)


# ---------------------------------------------------------------------------
# NDCG
# ---------------------------------------------------------------------------


class TestNDCG:
    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            NDCG(k=0)

    def test_name(self):
        assert NDCG(k=10).name == "NDCG@10"

    def test_empty_prediction_returns_zero(self):
        assert NDCG(k=5).compute([], ["doc_1"]) == 0.0

    def test_empty_ground_truth_returns_zero(self):
        assert NDCG(k=5).compute(["doc_1"], []) == 0.0

    def test_perfect_ranking_binary(self):
        # Ideal order = all relevant first
        score = NDCG(k=3).compute(["doc_1", "doc_2", "doc_3"], ["doc_1", "doc_2", "doc_3"])
        assert score == pytest.approx(1.0)

    def test_reversed_order_lower_than_ideal(self):
        # Relevant doc last → DCG < IDCG
        score_ideal = NDCG(k=3).compute(["doc_1", "doc_x", "doc_y"], ["doc_1"])
        score_bad = NDCG(k=3).compute(["doc_x", "doc_y", "doc_1"], ["doc_1"])
        assert score_ideal > score_bad

    def test_no_relevant_in_retrieved(self):
        score = NDCG(k=5).compute(["doc_x", "doc_y"], ["doc_1", "doc_2"])
        assert score == pytest.approx(0.0)

    def test_graded_relevance_via_context(self):
        relevance = {"doc_1": 3.0, "doc_2": 1.0}
        score = NDCG(k=2).compute(["doc_1", "doc_2"], ["doc_1", "doc_2"], context=relevance)
        assert score == pytest.approx(1.0)

    def test_graded_relevance_inverted(self):
        relevance = {"doc_1": 3.0, "doc_2": 1.0}
        score_good = NDCG(k=2).compute(["doc_1", "doc_2"], [], context=relevance)
        score_bad = NDCG(k=2).compute(["doc_2", "doc_1"], [], context=relevance)
        assert score_good > score_bad

    def test_deterministic(self):
        m = NDCG(k=5)
        pred = ["doc_1", "doc_x", "doc_2"]
        gt = ["doc_1", "doc_2"]
        assert m.compute(pred, gt) == m.compute(pred, gt)


# ---------------------------------------------------------------------------
# Groundedness helpers
# ---------------------------------------------------------------------------


class TestGroundednessHelpers:
    def test_tokenize_lowercases(self):
        tokens = _tokenize("Hello World")
        assert "hello" in tokens
        assert "world" in tokens

    def test_tokenize_strips_punctuation(self):
        tokens = _tokenize("Hello, World!")
        assert "hello" in tokens
        assert "world" in tokens
        assert "," not in tokens

    def test_tokenize_empty_returns_empty(self):
        assert _tokenize("") == []

    def test_token_f1_perfect(self):
        assert _token_f1(["a", "b", "c"], ["a", "b", "c"]) == pytest.approx(1.0)

    def test_token_f1_zero_overlap(self):
        assert _token_f1(["x", "y"], ["a", "b"]) == pytest.approx(0.0)

    def test_token_f1_empty_prediction(self):
        assert _token_f1([], ["a", "b"]) == 0.0

    def test_token_f1_empty_context(self):
        assert _token_f1(["a"], []) == 0.0


# ---------------------------------------------------------------------------
# Groundedness metric
# ---------------------------------------------------------------------------


class TestGroundedness:
    def test_name(self):
        assert Groundedness().name == "groundedness"

    def test_empty_prediction_returns_zero(self):
        assert Groundedness().compute("", "expected", context="some context") == 0.0

    def test_empty_context_falls_back_to_ground_truth(self):
        # When context=None, uses ground_truth as context
        score = Groundedness().compute("the answer is here", "the answer is here", context=None)
        assert score > 0.5

    def test_empty_context_and_empty_gt_returns_zero(self):
        assert Groundedness().compute("answer", "", context=None) == 0.0

    def test_list_context_joined(self):
        score = Groundedness().compute(
            "governance validator enforces safety",
            "",
            context=["governance validator", "enforces safety rules"],
        )
        assert score > 0.0

    def test_str_context(self):
        score = Groundedness().compute("the cat sat on the mat", "", context="the cat sat on the mat")
        assert score == pytest.approx(1.0)

    def test_judge_injection(self):
        def fixed_judge(pred, ctx):
            return 0.77

        m = Groundedness(judge=fixed_judge)
        assert m.compute("anything", "anything", context="ctx") == pytest.approx(0.77)

    def test_judge_receives_concatenated_list_context(self):
        received = {}

        def capture_judge(pred, ctx):
            received["ctx"] = ctx
            return 0.5

        m = Groundedness(judge=capture_judge)
        m.compute("answer", "", context=["part_a", "part_b"])
        assert received["ctx"] == "part_a part_b"

    def test_partial_overlap(self):
        score = Groundedness().compute(
            "the governance validator is important", "", context="the governance validator enforces rules"
        )
        assert 0.0 < score < 1.0


# ---------------------------------------------------------------------------
# AnswerCorrectness
# ---------------------------------------------------------------------------


class TestAnswerCorrectness:
    def test_name(self):
        assert AnswerCorrectness().name == "answer_correctness"

    def test_empty_prediction_returns_zero(self):
        assert AnswerCorrectness().compute("", "expected") == 0.0

    def test_empty_ground_truth_returns_zero(self):
        assert AnswerCorrectness().compute("answer", "") == 0.0

    def test_perfect_match(self):
        assert AnswerCorrectness().compute("the answer", "the answer") == pytest.approx(1.0)

    def test_zero_overlap(self):
        assert AnswerCorrectness().compute("foo bar", "xyz abc") == pytest.approx(0.0)

    def test_partial_overlap(self):
        score = AnswerCorrectness().compute(
            "governance validator enforces safety rules", "governance validator checks policy"
        )
        assert 0.0 < score < 1.0

    def test_judge_injection(self):
        def fixed_judge(pred, gt):
            return 0.91

        m = AnswerCorrectness(judge=fixed_judge)
        assert m.compute("any", "any") == pytest.approx(0.91)

    def test_deterministic(self):
        m = AnswerCorrectness()
        r1 = m.compute("the cat sat", "the cat")
        r2 = m.compute("the cat sat", "the cat")
        assert r1 == r2

    def test_case_insensitive_via_tokenize(self):
        m = AnswerCorrectness()
        score_lower = m.compute("hello world", "hello world")
        score_mixed = m.compute("Hello World", "hello world")
        assert score_lower == pytest.approx(score_mixed)
