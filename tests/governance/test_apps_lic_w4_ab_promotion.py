"""apps_lic calibration-holdout W4 — A/B production promotion tests.

Plan: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W4 DS3-P1

Tests verify:
  - REQUIRES_REAL_TRAFFIC flag is True at module level.
  - MIN_ARM_N_DEFAULT is 30.
  - ABTrafficAccumulator records scores and tracks per-arm counts.
  - ABTrafficAccumulator.arm_mean_reward correct.
  - ABTrafficAccumulator.total_n correct.
  - ABTrafficAccumulator.reset works (per-experiment and all).
  - ABPromotionGate returns VERDICT_NO_DATA when accumulator empty.
  - ABPromotionGate returns VERDICT_UNDERPOWERED when any arm < min_n.
  - ABPromotionGate returns VERDICT_PROMOTE when all arms >= min_n.
  - ABPromotionGate reasons include arm name and counts.
  - ABPromotionGate reasons mention REQUIRES_REAL_TRAFFIC when True.
  - ABPromotionGate respects config min_n_per_arm override.
  - ABPromotionGate never raises.
  - ABPromotionDecision fields complete and frozen.
  - Existing ABVariantEngine assign/score behaviour unchanged.
  - All new names in __all__.
"""

from __future__ import annotations

import pytest


# ===========================================================================
# Module-level flags
# ===========================================================================

class TestModuleFlags:
    def test_requires_real_traffic_is_true(self):
        from apps_lic.engines.ab_variant_engine import REQUIRES_REAL_TRAFFIC
        assert REQUIRES_REAL_TRAFFIC is True

    def test_min_arm_n_default_is_30(self):
        from apps_lic.engines.ab_variant_engine import MIN_ARM_N_DEFAULT
        assert MIN_ARM_N_DEFAULT == 30

    def test_all_new_names_exported(self):
        import apps_lic.engines.ab_variant_engine as m
        for name in (
            "ABTrafficAccumulator",
            "ABPromotionGate",
            "ABPromotionDecision",
            "REQUIRES_REAL_TRAFFIC",
            "MIN_ARM_N_DEFAULT",
            "VERDICT_PROMOTE",
            "VERDICT_UNDERPOWERED",
            "VERDICT_NO_DATA",
            "VERDICT_DISABLED",
            "VALID_VERDICTS",
        ):
            assert name in m.__all__, f"{name} missing from __all__"


# ===========================================================================
# ABTrafficAccumulator
# ===========================================================================

class TestABTrafficAccumulator:
    def _make_score(self, experiment_id, arm, reward=1.0):
        from apps_lic.engines.ab_variant_engine import ABVariantScore
        return ABVariantScore(
            experiment_id=experiment_id,
            arm=arm,
            request_id=f"req-{arm}",
            reward=reward,
        )

    def test_empty_accumulator_arm_counts(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        assert acc.arm_counts("exp1") == {}

    def test_record_increments_count(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        acc.record(self._make_score("exp1", "control"))
        acc.record(self._make_score("exp1", "control"))
        acc.record(self._make_score("exp1", "treatment"))
        counts = acc.arm_counts("exp1")
        assert counts["control"] == 2
        assert counts["treatment"] == 1

    def test_total_n(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        for _ in range(5):
            acc.record(self._make_score("exp1", "control"))
        for _ in range(3):
            acc.record(self._make_score("exp1", "treatment"))
        assert acc.total_n("exp1") == 8
        assert acc.total_n("other") == 0

    def test_arm_mean_reward(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        acc.record(self._make_score("exp1", "control", reward=0.8))
        acc.record(self._make_score("exp1", "control", reward=0.6))
        means = acc.arm_mean_reward("exp1")
        assert abs(means["control"] - 0.7) < 1e-9

    def test_arm_mean_reward_empty_returns_empty(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        assert acc.arm_mean_reward("nope") == {}

    def test_reset_single_experiment(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        acc.record(self._make_score("exp1", "control"))
        acc.record(self._make_score("exp2", "control"))
        acc.reset("exp1")
        assert acc.arm_counts("exp1") == {}
        assert acc.arm_counts("exp2") != {}

    def test_reset_all(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        acc.record(self._make_score("exp1", "control"))
        acc.record(self._make_score("exp2", "treatment"))
        acc.reset()
        assert acc.total_n("exp1") == 0
        assert acc.total_n("exp2") == 0

    def test_separate_experiments_isolated(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator
        acc = ABTrafficAccumulator()
        acc.record(self._make_score("expA", "control"))
        acc.record(self._make_score("expB", "treatment"))
        assert acc.arm_counts("expA") == {"control": 1}
        assert acc.arm_counts("expB") == {"treatment": 1}


# ===========================================================================
# ABPromotionGate — VERDICT_NO_DATA
# ===========================================================================

class TestABPromotionGateNoData:
    def test_empty_accumulator_returns_no_data(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, VERDICT_NO_DATA,
        )
        gate = ABPromotionGate(min_n=30)
        acc = ABTrafficAccumulator()
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_NO_DATA

    def test_no_data_reason_text(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator, ABPromotionGate
        gate = ABPromotionGate(min_n=30)
        acc = ABTrafficAccumulator()
        decision = gate.evaluate("exp1", acc)
        assert len(decision.reasons) >= 1
        assert "no observations" in decision.reasons[0].lower()

    def test_no_data_arm_counts_empty(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator, ABPromotionGate
        gate = ABPromotionGate()
        acc = ABTrafficAccumulator()
        decision = gate.evaluate("exp1", acc)
        assert decision.arm_counts == {}

    def test_no_data_min_n_reflects_gate_config(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator, ABPromotionGate
        gate = ABPromotionGate(min_n=42)
        acc = ABTrafficAccumulator()
        decision = gate.evaluate("exp1", acc)
        assert decision.min_n_required == 42


# ===========================================================================
# ABPromotionGate — VERDICT_UNDERPOWERED
# ===========================================================================

class TestABPromotionGateUnderpowered:
    def _fill_arm(self, acc, experiment_id, arm, n, reward=0.7):
        from apps_lic.engines.ab_variant_engine import ABVariantScore
        for i in range(n):
            acc.record(ABVariantScore(
                experiment_id=experiment_id,
                arm=arm,
                request_id=f"req-{i}",
                reward=reward,
            ))

    def test_one_arm_under_min_n(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_UNDERPOWERED,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 15)   # under min_n
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_UNDERPOWERED

    def test_both_arms_under_min_n(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_UNDERPOWERED,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 5)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 5)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_UNDERPOWERED

    def test_underpowered_reason_contains_arm_name(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ARM_CONTROL, ARM_TREATMENT,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 5)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        reasons_text = " ".join(decision.reasons)
        assert ARM_TREATMENT in reasons_text

    def test_underpowered_reason_contains_n_value(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ARM_CONTROL, ARM_TREATMENT,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 7)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        reasons_text = " ".join(decision.reasons)
        assert "7" in reasons_text

    def test_underpowered_reason_mentions_requires_real_traffic(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ARM_CONTROL, ARM_TREATMENT,
            REQUIRES_REAL_TRAFFIC,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 5)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        if REQUIRES_REAL_TRAFFIC:
            reasons_text = " ".join(decision.reasons)
            assert "REQUIRES_REAL_TRAFFIC" in reasons_text

    def test_underpowered_arm_counts_populated(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ARM_CONTROL, ARM_TREATMENT,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 25)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 10)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert decision.arm_counts[ARM_CONTROL] == 25
        assert decision.arm_counts[ARM_TREATMENT] == 10

    def test_exactly_min_n_minus_1_is_underpowered(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_UNDERPOWERED,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 29)  # 1 short
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_UNDERPOWERED


# ===========================================================================
# ABPromotionGate — VERDICT_PROMOTE
# ===========================================================================

class TestABPromotionGatePromote:
    def _fill_arm(self, acc, experiment_id, arm, n, reward=0.7):
        from apps_lic.engines.ab_variant_engine import ABVariantScore
        for i in range(n):
            acc.record(ABVariantScore(
                experiment_id=experiment_id,
                arm=arm,
                request_id=f"req-{arm}-{i}",
                reward=reward,
            ))

    def test_both_arms_at_min_n_promotes(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_PROMOTE,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 30)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_PROMOTE

    def test_arms_above_min_n_promotes(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_PROMOTE,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 50)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 45)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_PROMOTE

    def test_promote_reason_mentions_min_n(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ARM_CONTROL, ARM_TREATMENT,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 30)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        reasons_text = " ".join(decision.reasons)
        assert "30" in reasons_text

    def test_promote_arm_rewards_present(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ARM_CONTROL, ARM_TREATMENT,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 30, reward=0.6)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 30, reward=0.8)
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc)
        assert abs(decision.arm_rewards[ARM_CONTROL] - 0.6) < 1e-9
        assert abs(decision.arm_rewards[ARM_TREATMENT] - 0.8) < 1e-9

    def test_config_min_n_override(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_PROMOTE,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 10)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 10)
        # Override min_n to 5 via config
        gate = ABPromotionGate(config={"min_n_per_arm": 5})
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_PROMOTE
        assert decision.min_n_required == 5

    def test_config_min_n_underpowered_with_override(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_UNDERPOWERED,
        )
        acc = ABTrafficAccumulator()
        self._fill_arm(acc, "exp1", ARM_CONTROL, 3)
        self._fill_arm(acc, "exp1", ARM_TREATMENT, 3)
        gate = ABPromotionGate(config={"min_n_per_arm": 5})
        decision = gate.evaluate("exp1", acc)
        assert decision.verdict == VERDICT_UNDERPOWERED


# ===========================================================================
# ABPromotionGate — robustness
# ===========================================================================

class TestABPromotionGateRobustness:
    def test_evaluate_never_raises_on_empty(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator, ABPromotionGate
        gate = ABPromotionGate()
        acc = ABTrafficAccumulator()
        try:
            gate.evaluate("bad-exp", acc)
        except Exception as exc:
            pytest.fail(f"evaluate() raised: {exc}")

    def test_requires_real_traffic_surfaces_in_decision(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, REQUIRES_REAL_TRAFFIC,
        )
        gate = ABPromotionGate()
        acc = ABTrafficAccumulator()
        decision = gate.evaluate("exp1", acc)
        assert decision.requires_real_traffic == REQUIRES_REAL_TRAFFIC

    def test_promotion_decision_is_frozen(self):
        from apps_lic.engines.ab_variant_engine import ABTrafficAccumulator, ABPromotionGate
        gate = ABPromotionGate()
        acc = ABTrafficAccumulator()
        decision = gate.evaluate("exp1", acc)
        with pytest.raises((AttributeError, TypeError)):
            decision.verdict = "promote"  # type: ignore[misc]

    def test_custom_arms_to_compare(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ABVariantScore,
            ARM_HOLDOUT, VERDICT_PROMOTE,
        )
        acc = ABTrafficAccumulator()
        for i in range(30):
            acc.record(ABVariantScore("exp1", ARM_HOLDOUT, f"r{i}", 0.5))
        gate = ABPromotionGate(min_n=30)
        # Only evaluate holdout arm
        decision = gate.evaluate("exp1", acc, arms_to_compare=(ARM_HOLDOUT,))
        assert decision.verdict == VERDICT_PROMOTE

    def test_underpowered_when_arm_absent_from_accumulator(self):
        from apps_lic.engines.ab_variant_engine import (
            ABTrafficAccumulator, ABPromotionGate, ABVariantScore,
            ARM_CONTROL, ARM_TREATMENT, VERDICT_UNDERPOWERED,
        )
        acc = ABTrafficAccumulator()
        # Only record control; treatment arm absent
        for i in range(50):
            acc.record(ABVariantScore("exp1", ARM_CONTROL, f"r{i}", 0.7))
        gate = ABPromotionGate(min_n=30)
        decision = gate.evaluate("exp1", acc, arms_to_compare=(ARM_CONTROL, ARM_TREATMENT))
        assert decision.verdict == VERDICT_UNDERPOWERED


# ===========================================================================
# Regression: existing ABVariantEngine behaviour unchanged
# ===========================================================================

class TestABVariantEngineRegression:
    def test_assign_disabled_returns_control(self, monkeypatch):
        monkeypatch.delenv("AB_VARIANT_ENABLED", raising=False)
        from apps_lic.engines.ab_variant_engine import ABVariantEngine, ARM_CONTROL
        engine = ABVariantEngine(config={})
        assignment = engine.assign("req-001")
        assert assignment.enabled is False
        assert assignment.arm == ARM_CONTROL

    def test_assign_enabled_deterministic(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine, ABVariantConfig
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="e1", treatment_pct=50, holdout_pct=10, salt="s")
        a1 = engine.assign("req-stable", cfg)
        a2 = engine.assign("req-stable", cfg)
        assert a1.arm == a2.arm
        assert a1.bucket == a2.bucket

    def test_score_clamps_reward(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine, ABVariantConfig
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="e1")
        assignment = engine.assign("req-x", cfg)
        score = engine.score(assignment, reward=5.0)
        assert score.reward == 1.0
        score2 = engine.score(assignment, reward=-1.0)
        assert score2.reward == 0.0
