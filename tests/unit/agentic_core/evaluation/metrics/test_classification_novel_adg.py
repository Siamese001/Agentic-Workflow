"""
Novel tests — classification metrics.

Testing methods not present in test_classification_metrics_adg.py:

  1.  GOLDEN DATASET — drive assertions from classification_eval_set.json
  2.  CROSS-METRIC CONSISTENCY — precision == recall == f1 when P == R
  3.  SYMMETRY / COMPLEMENT — swapping pos/neg label produces complementary matrix
  4.  EVALUATION REPORT ROUND-TRIP — to_dict() → from_dict() preserves classification fields
  5.  CONTENT HASH STABILITY — identical EvaluationReport objects produce same hash
  6.  EVALUATION DELTA REPORT — from_reports() correctly diffs classification fields
  7.  PATHOLOGICAL INPUTS — single sample, all-same label, unknown label in predictions
  8.  ORDERING INDEPENDENCE — shuffling predictions/truth order doesn't change aggregate
  9.  CONTEXT ARG IGNORED — passing context= never changes score
  10. PER-CLASS SUPPORT SUM — per_class_scores support values sum to N
  11. MICRO AVERAGING BOUNDARY — micro F1 == accuracy on balanced binary inputs
  12. __init__ EXPORT COMPLETENESS — all symbols importable by name from the package
  13. LABEL POLYMORPHISM — bool, float, None as label types
  14. ADVERSARIAL INVERSION — inverting all predictions anti-correlates all metrics
  15. DETERMINISM — repeated compute() calls return identical float bits
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from agentic_core.evaluation.metrics.classification import (
    BinaryClassificationMetric,
    MultiClassF1Metric,
    _build_binary_confusion,
)
from agentic_core.evaluation.metrics.f1_score import F1Score

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GOLDEN_PATH = (
    Path(__file__).parents[5] / "agentic_core" / "evaluation" / "datasets" / "classification_eval_set.json"
)


def _load_golden():
    return json.loads(_GOLDEN_PATH.read_text(encoding="utf-8"))["examples"]


def _make_report(**overrides):
    """Build a minimal EvaluationReport with sane defaults."""
    from agentic_core.utils.workflow_engines.completeness_metrics import EvaluationReport

    defaults = {
        "report_id": "r1",
        "configuration_id": "cfg1",
        "system_version": "test",
        "precision_at_k": 0.8,
        "recall_at_k": 0.7,
        "mrr": 0.6,
        "ndcg": 0.5,
        "groundedness": 0.9,
        "answer_correctness": 0.75,
        "context_completeness_score": 0.8,
        "support_score": 0.7,
        "high_similarity_wrong_answer_rate": 0.1,
        "parent_reconstruction_applied_rate": 0.05,
        "missing_condition_rate": 0.02,
        "missing_scope_rate": 0.03,
        "missing_exception_rate": 0.01,
        "missing_temporal_qualifier_rate": 0.02,
        "classification_f1": 0.85,
        "classification_precision": 0.88,
        "classification_recall": 0.82,
        "sample_count": 100,
    }
    defaults.update(overrides)
    return EvaluationReport(**defaults)


# ---------------------------------------------------------------------------
# 1. GOLDEN DATASET — drive assertions from JSON
# ---------------------------------------------------------------------------


class TestGoldenDataset:
    """Each example in classification_eval_set.json drives a concrete assertion."""

    @pytest.fixture(scope="class")
    def examples(self):
        return _load_golden()

    def test_golden_file_exists(self):
        assert _GOLDEN_PATH.exists(), f"Golden dataset not found: {_GOLDEN_PATH}"

    def test_golden_has_examples(self, examples):
        assert len(examples) >= 9

    @pytest.mark.parametrize(
        "example_id",
        [
            "binary_perfect_precision",
            "binary_perfect_recall",
            "binary_perfect_f1",
            "binary_zero_f1",
        ],
    )
    def test_binary_golden_precision(self, examples, example_id):
        ex = next(e for e in examples if e["id"] == example_id)
        if "expected" not in ex or "precision" not in ex["expected"]:
            pytest.skip("No precision in expected")
        m = BinaryClassificationMetric(positive_label=ex["positive_label"], metric="precision")
        score = m.compute(ex["predictions"], ex["ground_truth"])
        assert abs(score - ex["expected"]["precision"]) < 1e-4, (
            f"{example_id}: precision={score} != {ex['expected']['precision']}"
        )

    @pytest.mark.parametrize(
        "example_id",
        [
            "binary_perfect_precision",
            "binary_perfect_recall",
            "binary_perfect_f1",
            "binary_zero_f1",
        ],
    )
    def test_binary_golden_recall(self, examples, example_id):
        ex = next(e for e in examples if e["id"] == example_id)
        if "expected" not in ex or "recall" not in ex["expected"]:
            pytest.skip("No recall in expected")
        m = BinaryClassificationMetric(positive_label=ex["positive_label"], metric="recall")
        score = m.compute(ex["predictions"], ex["ground_truth"])
        assert abs(score - ex["expected"]["recall"]) < 1e-4

    @pytest.mark.parametrize(
        "example_id",
        [
            "binary_perfect_precision",
            "binary_perfect_recall",
            "binary_perfect_f1",
            "binary_zero_f1",
            "binary_harmonic_mean_invariant",
        ],
    )
    def test_binary_golden_f1(self, examples, example_id):
        ex = next(e for e in examples if e["id"] == example_id)
        if "expected" not in ex or "f1" not in ex["expected"]:
            pytest.skip("No f1 in expected")
        m = F1Score(positive_label=ex["positive_label"])
        score = m.compute(ex["predictions"], ex["ground_truth"])
        assert abs(score - ex["expected"]["f1"]) < 1e-4

    def test_golden_confusion_matrix_total(self, examples):
        ex = next(e for e in examples if e["id"] == "confusion_matrix_total_invariant")
        m = BinaryClassificationMetric(positive_label=ex["positive_label"])
        cm = m.confusion(ex["predictions"], ex["ground_truth"])
        assert cm.total() == ex["expected"]["total"]
        assert cm.tp == ex["expected"]["tp"]
        assert cm.fp == ex["expected"]["fp"]
        assert cm.tn == ex["expected"]["tn"]
        assert cm.fn == ex["expected"]["fn"]

    def test_golden_multiclass_macro_f1(self, examples):
        ex = next(e for e in examples if e["id"] == "multiclass_macro_f1")
        m = MultiClassF1Metric(averaging="macro", metric="f1")
        score = m.compute(ex["predictions"], ex["ground_truth"])
        assert abs(score - ex["expected"]["f1_macro"]) < 1e-4

    def test_golden_multiclass_weighted_f1(self, examples):
        ex = next(e for e in examples if e["id"] == "multiclass_weighted_f1")
        m = MultiClassF1Metric(averaging="weighted", metric="f1")
        score = m.compute(ex["predictions"], ex["ground_truth"])
        assert abs(score - ex["expected"]["f1_weighted"]) < 1e-4

    def test_golden_multiclass_micro_f1(self, examples):
        ex = next(e for e in examples if e["id"] == "multiclass_micro_f1")
        m = MultiClassF1Metric(averaging="micro", metric="f1")
        score = m.compute(ex["predictions"], ex["ground_truth"])
        assert abs(score - ex["expected"]["f1_micro"]) < 1e-4


# ---------------------------------------------------------------------------
# 2. CROSS-METRIC CONSISTENCY
# ---------------------------------------------------------------------------


class TestCrossMetricConsistency:
    """Mathematical relationships that must hold between P, R, and F1."""

    def test_f1_leq_arithmetic_mean_of_p_and_r(self):
        # Harmonic mean <= Arithmetic mean always
        preds = [1, 1, 0, 1, 0, 0, 1]
        truth = [1, 0, 1, 1, 0, 1, 0]
        p = BinaryClassificationMetric(metric="precision").compute(preds, truth)
        r = BinaryClassificationMetric(metric="recall").compute(preds, truth)
        f1 = F1Score().compute(preds, truth)
        arith_mean = (p + r) / 2
        assert f1 <= arith_mean + 1e-9

    def test_f1_equals_precision_when_precision_equals_recall(self):
        # When P == R exactly, F1 == P == R
        # Construct: 3 TP, 1 FP, 1 FN → P = 3/4, R = 3/4
        preds = [1, 1, 1, 1, 0]
        truth = [1, 1, 1, 0, 1]
        p = BinaryClassificationMetric(metric="precision").compute(preds, truth)
        r = BinaryClassificationMetric(metric="recall").compute(preds, truth)
        f1 = F1Score().compute(preds, truth)
        if abs(p - r) < 1e-9:
            assert abs(f1 - p) < 1e-6

    def test_precision_recall_f1_all_one_on_perfect_prediction(self):
        preds = [1, 0, 1, 0, 1]
        truth = [1, 0, 1, 0, 1]
        p = BinaryClassificationMetric(metric="precision").compute(preds, truth)
        r = BinaryClassificationMetric(metric="recall").compute(preds, truth)
        f1 = F1Score().compute(preds, truth)
        assert p == r == f1 == 1.0

    def test_f1_bounded_by_zero_and_one(self):
        for _ in range(20):
            n = random.randint(1, 30)
            preds = [random.choice([0, 1]) for _ in range(n)]
            truth = [random.choice([0, 1]) for _ in range(n)]
            score = F1Score().compute(preds, truth)
            assert 0.0 <= score <= 1.0

    def test_precision_bounded(self):
        for _ in range(20):
            n = random.randint(1, 20)
            preds = [random.choice([0, 1]) for _ in range(n)]
            truth = [random.choice([0, 1]) for _ in range(n)]
            score = BinaryClassificationMetric(metric="precision").compute(preds, truth)
            assert 0.0 <= score <= 1.0

    def test_recall_bounded(self):
        for _ in range(20):
            n = random.randint(1, 20)
            preds = [random.choice([0, 1]) for _ in range(n)]
            truth = [random.choice([0, 1]) for _ in range(n)]
            score = BinaryClassificationMetric(metric="recall").compute(preds, truth)
            assert 0.0 <= score <= 1.0

    def test_multiclass_all_averaging_bounded(self):
        preds = ["A", "B", "C", "A", "B"]
        truth = ["A", "A", "C", "B", "B"]
        for avg in ("macro", "micro", "weighted"):
            score = MultiClassF1Metric(averaging=avg).compute(preds, truth)
            assert 0.0 <= score <= 1.0, f"averaging={avg} score={score} out of [0,1]"


# ---------------------------------------------------------------------------
# 3. SYMMETRY / COMPLEMENT
# ---------------------------------------------------------------------------


class TestSymmetryAndComplement:
    """Swapping the positive label produces the complement TP↔TN and FP↔FN."""

    def test_swapping_positive_label_swaps_tp_tn_and_fp_fn(self):
        preds = [1, 1, 0, 0, 1]
        truth = [1, 0, 1, 0, 1]
        cm1 = _build_binary_confusion(preds, truth, positive_label=1)
        cm0 = _build_binary_confusion(preds, truth, positive_label=0)
        assert cm1.tp == cm0.tn
        assert cm1.tn == cm0.tp
        assert cm1.fp == cm0.fn
        assert cm1.fn == cm0.fp

    def test_total_invariant_across_label_swap(self):
        preds = [1, 1, 0, 1, 0, 0]
        truth = [1, 0, 0, 1, 1, 0]
        cm1 = _build_binary_confusion(preds, truth, positive_label=1)
        cm0 = _build_binary_confusion(preds, truth, positive_label=0)
        assert cm1.total() == cm0.total() == len(preds)

    def test_accuracy_invariant_under_label_swap(self):
        # accuracy = (TP+TN)/N — symmetric regardless of which label is "positive"
        preds = [1, 0, 1, 0, 1, 0]
        truth = [1, 1, 0, 0, 1, 0]
        cm1 = _build_binary_confusion(preds, truth, positive_label=1)
        cm0 = _build_binary_confusion(preds, truth, positive_label=0)
        assert abs(cm1.accuracy() - cm0.accuracy()) < 1e-9


# ---------------------------------------------------------------------------
# 4. EVALUATION REPORT ROUND-TRIP
# ---------------------------------------------------------------------------


class TestEvaluationReportRoundTrip:
    """to_dict() → from_dict() must be a lossless round-trip for classification fields."""

    def test_classification_f1_survives_roundtrip(self):
        report = _make_report(classification_f1=0.731)
        restored = type(report).from_dict(report.to_dict())
        assert abs(restored.classification_f1 - report.classification_f1) < 1e-6

    def test_classification_precision_survives_roundtrip(self):
        report = _make_report(classification_precision=0.812)
        restored = type(report).from_dict(report.to_dict())
        assert abs(restored.classification_precision - report.classification_precision) < 1e-6

    def test_classification_recall_survives_roundtrip(self):
        report = _make_report(classification_recall=0.654)
        restored = type(report).from_dict(report.to_dict())
        assert abs(restored.classification_recall - report.classification_recall) < 1e-6

    def test_to_dict_contains_all_classification_keys(self):
        report = _make_report()
        d = report.to_dict()
        assert "classification_f1" in d
        assert "classification_precision" in d
        assert "classification_recall" in d

    def test_from_dict_defaults_zeros_when_missing(self):
        """Older serialized reports without classification keys default to 0.0."""
        report = _make_report()
        d = report.to_dict()
        del d["classification_f1"]
        del d["classification_precision"]
        del d["classification_recall"]
        restored = type(report).from_dict(d)
        assert restored.classification_f1 == 0.0
        assert restored.classification_precision == 0.0
        assert restored.classification_recall == 0.0

    def test_full_roundtrip_identity(self):
        """Every field survives to_dict → from_dict unchanged."""
        report = _make_report(
            classification_f1=0.777,
            classification_precision=0.8,
            classification_recall=0.75,
        )
        restored = type(report).from_dict(report.to_dict())
        assert restored.report_id == report.report_id
        assert restored.sample_count == report.sample_count
        assert abs(restored.classification_f1 - report.classification_f1) < 1e-6


# ---------------------------------------------------------------------------
# 5. CONTENT HASH STABILITY
# ---------------------------------------------------------------------------


class TestContentHashStability:
    """EvaluationReport.content_hash() must be deterministic and sensitive to changes."""

    def test_identical_reports_have_same_hash(self):
        r1 = _make_report(classification_f1=0.9)
        r2 = _make_report(classification_f1=0.9)
        assert r1.content_hash() == r2.content_hash()

    def test_different_classification_f1_gives_different_hash(self):
        r1 = _make_report(classification_f1=0.9)
        r2 = _make_report(classification_f1=0.91)
        assert r1.content_hash() != r2.content_hash()

    def test_different_classification_precision_gives_different_hash(self):
        r1 = _make_report(classification_precision=0.8)
        r2 = _make_report(classification_precision=0.85)
        assert r1.content_hash() != r2.content_hash()

    def test_hash_is_hex_string(self):
        r = _make_report()
        h = r.content_hash()
        assert isinstance(h, str)
        assert len(h) == 64  # sha256 hex digest
        int(h, 16)  # must be valid hex

    def test_canonical_bytes_excludes_metadata(self):
        """Metadata must not affect canonical_bytes (it's excluded by spec)."""
        r1 = _make_report(metadata={"run_id": "abc"})
        r2 = _make_report(metadata={"run_id": "xyz"})
        assert r1.canonical_bytes() == r2.canonical_bytes()


# ---------------------------------------------------------------------------
# 6. EVALUATION DELTA REPORT
# ---------------------------------------------------------------------------


class TestEvaluationDeltaReport:
    """from_reports() correctly computes deltas for new classification fields."""

    def test_delta_classification_f1_is_difference(self):
        from agentic_core.utils.workflow_engines.completeness_metrics import EvaluationDeltaReport

        baseline = _make_report(report_id="b1", configuration_id="base", classification_f1=0.7)
        candidate = _make_report(report_id="c1", configuration_id="cand", classification_f1=0.85)
        delta = EvaluationDeltaReport.from_reports("d1", baseline, candidate)
        assert abs(delta.delta_classification_f1 - 0.15) < 1e-5

    def test_delta_classification_precision_is_difference(self):
        from agentic_core.utils.workflow_engines.completeness_metrics import EvaluationDeltaReport

        baseline = _make_report(report_id="b2", configuration_id="base", classification_precision=0.6)
        candidate = _make_report(report_id="c2", configuration_id="cand", classification_precision=0.9)
        delta = EvaluationDeltaReport.from_reports("d2", baseline, candidate)
        assert abs(delta.delta_classification_precision - 0.3) < 1e-5

    def test_delta_classification_recall_is_difference(self):
        from agentic_core.utils.workflow_engines.completeness_metrics import EvaluationDeltaReport

        baseline = _make_report(report_id="b3", configuration_id="base", classification_recall=0.5)
        candidate = _make_report(report_id="c3", configuration_id="cand", classification_recall=0.75)
        delta = EvaluationDeltaReport.from_reports("d3", baseline, candidate)
        assert abs(delta.delta_classification_recall - 0.25) < 1e-5

    def test_delta_negative_when_candidate_is_worse(self):
        from agentic_core.utils.workflow_engines.completeness_metrics import EvaluationDeltaReport

        baseline = _make_report(report_id="b4", configuration_id="base", classification_f1=0.9)
        candidate = _make_report(report_id="c4", configuration_id="cand", classification_f1=0.7)
        delta = EvaluationDeltaReport.from_reports("d4", baseline, candidate)
        assert delta.delta_classification_f1 < 0.0

    def test_delta_to_dict_contains_classification_keys(self):
        from agentic_core.utils.workflow_engines.completeness_metrics import EvaluationDeltaReport

        baseline = _make_report(report_id="b5", configuration_id="base")
        candidate = _make_report(report_id="c5", configuration_id="cand")
        delta = EvaluationDeltaReport.from_reports("d5", baseline, candidate)
        d = delta.to_dict()
        assert "delta_classification_f1" in d
        assert "delta_classification_precision" in d
        assert "delta_classification_recall" in d


# ---------------------------------------------------------------------------
# 7. PATHOLOGICAL INPUTS
# ---------------------------------------------------------------------------


class TestPathologicalInputs:
    """Single sample, all-same label, unknown label in predictions only."""

    def test_single_sample_tp(self):
        score = F1Score().compute([1], [1])
        assert score == 1.0

    def test_single_sample_fp(self):
        score = F1Score().compute([1], [0])
        assert score == 0.0

    def test_single_sample_fn(self):
        score = F1Score().compute([0], [1])
        assert score == 0.0

    def test_single_sample_tn(self):
        # No positive predictions, no positive truths → precision=0 (denom=0), recall=0 (denom=0)
        score = F1Score().compute([0], [0])
        assert score == 0.0

    def test_all_same_label_in_truth_positive(self):
        # All truth = positive, all pred = positive → F1=1
        preds = [1] * 10
        truth = [1] * 10
        assert F1Score().compute(preds, truth) == 1.0

    def test_all_same_label_in_truth_negative(self):
        # All truth = negative, all pred = negative → TN=N, TP=FP=FN=0 → F1=0
        preds = [0] * 10
        truth = [0] * 10
        score = F1Score().compute(preds, truth)
        assert score == 0.0

    def test_unknown_label_only_in_predictions(self):
        # pred contains label "X" never in ground_truth → all X preds are FP
        # preds: "X","X","pos" — only 1 predicted "pos", which is TP (truth[2]=="pos")
        # FP = 0 for "pos" label (the one "pos" pred matches truth)
        # But "X","X" preds with truth "pos","pos" → those are FN (missed positives)
        # precision("pos") = TP/(TP+FP) = 1/(1+0) = 1.0
        preds = ["X", "X", "pos"]
        truth = ["pos", "pos", "pos"]
        m = BinaryClassificationMetric(positive_label="pos", metric="precision")
        score = m.compute(preds, truth)
        assert abs(score - 1.0) < 1e-5
        # recall = TP/(TP+FN) = 1/(1+2) = 0.333
        r_metric = BinaryClassificationMetric(positive_label="pos", metric="recall")
        recall = r_metric.compute(preds, truth)
        assert abs(recall - 1 / 3) < 1e-5

    def test_unknown_label_only_in_ground_truth(self):
        # truth contains "unknown" never predicted → those are FN for other classes
        preds = ["A", "A", "A"]
        truth = ["A", "A", "unknown"]
        m = MultiClassF1Metric(averaging="macro")
        score = m.compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_large_all_correct(self):
        n = 1000
        preds = [1] * n
        truth = [1] * n
        assert F1Score().compute(preds, truth) == 1.0

    def test_large_all_wrong(self):
        n = 1000
        preds = [1] * n
        truth = [0] * n
        assert F1Score().compute(preds, truth) == 0.0


# ---------------------------------------------------------------------------
# 8. ORDERING INDEPENDENCE
# ---------------------------------------------------------------------------


class TestOrderingIndependence:
    """Shuffling the (prediction, truth) pairs must not change the aggregate scores."""

    def _paired_shuffle(self, preds, truth, seed):
        pairs = list(zip(preds, truth))
        r = random.Random(seed)
        r.shuffle(pairs)
        return [p for p, _ in pairs], [t for _, t in pairs]

    def test_binary_f1_order_independent(self):
        preds = [1, 1, 0, 1, 0, 0, 1, 0, 1, 1]
        truth = [1, 0, 0, 1, 1, 0, 1, 1, 0, 1]
        original = F1Score().compute(preds, truth)
        for seed in range(5):
            sp, st = self._paired_shuffle(preds, truth, seed)
            assert abs(F1Score().compute(sp, st) - original) < 1e-9

    def test_multiclass_macro_f1_order_independent(self):
        preds = ["A", "B", "C", "A", "B", "C", "A", "B"]
        truth = ["A", "A", "C", "B", "B", "A", "A", "C"]
        m = MultiClassF1Metric(averaging="macro")
        original = m.compute(preds, truth)
        for seed in range(5):
            sp, st = self._paired_shuffle(preds, truth, seed)
            assert abs(m.compute(sp, st) - original) < 1e-9

    def test_confusion_matrix_order_independent(self):
        preds = [1, 0, 1, 0, 1, 0, 0, 1]
        truth = [1, 1, 0, 0, 1, 0, 1, 0]
        m = BinaryClassificationMetric()
        cm_orig = m.confusion(preds, truth)
        for seed in range(5):
            sp, st = self._paired_shuffle(preds, truth, seed)
            cm = m.confusion(sp, st)
            assert cm.tp == cm_orig.tp
            assert cm.fp == cm_orig.fp
            assert cm.tn == cm_orig.tn
            assert cm.fn == cm_orig.fn


# ---------------------------------------------------------------------------
# 9. CONTEXT ARG IGNORED
# ---------------------------------------------------------------------------


class TestContextArgIgnored:
    """Passing context= must never change the computed score."""

    def test_binary_f1_ignores_context(self):
        preds = [1, 0, 1, 0]
        truth = [1, 1, 0, 0]
        m = F1Score()
        base = m.compute(preds, truth)
        assert m.compute(preds, truth, context=None) == base
        assert m.compute(preds, truth, context="some_context") == base
        assert m.compute(preds, truth, context={"key": "val"}) == base
        assert m.compute(preds, truth, context=42) == base

    def test_binary_precision_ignores_context(self):
        preds = [1, 1, 0]
        truth = [1, 0, 0]
        m = BinaryClassificationMetric(metric="precision")
        base = m.compute(preds, truth)
        assert m.compute(preds, truth, context=["a", "b"]) == base

    def test_multiclass_ignores_context(self):
        preds = ["A", "B", "C"]
        truth = ["A", "A", "C"]
        m = MultiClassF1Metric(averaging="macro")
        base = m.compute(preds, truth)
        assert m.compute(preds, truth, context="ignored") == base


# ---------------------------------------------------------------------------
# 10. PER-CLASS SUPPORT SUM
# ---------------------------------------------------------------------------


class TestPerClassSupportSum:
    """per_class_scores support values must sum to len(ground_truth)."""

    def test_support_sums_to_n(self):
        preds = ["A", "B", "C", "A", "B"]
        truth = ["A", "A", "C", "B", "B"]
        m = MultiClassF1Metric()
        per_class = m.per_class_scores(preds, truth)
        total_support = sum(v["support"] for v in per_class.values())
        assert abs(total_support - len(truth)) < 1e-9

    def test_support_sums_to_n_imbalanced(self):
        preds = ["X"] * 8 + ["Y"] * 2
        truth = ["X"] * 7 + ["Y"] * 3
        m = MultiClassF1Metric()
        per_class = m.per_class_scores(preds, truth)
        total_support = sum(v["support"] for v in per_class.values())
        assert abs(total_support - len(truth)) < 1e-9

    def test_support_is_ground_truth_count_not_prediction_count(self):
        # truth has 4 A and 1 B, preds may differ
        preds = ["B", "B", "B", "A", "A"]
        truth = ["A", "A", "A", "A", "B"]
        m = MultiClassF1Metric()
        per_class = m.per_class_scores(preds, truth)
        assert per_class["A"]["support"] == 4.0
        assert per_class["B"]["support"] == 1.0

    def test_support_all_one_class(self):
        preds = ["A", "A", "A"]
        truth = ["A", "A", "A"]
        m = MultiClassF1Metric()
        per_class = m.per_class_scores(preds, truth)
        assert per_class["A"]["support"] == 3.0


# ---------------------------------------------------------------------------
# 11. MICRO AVERAGING BOUNDARY
# ---------------------------------------------------------------------------


class TestMicroAveragingBoundary:
    """Micro-F1 == accuracy on balanced binary inputs."""

    def test_micro_f1_matches_accuracy_on_balanced_binary(self):
        # For balanced binary with equal class sizes: micro-F1 == accuracy
        # Use macro binary so accuracy = (TP+TN)/N
        # micro-F1 in 2-class OvR = overall (correct / total)
        preds = [0, 1, 0, 1, 0, 1]
        truth = [0, 1, 1, 0, 0, 1]
        cm = BinaryClassificationMetric().confusion(preds, truth)
        acc = cm.accuracy()
        # Micro-F1 over 2 classes: TP_0=TN_1=2, TP_1=TN_0=2, FP_0=FN_1=1, FP_1=FN_0=1
        micro = MultiClassF1Metric(averaging="micro").compute(preds, truth)
        assert abs(micro - acc) < 1e-5

    def test_micro_f1_equals_macro_when_classes_balanced(self):
        # Perfectly balanced predictions — macro and micro coincide
        preds = ["A", "B", "A", "B"]
        truth = ["A", "A", "B", "B"]
        macro = MultiClassF1Metric(averaging="macro").compute(preds, truth)
        micro = MultiClassF1Metric(averaging="micro").compute(preds, truth)
        # Both should be equal when support is symmetric
        assert abs(macro - micro) < 1e-5

    def test_micro_precision_equals_micro_recall_on_perfect(self):
        preds = ["A", "B", "C"]
        truth = ["A", "B", "C"]
        mp = MultiClassF1Metric(averaging="micro", metric="precision").compute(preds, truth)
        mr = MultiClassF1Metric(averaging="micro", metric="recall").compute(preds, truth)
        mf = MultiClassF1Metric(averaging="micro", metric="f1").compute(preds, truth)
        assert mp == mr == mf == 1.0


# ---------------------------------------------------------------------------
# 12. __init__ EXPORT COMPLETENESS
# ---------------------------------------------------------------------------


class TestInitExportCompleteness:
    """All declared symbols are importable by name from the package."""

    _EXPECTED_SYMBOLS = [
        "EvaluationMetric",
        "RetrievalMetric",
        "GenerationMetric",
        "ClassificationMetric",
        "ConfusionMatrix",
        "BinaryClassificationMetric",
        "MultiClassF1Metric",
        "F1Score",
    ]

    def test_all_symbols_importable_from_package(self):
        import agentic_core.evaluation.metrics as pkg

        for sym in self._EXPECTED_SYMBOLS:
            assert hasattr(pkg, sym), f"Symbol '{sym}' missing from agentic_core.evaluation.metrics"

    def test_all_symbols_in_dunder_all(self):
        import agentic_core.evaluation.metrics as pkg

        for sym in self._EXPECTED_SYMBOLS:
            assert sym in pkg.__all__, f"'{sym}' not in __all__"

    def test_f1score_importable_direct(self):
        from agentic_core.evaluation.metrics import F1Score as _F1Score

        assert _F1Score is not None

    def test_confusion_matrix_importable_direct(self):
        from agentic_core.evaluation.metrics import ConfusionMatrix as _CM

        assert _CM is not None


# ---------------------------------------------------------------------------
# 13. LABEL POLYMORPHISM
# ---------------------------------------------------------------------------


class TestLabelPolymorphism:
    """bool, float, None as label types must not crash and must produce valid scores."""

    def test_bool_labels_binary(self):
        preds = [True, False, True, True]
        truth = [True, True, False, True]
        score = BinaryClassificationMetric(positive_label=True).compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_float_labels(self):
        preds = [1.0, 0.0, 1.0, 0.0]
        truth = [1.0, 0.0, 0.0, 1.0]
        score = F1Score(positive_label=1.0).compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_none_as_negative_label(self):
        preds = [1, None, 1, None]
        truth = [1, None, None, 1]
        score = F1Score(positive_label=1).compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_mixed_int_labels_multiclass(self):
        preds = [0, 1, 2, 0, 1, 2]
        truth = [0, 0, 2, 1, 1, 0]
        score = MultiClassF1Metric(averaging="macro").compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_single_character_string_labels(self):
        preds = list("AAABBBCCC")
        truth = list("AABBABCBC")
        score = MultiClassF1Metric(averaging="weighted").compute(preds, truth)
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# 14. ADVERSARIAL INVERSION
# ---------------------------------------------------------------------------


class TestAdversarialInversion:
    """Inverting all predictions: recall drops when precision was high and vice versa."""

    def test_inverting_perfect_predictor_gives_zero_scores(self):
        # Perfect predictor: all 1s correct. Invert: all 1s become 0s.
        truth = [1, 1, 1, 0, 0]
        perfect_preds = truth[:]
        inverted_preds = [1 - x for x in truth]
        f1_perfect = F1Score().compute(perfect_preds, truth)
        f1_inverted = F1Score().compute(inverted_preds, truth)
        assert f1_perfect == 1.0
        assert f1_inverted == 0.0

    def test_random_inversion_anticorrelates_tp(self):
        preds = [1, 1, 0, 0, 1, 0, 1, 0]
        truth = [1, 0, 1, 0, 1, 1, 0, 0]
        cm_orig = BinaryClassificationMetric().confusion(preds, truth)
        inverted = [1 - p for p in preds]
        cm_inv = BinaryClassificationMetric().confusion(inverted, truth)
        # TP of original == FN of inverted, FP of original == TN of inverted
        assert cm_orig.tp == cm_inv.fn
        assert cm_orig.fp == cm_inv.tn
        assert cm_orig.tn == cm_inv.fp
        assert cm_orig.fn == cm_inv.tp

    def test_inversion_swaps_cm_rows(self):
        """TP↔FN and FP↔TN when binary predictions are fully inverted."""
        preds = [1, 0, 1, 1, 0, 0]
        truth = [1, 1, 0, 1, 0, 1]
        m = BinaryClassificationMetric()
        cm = m.confusion(preds, truth)
        inv_cm = m.confusion([1 - p for p in preds], truth)
        assert cm.tp == inv_cm.fn
        assert cm.fn == inv_cm.tp
        assert cm.fp == inv_cm.tn
        assert cm.tn == inv_cm.fp


# ---------------------------------------------------------------------------
# 15. DETERMINISM
# ---------------------------------------------------------------------------


class TestDeterminism:
    """Repeated calls with the same inputs must return bit-for-bit identical floats."""

    def test_f1score_deterministic_repeated_calls(self):
        preds = [1, 0, 1, 1, 0, 0, 1, 0]
        truth = [1, 1, 0, 1, 0, 1, 0, 0]
        m = F1Score()
        results = {m.compute(preds, truth) for _ in range(10)}
        assert len(results) == 1

    def test_multiclass_macro_deterministic(self):
        preds = ["A", "B", "C", "A"]
        truth = ["A", "A", "C", "B"]
        m = MultiClassF1Metric(averaging="macro")
        results = {m.compute(preds, truth) for _ in range(10)}
        assert len(results) == 1

    def test_confusion_matrix_deterministic(self):
        preds = [1, 0, 1, 0, 1]
        truth = [1, 1, 0, 0, 1]
        m = BinaryClassificationMetric()
        cms = [m.confusion(preds, truth) for _ in range(5)]
        assert all(c == cms[0] for c in cms)

    def test_content_hash_deterministic(self):
        r = _make_report(classification_f1=0.88)
        hashes = {r.content_hash() for _ in range(10)}
        assert len(hashes) == 1
