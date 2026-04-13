"""Governed activation path tests for the C3 heal-classifier.

Coverage:
  TestActivationCriteria      — criteria checker: all pass, each individual failure, multiple
  TestActivationState         — three-state machine: no record, shadow record, active record,
                                hash mismatch, criteria fail, None dir, malformed record
  TestWireGoverneScorer       — wire_governed_scorer end-to-end activation/mode selection
  TestActiveModeRouting       — active mode ML routing + hard-override fallbacks
  TestRollbackControls        — RollbackMonitor: thresholds, latching, reason capture
  TestGovernedScorerRollback  — GovernedConfidenceScorer fallback after rollback latch
  TestTelemetryActivationMode — telemetry present in both shadow and active mode
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from agentic_core.L2_execution.healers.activation_criteria import (
    ActivationCriteria,
    CriteriaEvidence,
    RollbackMonitor,
    check_activation_criteria,
)
from agentic_core.L2_execution.healers.activation_state import (
    ActivationMode,
    ActivationRecord,
    load_activation_record,
    resolve_activation_mode,
)
from agentic_core.L2_execution.healers.artifact_loader import (
    load_artifact,
    wire_governed_scorer,
)
from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScorer,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import (
    FailureSignalBuilder,
    HealFailureClass,
)
from agentic_core.L2_execution.healers.governed_scorer import GovernedConfidenceScorer
from agentic_core.L2_execution.healers.heal_classifier_model import (
    HealClassifierModel,
)
from agentic_core.L2_execution.types.heal_contract_types import (
    ClassifierSource,
    HealClassifierTelemetry,
)
from tools.heal_classifier.constants import REPAIR_OUTCOME_CLASSES
from tools.heal_classifier.dataset import make_split
from tools.heal_classifier.packager import ArtifactPackager
from tools.heal_classifier.trainer import HealClassifierTrainer, TrainerConfig


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_synthetic_df(n: int = 500, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    outcomes = np.tile(REPAIR_OUTCOME_CLASSES, n // 4 + 1)[:n]
    rng.shuffle(outcomes)
    return pd.DataFrame(
        {
            "run_id": [f"run-{i}" for i in range(n)],
            "signal_hash": [f"sig-{i}" for i in range(n)],
            "failure_class": rng.integers(0, 4, size=n),
            "retry_count": rng.integers(0, 5, size=n),
            "error_code_hash": rng.integers(0, 2**32, size=n).astype(np.int64),
            "lineage_hash_prefix": rng.integers(0, 2**32, size=n).astype(np.int64),
            "budget_remaining": rng.uniform(0.0, 0.9, size=n),
            "source_layer_id": rng.integers(0, 2**32, size=n).astype(np.int64),
            "repair_outcome": outcomes,
            "ood_flag": [False] * n,
            "source": ["ML_CLASSIFIER"] * n,
            "divergence_flag": [True] * n,
            "run_clock": np.arange(n, dtype=float),
        }
    )


def _fast_config() -> TrainerConfig:
    return TrainerConfig(
        n_estimators=10,
        max_depth=2,
        learning_rate=0.1,
        subsample=1.0,
        min_samples_leaf=1,
        random_state=0,
    )


def _valid_evidence(
    shadow_event_count: int = 1000,
    divergence_rate: float = 0.15,
    repair_success_rate: float = 0.75,
    ood_rate: float = 0.005,
    latency_p99_us: int = 200,
    artifact_hash_valid: bool = True,
    replay_binding_present: bool = True,
    manual_review_passed: bool = True,
) -> CriteriaEvidence:
    return CriteriaEvidence(
        shadow_event_count=shadow_event_count,
        divergence_rate=divergence_rate,
        repair_success_rate=repair_success_rate,
        ood_rate=ood_rate,
        latency_p99_us=latency_p99_us,
        artifact_hash_valid=artifact_hash_valid,
        replay_binding_present=replay_binding_present,
        manual_review_passed=manual_review_passed,
    )


def _make_telemetry(
    source: ClassifierSource = ClassifierSource.ML_CLASSIFIER,
    inference_latency_us: int = 100,
    recommended_tier: str = "HIGH",
    mvh: str = "abc1234567890abc",
) -> HealClassifierTelemetry:
    return HealClassifierTelemetry(
        run_id="run-test",
        check_id="chk-test",
        source=source,
        recommended_tier=recommended_tier,
        heal_confidence=0.80,
        ood_flag=False,
        model_version_hash=mvh,
        inference_latency_us=inference_latency_us,
        heuristic_tier="HIGH",
        divergence_flag=False,
    )


def _make_signal(
    retry_count: int = 0,
    error_code: str = "schema_validation_error",
    failure_class: HealFailureClass = HealFailureClass.DRIFT_DETECTION,
    budget_remaining: float = 0.5,
) -> Any:
    return (
        FailureSignalBuilder()
        .with_check("chk-act-001", retry_count)
        .with_error(error_code, "test error")
        .with_lineage("abcd1234ef567890")
        .from_layer("L2", "test_op")
        .with_failure_class(failure_class)
        .with_budget_remaining(budget_remaining)
        .build()
    )


def _write_active_record(artifact_dir: Path, mvh: str, **overrides: Any) -> None:
    record: dict[str, Any] = {
        "activation_mode": "active",
        "artifact_hash": mvh,
        "shadow_event_count": 1000,
        "divergence_rate": 0.15,
        "repair_success_rate": 0.75,
        "ood_rate": 0.005,
        "latency_p99_us": 200,
        "manual_review_passed": True,
        "replay_binding_present": True,
    }
    record.update(overrides)
    (artifact_dir / "activation_record.json").write_text(
        json.dumps(record), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_artifact_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp = tmp_path_factory.mktemp("act_artifact")
    df = _make_synthetic_df()
    split = make_split(df)
    trainer = HealClassifierTrainer(_fast_config())
    result = trainer.train(
        split.X_train, split.y_train,
        split.X_calib, split.y_calib,
        split.X_val, split.y_val,
        list(split.label_encoder.classes_),
        failure_class_train=split.failure_class_train,
        failure_class_val=split.failure_class_val,
    )
    ArtifactPackager().pack(result, tmp)
    return tmp


@pytest.fixture()
def active_artifact_dir(real_artifact_dir: Path, tmp_path: Path) -> Path:
    """Real artifact + valid activation_record.json with mode=active."""
    art = tmp_path / "active_art"
    shutil.copytree(real_artifact_dir, art)
    mvh = (art / "model_version_hash").read_text(encoding="utf-8").strip()
    _write_active_record(art, mvh)
    return art


# ---------------------------------------------------------------------------
# TestActivationCriteria
# ---------------------------------------------------------------------------

class TestActivationCriteria:
    def test_all_criteria_pass(self) -> None:
        result = check_activation_criteria(_valid_evidence())
        assert result.passed
        assert result.failures == []

    def test_shadow_event_count_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(shadow_event_count=10))
        assert not result.passed
        assert any("shadow_event_count" in f for f in result.failures)

    def test_divergence_rate_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(divergence_rate=0.50))
        assert not result.passed
        assert any("divergence_rate" in f for f in result.failures)

    def test_repair_success_rate_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(repair_success_rate=0.40))
        assert not result.passed
        assert any("repair_success_rate" in f for f in result.failures)

    def test_ood_rate_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(ood_rate=0.05))
        assert not result.passed
        assert any("ood_rate" in f for f in result.failures)

    def test_latency_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(latency_p99_us=2000))
        assert not result.passed
        assert any("latency_p99_us" in f for f in result.failures)

    def test_artifact_hash_invalid_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(artifact_hash_valid=False))
        assert not result.passed
        assert any("artifact_hash_valid" in f for f in result.failures)

    def test_replay_binding_missing_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(replay_binding_present=False))
        assert not result.passed
        assert any("replay_binding_present" in f for f in result.failures)

    def test_manual_review_not_passed_fails(self) -> None:
        result = check_activation_criteria(_valid_evidence(manual_review_passed=False))
        assert not result.passed
        assert any("manual_review_passed" in f for f in result.failures)

    def test_multiple_criteria_fail_all_reported(self) -> None:
        result = check_activation_criteria(
            _valid_evidence(shadow_event_count=1, repair_success_rate=0.1)
        )
        assert not result.passed
        assert len(result.failures) >= 2

    def test_custom_criteria_thresholds(self) -> None:
        """Lower min_shadow_events lets a small count pass."""
        strict = ActivationCriteria(min_shadow_events=5000)
        lenient = ActivationCriteria(min_shadow_events=50)

        assert not check_activation_criteria(_valid_evidence(shadow_event_count=100), strict).passed
        assert check_activation_criteria(_valid_evidence(shadow_event_count=100), lenient).passed


# ---------------------------------------------------------------------------
# TestActivationState
# ---------------------------------------------------------------------------

class TestActivationState:
    def test_no_record_returns_shadow(self, tmp_path: Path) -> None:
        mode, result = resolve_activation_mode(tmp_path, "abc123")
        assert mode == ActivationMode.SHADOW
        assert result is None

    def test_shadow_record_returns_shadow(self, tmp_path: Path) -> None:
        (tmp_path / "activation_record.json").write_text(
            json.dumps({"activation_mode": "shadow", "artifact_hash": "abc123"}),
            encoding="utf-8",
        )
        mode, _ = resolve_activation_mode(tmp_path, "abc123")
        assert mode == ActivationMode.SHADOW

    def test_active_record_all_criteria_pass_returns_active(self, tmp_path: Path) -> None:
        mvh = "abc1234567890abc"
        _write_active_record(tmp_path, mvh)
        mode, result = resolve_activation_mode(tmp_path, mvh)
        assert mode == ActivationMode.ACTIVE
        assert result is not None
        assert result.passed

    def test_active_record_hash_mismatch_returns_shadow(self, tmp_path: Path) -> None:
        _write_active_record(tmp_path, "correct_hash_abc1")
        mode, _ = resolve_activation_mode(tmp_path, "different_hash_xy")
        assert mode == ActivationMode.SHADOW

    def test_active_record_criteria_fail_returns_shadow(self, tmp_path: Path) -> None:
        mvh = "abc1234567890abc"
        _write_active_record(tmp_path, mvh, shadow_event_count=5)
        mode, result = resolve_activation_mode(tmp_path, mvh)
        assert mode == ActivationMode.SHADOW
        assert result is not None
        assert not result.passed

    def test_none_dir_returns_absent(self) -> None:
        mode, result = resolve_activation_mode(None, "anyhash")
        assert mode == ActivationMode.ABSENT
        assert result is None

    def test_empty_mvh_returns_shadow_not_absent(self, tmp_path: Path) -> None:
        """Empty mvh (load failed) → SHADOW, not ABSENT, since dir exists."""
        mode, _ = resolve_activation_mode(tmp_path, "")
        assert mode == ActivationMode.SHADOW

    def test_malformed_record_returns_shadow(self, tmp_path: Path) -> None:
        (tmp_path / "activation_record.json").write_text(
            "not valid json {{{{", encoding="utf-8"
        )
        mode, _ = resolve_activation_mode(tmp_path, "somehash")
        assert mode == ActivationMode.SHADOW

    def test_load_activation_record_absent_returns_none(self, tmp_path: Path) -> None:
        assert load_activation_record(tmp_path) is None

    def test_load_activation_record_parses_all_fields(self, tmp_path: Path) -> None:
        mvh = "abc1234567890abc"
        _write_active_record(tmp_path, mvh)
        record = load_activation_record(tmp_path)
        assert record is not None
        assert record.activation_mode == "active"
        assert record.artifact_hash == mvh
        assert record.manual_review_passed is True
        assert record.replay_binding_present is True


# ---------------------------------------------------------------------------
# TestWireGoverneScorer
# ---------------------------------------------------------------------------

class TestWireGoverneScorer:
    def test_no_artifact_returns_absent_mode(self) -> None:
        scorer = wire_governed_scorer(None)
        assert scorer.activation_mode == ActivationMode.ABSENT
        assert scorer._model is None
        assert scorer._shadow_mode is True

    def test_no_record_returns_shadow_mode(self, real_artifact_dir: Path) -> None:
        scorer = wire_governed_scorer(real_artifact_dir)
        assert scorer.activation_mode == ActivationMode.SHADOW
        assert scorer._shadow_mode is True

    def test_active_record_returns_active_mode(
        self, active_artifact_dir: Path
    ) -> None:
        scorer = wire_governed_scorer(active_artifact_dir)
        assert scorer.activation_mode == ActivationMode.ACTIVE
        assert scorer._shadow_mode is False

    def test_active_mode_requires_second_activation_evidence(
        self, real_artifact_dir: Path
    ) -> None:
        """Without activation_record.json, ACTIVE is impossible regardless of artifact."""
        scorer = wire_governed_scorer(real_artifact_dir)
        assert scorer.activation_mode != ActivationMode.ACTIVE

    def test_hash_mismatch_in_record_forces_shadow(
        self, real_artifact_dir: Path, tmp_path: Path
    ) -> None:
        art = tmp_path / "hash_mismatch"
        shutil.copytree(real_artifact_dir, art)
        _write_active_record(art, "wrong_hash_00000000")
        scorer = wire_governed_scorer(art)
        assert scorer.activation_mode == ActivationMode.SHADOW

    def test_failing_criteria_in_record_forces_shadow(
        self, real_artifact_dir: Path, tmp_path: Path
    ) -> None:
        art = tmp_path / "bad_criteria"
        shutil.copytree(real_artifact_dir, art)
        mvh = (art / "model_version_hash").read_text(encoding="utf-8").strip()
        _write_active_record(art, mvh, shadow_event_count=1, repair_success_rate=0.1)
        scorer = wire_governed_scorer(art)
        assert scorer.activation_mode == ActivationMode.SHADOW

    def test_active_mode_sets_shadow_false(
        self, active_artifact_dir: Path
    ) -> None:
        scorer = wire_governed_scorer(active_artifact_dir)
        assert scorer._shadow_mode is False

    def test_active_mode_has_rollback_monitor(
        self, active_artifact_dir: Path
    ) -> None:
        scorer = wire_governed_scorer(active_artifact_dir)
        assert scorer._rollback_monitor is not None

    def test_shadow_mode_has_no_rollback_monitor(
        self, real_artifact_dir: Path
    ) -> None:
        scorer = wire_governed_scorer(real_artifact_dir)
        assert scorer._rollback_monitor is None

    def test_active_mode_expected_hash_bound(
        self, active_artifact_dir: Path
    ) -> None:
        stored = (active_artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
        scorer = wire_governed_scorer(active_artifact_dir)
        assert scorer._expected_model_hash == stored

    def test_active_mode_envelope_bound(
        self, active_artifact_dir: Path
    ) -> None:
        from agentic_core.L2_execution.determinism.replay_envelope import EnvelopeBuilder

        builder = (
            EnvelopeBuilder()
            .with_replay_key("rk")
            .with_policy_hash("ph")
            .with_run_id("rid")
        )
        wire_governed_scorer(active_artifact_dir, envelope_builder=builder)
        envelope = builder.build()
        stored = (active_artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
        assert envelope.ml_model_hashes.get("heal_classifier") == stored


# ---------------------------------------------------------------------------
# TestActiveModeRouting
# ---------------------------------------------------------------------------

class TestActiveModeRouting:
    """Active mode ML routing tests using the deterministic stub model.

    These tests isolate the routing logic from the real trained artifact so
    they do not depend on OOD detection or artifact availability.
    """

    def _make_active_scorer(self, force_tier: str = "LOW") -> GovernedConfidenceScorer:
        """Build a GovernedConfidenceScorer in ACTIVE mode with a stub model."""
        stub = HealClassifierModel.from_stub(force_tier=force_tier)
        inner = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=False,
        )
        return GovernedConfidenceScorer(inner=inner, activation_mode=ActivationMode.ACTIVE)

    def _make_shadow_scorer(self, force_tier: str = "LOW") -> GovernedConfidenceScorer:
        stub = HealClassifierModel.from_stub(force_tier=force_tier)
        inner = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=True,
        )
        return GovernedConfidenceScorer(inner=inner, activation_mode=ActivationMode.SHADOW)

    def test_active_mode_ml_tier_drives_routing(self) -> None:
        """In active mode, ML LOW recommendation overrides heuristic HIGH."""
        scorer = self._make_active_scorer(force_tier="LOW")
        # schema_validation_error, retry=0 → heuristic would say HIGH
        signal = _make_signal(retry_count=0, error_code="schema_validation_error")

        score = scorer.score(signal)
        assert score.tier == HealTier.LOW  # ML wins (force_tier="LOW")

    def test_shadow_mode_heuristic_drives_routing(self) -> None:
        """In shadow mode, heuristic HIGH overrides ML LOW."""
        scorer = self._make_shadow_scorer(force_tier="LOW")
        signal = _make_signal(retry_count=0, error_code="schema_validation_error")

        score = scorer.score(signal)
        assert score.tier == HealTier.HIGH  # Heuristic wins

    def test_active_ml_result_attached_to_score(self) -> None:
        scorer = self._make_active_scorer(force_tier="MEDIUM")
        score = scorer.score(_make_signal())
        assert score.ml_result is not None
        assert score.ml_result.source == ClassifierSource.ML_CLASSIFIER

    def test_active_mode_unknown_failure_class_forces_heuristic(self) -> None:
        """Hard rule: UNKNOWN failure_class → heuristic even in active mode."""
        scorer = self._make_active_scorer(force_tier="LOW")
        signal = _make_signal(
            failure_class=HealFailureClass.UNKNOWN,
            error_code="schema_validation_error",
        )
        score = scorer.score(signal)
        # _classify_ml detects UNKNOWN → returns heuristic result
        # heuristic for schema_validation_error at retry=0 → HIGH
        assert score.tier == HealTier.HIGH

    def test_active_mode_sentinel_budget_forces_heuristic(self) -> None:
        """Hard rule: budget_remaining=1.0 (sentinel) → heuristic even in active mode."""
        scorer = self._make_active_scorer(force_tier="LOW")
        signal = _make_signal(budget_remaining=1.0, error_code="schema_validation_error")
        score = scorer.score(signal)
        # sentinel budget → heuristic HIGH (not ML LOW)
        assert score.tier == HealTier.HIGH

    def test_shadow_ml_result_attached_but_tier_from_heuristic(self) -> None:
        """In shadow mode: ml_result present, but score.tier == heuristic tier."""
        scorer = self._make_shadow_scorer(force_tier="LOW")
        signal = _make_signal(retry_count=0, error_code="schema_validation_error")
        score = scorer.score(signal)

        # Shadow: tier from heuristic
        heuristic = ConfidenceScorer(model=None, shadow_mode=True)
        expected_tier = heuristic.score(signal).tier
        assert score.tier == expected_tier

        # ML result still attached
        assert score.ml_result is not None

    def test_active_mode_high_retry_ml_wins_over_heuristic(self) -> None:
        """In active mode with force_tier=HIGH, ML HIGH overrides heuristic LOW."""
        scorer = self._make_active_scorer(force_tier="HIGH")
        # network_error + retry=4 → heuristic LOW
        signal = _make_signal(retry_count=4, error_code="network_error")

        heuristic = ConfidenceScorer(model=None, shadow_mode=True)
        heuristic_score = heuristic.score(signal)
        assert heuristic_score.tier == HealTier.LOW  # confirm heuristic baseline

        active_score = scorer.score(signal)
        assert active_score.tier == HealTier.HIGH  # ML wins


# ---------------------------------------------------------------------------
# TestRollbackControls
# ---------------------------------------------------------------------------

class TestRollbackControls:
    """Tests for RollbackMonitor in isolation."""

    def _make_monitor(
        self, window_size: int = 20, max_fallback_rate: float = 0.10
    ) -> RollbackMonitor:
        criteria = ActivationCriteria(
            max_fallback_rate=max_fallback_rate,
            max_latency_p99_us=500,
            min_repair_success_rate=0.60,
        )
        return RollbackMonitor(window_size=window_size, criteria=criteria)

    def test_fresh_monitor_no_rollback(self) -> None:
        monitor = self._make_monitor()
        assert monitor.should_rollback() == (False, "")

    def test_insufficient_events_no_rollback(self) -> None:
        monitor = self._make_monitor(window_size=100)
        # min_sample = max(10, 10) = 10; add only 9
        for _ in range(9):
            monitor.record(_make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK))
        assert not monitor.should_rollback()[0]

    def test_high_fallback_rate_triggers_rollback(self) -> None:
        monitor = self._make_monitor(window_size=20, max_fallback_rate=0.10)
        # 10 events, all fallback → 100% > 10%
        for _ in range(10):
            monitor.record(_make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK))
        triggered, reason = monitor.should_rollback()
        assert triggered
        assert "fallback_rate" in reason

    def test_low_fallback_rate_no_rollback(self) -> None:
        monitor = self._make_monitor(window_size=20, max_fallback_rate=0.50)
        # 10 events, 1 fallback → 10% ≤ 50%
        for i in range(10):
            src = ClassifierSource.HEURISTIC_FALLBACK if i == 0 else ClassifierSource.ML_CLASSIFIER
            monitor.record(_make_telemetry(source=src))
        assert not monitor.should_rollback()[0]

    def test_high_latency_p99_triggers_rollback(self) -> None:
        monitor = self._make_monitor(window_size=20)
        # 10 events, all with latency=2000us > max=500us
        for _ in range(10):
            monitor.record(_make_telemetry(inference_latency_us=2000))
        triggered, reason = monitor.should_rollback()
        assert triggered
        assert "latency_p99" in reason

    def test_low_repair_success_triggers_rollback(self) -> None:
        monitor = self._make_monitor(window_size=20)
        # 10 events, all repair_succeeded=False → 0% < 60%
        for _ in range(10):
            monitor.record(_make_telemetry(), repair_succeeded=False)
        triggered, reason = monitor.should_rollback()
        assert triggered
        assert "repair_success" in reason

    def test_good_metrics_no_rollback(self) -> None:
        monitor = self._make_monitor(window_size=20)
        for _ in range(15):
            monitor.record(_make_telemetry(inference_latency_us=100), repair_succeeded=True)
        assert not monitor.should_rollback()[0]

    def test_rollback_latches_permanently(self) -> None:
        monitor = self._make_monitor(window_size=20, max_fallback_rate=0.10)
        # Trigger rollback with 10 fallback events
        for _ in range(10):
            monitor.record(_make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK))
        assert monitor.is_latched

        # Add good events — latch must NOT clear
        for _ in range(100):
            monitor.record(_make_telemetry(source=ClassifierSource.ML_CLASSIFIER), repair_succeeded=True)
        assert monitor.is_latched
        assert monitor.should_rollback()[0]

    def test_rollback_reason_is_captured(self) -> None:
        monitor = self._make_monitor(window_size=20, max_fallback_rate=0.10)
        for _ in range(10):
            monitor.record(_make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK))
        _, reason = monitor.should_rollback()
        assert reason != ""
        assert "fallback_rate" in reason

    def test_stats_returns_window_metrics(self) -> None:
        monitor = self._make_monitor(window_size=20)
        for _ in range(5):
            monitor.record(_make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK))
        s = monitor.stats()
        assert s["n"] == 5
        assert s["fallback_rate"] == 1.0

    def test_record_outcome_feeds_repair_success(self) -> None:
        """repair_succeeded=False consistently triggers repair_success rollback."""
        monitor = self._make_monitor(window_size=20)
        for _ in range(10):
            monitor.record(_make_telemetry(), repair_succeeded=False)
        assert monitor.should_rollback()[0]


# ---------------------------------------------------------------------------
# TestGovernedScorerRollback
# ---------------------------------------------------------------------------

class TestGovernedScorerRollback:
    """Tests for GovernedConfidenceScorer rollback behavior at score() time."""

    def _make_active_scorer_with_monitor(
        self,
        window_size: int = 20,
        max_fallback_rate: float = 0.10,
    ) -> GovernedConfidenceScorer:
        criteria = ActivationCriteria(
            max_fallback_rate=max_fallback_rate,
            max_latency_p99_us=500,
        )
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        inner = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=False,
        )
        monitor = RollbackMonitor(window_size=window_size, criteria=criteria)
        return GovernedConfidenceScorer(
            inner=inner,
            activation_mode=ActivationMode.ACTIVE,
            rollback_monitor=monitor,
        )

    def test_before_rollback_active_ml_routing(self) -> None:
        scorer = self._make_active_scorer_with_monitor()
        signal = _make_signal(retry_count=0, error_code="schema_validation_error")
        score = scorer.score(signal)
        # ML force_tier=LOW wins in active mode (heuristic would be HIGH)
        assert score.tier == HealTier.LOW

    def test_after_rollback_heuristic_routing(self) -> None:
        scorer = self._make_active_scorer_with_monitor(window_size=20)
        # Trigger rollback via 10 fallback telemetry events
        for _ in range(10):
            scorer.record_outcome(
                _make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK)
            )

        assert scorer.is_rolled_back

        signal = _make_signal(retry_count=0, error_code="schema_validation_error")
        score = scorer.score(signal)
        # After rollback: heuristic routing → HIGH for schema_validation_error
        assert score.tier == HealTier.HIGH

    def test_rollback_reason_accessible_on_scorer(self) -> None:
        scorer = self._make_active_scorer_with_monitor(window_size=20)
        assert scorer.rollback_reason == ""
        for _ in range(10):
            scorer.record_outcome(
                _make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK)
            )
        assert "fallback_rate" in scorer.rollback_reason

    def test_shadow_mode_scorer_never_has_rollback_monitor(self) -> None:
        stub = HealClassifierModel.from_stub()
        inner = ConfidenceScorer(model=stub, shadow_mode=True)
        scorer = GovernedConfidenceScorer(inner=inner, activation_mode=ActivationMode.SHADOW)
        assert scorer._rollback_monitor is None
        assert not scorer.is_rolled_back

    def test_absent_mode_no_rollback_monitor(self) -> None:
        inner = ConfidenceScorer(model=None, shadow_mode=True)
        scorer = GovernedConfidenceScorer(inner=inner, activation_mode=ActivationMode.ABSENT)
        assert scorer._rollback_monitor is None

    def test_active_with_latency_rollback(self) -> None:
        """Latency p99 > threshold triggers rollback and forces heuristic routing."""
        criteria = ActivationCriteria(max_latency_p99_us=100, max_fallback_rate=1.0)
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        inner = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=False,
        )
        monitor = RollbackMonitor(window_size=20, criteria=criteria)
        scorer = GovernedConfidenceScorer(
            inner=inner,
            activation_mode=ActivationMode.ACTIVE,
            rollback_monitor=monitor,
        )

        # Inject 10 high-latency ML events
        for _ in range(10):
            scorer.record_outcome(_make_telemetry(inference_latency_us=5000))

        assert scorer.is_rolled_back

        signal = _make_signal(retry_count=0, error_code="schema_validation_error")
        assert scorer.score(signal).tier == HealTier.HIGH

    def test_active_with_repair_success_rollback(self) -> None:
        """Low repair success triggers rollback."""
        criteria = ActivationCriteria(min_repair_success_rate=0.80, max_fallback_rate=1.0)
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        inner = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=False,
        )
        monitor = RollbackMonitor(window_size=20, criteria=criteria)
        scorer = GovernedConfidenceScorer(
            inner=inner,
            activation_mode=ActivationMode.ACTIVE,
            rollback_monitor=monitor,
        )

        for _ in range(10):
            scorer.record_outcome(_make_telemetry(), repair_succeeded=False)

        assert scorer.is_rolled_back
        signal = _make_signal(retry_count=0, error_code="schema_validation_error")
        assert scorer.score(signal).tier == HealTier.HIGH


# ---------------------------------------------------------------------------
# TestTelemetryActivationMode
# ---------------------------------------------------------------------------

class TestTelemetryActivationMode:
    def test_active_mode_emits_telemetry_on_score(
        self, active_artifact_dir: Path
    ) -> None:
        events: list[HealClassifierTelemetry] = []
        scorer = wire_governed_scorer(
            active_artifact_dir,
            run_id="run-act-tel",
            telemetry_sink=events.append,
        )
        assert scorer.activation_mode == ActivationMode.ACTIVE
        signal = _make_signal()
        scorer.score(signal)
        assert len(events) == 1

    def test_shadow_mode_emits_telemetry_unchanged(
        self, real_artifact_dir: Path
    ) -> None:
        events: list[HealClassifierTelemetry] = []
        scorer = wire_governed_scorer(
            real_artifact_dir,
            run_id="run-shad-tel",
            telemetry_sink=events.append,
        )
        assert scorer.activation_mode == ActivationMode.SHADOW
        signal = _make_signal()
        scorer.score(signal)
        assert len(events) == 1

    def test_after_rollback_no_ml_telemetry_emitted(self) -> None:
        """After rollback, _heuristic_fallback scorer has no sink → no telemetry."""
        events: list[HealClassifierTelemetry] = []
        stub = HealClassifierModel.from_stub(force_tier="LOW")
        inner = ConfidenceScorer(
            model=stub,
            expected_model_hash=stub.model_version_hash,
            shadow_mode=False,
            telemetry_sink=events.append,
        )
        criteria = ActivationCriteria(max_fallback_rate=0.05)
        monitor = RollbackMonitor(window_size=20, criteria=criteria)
        scorer = GovernedConfidenceScorer(
            inner=inner,
            activation_mode=ActivationMode.ACTIVE,
            rollback_monitor=monitor,
        )

        # Trigger rollback
        for _ in range(10):
            scorer.record_outcome(
                _make_telemetry(source=ClassifierSource.HEURISTIC_FALLBACK)
            )
        assert scorer.is_rolled_back

        # Score after rollback — heuristic_fallback has no sink → no new events
        pre_count = len(events)
        scorer.score(_make_signal())
        assert len(events) == pre_count

    def test_active_telemetry_run_id_bound(
        self, active_artifact_dir: Path
    ) -> None:
        events: list[HealClassifierTelemetry] = []
        scorer = wire_governed_scorer(
            active_artifact_dir,
            run_id="run-id-check",
            telemetry_sink=events.append,
        )
        scorer.score(_make_signal())
        assert events[0].run_id == "run-id-check"

    def test_activation_mode_reported_by_scorer(
        self, active_artifact_dir: Path
    ) -> None:
        scorer = wire_governed_scorer(active_artifact_dir)
        assert scorer.activation_mode == ActivationMode.ACTIVE

    def test_shadow_activation_mode_reported_by_scorer(
        self, real_artifact_dir: Path
    ) -> None:
        scorer = wire_governed_scorer(real_artifact_dir)
        assert scorer.activation_mode == ActivationMode.SHADOW
