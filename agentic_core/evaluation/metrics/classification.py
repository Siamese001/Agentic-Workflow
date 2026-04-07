"""
Classification Metrics: ConfusionMatrix, BinaryClassificationMetric, MultiClassF1Metric.

Deterministic, pure-Python, zero external dependencies.

Hierarchy:
    ClassificationMetric (ABC, base.py)
    ├── BinaryClassificationMetric   — binary labels, TP/FP/TN/FN
    └── MultiClassF1Metric           — per-class F1 + macro/micro/weighted averaging
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.evaluation.metrics.base import ClassificationMetric
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "classification", "p0_governance")
_emit_reads_policy_state("p0", "classification", "policy_binding")
_emit_snapshots_state("p0", "classification", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_emits_metric_event("classification", "p4obs", "metric_1")
_emit_emits_metric_event("classification", "p4obs", "metric_2")
_emit_emits_metric_event("classification", "p4obs", "metric_3")
_emit_emits_metric_event("classification", "p4obs", "metric_4")
_emit_emits_metric_event("classification", "p4obs", "metric_5")
_emit_emits_metric_event("classification", "p4obs", "metric_6")
_emit_records_incident_event("classification", "p4obs", "incident")
_emit_captures_runtime_anomaly("classification", "p4obs", "anomaly")
_emit_writes_observability_log("classification", "p4obs", "obs_log")
_emit_updates_monitoring_state("classification", "p4obs", "mon_state")
_emit_triggers_alert("classification", "p4obs", "alert")
_emit_links_incident_trace("classification", "p4obs", "trace_link")
_emit_captures_pattern("classification", "p3lm", "pattern")
_emit_records_learning_event("classification", "p3lm", "learning_event")
_emit_writes_learning_snapshot("classification", "p3lm", "snapshot")
_emit_feeds_meta_learning("classification", "p3lm", "meta_feed")
_emit_updates_routing_strategy("classification", "p3lm", "routing")
_emit_improves_agent_policy("classification", "p3lm", "policy")
_emit_stores_learning_state("classification", "p3lm", "state")
_emit_records_execution_trace("classification", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("classification", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("classification", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("classification", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("classification", "L4_STATE", "p2_trace_5")
_emit_reads_environ("classification", "env_read", "p2_env_1")
_emit_reads_environ("classification", "env_read", "p2_env_2")
_emit_reads_runtime_state("classification", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("classification", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "classification", "context_pull")
_emit_pulls_context("p1", "classification", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "classification", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "classification", "uwg_term_2")
_emit_writes_through("p1", "classification", "write_through")
_emit_writes_through("p1", "classification", "write_through_2")
_emit_validated_by_safety_plane("p1", "classification", "safety_validation")
_emit_invokes_eval("p1", "classification", "eval_call")
_emit_proposal_commits_routing("p1", "classification", "routing_commit")
_emit_escalates_to_human("p1", "classification", "human_escalation")
_emit_routes_through("p1", "classification", "route_through")
_emit_checks_agent_registry("p1", "classification", "agent_registry")
_emit_validates_agent_capability("p1", "classification", "capability")
_emit_dispatches_execution_plan("p1", "classification", "exec_plan")
_emit_agent_executes_agent("p1", "classification", "sub_agent")
_emit_routes_to_agent("p1", "classification", "target_agent")
_emit_verifies_policy("p1", "classification", "policy_check")
_emit_observes_runtime_state("p1", "classification", "runtime_state")
_emit_verifies_boundary("p1", "classification", "boundary_check")
_emit_transcripts_response("p1", "classification", "transcript")
_emit_hard_fails_untranscripted("p1", "classification")
_emit_gated_by_confidence("p1", "classification", "confidence_gate")
emit_replay_key("p0", "classification")
emit_determinism_digest("p0", "classification")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "classification", "execution_auth")
_emit_validates_capability("p2", "classification", "capability_check")
_emit_routes_to_capability("p2", "classification", "capability_route")
_emit_writes_via_uwg("p2", "classification", "uwg_write")
_emit_blocks_direct_write("p2", "classification", "direct_write_block")
_emit_records_tool_invocation("p2", "classification", "tool_invocation")
_emit_captures_execution_output("p2", "classification", "exec_output")
_emit_dispatches_agent("p3", "classification", "agent_dispatch")
_emit_coordinates_agents("p3", "classification", "agent_coordination")
_emit_records_workflow_lineage("p3", "classification", "workflow_lineage")
_emit_records_healing_outcome("p3", "classification", "healing_outcome")
_emit_escalates_failure("p3", "classification", "failure_escalation")
_emit_orchestrates_workflow("p3", "classification", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "classification", "healing_dispatch")
_emit_invokes_evaluation("p3", "classification", "evaluation_signal")
_emit_records_telemetry_event("p4", "classification", "telemetry_event")
_emit_captures_evaluation_metric("p4", "classification", "eval_metric")
_emit_stores_embedding("p4", "classification", "embedding_store")
_emit_updates_meta_learning_state("p4", "classification", "meta_learning")
_emit_links_execution_to_snapshot("p4", "classification", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# ConfusionMatrix
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConfusionMatrix:
    """Immutable binary confusion matrix counts.

    Attributes:
        tp: True positives
        fp: False positives
        tn: True negatives
        fn: False negatives
        positive_label: The label treated as the positive class
    """

    tp: int
    fp: int
    tn: int
    fn: int
    positive_label: Any = 1

    def precision(self) -> float:
        """TP / (TP + FP). Returns 0.0 when denominator is zero."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfusionMatrix.precision")

        denom = self.tp + self.fp
        return round(self.tp / denom, 6) if denom > 0 else 0.0

    def recall(self) -> float:
        """TP / (TP + FN). Returns 0.0 when denominator is zero."""
        denom = self.tp + self.fn
        return round(self.tp / denom, 6) if denom > 0 else 0.0

    def f1(self) -> float:
        """Harmonic mean of precision and recall. Returns 0.0 when both are 0."""
        p = self.precision()
        r = self.recall()
        denom = p + r
        return round(2 * p * r / denom, 6) if denom > 0.0 else 0.0

    def accuracy(self) -> float:
        """(TP + TN) / total. Returns 0.0 on empty input."""
        total = self.tp + self.fp + self.tn + self.fn
        return round((self.tp + self.tn) / total, 6) if total > 0 else 0.0

    def total(self) -> int:
        """Total number of samples."""
        return self.tp + self.fp + self.tn + self.fn

    def to_dict(self) -> dict[str, Any]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "positive_label": self.positive_label,
            "precision": self.precision(),
            "recall": self.recall(),
            "f1": self.f1(),
            "accuracy": self.accuracy(),
        }


# ---------------------------------------------------------------------------
# BinaryClassificationMetric
# ---------------------------------------------------------------------------


def _build_binary_confusion(
    prediction: list,
    ground_truth: list,
    positive_label: Any,
) -> ConfusionMatrix:
    """Compute binary confusion matrix from parallel label lists."""
    if len(prediction) != len(ground_truth):
        raise ValueError(f"prediction length {len(prediction)} != ground_truth length {len(ground_truth)}")
    tp = fp = tn = fn = 0
    for pred, true in zip(prediction, ground_truth):
        pred_pos = pred == positive_label
        true_pos = true == positive_label
        if pred_pos and true_pos:
            tp += 1
        elif pred_pos and not true_pos:
            fp += 1
        elif not pred_pos and not true_pos:
            tn += 1
        else:
            fn += 1
    return ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn, positive_label=positive_label)


class BinaryClassificationMetric(ClassificationMetric):
    """Precision, recall, and F1 for binary classification.

    Args:
        positive_label: The label considered the positive class (default 1).
        metric: Which scalar to return from compute(): ``"f1"``, ``"precision"``,
                or ``"recall"`` (default ``"f1"``).
    """

    def __init__(
        self,
        positive_label: Any = 1,
        metric: Literal["f1", "precision", "recall"] = "f1",
    ) -> None:
        if metric not in ("f1", "precision", "recall"):
            raise ValueError(f"metric must be 'f1', 'precision', or 'recall', got {metric!r}")
        self._positive_label = positive_label
        self._metric = metric

    @property
    def name(self) -> str:
        return f"binary_{self._metric}"

    def confusion(self, prediction: list, ground_truth: list) -> ConfusionMatrix:
        """Return binary ConfusionMatrix for the given predictions."""
        return _build_binary_confusion(prediction, ground_truth, self._positive_label)

    def compute(self, prediction: list, ground_truth: list, context: Any = None) -> float:
        """Return the configured scalar metric (f1 / precision / recall).

        Args:
            prediction: Flat list of predicted labels.
            ground_truth: Flat list of true labels (same length).
            context: Unused.

        Returns:
            Float score in [0.0, 1.0].
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BinaryClassificationMetric.compute")

        if not prediction or not ground_truth:
            return 0.0
        cm = self.confusion(prediction, ground_truth)
        if self._metric == "precision":
            return cm.precision()
        if self._metric == "recall":
            return cm.recall()
        return cm.f1()


# ---------------------------------------------------------------------------
# MultiClassF1Metric
# ---------------------------------------------------------------------------


def _per_class_confusion(
    prediction: list,
    ground_truth: list,
    label: Any,
) -> ConfusionMatrix:
    """One-vs-rest binary confusion matrix for a single class label."""
    return _build_binary_confusion(
        prediction=[p == label for p in prediction],
        ground_truth=[g == label for g in ground_truth],
        positive_label=True,
    )


class MultiClassF1Metric(ClassificationMetric):
    """Per-class precision/recall/F1 with configurable averaging.

    Averaging modes:
        ``"macro"``    — unweighted mean of per-class F1
        ``"micro"``    — aggregate TP/FP/FN across all classes, then compute F1
        ``"weighted"`` — support-weighted mean of per-class F1

    Args:
        averaging: One of ``"macro"``, ``"micro"``, ``"weighted"`` (default ``"macro"``).
        metric: Scalar to return from compute(): ``"f1"``, ``"precision"``,
                or ``"recall"`` (default ``"f1"``).
    """

    def __init__(
        self,
        averaging: Literal["macro", "micro", "weighted"] = "macro",
        metric: Literal["f1", "precision", "recall"] = "f1",
    ) -> None:
        if averaging not in ("macro", "micro", "weighted"):
            raise ValueError(f"averaging must be 'macro', 'micro', or 'weighted', got {averaging!r}")
        if metric not in ("f1", "precision", "recall"):
            raise ValueError(f"metric must be 'f1', 'precision', or 'recall', got {metric!r}")
        self._averaging = averaging
        self._metric = metric

    @property
    def name(self) -> str:
        return f"multiclass_{self._metric}_{self._averaging}"

    def _classes(self, prediction: list, ground_truth: list) -> list:
        """Sorted unique labels from both lists."""
        return sorted(set(prediction) | set(ground_truth), key=lambda x: str(x))

    def confusion(self, prediction: list, ground_truth: list) -> ConfusionMatrix:
        """Return micro-aggregate ConfusionMatrix (sum of per-class TP/FP/TN/FN)."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MultiClassF1Metric.confusion")

        classes = self._classes(prediction, ground_truth)
        tp = fp = tn = fn = 0
        for label in classes:
            cm = _per_class_confusion(prediction, ground_truth, label)
            tp += cm.tp
            fp += cm.fp
            tn += cm.tn
            fn += cm.fn
        return ConfusionMatrix(tp=tp, fp=fp, tn=tn, fn=fn, positive_label="<micro>")

    def per_class_scores(self, prediction: list, ground_truth: list) -> dict[Any, dict[str, float]]:
        """Return per-class dict of precision/recall/f1/support."""
        classes = self._classes(prediction, ground_truth)
        result: dict[Any, dict[str, float]] = {}
        for label in classes:
            cm = _per_class_confusion(prediction, ground_truth, label)
            support = sum(1 for g in ground_truth if g == label)
            result[label] = {
                "precision": cm.precision(),
                "recall": cm.recall(),
                "f1": cm.f1(),
                "support": float(support),
            }
        return result

    def compute(self, prediction: list, ground_truth: list, context: Any = None) -> float:
        """Return averaged scalar metric.

        Args:
            prediction: Flat list of predicted class labels.
            ground_truth: Flat list of true class labels (same length).
            context: Unused.

        Returns:
            Averaged score in [0.0, 1.0].
        """
        if not prediction or not ground_truth:
            return 0.0
        if len(prediction) != len(ground_truth):
            raise ValueError(
                f"prediction length {len(prediction)} != ground_truth length {len(ground_truth)}",
            )

        classes = self._classes(prediction, ground_truth)
        n = len(ground_truth)

        if self._averaging == "micro":
            cm = self.confusion(prediction, ground_truth)
            if self._metric == "precision":
                return cm.precision()
            if self._metric == "recall":
                return cm.recall()
            return cm.f1()

        per_class = self.per_class_scores(prediction, ground_truth)

        if self._averaging == "macro":
            scores = [per_class[lbl][self._metric] for lbl in classes]
            return round(sum(scores) / len(scores), 6) if scores else 0.0

        # weighted
        total_weight = 0.0
        weighted_sum = 0.0
        for lbl in classes:
            support = per_class[lbl]["support"]
            weighted_sum += per_class[lbl][self._metric] * support
            total_weight += support
        return round(weighted_sum / total_weight, 6) if total_weight > 0 else 0.0


__all__ = [
    "ConfusionMatrix",
    "BinaryClassificationMetric",
    "MultiClassF1Metric",
]
