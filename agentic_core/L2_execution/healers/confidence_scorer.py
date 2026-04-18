"""C3 Confidence Scoring - Tier routing for healing.

10C-REQ-137: Score heal confidence High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

from .failure_signal import FailureSignal, HealFailureClass
from .heal_classifier_model import ClassifierFeatures, HealClassifierModel
from ..types.heal_contract_types import (
    ClassifierSource,
    HealClassifierResult,
    HealClassifierTelemetry,
)


class HealTier(Enum):
    """Healing tier based on confidence."""

    HIGH = auto()  # >0.85: Local deterministic rules
    MEDIUM = auto()  # 0.50-0.85: Qwen vLLM
    LOW = auto()  # <0.50: Gemini 2.5 Pro
    HITL = auto()  # Uncertain: Human review


@dataclass
class ConfidenceScore:
    """Confidence scoring result."""

    score: float  # 0.0-1.0
    tier: HealTier
    confidence_in_score: float  # Meta-confidence
    reasoning: str
    ml_result: HealClassifierResult | None = None  # Phase 2: advisory ML output; None until model wired


class ConfidenceScorer:
    """C3 Confidence scorer for healing tier routing.

    10C-REQ-137: Score heal confidence High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro.

    **HITL DECISION REQUIRED**: The thresholds below (0.85, 0.50) are defaults.
    These should be calibrated based on actual healing success rates.
    """

    # HITL-10C-003: These thresholds require stakeholder approval
    HIGH_THRESHOLD = 0.85
    MEDIUM_THRESHOLD = 0.50

    def __init__(
        self,
        model: HealClassifierModel | None = None,
        expected_model_hash: str = "",
        shadow_mode: bool = True,
        telemetry_sink: Callable[[HealClassifierTelemetry], None] | None = None,
        run_id: str = "",
    ) -> None:
        self._model = model
        self._expected_model_hash = expected_model_hash
        self._shadow_mode = shadow_mode
        self._telemetry_sink = telemetry_sink
        self._run_id = run_id
        self._error_patterns: dict[str, float] = {
            # Known patterns get higher confidence for local healing
            "schema_validation_error": 0.90,
            "type_mismatch": 0.88,
            "missing_required_field": 0.85,
            "timeout": 0.60,
            "rate_limit": 0.65,
            "network_error": 0.40,
            "model_error": 0.35,
            "unknown_error": 0.20,
        }

    def score(self, signal: FailureSignal) -> ConfidenceScore:
        """Score confidence for healing signal.

        Phase 5 shadow mode: routing tier is always from the heuristic.
        ML result (if available) is attached for BUS T telemetry only.
        """
        heuristic_result = self._classify_heuristic(signal)

        ml_result: HealClassifierResult | None = None
        if self._model is not None:
            ml_result = self._classify_ml(signal)

        # Shadow mode or ML fallback: routing always uses heuristic tier
        if self._shadow_mode or ml_result is None or ml_result.source != ClassifierSource.ML_CLASSIFIER:
            routing_result = heuristic_result
        else:
            routing_result = ml_result

        # meta_confidence and reasoning always derived from heuristic (stable, observable)
        meta_confidence = 0.90 if signal.error_code in self._error_patterns else 0.60

        result = ConfidenceScore(
            score=routing_result.heal_confidence,
            tier=HealTier[routing_result.recommended_tier],
            confidence_in_score=meta_confidence,
            reasoning=f"pattern:{signal.error_code},retry:{signal.retry_count}",
            ml_result=ml_result,
        )

        self._emit_telemetry(signal, heuristic_result, ml_result)
        return result

    def _classify_heuristic(self, signal: FailureSignal) -> HealClassifierResult:
        """Rule-based heuristic — exact pre-ML behaviour, preserved as the permanent fallback."""
        base_score = self._error_patterns.get(signal.error_code, 0.30)
        retry_penalty = min(signal.retry_count * 0.10, 0.30)
        adjusted_score = max(0.0, base_score - retry_penalty)
        tier = self._tier_from_score(adjusted_score)
        return HealClassifierResult(
            heal_confidence=adjusted_score,
            recommended_tier=tier.name,
            confidence_per_tier={t.name: 0.0 for t in HealTier},
            ood_flag=False,
            source=ClassifierSource.HEURISTIC_FALLBACK,
            model_version_hash="HEURISTIC",
            inference_latency_us=0,
        )

    def _classify_ml(self, signal: FailureSignal) -> HealClassifierResult:
        """Attempt ML classification; fall back to heuristic on any trigger."""
        if self._model is None:
            return self._classify_heuristic(signal)

        if self._expected_model_hash and self._model.model_version_hash != self._expected_model_hash:
            return self._classify_heuristic(signal)

        # Build features — timestamp excluded (C1: no wall-clock in classifier input)
        try:
            features = ClassifierFeatures(
                failure_class=list(HealFailureClass).index(signal.failure_class),
                retry_count=signal.retry_count,
                error_code_hash=int(hashlib.sha256(signal.error_code.encode()).hexdigest()[:8], 16),
                lineage_hash_prefix=(
                    int(signal.lineage_hash[:8], 16) if len(signal.lineage_hash) >= 8 else 0
                ),
                budget_remaining=signal.budget_remaining,
                source_layer_id=int(hashlib.sha256(signal.source_layer.encode()).hexdigest()[:8], 16),
            )
        except (ValueError, OverflowError):
            return self._classify_heuristic(signal)

        # OOD: UNKNOWN class or sentinel budget_remaining=1.0 means caller did not populate fields
        ood = signal.failure_class == HealFailureClass.UNKNOWN or signal.budget_remaining == 1.0

        try:
            t_start = time.perf_counter()
            result = self._model.predict(features)
            elapsed_us = int((time.perf_counter() - t_start) * 1_000_000)
        except (
            RuntimeError,
            ValueError,
            TypeError,
        ):  # guardian: allow-exception -- model.predict() may raise any framework error; fallback required for routing safety
            return self._classify_heuristic(signal)

        if elapsed_us > 1000:
            return self._classify_heuristic(signal)

        if ood or result.ood_flag:
            return self._classify_heuristic(signal)

        return HealClassifierResult(
            heal_confidence=result.heal_confidence,
            recommended_tier=result.recommended_tier,
            confidence_per_tier=result.confidence_per_tier,
            ood_flag=False,
            source=ClassifierSource.ML_CLASSIFIER,
            model_version_hash=self._model.model_version_hash,
            inference_latency_us=elapsed_us,
        )

    def _emit_telemetry(
        self,
        signal: FailureSignal,
        heuristic_result: HealClassifierResult,
        ml_result: HealClassifierResult | None,
    ) -> None:
        """Emit HealClassifierTelemetry to BUS T sink; no-op when sink is None."""
        if self._telemetry_sink is None:
            return
        active = ml_result if ml_result is not None else heuristic_result
        divergence = ml_result is not None and ml_result.recommended_tier != heuristic_result.recommended_tier
        event = HealClassifierTelemetry(
            run_id=self._run_id,
            check_id=signal.check_id,
            source=active.source,
            recommended_tier=active.recommended_tier,
            heal_confidence=active.heal_confidence,
            ood_flag=active.ood_flag,
            model_version_hash=active.model_version_hash,
            inference_latency_us=active.inference_latency_us,
            heuristic_tier=heuristic_result.recommended_tier,
            divergence_flag=divergence,
        )
        try:
            self._telemetry_sink(event)
        except (
            RuntimeError,
            ValueError,
            TypeError,
            OSError,
            AttributeError,
        ):
            pass

    def _tier_from_score(self, score: float) -> HealTier:
        """Convert score to healing tier."""
        if score >= self.HIGH_THRESHOLD:
            return HealTier.HIGH
        elif score >= self.MEDIUM_THRESHOLD:
            return HealTier.MEDIUM
        else:
            return HealTier.LOW

    def get_model_for_tier(self, tier: HealTier) -> str:
        """Get model assignment for tier.

        HITL-10C-003: Model assignments should be reviewed.
        """
        model_map = {
            HealTier.HIGH: "local_deterministic",
            HealTier.MEDIUM: "qwen_vllm",
            HealTier.LOW: "gemini_2.5_pro",
            HealTier.HITL: "human_review",
        }
        return model_map[tier]

    def set_thresholds(self, high: float, medium: float) -> None:
        """Set confidence thresholds.

        HITL-10C-003: Threshold changes require approval.
        """
        self.HIGH_THRESHOLD = max(0.5, min(0.95, high))
        self.MEDIUM_THRESHOLD = max(0.1, min(0.7, medium))
