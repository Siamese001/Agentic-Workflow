"""Unit tests for apps_lic.engines.ab_variant_engine.

Wave 4.1 — plan adg-testing-hotspots-wave-plan-a7f3c1
Module fan-in: 30.

Purpose: cover the deterministic, decision-only A/B variant surface —
ABVariantConfig (__post_init__ ValueError path), deterministic hash-bucket
assignment (disabled sentinel + arm partitioning), reward clamping in score(),
ABTrafficAccumulator counting/mean/reset, and ABPromotionGate verdicts
(no_data / underpowered / promote). All real instances; AB_VARIANT_ENABLED is
toggled via monkeypatch on the real env. No mocks.
"""

from __future__ import annotations

import pytest

from apps_lic.engines import ab_variant_engine as mod
from apps_lic.engines.ab_variant_engine import (
    ARM_CONTROL,
    ARM_HOLDOUT,
    ARM_TREATMENT,
    MIN_ARM_N_DEFAULT,
    REQUIRES_REAL_TRAFFIC,
    VALID_ARMS,
    VALID_VERDICTS,
    VERDICT_NO_DATA,
    VERDICT_PROMOTE,
    VERDICT_UNDERPOWERED,
    ABPromotionGate,
    ABTrafficAccumulator,
    ABVariantAssignment,
    ABVariantConfig,
    ABVariantEngine,
    ABVariantScore,
    _hash_bucket,
)


@pytest.fixture
def enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AB_VARIANT_ENABLED", "1")


@pytest.fixture
def disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AB_VARIANT_ENABLED", raising=False)


class TestConstants:
    def test_valid_arms(self) -> None:
        assert VALID_ARMS == frozenset({ARM_CONTROL, ARM_TREATMENT, ARM_HOLDOUT})

    def test_valid_verdicts_membership(self) -> None:
        assert VERDICT_PROMOTE in VALID_VERDICTS
        assert VERDICT_UNDERPOWERED in VALID_VERDICTS
        assert VERDICT_NO_DATA in VALID_VERDICTS

    def test_requires_real_traffic_flag(self) -> None:
        assert REQUIRES_REAL_TRAFFIC is True

    def test_min_arm_n_default(self) -> None:
        assert MIN_ARM_N_DEFAULT == 30


class TestHashBucket:
    def test_range(self) -> None:
        for rid in ("a", "b", "req-999", "x" * 50):
            assert 0 <= _hash_bucket(rid) <= 99

    def test_deterministic(self) -> None:
        assert _hash_bucket("req-1") == _hash_bucket("req-1")

    def test_salt_changes_bucket_space(self) -> None:
        # Salt independence: at least one id maps differently with a salt.
        diffs = [
            _hash_bucket(f"req-{i}") != _hash_bucket(f"req-{i}", salt="s")
            for i in range(20)
        ]
        assert any(diffs)


class TestABVariantConfig:
    def test_defaults(self) -> None:
        cfg = ABVariantConfig(experiment_id="exp")
        assert cfg.treatment_pct == 50
        assert cfg.holdout_pct == 10
        assert cfg.salt == ""

    def test_frozen(self) -> None:
        cfg = ABVariantConfig(experiment_id="exp")
        with pytest.raises(Exception):
            cfg.treatment_pct = 99  # type: ignore[misc]

    def test_post_init_rejects_over_100(self) -> None:
        with pytest.raises(ValueError, match=r"> 100"):
            ABVariantConfig(experiment_id="exp", treatment_pct=70, holdout_pct=40)

    def test_post_init_allows_exactly_100(self) -> None:
        cfg = ABVariantConfig(experiment_id="exp", treatment_pct=90, holdout_pct=10)
        assert cfg.treatment_pct + cfg.holdout_pct == 100


class TestAssignDisabled:
    def test_disabled_sentinel(self, disabled: None) -> None:
        engine = ABVariantEngine(config={})
        assignment = engine.assign("req-1", ABVariantConfig(experiment_id="exp"))
        assert assignment.enabled is False
        assert assignment.arm == ARM_CONTROL
        assert assignment.bucket == -1
        assert assignment.experiment_id == "exp"

    def test_disabled_with_no_config(self, disabled: None) -> None:
        engine = ABVariantEngine(config={})
        assignment = engine.assign("req-1")
        assert assignment.enabled is False
        assert assignment.experiment_id == ""


class TestAssignEnabled:
    def test_holdout_assignment(self, enabled: None, monkeypatch: pytest.MonkeyPatch) -> None:
        # Force bucket into holdout band [0, holdout_pct).
        monkeypatch.setattr(mod, "_hash_bucket", lambda *a, **k: 5)
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="exp", treatment_pct=50, holdout_pct=10)
        assert engine.assign("req-1", cfg).arm == ARM_HOLDOUT

    def test_treatment_assignment(self, enabled: None, monkeypatch: pytest.MonkeyPatch) -> None:
        # bucket in [holdout, holdout+treatment) = [10, 60)
        monkeypatch.setattr(mod, "_hash_bucket", lambda *a, **k: 40)
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="exp", treatment_pct=50, holdout_pct=10)
        assert engine.assign("req-1", cfg).arm == ARM_TREATMENT

    def test_control_assignment(self, enabled: None, monkeypatch: pytest.MonkeyPatch) -> None:
        # bucket >= holdout+treatment = 60
        monkeypatch.setattr(mod, "_hash_bucket", lambda *a, **k: 80)
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="exp", treatment_pct=50, holdout_pct=10)
        assert engine.assign("req-1", cfg).arm == ARM_CONTROL

    def test_enabled_default_config_from_policy(self, enabled: None) -> None:
        engine = ABVariantEngine(
            config={
                "default_experiment_id": "polexp",
                "treatment_pct": 50,
                "holdout_pct": 10,
            }
        )
        assignment = engine.assign("req-stable")
        assert assignment.enabled is True
        assert assignment.experiment_id == "polexp"
        assert assignment.arm in VALID_ARMS

    def test_assignment_is_stable(self, enabled: None) -> None:
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="exp")
        a1 = engine.assign("req-stable", cfg)
        a2 = engine.assign("req-stable", cfg)
        assert a1.bucket == a2.bucket
        assert a1.arm == a2.arm


class TestScore:
    def _assignment(self) -> ABVariantAssignment:
        return ABVariantAssignment(
            enabled=True,
            experiment_id="exp",
            request_id="req-1",
            bucket=10,
            arm=ARM_TREATMENT,
        )

    def test_score_passthrough(self) -> None:
        engine = ABVariantEngine(config={})
        score = engine.score(self._assignment(), reward=0.5, outcome_label="opened")
        assert score.reward == 0.5
        assert score.outcome_label == "opened"
        assert score.arm == ARM_TREATMENT

    @pytest.mark.parametrize(
        "raw,clamped",
        [(2.0, 1.0), (-1.0, 0.0), (0.0, 0.0), (1.0, 1.0), (0.3, 0.3)],
    )
    def test_reward_clamped(self, raw: float, clamped: float) -> None:
        engine = ABVariantEngine(config={})
        score = engine.score(self._assignment(), reward=raw)
        assert score.reward == clamped


class TestABTrafficAccumulator:
    def _score(self, arm: str, reward: float, eid: str = "exp") -> ABVariantScore:
        return ABVariantScore(experiment_id=eid, arm=arm, request_id="r", reward=reward)

    def test_counts_and_total(self) -> None:
        acc = ABTrafficAccumulator()
        acc.record(self._score(ARM_CONTROL, 1.0))
        acc.record(self._score(ARM_CONTROL, 0.0))
        acc.record(self._score(ARM_TREATMENT, 1.0))
        assert acc.arm_counts("exp") == {ARM_CONTROL: 2, ARM_TREATMENT: 1}
        assert acc.total_n("exp") == 3

    def test_mean_reward(self) -> None:
        acc = ABTrafficAccumulator()
        acc.record(self._score(ARM_CONTROL, 1.0))
        acc.record(self._score(ARM_CONTROL, 0.0))
        assert acc.arm_mean_reward("exp")[ARM_CONTROL] == 0.5

    def test_unknown_experiment_empty(self) -> None:
        acc = ABTrafficAccumulator()
        assert acc.arm_counts("nope") == {}
        assert acc.total_n("nope") == 0
        assert acc.arm_mean_reward("nope") == {}

    def test_reset_single_experiment(self) -> None:
        acc = ABTrafficAccumulator()
        acc.record(self._score(ARM_CONTROL, 1.0, eid="a"))
        acc.record(self._score(ARM_CONTROL, 1.0, eid="b"))
        acc.reset("a")
        assert acc.total_n("a") == 0
        assert acc.total_n("b") == 1

    def test_reset_all(self) -> None:
        acc = ABTrafficAccumulator()
        acc.record(self._score(ARM_CONTROL, 1.0, eid="a"))
        acc.record(self._score(ARM_CONTROL, 1.0, eid="b"))
        acc.reset()
        assert acc.total_n("a") == 0
        assert acc.total_n("b") == 0


class TestABPromotionGate:
    def _fill(self, acc: ABTrafficAccumulator, arm: str, n: int, eid: str = "exp") -> None:
        for _ in range(n):
            acc.record(ABVariantScore(experiment_id=eid, arm=arm, request_id="r", reward=1.0))

    def test_no_data(self) -> None:
        gate = ABPromotionGate()
        decision = gate.evaluate("exp", ABTrafficAccumulator())
        assert decision.verdict == VERDICT_NO_DATA
        assert decision.requires_real_traffic is REQUIRES_REAL_TRAFFIC
        assert decision.min_n_required == MIN_ARM_N_DEFAULT

    def test_underpowered(self) -> None:
        acc = ABTrafficAccumulator()
        self._fill(acc, ARM_CONTROL, 30)
        self._fill(acc, ARM_TREATMENT, 5)
        decision = ABPromotionGate().evaluate("exp", acc)
        assert decision.verdict == VERDICT_UNDERPOWERED
        assert any("treatment" in r for r in decision.reasons)

    def test_promote(self) -> None:
        acc = ABTrafficAccumulator()
        self._fill(acc, ARM_CONTROL, 30)
        self._fill(acc, ARM_TREATMENT, 30)
        decision = ABPromotionGate().evaluate("exp", acc)
        assert decision.verdict == VERDICT_PROMOTE
        assert decision.arm_counts == {ARM_CONTROL: 30, ARM_TREATMENT: 30}

    def test_custom_min_n_via_config(self) -> None:
        acc = ABTrafficAccumulator()
        self._fill(acc, ARM_CONTROL, 5)
        self._fill(acc, ARM_TREATMENT, 5)
        gate = ABPromotionGate(config={"min_n_per_arm": 5})
        decision = gate.evaluate("exp", acc)
        assert decision.min_n_required == 5
        assert decision.verdict == VERDICT_PROMOTE

    def test_custom_arms_to_compare(self) -> None:
        acc = ABTrafficAccumulator()
        self._fill(acc, ARM_CONTROL, 30)
        self._fill(acc, ARM_HOLDOUT, 30)
        decision = ABPromotionGate().evaluate(
            "exp", acc, arms_to_compare=(ARM_CONTROL, ARM_HOLDOUT)
        )
        assert decision.verdict == VERDICT_PROMOTE
