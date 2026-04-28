"""Phase 5 shadow-mode telemetry tests for C3 HealClassifierTelemetry.

Verifies that BUS T events are emitted on every ConfidenceScorer.score() call,
that all required fields are present, and that divergence_flag correctly
identifies cases where the ML recommendation differs from the heuristic tier.

Routing is always heuristic in shadow_mode=True (default), so these tests
also confirm the shadow-mode contract: tier != divergence, score unchanged.
"""

from __future__ import annotations

from typing import List

import pytest

from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScorer,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import (
    FailureSignalBuilder,
    HealFailureClass,
)
from agentic_core.L2_execution.healers.heal_classifier_model import HealClassifierModel
from agentic_core.L2_execution.types.heal_contract_types import (
    ClassifierSource,
    HealClassifierTelemetry,
)

_TELEMETRY_FIELDS = (
    "run_id",
    "check_id",
    "source",
    "recommended_tier",
    "heal_confidence",
    "ood_flag",
    "model_version_hash",
    "inference_latency_us",
    "heuristic_tier",
    "divergence_flag",
)


def _make_signal(
    error_code: str = "schema_validation_error",
    retry_count: int = 0,
    failure_class: HealFailureClass = HealFailureClass.IMPORT_BOUNDARY,
    budget_remaining: float = 0.7,
    check_id: str = "chk-telemetry",
):
    return (
        FailureSignalBuilder()
        .from_context({})
        .with_check(check_id, retry_count)
        .with_error(error_code, "msg")
        .with_lineage("deadbeef12345678")
        .from_layer("L2", "heal")
        .with_failure_class(failure_class)
        .with_budget_remaining(budget_remaining)
        .build()
    )


class TestPhase5TelemetryEmission:
    def test_telemetry_emitted_on_every_score_call(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append)
        scorer.score(_make_signal())
        scorer.score(_make_signal(error_code="timeout"))
        assert len(events) == 2

    def test_no_telemetry_without_sink(self):
        scorer = ConfidenceScorer()
        scorer.score(_make_signal())  # must not raise

    def test_all_required_fields_present(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append)
        scorer.score(_make_signal())
        event = events[0]
        for field in _TELEMETRY_FIELDS:
            assert hasattr(event, field), f"missing field: {field}"

    def test_check_id_matches_signal(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append)
        scorer.score(_make_signal(check_id="chk-specific"))
        assert events[0].check_id == "chk-specific"

    def test_run_id_propagated_from_scorer(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append, run_id="run-xyz")
        scorer.score(_make_signal())
        assert events[0].run_id == "run-xyz"

    def test_default_run_id_is_empty_string(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append)
        scorer.score(_make_signal())
        assert events[0].run_id == ""

    def test_heuristic_only_source_is_heuristic_fallback(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append)
        scorer.score(_make_signal())
        assert events[0].source == ClassifierSource.HEURISTIC_FALLBACK

    def test_divergence_flag_false_when_no_model(self):
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(telemetry_sink=events.append)
        scorer.score(_make_signal())
        assert events[0].divergence_flag is False

    def test_telemetry_sink_exception_does_not_propagate(self):
        def bad_sink(event: HealClassifierTelemetry) -> None:
            raise RuntimeError("sink failure")

        scorer = ConfidenceScorer(telemetry_sink=bad_sink)
        result = scorer.score(_make_signal())  # must not raise
        assert result.tier == HealTier.HIGH


class TestPhase5ShadowModeContract:
    def test_shadow_mode_routing_tier_from_heuristic(self):
        """Even with stub returning LOW, shadow_mode keeps heuristic HIGH routing."""
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
            telemetry_sink=events.append,
        )
        # schema_validation_error → heuristic HIGH; stub force_tier=LOW
        sig = _make_signal()
        result = scorer.score(sig)
        assert result.tier == HealTier.HIGH  # shadow_mode: heuristic wins

    def test_divergence_flag_true_when_tiers_differ(self):
        """divergence_flag must be True when ML recommends a tier the heuristic does not."""
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
            telemetry_sink=events.append,
        )
        sig = _make_signal()  # heuristic=HIGH, stub=LOW
        scorer.score(sig)
        assert events[0].divergence_flag is True
        assert events[0].heuristic_tier == "HIGH"
        assert events[0].recommended_tier == "LOW"

    def test_divergence_flag_false_when_tiers_agree(self):
        """divergence_flag is False when ML and heuristic agree on tier."""
        stub = HealClassifierModel.from_stub(force_tier="HIGH")
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
            telemetry_sink=events.append,
        )
        sig = _make_signal()  # heuristic=HIGH, stub=HIGH
        scorer.score(sig)
        assert events[0].divergence_flag is False

    def test_ml_result_on_score_object_contains_stub_output(self):
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
        )
        sig = _make_signal()
        result = scorer.score(sig)
        assert result.ml_result is not None
        assert result.ml_result.source == ClassifierSource.ML_CLASSIFIER
        assert result.ml_result.recommended_tier == "LOW"

    def test_ood_telemetry_source_is_heuristic_when_fallback_triggered(self):
        """When OOD triggers fallback, telemetry source reflects HEURISTIC_FALLBACK."""
        stub = HealClassifierModel.from_stub()
        events: List[HealClassifierTelemetry] = []
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
            telemetry_sink=events.append,
        )
        # budget_remaining=1.0 triggers OOD → fallback
        sig = _make_signal(budget_remaining=1.0, failure_class=HealFailureClass.SSOT_DRIFT)
        scorer.score(sig)
        assert events[0].source == ClassifierSource.HEURISTIC_FALLBACK
        assert events[0].divergence_flag is False  # both from heuristic
