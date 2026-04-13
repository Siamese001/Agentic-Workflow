"""GBDT trainer with isotonic calibration and OOD detection."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import classification_report, f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize
from sklearn.svm import OneClassSVM

from .constants import NON_UNKNOWN_CLASSES, REPAIR_OUTCOME_CLASSES


class _IsotonicCalibratedModel:
    """Per-class isotonic calibration wrapper around a pre-fitted GBDT.

    sklearn >= 1.4 removed cv="prefit" from CalibratedClassifierCV.
    This wrapper reproduces that behaviour without relying on deprecated API.
    """

    def __init__(
        self,
        base_model: Any,
        calibrators: list[IsotonicRegression],
    ) -> None:
        self._base = base_model
        self._calibrators = calibrators

    @property
    def classes_(self) -> Any:
        return self._base.classes_

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        raw = self._base.predict_proba(X)
        calibrated = np.column_stack([cal.predict(raw[:, i]) for i, cal in enumerate(self._calibrators)])
        # Renormalise rows to sum to 1
        row_sums = calibrated.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0.0] = 1.0
        return calibrated / row_sums


def _build_isotonic_calibrated(
    base_model: Any,
    X_calib: np.ndarray,
    y_calib: np.ndarray,
) -> _IsotonicCalibratedModel:
    """Fit per-class IsotonicRegression on calib probabilities."""
    raw = base_model.predict_proba(X_calib)
    n_classes = raw.shape[1]
    calibrators: list[IsotonicRegression] = []
    for i in range(n_classes):
        ir = IsotonicRegression(out_of_bounds="clip")
        ir.fit(raw[:, i], (y_calib == i).astype(float))
        calibrators.append(ir)
    return _IsotonicCalibratedModel(base_model, calibrators)


@dataclass
class TrainerConfig:
    n_estimators: int = 100
    max_depth: int = 3
    learning_rate: float = 0.1
    subsample: float = 0.8
    min_samples_leaf: int = 20
    random_state: int = 42


@dataclass
class EvalMetrics:
    macro_f1: float
    per_class_f1: dict[str, float]
    ece: float
    macro_auroc: float
    classification_report_text: str
    per_failure_class_f1: dict[str, float] = field(default_factory=dict)
    fallback_rate: float = 0.0


@dataclass
class TrainingResult:
    model: Any  # CalibratedClassifierCV
    ood_detector: Any  # OneClassSVM
    config: TrainerConfig
    train_metrics: EvalMetrics
    val_metrics: EvalMetrics
    ood_threshold: float
    ood_fpr_train: float
    label_classes: list[str]
    n_train: int
    n_calib: int
    n_val: int


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------


def compute_ece(probs: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> float:
    """Expected Calibration Error — multi-class via max-confidence binning."""
    confidence = np.max(probs, axis=1)
    predicted = np.argmax(probs, axis=1)
    correct = (predicted == y_true).astype(float)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (confidence > lo) & (confidence <= hi)
        if mask.sum() == 0:
            continue
        ece += mask.sum() / n * abs(correct[mask].mean() - confidence[mask].mean())
    return float(ece)


def compute_macro_auroc(probs: np.ndarray, y_true: np.ndarray, n_classes: int) -> float:
    try:
        y_bin = label_binarize(y_true, classes=list(range(n_classes)))
        if n_classes == 2:
            y_bin = np.hstack([1 - y_bin, y_bin])
        return float(roc_auc_score(y_bin, probs, multi_class="ovr", average="macro"))
    except (ValueError, TypeError):
        return 0.0


def compute_eval_metrics(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    label_classes: list[str],
    failure_class_col: np.ndarray | None = None,
) -> EvalMetrics:
    probs = model.predict_proba(X)
    preds = np.argmax(probs, axis=1)
    n_classes = len(label_classes)

    macro_f1 = float(f1_score(y, preds, average="macro", zero_division=0))
    per_class_f1 = {
        cls: float(f1_score(y, preds, labels=[i], average="macro", zero_division=0))
        for i, cls in enumerate(label_classes)
    }
    ece = compute_ece(probs, y)
    macro_auroc = compute_macro_auroc(probs, y, n_classes)
    report = classification_report(y, preds, target_names=label_classes, zero_division=0)

    per_failure_class_f1: dict[str, float] = {}
    if failure_class_col is not None:
        for fc_idx, fc_name in enumerate(NON_UNKNOWN_CLASSES):
            mask = failure_class_col == fc_idx
            if mask.sum() >= 5:
                per_failure_class_f1[fc_name] = float(
                    f1_score(y[mask], preds[mask], average="macro", zero_division=0)
                )

    return EvalMetrics(
        macro_f1=macro_f1,
        per_class_f1=per_class_f1,
        ece=ece,
        macro_auroc=macro_auroc,
        classification_report_text=report,
        per_failure_class_f1=per_failure_class_f1,
    )


# ---------------------------------------------------------------------------
# Trainer
# ---------------------------------------------------------------------------


class HealClassifierTrainer:
    def __init__(self, config: TrainerConfig | None = None) -> None:
        self.config = config or TrainerConfig()

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_calib: np.ndarray,
        y_calib: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        label_classes: list[str],
        failure_class_train: np.ndarray | None = None,
        failure_class_val: np.ndarray | None = None,
    ) -> TrainingResult:
        cfg = self.config

        base_gbdt = GradientBoostingClassifier(
            n_estimators=cfg.n_estimators,
            max_depth=cfg.max_depth,
            learning_rate=cfg.learning_rate,
            subsample=cfg.subsample,
            min_samples_leaf=cfg.min_samples_leaf,
            random_state=cfg.random_state,
        )
        # Fit base on train+calib combined; then calibrate using calib fold only
        X_fit = np.vstack([X_train, X_calib])
        y_fit = np.concatenate([y_train, y_calib])
        base_gbdt.fit(X_fit, y_fit)

        calibrated = _build_isotonic_calibrated(base_gbdt, X_calib, y_calib)

        ood_detector = OneClassSVM(nu=0.01, kernel="rbf", gamma="scale")
        ood_detector.fit(X_train)
        train_scores = ood_detector.decision_function(X_train)
        ood_threshold = float(np.percentile(train_scores, 1))
        ood_fpr_train = float((train_scores < ood_threshold).mean())

        train_metrics = compute_eval_metrics(calibrated, X_train, y_train, label_classes, failure_class_train)
        val_metrics = compute_eval_metrics(calibrated, X_val, y_val, label_classes, failure_class_val)

        return TrainingResult(
            model=calibrated,
            ood_detector=ood_detector,
            config=cfg,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            ood_threshold=ood_threshold,
            ood_fpr_train=ood_fpr_train,
            label_classes=label_classes,
            n_train=len(X_train),
            n_calib=len(X_calib),
            n_val=len(X_val),
        )

    def measure_inference_latency_us(
        self,
        model: Any,
        X_sample: np.ndarray,
        n_warmup: int = 10,
        n_measure: int = 100,
    ) -> float:
        """Median single-row inference latency in microseconds."""
        row = X_sample[:1]
        for _ in range(n_warmup):
            model.predict_proba(row)
        times = []
        for _ in range(n_measure):
            t0 = time.perf_counter()
            model.predict_proba(row)
            times.append((time.perf_counter() - t0) * 1_000_000)
        return float(np.median(times))
