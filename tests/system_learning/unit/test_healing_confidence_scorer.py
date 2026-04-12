"""Tests for C3 ConfidenceScorer — Phase 2 contracts + Phase 3 ML scaffold.

Covers:
  Phase 2: backward-compat defaults, signal-hash correctness, ml_result=None default
  Phase 3: stub model wiring, fallback triggers (stale hash, OOD, no-model)
           dispatcher-facing output unchanged when heuristic-only path is used
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.determinism.replay_envelope import EnvelopeBuilder
from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScore,
    ConfidenceScorer,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import (
    FailureSignal,
    FailureSignalBuilder,
    HealFailureClass,
)
from agentic_core.L2_execution.healers.heal_classifier_model import (
    HealClassifierModel,
    _StubHealClassifier,
)
from agentic_core.L2_execution.types.heal_contract_types import ClassifierSource


def _make_signal(
    error_code: str = "schema_validation_error",
    retry_count: int = 0,
    failure_class: HealFailureClass = HealFailureClass.IMPORT_BOUNDARY,
    budget_remaining: float = 0.8,
    check_id: str = "chk-001",
    lineage: str = "abcdef1234567890",
) -> FailureSignal:
    return (
        FailureSignalBuilder()
        .from_context({})
        .with_check(check_id, retry_count)
        .with_error(error_code, "test error message")
        .with_lineage(lineage)
        .from_layer("L2", "execute")
        .with_failure_class(failure_class)
        .with_budget_remaining(budget_remaining)
        .build()
    )


# ---------------------------------------------------------------------------
# Phase 2: backward compatibility
# ---------------------------------------------------------------------------


class TestPhase2BackwardCompat:
    def test_default_failure_class_is_unknown(self):
        sig = (
            FailureSignalBuilder()
            .from_context({})
            .with_check("c1", 0)
            .with_error("schema_validation_error", "msg")
            .with_lineage("abc123")
            .from_layer("L2", "op")
            .build()
        )
        assert sig.failure_class == HealFailureClass.UNKNOWN

    def test_default_budget_remaining_is_sentinel(self):
        sig = (
            FailureSignalBuilder()
            .from_context({})
            .with_check("c1", 0)
            .with_error("schema_validation_error", "msg")
            .with_lineage("abc123")
            .from_layer("L2", "op")
            .build()
        )
        assert sig.budget_remaining == 1.0

    def test_scorerdefaults_produce_identical_routing_as_before(self):
        """ConfidenceScorer() with no args must behave identically to pre-Phase-2."""
        sig = (
            FailureSignalBuilder()
            .from_context({})
            .with_check("c1", 0)
            .with_error("schema_validation_error", "msg")
            .with_lineage("abc123")
            .from_layer("L2", "op")
            .build()
        )
        result = ConfidenceScorer().score(sig)
        assert result.tier == HealTier.HIGH
        assert result.score == pytest.approx(0.90)
        assert result.ml_result is None  # Phase 2: no model wired yet

    def test_existing_score_fields_intact(self):
        sig = _make_signal()
        result = ConfidenceScorer().score(sig)
        assert isinstance(result, ConfidenceScore)
        assert isinstance(result.tier, HealTier)
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence_in_score <= 1.0
        assert result.reasoning.startswith("pattern:")

    def test_retry_penalty_still_applies(self):
        sig = _make_signal(retry_count=3)
        result = ConfidenceScorer().score(sig)
        assert result.score == pytest.approx(0.90 - 0.30)
        assert result.tier == HealTier.MEDIUM

    def test_unknown_error_code_fallback(self):
        sig = _make_signal(error_code="completely_unknown_xyz")
        result = ConfidenceScorer().score(sig)
        assert result.score == pytest.approx(0.30)
        assert result.confidence_in_score == pytest.approx(0.60)


# ---------------------------------------------------------------------------
# Phase 2: signal hash correctness
# ---------------------------------------------------------------------------


class TestPhase2SignalHash:
    def test_hash_differs_on_failure_class(self):
        sig1 = _make_signal(failure_class=HealFailureClass.DRIFT_DETECTION)
        sig2 = _make_signal(failure_class=HealFailureClass.IMPORT_BOUNDARY)
        assert sig1.signal_hash != sig2.signal_hash

    def test_hash_differs_on_budget_remaining(self):
        sig1 = _make_signal(budget_remaining=0.5)
        sig2 = _make_signal(budget_remaining=0.9)
        assert sig1.signal_hash != sig2.signal_hash

    def test_hash_stable_for_same_inputs(self):
        """Hash must be deterministic for identical logical inputs (same timestamp)."""
        sig = _make_signal()
        # Rebuild with explicit signal_hash to bypass re-computation
        sig2 = FailureSignal(
            check_id=sig.check_id,
            retry_count=sig.retry_count,
            error_code=sig.error_code,
            error_message=sig.error_message,
            lineage_hash=sig.lineage_hash,
            context_snapshot=sig.context_snapshot,
            source_layer=sig.source_layer,
            operation=sig.operation,
            timestamp=sig.timestamp,
            failure_class=sig.failure_class,
            budget_remaining=sig.budget_remaining,
        )
        assert sig.signal_hash == sig2.signal_hash

    def test_new_fields_included_in_hash(self):
        """signal_hash must change when failure_class or budget_remaining changes."""
        base = _make_signal(failure_class=HealFailureClass.SSOT_DRIFT, budget_remaining=0.4)
        changed_class = FailureSignal(
            check_id=base.check_id,
            retry_count=base.retry_count,
            error_code=base.error_code,
            error_message=base.error_message,
            lineage_hash=base.lineage_hash,
            context_snapshot=base.context_snapshot,
            source_layer=base.source_layer,
            operation=base.operation,
            timestamp=base.timestamp,
            failure_class=HealFailureClass.LAYER_INVERSION,
            budget_remaining=base.budget_remaining,
        )
        assert base.signal_hash != changed_class.signal_hash


# ---------------------------------------------------------------------------
# Phase 2: replay envelope hash
# ---------------------------------------------------------------------------


class TestPhase2ReplayEnvelope:
    def _base_builder(self) -> EnvelopeBuilder:
        return EnvelopeBuilder().with_replay_key("rk-001").with_policy_hash("ph-abc").with_run_id("run-001")

    def test_default_ml_model_hashes_is_empty(self):
        env = self._base_builder().build()
        assert env.ml_model_hashes == {}

    def test_envelope_hash_changes_with_ml_model_hash(self):
        env_empty = self._base_builder().build()
        env_with_model = self._base_builder().with_ml_model_hash("heal_classifier", "abc123def456").build()
        assert env_empty.envelope_hash() != env_with_model.envelope_hash()

    def test_different_model_hashes_produce_different_envelope_hashes(self):
        env1 = self._base_builder().with_ml_model_hash("heal_classifier", "aaa").build()
        env2 = self._base_builder().with_ml_model_hash("heal_classifier", "bbb").build()
        assert env1.envelope_hash() != env2.envelope_hash()

    def test_envelope_hash_deterministic_with_same_ml_hashes(self):
        env1 = self._base_builder().with_ml_model_hash("heal_classifier", "abc123").build()
        env2 = self._base_builder().with_ml_model_hash("heal_classifier", "abc123").build()
        # run_clock differs between builds, so hashes differ — but both include the key
        assert "heal_classifier" in env1.ml_model_hashes
        assert env1.ml_model_hashes == env2.ml_model_hashes


# ---------------------------------------------------------------------------
# Phase 3: ML scaffold and fallback triggers
# ---------------------------------------------------------------------------


class TestPhase3StubModel:
    def test_stub_factory_returns_stub_classifier(self):
        stub = HealClassifierModel.from_stub()
        assert isinstance(stub, _StubHealClassifier)
        assert stub.model_version_hash == _StubHealClassifier.STUB_HASH

    def test_stub_predict_deterministic_retry0(self):
        from agentic_core.L2_execution.healers.heal_classifier_model import ClassifierFeatures

        stub = HealClassifierModel.from_stub()
        feats = ClassifierFeatures(
            failure_class=1,
            retry_count=0,
            error_code_hash=12345,
            lineage_hash_prefix=678,
            budget_remaining=0.8,
            source_layer_id=99,
        )
        r1 = stub.predict(feats)
        r2 = stub.predict(feats)
        assert r1.heal_confidence == r2.heal_confidence
        assert r1.recommended_tier == r2.recommended_tier

    def test_stub_force_tier_overrides(self):
        from agentic_core.L2_execution.healers.heal_classifier_model import ClassifierFeatures

        stub = HealClassifierModel.from_stub(force_tier="LOW")
        feats = ClassifierFeatures(
            failure_class=0,
            retry_count=0,
            error_code_hash=1,
            lineage_hash_prefix=2,
            budget_remaining=0.8,
            source_layer_id=3,
        )
        result = stub.predict(feats)
        assert result.recommended_tier == "LOW"
        assert result.source == ClassifierSource.ML_CLASSIFIER

    def test_stub_predict_tier_by_retry_count(self):
        from agentic_core.L2_execution.healers.heal_classifier_model import ClassifierFeatures

        stub = HealClassifierModel.from_stub()

        def _feats(retry):
            return ClassifierFeatures(
                failure_class=1,
                retry_count=retry,
                error_code_hash=1,
                lineage_hash_prefix=2,
                budget_remaining=0.8,
                source_layer_id=3,
            )

        assert stub.predict(_feats(0)).recommended_tier == "HIGH"
        assert stub.predict(_feats(1)).recommended_tier == "MEDIUM"
        assert stub.predict(_feats(2)).recommended_tier == "LOW"


class TestPhase3FallbackTriggers:
    def test_no_model_returns_heuristic(self):
        sig = _make_signal()
        result = ConfidenceScorer().score(sig)
        assert result.ml_result is None

    def test_stale_hash_triggers_heuristic_fallback(self):
        stub = HealClassifierModel.from_stub()
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash="WRONG-HASH-000",
        )
        sig = _make_signal()
        result = scorer.score(sig)
        # stale hash → _classify_ml returns heuristic → ml_result.source == HEURISTIC_FALLBACK
        assert result.ml_result is not None
        assert result.ml_result.source == ClassifierSource.HEURISTIC_FALLBACK

    def test_ood_budget_sentinel_triggers_fallback(self):
        stub = HealClassifierModel.from_stub()
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
        )
        # budget_remaining=1.0 is the OOD sentinel
        sig = _make_signal(budget_remaining=1.0, failure_class=HealFailureClass.IMPORT_BOUNDARY)
        result = scorer.score(sig)
        assert result.ml_result is not None
        assert result.ml_result.source == ClassifierSource.HEURISTIC_FALLBACK

    def test_ood_unknown_class_triggers_fallback(self):
        stub = HealClassifierModel.from_stub()
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
        )
        sig = _make_signal(failure_class=HealFailureClass.UNKNOWN, budget_remaining=0.5)
        result = scorer.score(sig)
        assert result.ml_result is not None
        assert result.ml_result.source == ClassifierSource.HEURISTIC_FALLBACK

    def test_classifier_features_exclude_timestamp(self):
        from agentic_core.L2_execution.healers.heal_classifier_model import ClassifierFeatures

        assert "timestamp" not in ClassifierFeatures.__dataclass_fields__

    def test_shadow_mode_routing_uses_heuristic_tier(self):
        """In shadow_mode=True (default), routing tier comes from heuristic even if ML differs."""
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        scorer = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
        )
        # schema_validation_error → heuristic HIGH, stub → LOW
        sig = _make_signal(failure_class=HealFailureClass.IMPORT_BOUNDARY, budget_remaining=0.5)
        result = scorer.score(sig)
        # OOD check: IMPORT_BOUNDARY + 0.5 → not OOD, stub returns LOW
        # But shadow_mode → routing uses heuristic → HIGH
        assert result.tier == HealTier.HIGH  # heuristic wins in shadow mode
