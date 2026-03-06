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
            ["doc_1", "doc_2", "doc_3", "doc_4"],
            ["doc_1", "doc_2", "doc_3"]
        ) == pytest.approx(1.0)

    def test_zero_precision(self):
        assert PrecisionAtK(k=3).compute(
            ["doc_x", "doc_y", "doc_z"],
            ["doc_1", "doc_2"]
        ) == pytest.approx(0.0)

    def test_partial_precision(self):
        score = PrecisionAtK(k=4).compute(
            ["doc_1", "doc_x", "doc_2", "doc_y"],
            ["doc_1", "doc_2"]
        )
        assert score == pytest.approx(0.5)  # 2/4

    def test_truncates_to_k(self):
        # Only top-k (3) considered; docs beyond ignored
        score = PrecisionAtK(k=3).compute(
            ["doc_x", "doc_y", "doc_z", "doc_1"],  # doc_1 is 4th, outside k=3
            ["doc_1"]
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
            ["doc_1", "doc_2", "doc_3"],
            ["doc_1", "doc_2", "doc_3"]
        ) == pytest.approx(1.0)

    def test_zero_recall(self):
        assert RecallAtK(k=5).compute(
            ["doc_x", "doc_y"],
            ["doc_1", "doc_2"]
        ) == pytest.approx(0.0)

    def test_partial_recall(self):
        # 1 of 2 relevant docs in top-5
        score = RecallAtK(k=5).compute(
            ["doc_1", "doc_x", "doc_y"],
            ["doc_1", "doc_2"]
        )
        assert score == pytest.approx(0.5)

    def test_recall_caps_at_one(self):
        # Duplicates in prediction shouldn't inflate recall past 1.0
        score = RecallAtK(k=5).compute(
            ["doc_1", "doc_1", "doc_1"],
            ["doc_1"]
        )
        assert score == pytest.approx(1.0)

    def test_k_boundary_plus_one(self):
        # Relevant doc at position k+1 should NOT be counted
        score = RecallAtK(k=3).compute(
            ["doc_x", "doc_y", "doc_z", "doc_1"],
            ["doc_1"]
        )
        assert score == pytest.approx(0.0)

    def test_k_boundary_exact(self):
        # Relevant doc at exactly position k should be counted
        score = RecallAtK(k=3).compute(
            ["doc_x", "doc_y", "doc_1"],
            ["doc_1"]
        )
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
            context=["governance validator", "enforces safety rules"]
        )
        assert score > 0.0

    def test_str_context(self):
        score = Groundedness().compute(
            "the cat sat on the mat",
            "",
            context="the cat sat on the mat"
        )
        assert score == pytest.approx(1.0)

    def test_judge_injection(self):
        fixed_judge = lambda pred, ctx: 0.77
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
            "the governance validator is important",
            "",
            context="the governance validator enforces rules"
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
            "governance validator enforces safety rules",
            "governance validator checks policy"
        )
        assert 0.0 < score < 1.0

    def test_judge_injection(self):
        fixed_judge = lambda pred, gt: 0.91
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
