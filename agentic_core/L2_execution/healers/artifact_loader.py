"""Runtime artifact loader for the C3 heal-classifier.

Loads a packaged artifact from disk, verifies completeness and hash integrity,
and returns a production-backed HealClassifierModel.

Fail-closed contract:
  - Any loading error → (None, "") → ConfidenceScorer falls back to heuristic-only.
  - Never raises from try_load_artifact() or wire_shadow_mode_scorer().

Shadow-mode invariant:
  - wire_shadow_mode_scorer() always returns shadow_mode=True.
  - Active-mode wiring is NOT in scope for this module.

E1 bind site:
  - Call wire_shadow_mode_scorer(artifact_dir, envelope_builder=builder) at E1 startup.
  - This binds the verified model_version_hash into both the scorer and the replay envelope.
"""

from __future__ import annotations

import hashlib
import io
import json
import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .heal_classifier_model import (
    ClassifierFeatures,
    HealClassifierLoadError,
    HealClassifierModel,
)
from ..types.heal_contract_types import ClassifierSource, HealClassifierResult
from tqdm import tqdm

if TYPE_CHECKING:
    from typing import Callable
    from .activation_criteria import ActivationCriteria
    from .confidence_scorer import ConfidenceScorer
    from .governed_scorer import GovernedConfidenceScorer
    from ..determinism.replay_envelope import EnvelopeBuilder
    from ..types.heal_contract_types import HealClassifierTelemetry


# Files concatenated (in order) to derive model_version_hash
_HASH_INPUT_FILES: tuple[str, ...] = (
    "model.pkl",
    "ood_detector.pkl",
    "feature_schema.json",
)

_MAX_ARTIFACT_BYTES: int = 25 * 1024 * 1024
_ALLOWED_PICKLE_GLOBALS: tuple[str, ...] = (
    "sklearn.",
    "numpy.",
    "scipy.",
    "collections.",
    "builtins.",
)

# All files that must be present for a valid artifact package
_REQUIRED_FILES: tuple[str, ...] = (
    "model.pkl",
    "ood_detector.pkl",
    "feature_schema.json",
    "calibration_meta.json",
    "training_meta.json",
    "ood_meta.json",
    "hash_manifest.json",
    "model_version_hash",
)

# Repair-outcome label → HealTier name
_OUTCOME_TO_TIER: dict[str, str] = {
    "HEALED_LOCAL": "HIGH",
    "HEALED_LLM": "MEDIUM",
    "HEALED_HITL": "HITL",
    "FAILED": "LOW",
}

# Labels that count as automated healing success for heal_confidence
_HEALED_LABELS: frozenset[str] = frozenset({"HEALED_LOCAL", "HEALED_LLM"})


# ---------------------------------------------------------------------------
# Production HealClassifierModel implementation
# ---------------------------------------------------------------------------


class _PackagedHealClassifierModel(HealClassifierModel):
    """Production HealClassifierModel backed by a loaded sklearn GBDT + OOD detector.

    predict() must complete in < 1 ms (enforced upstream in ConfidenceScorer._classify_ml).
    All numpy/sklearn imports are deferred inside predict() to keep module-level import lean.
    """

    def __init__(
        self,
        raw_model: Any,
        ood_detector: Any,
        mvh: str,
        ood_threshold: float,
        label_classes: list[str],
    ) -> None:
        self._raw_model = raw_model
        self._ood_detector = ood_detector
        self._mvh = mvh
        self._ood_threshold = ood_threshold
        self._label_classes = label_classes

    @property
    def model_version_hash(self) -> str:
        return self._mvh

    def predict(self, features: ClassifierFeatures) -> HealClassifierResult:
        import time

        import numpy as np

        X = np.array(
            [
                [
                    float(features.failure_class),
                    float(features.retry_count),
                    float(features.error_code_hash),
                    float(features.lineage_hash_prefix),
                    float(features.budget_remaining),
                    float(features.source_layer_id),
                ]
            ]
        )

        t_start = time.perf_counter()
        probs_row = self._raw_model.predict_proba(X)[0]
        elapsed_us = int((time.perf_counter() - t_start) * 1_000_000)

        pred_idx = int(np.argmax(probs_row))
        pred_label = self._label_classes[pred_idx]

        heal_confidence = float(
            sum(p for lbl, p in zip(self._label_classes, probs_row) if lbl in _HEALED_LABELS)
        )

        recommended_tier = _OUTCOME_TO_TIER.get(pred_label, "LOW")

        ood_score = float(self._ood_detector.decision_function(X)[0])
        ood_flag = ood_score < self._ood_threshold

        return HealClassifierResult(
            heal_confidence=heal_confidence,
            recommended_tier=recommended_tier,
            confidence_per_tier={lbl: float(p) for lbl, p in zip(self._label_classes, probs_row)},
            ood_flag=ood_flag,
            source=ClassifierSource.ML_CLASSIFIER,
            model_version_hash=self._mvh,
            inference_latency_us=elapsed_us,
        )


# ---------------------------------------------------------------------------
# Artifact verification helpers
# ---------------------------------------------------------------------------


def _verify_completeness(artifact_dir: Path) -> list[str]:
    """Return list of missing required files; empty list = complete."""
    return [f for f in _REQUIRED_FILES if not (artifact_dir / f).exists()]


def _compute_model_version_hash(artifact_dir: Path) -> str:
    """SHA-256(model.pkl || ood_detector.pkl || feature_schema.json)[:16]."""
    content = b"".join((artifact_dir / f).read_bytes() for f in _HASH_INPUT_FILES)
    return hashlib.sha256(content).hexdigest()[:16]


def _verify_hash_manifest(artifact_dir: Path) -> None:
    manifest = json.loads((artifact_dir / "hash_manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise HealClassifierLoadError("hash_manifest.json must be a JSON object")

    for filename in tqdm(_REQUIRED_FILES, desc="Processing", unit="item"):
        if filename == "hash_manifest.json":
            continue
        expected = manifest.get(filename)
        if not isinstance(expected, str) or len(expected) != 64:
            raise HealClassifierLoadError(f"Missing or invalid sha256 for {filename!r} in hash_manifest.json")

        file_path = artifact_dir / filename
        if file_path.stat().st_size > _MAX_ARTIFACT_BYTES:
            raise HealClassifierLoadError(f"Artifact file too large: {filename}")

        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual != expected:
            raise HealClassifierLoadError(
                f"SHA-256 mismatch for {filename!r}: expected={expected!r} actual={actual!r}"
            )


class _RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str) -> Any:
        fqcn = f"{module}.{name}"
        if any(module.startswith(prefix) for prefix in _ALLOWED_PICKLE_GLOBALS):
            return super().find_class(module, name)
        raise HealClassifierLoadError(f"Disallowed pickle global: {fqcn}")


def _restricted_pickle_load(path: Path) -> Any:
    with path.open("rb") as fh:
        payload = fh.read()
    if len(payload) > _MAX_ARTIFACT_BYTES:
        raise HealClassifierLoadError(f"Pickle payload too large: {path.name}")
    return _RestrictedUnpickler(io.BytesIO(payload)).load()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_artifact(artifact_dir: Path) -> tuple[HealClassifierModel, str]:
    """Load and fully verify a packaged artifact.

    Returns:
        (model, model_version_hash)  — both are guaranteed valid.

    Raises:
        HealClassifierLoadError: artifact incomplete, hash mismatch, or unpickle failure.
    """
    missing = _verify_completeness(artifact_dir)
    if missing:
        raise HealClassifierLoadError(f"Artifact incomplete — missing files: {missing}")

    computed = _compute_model_version_hash(artifact_dir)
    stored = (artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
    if stored != computed:
        raise HealClassifierLoadError(f"model_version_hash mismatch: stored={stored!r} computed={computed!r}")
    _verify_hash_manifest(artifact_dir)

    try:
        raw_model = _restricted_pickle_load(artifact_dir / "model.pkl")
        ood_detector = _restricted_pickle_load(artifact_dir / "ood_detector.pkl")
    except (pickle.UnpicklingError, AttributeError, ImportError) as exc:
        raise HealClassifierLoadError(f"Failed to unpickle model files: {exc}") from exc

    feature_schema = json.loads((artifact_dir / "feature_schema.json").read_text(encoding="utf-8"))
    ood_meta = json.loads((artifact_dir / "ood_meta.json").read_text(encoding="utf-8"))
    if not isinstance(feature_schema, dict):
        raise HealClassifierLoadError("feature_schema.json must be a JSON object")
    if not isinstance(ood_meta, dict):
        raise HealClassifierLoadError("ood_meta.json must be a JSON object")
    label_classes = feature_schema.get("label_classes", [])
    if (
        not isinstance(label_classes, list)
        or not label_classes
        or not all(isinstance(x, str) for x in label_classes)
    ):
        raise HealClassifierLoadError("feature_schema.json must include non-empty label_classes[str]")
    threshold = ood_meta.get("threshold", 0.0)
    if not isinstance(threshold, (int, float)):
        raise HealClassifierLoadError("ood_meta.json threshold must be numeric")
    if not hasattr(raw_model, "predict_proba"):
        raise HealClassifierLoadError("Loaded model does not implement predict_proba")
    if not hasattr(ood_detector, "decision_function"):
        raise HealClassifierLoadError("Loaded OOD detector does not implement decision_function")

    model = _PackagedHealClassifierModel(
        raw_model=raw_model,
        ood_detector=ood_detector,
        mvh=stored,
        ood_threshold=float(threshold),
        label_classes=label_classes,
    )
    return model, stored


def try_load_artifact(
    artifact_dir: Path | str | None,
) -> tuple[HealClassifierModel | None, str]:
    """Fail-closed artifact loader.

    Returns (model, hash) on success, (None, "") on any failure.
    Never raises — all errors produce heuristic fallback.
    """
    if artifact_dir is None:
        return None, ""
    try:
        return load_artifact(Path(artifact_dir))
    except Exception:  # guardian: allow-broad-exception -- artifact loading may raise any sklearn/pickle/IO error; fail-closed fallback to heuristic required for routing safety
        return None, ""


def wire_shadow_mode_scorer(
    artifact_dir: Path | str | None,
    run_id: str = "",
    telemetry_sink: Callable[[HealClassifierTelemetry], None] | None = None,
    envelope_builder: EnvelopeBuilder | None = None,
) -> ConfidenceScorer:
    """Build a shadow-mode ConfidenceScorer wired to the packaged artifact.

    This is the E1 bind site.  Call once at startup before any scoring.

    If artifact_dir is provided and valid:
      - Model is loaded and hash-verified.
      - expected_model_hash is set on the scorer (per-inference re-verification).
      - envelope_builder.with_ml_model_hash("heal_classifier", hash) is called so
        the C1 replay digest covers the exact artifact used during this run.

    If artifact_dir is None or loading fails:
      - Returns heuristic-only scorer (model=None, expected_model_hash="").
      - envelope_builder is NOT mutated.

    Always returns shadow_mode=True.  Active-mode wiring is a separate governed step.

    Args:
        artifact_dir:      Path to unpacked artifact directory; None = heuristic-only.
        run_id:            Run ID bound into telemetry events.
        telemetry_sink:    Callable for BUS T telemetry; None = no emission.
        envelope_builder:  EnvelopeBuilder to bind model hash at E1; None = skip bind.

    Returns:
        ConfidenceScorer in shadow_mode=True.
    """
    from .confidence_scorer import ConfidenceScorer

    model, mvh = try_load_artifact(artifact_dir)

    if model is not None and mvh and envelope_builder is not None:
        envelope_builder.with_ml_model_hash("heal_classifier", mvh)

    return ConfidenceScorer(
        model=model,
        expected_model_hash=mvh,
        shadow_mode=True,
        telemetry_sink=telemetry_sink,
        run_id=run_id,
    )


def wire_governed_scorer(
    artifact_dir: Path | str | None,
    run_id: str = "",
    telemetry_sink: Callable[[HealClassifierTelemetry], None] | None = None,
    envelope_builder: EnvelopeBuilder | None = None,
    criteria: ActivationCriteria | None = None,
    rollback_window_size: int = 200,
) -> GovernedConfidenceScorer:
    """Build a GovernedConfidenceScorer with full shadow→active activation logic.

    This is the governed E1 bind site.  Reads activation_record.json from the
    artifact directory (if present) and resolves the correct activation mode:

      ABSENT  — artifact_dir is None or artifact fails to load.
      SHADOW  — no valid active-mode activation record; heuristic routing.
      ACTIVE  — valid activation_record.json with mode="active", matching hash,
                and all criteria passing; ML tier drives routing.

    Active mode can only be entered when all of the following are true:
      1. Artifact loads and hash-verifies successfully.
      2. artifact_dir/activation_record.json exists with activation_mode="active".
      3. The record's artifact_hash matches the verified model_version_hash.
      4. All ActivationCriteria pass against the evidence in the record.

    A RollbackMonitor is attached only in ACTIVE mode.  Feed it outcomes via
    GovernedConfidenceScorer.record_outcome() to enable automatic rollback.

    Args:
        artifact_dir:        Path to unpacked artifact directory; None = heuristic-only.
        run_id:              Bound into telemetry events.
        telemetry_sink:      BUS T telemetry callable; None = no emission.
        envelope_builder:    EnvelopeBuilder to bind model hash at E1; None = skip.
        criteria:            Optional threshold overrides; None = defaults.
        rollback_window_size: Sliding window size for the rollback monitor.

    Returns:
        GovernedConfidenceScorer in ABSENT, SHADOW, or ACTIVE mode.
    """
    from .activation_criteria import ActivationCriteria as _AC, RollbackMonitor
    from .activation_state import ActivationMode, resolve_activation_mode
    from .confidence_scorer import ConfidenceScorer
    from .governed_scorer import GovernedConfidenceScorer

    model, mvh = try_load_artifact(artifact_dir)

    if model is not None and mvh and envelope_builder is not None:
        envelope_builder.with_ml_model_hash("heal_classifier", mvh)

    resolved_dir = Path(artifact_dir) if artifact_dir is not None else None
    mode, _criteria_result = resolve_activation_mode(resolved_dir, mvh, criteria)

    shadow_mode = mode != ActivationMode.ACTIVE

    inner = ConfidenceScorer(
        model=model,
        expected_model_hash=mvh,
        shadow_mode=shadow_mode,
        telemetry_sink=telemetry_sink,
        run_id=run_id,
    )

    rollback_monitor: RollbackMonitor | None = None
    if mode == ActivationMode.ACTIVE:
        rollback_monitor = RollbackMonitor(
            window_size=rollback_window_size,
            criteria=criteria,
        )

    return GovernedConfidenceScorer(
        inner=inner,
        activation_mode=mode,
        rollback_monitor=rollback_monitor,
    )
