"""
Unit tests — agentic_core.evaluation.metrics classification hierarchy.

ADG coverage targets:
  - agentic_core/evaluation/metrics/base.py         → ClassificationMetric ABC
  - agentic_core/evaluation/metrics/classification.py → ConfusionMatrix,
                                                        BinaryClassificationMetric,
                                                        MultiClassF1Metric
  - agentic_core/evaluation/metrics/f1_score.py      → F1Score
"""

from __future__ import annotations

import pytest

from agentic_core.evaluation.metrics.classification import (
    BinaryClassificationMetric,
    ConfusionMatrix,
    MultiClassF1Metric,
)
from agentic_core.evaluation.metrics.f1_score import F1Score
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

_emit_records_execution_trace("p0", "evidence", "test_classification_metrics_adg")
_emit_applies_guardrail("p0", "test_classification_metrics_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_classification_metrics_adg", "policy_binding")
_emit_snapshots_state("p0", "test_classification_metrics_adg", "state_snapshot")
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_classification_metrics_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_classification_metrics_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_classification_metrics_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_classification_metrics_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_classification_metrics_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_classification_metrics_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_classification_metrics_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_classification_metrics_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_classification_metrics_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_classification_metrics_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_classification_metrics_adg", "p4obs", "alert")
_emit_links_incident_trace("test_classification_metrics_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_classification_metrics_adg", "p3lm", "pattern")
_emit_records_learning_event("test_classification_metrics_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_classification_metrics_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_classification_metrics_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_classification_metrics_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_classification_metrics_adg", "p3lm", "policy")
_emit_stores_learning_state("test_classification_metrics_adg", "p3lm", "state")
_emit_records_execution_trace("test_classification_metrics_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_classification_metrics_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_classification_metrics_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_classification_metrics_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_classification_metrics_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_classification_metrics_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_classification_metrics_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_classification_metrics_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_classification_metrics_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_classification_metrics_adg", "context_pull")
_emit_pulls_context("p1", "test_classification_metrics_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_classification_metrics_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_classification_metrics_adg", "uwg_term_2")
_emit_writes_through("p1", "test_classification_metrics_adg", "write_through")
_emit_writes_through("p1", "test_classification_metrics_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_classification_metrics_adg", "safety_validation")
_emit_invokes_eval("p1", "test_classification_metrics_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_classification_metrics_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_classification_metrics_adg", "human_escalation")
_emit_routes_through("p1", "test_classification_metrics_adg", "route_through")
_emit_checks_agent_registry("p1", "test_classification_metrics_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_classification_metrics_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_classification_metrics_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_classification_metrics_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_classification_metrics_adg", "target_agent")
_emit_verifies_policy("p1", "test_classification_metrics_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_classification_metrics_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_classification_metrics_adg", "boundary_check")
_emit_transcripts_response("p1", "test_classification_metrics_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_classification_metrics_adg")
_emit_gated_by_confidence("p1", "test_classification_metrics_adg", "confidence_gate")
emit_replay_key("p0", "test_classification_metrics_adg")
emit_determinism_digest("p0", "test_classification_metrics_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_classification_metrics_adg", "execution_auth")
_emit_validates_capability("p2", "test_classification_metrics_adg", "capability_check")
_emit_routes_to_capability("p2", "test_classification_metrics_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_classification_metrics_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_classification_metrics_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_classification_metrics_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_classification_metrics_adg", "exec_output")
_emit_dispatches_agent("p3", "test_classification_metrics_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_classification_metrics_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_classification_metrics_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_classification_metrics_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_classification_metrics_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_classification_metrics_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_classification_metrics_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_classification_metrics_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_classification_metrics_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_classification_metrics_adg", "eval_metric")
_emit_stores_embedding("p4", "test_classification_metrics_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_classification_metrics_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_classification_metrics_adg", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# ConfusionMatrix
# ---------------------------------------------------------------------------


class TestConfusionMatrix:
    def _cm(self, tp, fp, tn, fn):
        return ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn)

    def test_precision_all_correct(self):
        cm = self._cm(tp=5, fp=0, tn=3, fn=2)
        assert cm.precision() == 1.0

    def test_precision_all_wrong(self):
        cm = self._cm(tp=0, fp=5, tn=3, fn=2)
        assert cm.precision() == 0.0

    def test_precision_zero_denominator(self):
        cm = self._cm(tp=0, fp=0, tn=5, fn=3)
        assert cm.precision() == 0.0

    def test_recall_all_correct(self):
        cm = self._cm(tp=5, fp=2, tn=3, fn=0)
        assert cm.recall() == 1.0

    def test_recall_zero_denominator(self):
        cm = self._cm(tp=0, fp=2, tn=5, fn=0)
        assert cm.recall() == 0.0

    def test_f1_perfect(self):
        cm = self._cm(tp=5, fp=0, tn=3, fn=0)
        assert cm.f1() == 1.0

    def test_f1_zero(self):
        cm = self._cm(tp=0, fp=3, tn=2, fn=5)
        assert cm.f1() == 0.0

    def test_f1_harmonic_mean(self):
        cm = self._cm(tp=2, fp=2, tn=2, fn=2)
        p = cm.precision()
        r = cm.recall()
        expected = 2 * p * r / (p + r)
        assert abs(cm.f1() - expected) < 1e-6

    def test_total_invariant(self):
        cm = self._cm(tp=3, fp=2, tn=4, fn=1)
        assert cm.total() == cm.tp + cm.fp + cm.tn + cm.fn
        assert cm.total() == 10

    def test_accuracy(self):
        cm = self._cm(tp=4, fp=1, tn=4, fn=1)
        assert abs(cm.accuracy() - 0.8) < 1e-6

    def test_to_dict_keys(self):
        cm = self._cm(tp=2, fp=1, tn=3, fn=1)
        d = cm.to_dict()
        for key in ("tp", "fp", "tn", "fn", "precision", "recall", "f1", "accuracy"):
            assert key in d

    def test_frozen(self):
        cm = self._cm(tp=1, fp=0, tn=2, fn=1)
        with pytest.raises((AttributeError, TypeError)):
            cm.tp = 99  # type: ignore[misc]

    def test_positive_label_stored(self):
        cm = ConfusionMatrix(tp=1, fp=0, tn=1, fn=0, positive_label="pos")
        assert cm.positive_label == "pos"


# ---------------------------------------------------------------------------
# BinaryClassificationMetric
# ---------------------------------------------------------------------------


class TestBinaryClassificationMetric:
    def test_perfect_precision(self):
        m = BinaryClassificationMetric(positive_label=1, metric="precision")
        assert m.compute([1, 1, 1], [1, 1, 1]) == 1.0

    def test_zero_precision(self):
        m = BinaryClassificationMetric(positive_label=1, metric="precision")
        assert m.compute([0, 0, 0], [1, 1, 1]) == 0.0

    def test_perfect_recall(self):
        m = BinaryClassificationMetric(positive_label=1, metric="recall")
        assert m.compute([1, 1, 1, 1], [1, 1, 1, 0]) == 1.0

    def test_zero_recall(self):
        m = BinaryClassificationMetric(positive_label=1, metric="recall")
        assert m.compute([0, 0], [1, 1]) == 0.0

    def test_f1_perfect(self):
        m = BinaryClassificationMetric(positive_label=1)
        assert m.compute([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0

    def test_f1_zero(self):
        m = BinaryClassificationMetric(positive_label=1)
        assert m.compute([0, 0, 0], [1, 1, 1]) == 0.0

    def test_f1_harmonic(self):
        m_p = BinaryClassificationMetric(positive_label=1, metric="precision")
        m_r = BinaryClassificationMetric(positive_label=1, metric="recall")
        m_f = BinaryClassificationMetric(positive_label=1, metric="f1")
        preds = [1, 1, 0, 1, 0]
        truth = [1, 0, 1, 1, 0]
        p = m_p.compute(preds, truth)
        r = m_r.compute(preds, truth)
        f1 = m_f.compute(preds, truth)
        expected = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        assert abs(f1 - expected) < 1e-5

    def test_empty_input_returns_zero(self):
        m = BinaryClassificationMetric(positive_label=1)
        assert m.compute([], []) == 0.0

    def test_length_mismatch_raises(self):
        m = BinaryClassificationMetric(positive_label=1)
        with pytest.raises(ValueError, match="length"):
            m.compute([1, 0], [1])

    def test_string_labels(self):
        m = BinaryClassificationMetric(positive_label="pos", metric="f1")
        preds = ["pos", "neg", "pos"]
        truth = ["pos", "pos", "neg"]
        score = m.compute(preds, truth)
        assert 0.0 < score < 1.0

    def test_name_includes_metric(self):
        assert "precision" in BinaryClassificationMetric(metric="precision").name
        assert "recall" in BinaryClassificationMetric(metric="recall").name
        assert "f1" in BinaryClassificationMetric(metric="f1").name

    def test_invalid_metric_raises(self):
        with pytest.raises(ValueError):
            BinaryClassificationMetric(metric="accuracy")  # type: ignore[arg-type]

    def test_confusion_returns_confusion_matrix(self):
        m = BinaryClassificationMetric(positive_label=1)
        cm = m.confusion([1, 0, 1], [1, 1, 0])
        assert isinstance(cm, ConfusionMatrix)
        assert cm.total() == 3

    def test_confusion_all_positive(self):
        m = BinaryClassificationMetric(positive_label=1)
        cm = m.confusion([1, 1, 1], [1, 1, 1])
        assert cm.tp == 3
        assert cm.fp == 0
        assert cm.fn == 0
        assert cm.tn == 0

    def test_confusion_all_negative(self):
        m = BinaryClassificationMetric(positive_label=1)
        cm = m.confusion([0, 0, 0], [0, 0, 0])
        assert cm.tn == 3
        assert cm.tp == cm.fp == cm.fn == 0


# ---------------------------------------------------------------------------
# F1Score
# ---------------------------------------------------------------------------


class TestF1Score:
    def test_name(self):
        assert F1Score().name == "f1_score"

    def test_perfect(self):
        m = F1Score()
        assert m.compute([1, 0, 1], [1, 0, 1]) == 1.0

    def test_zero(self):
        m = F1Score()
        assert m.compute([0, 0], [1, 1]) == 0.0

    def test_harmonic_mean_contract(self):
        m = F1Score(positive_label=1)
        p_m = BinaryClassificationMetric(positive_label=1, metric="precision")
        r_m = BinaryClassificationMetric(positive_label=1, metric="recall")
        preds = [1, 1, 0, 0, 1]
        truth = [1, 0, 0, 1, 1]
        p = p_m.compute(preds, truth)
        r = r_m.compute(preds, truth)
        f1 = m.compute(preds, truth)
        expected = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        assert abs(f1 - expected) < 1e-5

    def test_custom_positive_label(self):
        m = F1Score(positive_label="cat")
        preds = ["cat", "dog", "cat"]
        truth = ["cat", "cat", "dog"]
        score = m.compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_confusion_delegation(self):
        m = F1Score()
        cm = m.confusion([1, 0, 1, 0], [1, 1, 0, 0])
        assert isinstance(cm, ConfusionMatrix)
        assert cm.tp + cm.fp + cm.tn + cm.fn == 4

    def test_inherits_binary_classification(self):
        assert isinstance(F1Score(), BinaryClassificationMetric)


# ---------------------------------------------------------------------------
# MultiClassF1Metric
# ---------------------------------------------------------------------------


class TestMultiClassF1Metric:
    def test_macro_equal_classes(self):
        m = MultiClassF1Metric(averaging="macro", metric="f1")
        preds = ["A", "B", "C", "A", "B", "C"]
        truth = ["A", "A", "C", "A", "B", "B"]
        score = m.compute(preds, truth)
        per_class = m.per_class_scores(preds, truth)
        expected = sum(v["f1"] for v in per_class.values()) / len(per_class)
        assert abs(score - expected) < 1e-5

    def test_macro_matches_per_class_mean(self):
        m = MultiClassF1Metric(averaging="macro")
        preds = ["cat", "dog", "bird", "cat", "dog", "bird"]
        truth = ["cat", "cat", "bird", "cat", "dog", "dog"]
        score = m.compute(preds, truth)
        per_class = m.per_class_scores(preds, truth)
        expected = sum(v["f1"] for v in per_class.values()) / len(per_class)
        assert abs(score - expected) < 1e-5

    def test_weighted_uses_support(self):
        m_w = MultiClassF1Metric(averaging="weighted")
        preds = ["A", "A", "B", "B", "C"]
        truth = ["A", "B", "B", "B", "C"]
        w_score = m_w.compute(preds, truth)
        per_class = m_w.per_class_scores(preds, truth)
        total_support = sum(v["support"] for v in per_class.values())
        expected = sum(v["f1"] * v["support"] for v in per_class.values()) / total_support
        assert abs(w_score - expected) < 1e-5

    def test_micro_aggregates_counts(self):
        m = MultiClassF1Metric(averaging="micro")
        preds = ["A", "B", "A", "B"]
        truth = ["A", "A", "B", "B"]
        score = m.compute(preds, truth)
        assert 0.0 <= score <= 1.0

    def test_perfect_macro_f1(self):
        m = MultiClassF1Metric(averaging="macro")
        preds = ["A", "B", "C"]
        truth = ["A", "B", "C"]
        assert m.compute(preds, truth) == 1.0

    def test_empty_input_returns_zero(self):
        m = MultiClassF1Metric()
        assert m.compute([], []) == 0.0

    def test_length_mismatch_raises(self):
        m = MultiClassF1Metric()
        with pytest.raises(ValueError, match="length"):
            m.compute(["A", "B"], ["A"])

    def test_invalid_averaging_raises(self):
        with pytest.raises(ValueError):
            MultiClassF1Metric(averaging="none")  # type: ignore[arg-type]

    def test_invalid_metric_raises(self):
        with pytest.raises(ValueError):
            MultiClassF1Metric(metric="accuracy")  # type: ignore[arg-type]

    def test_name_includes_averaging_and_metric(self):
        m = MultiClassF1Metric(averaging="weighted", metric="precision")
        assert "weighted" in m.name
        assert "precision" in m.name

    def test_per_class_scores_keys(self):
        m = MultiClassF1Metric()
        preds = ["A", "B", "A"]
        truth = ["A", "A", "B"]
        per_class = m.per_class_scores(preds, truth)
        for label_scores in per_class.values():
            assert "precision" in label_scores
            assert "recall" in label_scores
            assert "f1" in label_scores
            assert "support" in label_scores

    def test_confusion_is_micro_aggregate(self):
        m = MultiClassF1Metric()
        preds = ["A", "B", "C"]
        truth = ["A", "A", "C"]
        cm = m.confusion(preds, truth)
        assert isinstance(cm, ConfusionMatrix)
        assert cm.positive_label == "<micro>"

    def test_macro_precision(self):
        m = MultiClassF1Metric(averaging="macro", metric="precision")
        preds = ["A", "A", "B"]
        truth = ["A", "B", "B"]
        score = m.compute(preds, truth)
        per_class = m.per_class_scores(preds, truth)
        expected = sum(v["precision"] for v in per_class.values()) / len(per_class)
        assert abs(score - expected) < 1e-5

    def test_macro_recall(self):
        m = MultiClassF1Metric(averaging="macro", metric="recall")
        preds = ["A", "A", "B"]
        truth = ["A", "B", "B"]
        score = m.compute(preds, truth)
        per_class = m.per_class_scores(preds, truth)
        expected = sum(v["recall"] for v in per_class.values()) / len(per_class)
        assert abs(score - expected) < 1e-5

    def test_single_class_all_correct(self):
        m = MultiClassF1Metric(averaging="macro")
        preds = ["A", "A", "A"]
        truth = ["A", "A", "A"]
        assert m.compute(preds, truth) == 1.0

    def test_weighted_vs_macro_differ_on_imbalanced(self):
        m_macro = MultiClassF1Metric(averaging="macro")
        m_weighted = MultiClassF1Metric(averaging="weighted")
        preds = ["A"] * 8 + ["B"]
        truth = ["A"] * 7 + ["B", "B"]
        macro = m_macro.compute(preds, truth)
        weighted = m_weighted.compute(preds, truth)
        assert abs(macro - weighted) > 1e-5


# ---------------------------------------------------------------------------
# ClassificationMetric ABC (base.py)
# ---------------------------------------------------------------------------


class TestClassificationMetricABC:
    def test_binary_metric_is_classification_metric(self):
        from agentic_core.evaluation.metrics.base import ClassificationMetric

        assert isinstance(BinaryClassificationMetric(), ClassificationMetric)

    def test_multiclass_metric_is_classification_metric(self):
        from agentic_core.evaluation.metrics.base import ClassificationMetric

        assert isinstance(MultiClassF1Metric(), ClassificationMetric)

    def test_f1score_is_classification_metric(self):
        from agentic_core.evaluation.metrics.base import ClassificationMetric

        assert isinstance(F1Score(), ClassificationMetric)

    def test_f1score_is_evaluation_metric(self):
        from agentic_core.evaluation.metrics.base import EvaluationMetric

        assert isinstance(F1Score(), EvaluationMetric)
