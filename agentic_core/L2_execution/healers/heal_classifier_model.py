"""C3 Heal Classifier Model — ML scaffold for heal-confidence scoring.

Defines the feature contract, model ABC, and deterministic stub used for
Phase 5 shadow mode.  No trained artifact is loaded here; real model loading
is deferred to the Phase 6 production rollout.

C1 COMPLIANCE:
  - ClassifierFeatures deliberately excludes timestamp.
  - predict() must be deterministic: same features + same artifact → same output.
  - No wall-clock reads, network I/O, or non-deterministic state inside predict().
"""

from __future__ import annotations

import hashlib
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..types.heal_contract_types import ClassifierSource, HealClassifierResult

# Wave F2 M4 (ADR-025, 2026-04-21): Classifier output feeds routing decisions
# that should flow through the unified heal_router.v1 schema. Emit a one-time
# DeprecationWarning so callers know to consume classifier results via
# `HealRouterTelemetryEmitter` rather than building private telemetry surfaces.
warnings.warn(
    (
        "agentic_core.L2_execution.healers.heal_classifier_model routes its "
        "outputs through the unified heal_router.v1 OTEL schema "
        "(agentic_core.L6_observability.heal_router_otel). Direct telemetry "
        "hooks on classifier results are deprecated (ADR-025 Wave F2 M4)."
    ),
    DeprecationWarning,
    stacklevel=2,
)


class HealClassifierLoadError(Exception):
    """Raised when a model artifact cannot be loaded or hash validation fails."""


@dataclass(frozen=True)
class ClassifierFeatures:
    """Flat numeric feature set derived from FailureSignal for ML inference.

    timestamp is intentionally absent — the C1 determinism surface forbids
    wall-clock values from entering classifier input.
    """

    failure_class: int
    retry_count: int
    error_code_hash: int
    lineage_hash_prefix: int
    budget_remaining: float
    source_layer_id: int


class HealClassifierModel(ABC):
    """Abstract base for heal-confidence classifiers.

    Concrete implementations provide predict() backed by a trained artifact.
    model_version_hash must match the value bound in
    ReplayEnvelope.ml_model_hashes["heal_classifier"] so the C1 digest
    covers the exact artifact used during the run.
    """

    @property
    @abstractmethod
    def model_version_hash(self) -> str:
        """First 16 hex chars of SHA-256 of the model artifact file."""

    @abstractmethod
    def predict(self, features: ClassifierFeatures) -> HealClassifierResult:
        """Return HealClassifierResult for given features.

        Contract:
          - Deterministic: same features + same artifact -> same output.
          - Must complete in < 1 ms (enforced by ConfidenceScorer._classify_ml).
          - Must NOT read wall clock, network, or non-deterministic state.
          - May set ood_flag=True to signal out-of-distribution input.
        """

    @classmethod
    def from_stub(cls, force_tier: str | None = None) -> _StubHealClassifier:
        """Return a deterministic stub for testing and Phase 5 shadow mode.

        Args:
            force_tier: When set, stub always recommends this HealTier name
                        (e.g. "LOW").  If None, output is derived from features.
        """
        return _StubHealClassifier(force_tier=force_tier)


class _StubHealClassifier(HealClassifierModel):
    """Deterministic stub — not a trained model.

    Output is derived purely from ClassifierFeatures so test assertions are
    stable.  The stub_hash constant is the expected value in
    EnvelopeBuilder.with_ml_model_hash("heal_classifier", _StubHealClassifier.STUB_HASH).
    """

    STUB_HASH: str = "STUB-00000000"

    def __init__(self, force_tier: str | None = None) -> None:
        self._force_tier = force_tier

    @property
    def model_version_hash(self) -> str:
        return self.STUB_HASH

    def predict(self, features: ClassifierFeatures) -> HealClassifierResult:
        """Deterministic prediction.  No external I/O."""
        if self._force_tier is not None:
            tier = self._force_tier
            _conf_map = {"HIGH": 0.90, "MEDIUM": 0.65, "LOW": 0.30, "HITL": 0.10}
            conf = _conf_map.get(tier, 0.30)
        elif features.retry_count == 0:
            tier = "HIGH"
            conf = 0.88
        elif features.retry_count == 1:
            tier = "MEDIUM"
            conf = 0.62
        else:
            tier = "LOW"
            conf = 0.32

        return HealClassifierResult(
            heal_confidence=conf,
            recommended_tier=tier,
            confidence_per_tier={t: 0.0 for t in ("HIGH", "MEDIUM", "LOW", "HITL")},
            ood_flag=False,
            source=ClassifierSource.ML_CLASSIFIER,
            model_version_hash=self.STUB_HASH,
            inference_latency_us=10,
        )
