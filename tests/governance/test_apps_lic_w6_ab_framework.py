"""apps_lic W6 (D5) — A/B variant framework sentinel tests.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-deferred-scope-followup-d3f9b2.md W6 D5-P1, D5-P2, D5-P3

Coverage:
  D5-P1 ABVariantEngine:
    - Config file presence and schema
    - Disabled sentinel when AB_VARIANT_ENABLED unset
    - Deterministic assignment (same request_id → same arm)
    - Correct arm split (treatment / control / holdout bands)
    - ABVariantConfig total pct > 100 raises
    - ABVariantAssignment shape + immutability
    - ABVariantScore clamping (reward outside [0,1])
    - score() builds correct record from assignment
  D5-P2 variant_promotion_gate:
    - VariantPromotionVerdict shape + immutability
    - Insufficient sample → no-promote
    - High treatment success rate → promote
    - promote property delegates to inner verdict
    - experiment_id and arm labels preserved
  D5-P3 per-variant regret:
    - VariantRegretSample shape + immutability
    - record_variant_regret feeds RegretLedger
    - aggregate_variant_regret groups by experiment + arm
    - Zero regret when chosen == best_alternative
    - Non-negative regret invariant
"""

from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError


# ===========================================================================
# D5-P1: ABVariantEngine
# ===========================================================================

class TestABVariantConfig:
    def test_config_file_exists(self):
        from pathlib import Path
        cfg = (
            Path(__file__).parent.parent.parent
            / "apps_lic" / "config" / "ab_variant_policy.yaml"
        )
        assert cfg.exists(), f"ab_variant_policy.yaml missing at {cfg}"

    def test_config_has_required_keys(self):
        from pathlib import Path
        import yaml
        cfg = yaml.safe_load(
            open(Path(__file__).parent.parent.parent / "apps_lic" / "config" / "ab_variant_policy.yaml")
        )
        assert "treatment_pct" in cfg
        assert "holdout_pct" in cfg
        assert "default_experiment_id" in cfg

    def test_total_exceeds_100_raises(self):
        from apps_lic.engines.ab_variant_engine import ABVariantConfig
        with pytest.raises(ValueError, match="100"):
            ABVariantConfig(experiment_id="x", treatment_pct=80, holdout_pct=30)

    def test_valid_config_constructs(self):
        from apps_lic.engines.ab_variant_engine import ABVariantConfig
        cfg = ABVariantConfig(experiment_id="test", treatment_pct=50, holdout_pct=10)
        assert cfg.treatment_pct == 50
        assert cfg.holdout_pct == 10


class TestABVariantEngineDisabled:
    def test_disabled_without_env_var(self, monkeypatch):
        monkeypatch.delenv("AB_VARIANT_ENABLED", raising=False)
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        engine = ABVariantEngine(config={})
        result = engine.assign("req-001")
        assert result.enabled is False
        assert result.arm == "control"
        assert result.bucket == -1

    def test_disabled_experiment_id_preserved(self, monkeypatch):
        monkeypatch.delenv("AB_VARIANT_ENABLED", raising=False)
        from apps_lic.engines.ab_variant_engine import ABVariantEngine, ABVariantConfig
        engine = ABVariantEngine(config={})
        cfg = ABVariantConfig(experiment_id="my-exp")
        result = engine.assign("req-001", variant_config=cfg)
        assert result.experiment_id == "my-exp"


class TestABVariantEngineEnabled:
    def _engine(self):
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        return ABVariantEngine(config={
            "default_experiment_id": "test_exp",
            "treatment_pct": 50,
            "holdout_pct": 10,
            "salt": "",
        })

    def test_enabled_returns_enabled_true(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        result = self._engine().assign("req-001")
        assert result.enabled is True

    def test_deterministic_same_request_same_arm(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        engine = self._engine()
        r1 = engine.assign("req-stable")
        r2 = engine.assign("req-stable")
        assert r1.arm == r2.arm
        assert r1.bucket == r2.bucket

    def test_different_requests_may_differ(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        engine = self._engine()
        arms = {engine.assign(f"req-{i}").arm for i in range(200)}
        assert len(arms) > 1, "200 requests should produce at least 2 distinct arms"

    def test_bucket_in_range(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        engine = self._engine()
        for i in range(50):
            r = engine.assign(f"req-{i}")
            assert 0 <= r.bucket <= 99

    def test_holdout_arm_in_low_bucket(self, monkeypatch):
        from apps_lic.engines.ab_variant_engine import ABVariantConfig, _hash_bucket
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        # Find a request_id that hashes to bucket < 10 (holdout)
        engine = self._engine()
        cfg = ABVariantConfig(experiment_id="e", treatment_pct=50, holdout_pct=10, salt="")
        for i in range(1000):
            rid = f"holdout-probe-{i}"
            if _hash_bucket(rid, "") < 10:
                result = engine.assign(rid, variant_config=cfg)
                assert result.arm == "holdout"
                return
        pytest.skip("no bucket < 10 found in 1000 probes")

    def test_treatment_arm_assignment(self, monkeypatch):
        from apps_lic.engines.ab_variant_engine import ABVariantConfig, _hash_bucket, ARM_TREATMENT
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        engine = self._engine()
        cfg = ABVariantConfig(experiment_id="e", treatment_pct=50, holdout_pct=10, salt="")
        for i in range(1000):
            rid = f"treat-probe-{i}"
            b = _hash_bucket(rid, "")
            if 10 <= b < 60:
                result = engine.assign(rid, variant_config=cfg)
                assert result.arm == ARM_TREATMENT
                return
        pytest.skip("no treatment bucket found in 1000 probes")

    def test_control_arm_assignment(self, monkeypatch):
        from apps_lic.engines.ab_variant_engine import ABVariantConfig, _hash_bucket, ARM_CONTROL
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        engine = self._engine()
        cfg = ABVariantConfig(experiment_id="e", treatment_pct=50, holdout_pct=10, salt="")
        for i in range(1000):
            rid = f"ctrl-probe-{i}"
            b = _hash_bucket(rid, "")
            if b >= 60:
                result = engine.assign(rid, variant_config=cfg)
                assert result.arm == ARM_CONTROL
                return
        pytest.skip("no control bucket found in 1000 probes")


class TestABVariantAssignmentShape:
    def test_assignment_is_immutable(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        result = ABVariantEngine(config={}).assign("req-x")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.arm = "tampered"  # type: ignore

    def test_required_fields_present(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        r = ABVariantEngine(config={}).assign("req-x")
        for f in ("enabled", "experiment_id", "request_id", "bucket", "arm"):
            assert hasattr(r, f)


class TestABVariantScore:
    def test_reward_clamped_below_zero(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        engine = ABVariantEngine(config={})
        assignment = engine.assign("req-x")
        score = engine.score(assignment, reward=-0.5, outcome_label="bad")
        assert score.reward == 0.0

    def test_reward_clamped_above_one(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        engine = ABVariantEngine(config={})
        assignment = engine.assign("req-x")
        score = engine.score(assignment, reward=1.5)
        assert score.reward == 1.0

    def test_score_mirrors_assignment(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        engine = ABVariantEngine(config={})
        assignment = engine.assign("req-y")
        score = engine.score(assignment, reward=0.8, outcome_label="opened")
        assert score.arm == assignment.arm
        assert score.experiment_id == assignment.experiment_id
        assert score.request_id == "req-y"
        assert score.outcome_label == "opened"

    def test_score_is_immutable(self, monkeypatch):
        monkeypatch.setenv("AB_VARIANT_ENABLED", "1")
        from apps_lic.engines.ab_variant_engine import ABVariantEngine
        score = ABVariantEngine(config={}).score(
            ABVariantEngine(config={}).assign("req-z"), reward=0.5
        )
        with pytest.raises((FrozenInstanceError, AttributeError)):
            score.reward = 99.9  # type: ignore


# ===========================================================================
# D5-P2: variant_promotion_gate
# ===========================================================================

class TestVariantPromotionGate:
    def _gate(self, *, treatment_scores, control_scores, min_n=30):
        from agentic_core.L6_observability.promotion_gates import variant_promotion_gate
        return variant_promotion_gate(
            experiment_id="test-exp",
            treatment_scores=treatment_scores,
            control_scores=control_scores,
            min_n_each_arm=min_n,
        )

    def test_insufficient_sample_no_promote(self):
        result = self._gate(treatment_scores=[1.0] * 5, control_scores=[0.0] * 5, min_n=30)
        assert result.promote is False
        assert "insufficient" in result.reason.lower()

    def test_dominant_treatment_promotes(self):
        result = self._gate(
            treatment_scores=[1.0] * 50,
            control_scores=[0.0] * 50,
            min_n=30,
        )
        assert result.promote is True

    def test_equal_arms_no_promote(self):
        result = self._gate(
            treatment_scores=[0.5] * 50,
            control_scores=[0.5] * 50,
            min_n=30,
        )
        assert result.promote is False

    def test_verdict_shape_immutable(self):
        result = self._gate(
            treatment_scores=[0.8] * 50,
            control_scores=[0.5] * 50,
            min_n=30,
        )
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.experiment_id = "tampered"  # type: ignore

    def test_experiment_id_preserved(self):
        from agentic_core.L6_observability.promotion_gates import variant_promotion_gate
        result = variant_promotion_gate(
            experiment_id="my-unique-exp-99",
            treatment_scores=[1.0] * 5,
            control_scores=[0.5] * 5,
            min_n_each_arm=3,
        )
        assert result.experiment_id == "my-unique-exp-99"

    def test_arm_labels_preserved(self):
        from agentic_core.L6_observability.promotion_gates import variant_promotion_gate
        result = variant_promotion_gate(
            experiment_id="e",
            treatment_scores=[1.0] * 40,
            control_scores=[0.0] * 40,
            treatment_arm="arc_v2",
            control_arm="baseline",
            min_n_each_arm=30,
        )
        assert result.treatment_arm == "arc_v2"
        assert result.control_arm == "baseline"

    def test_promote_property_delegates(self):
        from agentic_core.L6_observability.promotion_gates import variant_promotion_gate
        result = variant_promotion_gate(
            experiment_id="e",
            treatment_scores=[1.0] * 50,
            control_scores=[0.0] * 50,
            min_n_each_arm=30,
        )
        assert result.promote == result.verdict.promote

    def test_variant_promotion_verdict_in_all(self):
        from agentic_core.L6_observability import promotion_gates
        assert "VariantPromotionVerdict" in promotion_gates.__all__
        assert "variant_promotion_gate" in promotion_gates.__all__


# ===========================================================================
# D5-P3: per-variant regret
# ===========================================================================

class TestVariantRegretSample:
    def _sample(self):
        from agentic_core.L6_observability.regret_accounting import (
            RegretLedger, record_variant_regret,
        )
        ledger = RegretLedger()
        return record_variant_regret(
            ledger,
            decision_id="d-001",
            decision_layer="L0_routing",
            chosen_reward=0.6,
            best_alternative_reward=0.8,
            experiment_id="exp-1",
            arm="treatment",
        )

    def test_returns_variant_regret_sample(self):
        from agentic_core.L6_observability.regret_accounting import VariantRegretSample
        assert isinstance(self._sample(), VariantRegretSample)

    def test_sample_is_immutable(self):
        s = self._sample()
        with pytest.raises((FrozenInstanceError, AttributeError)):
            s.arm = "tampered"  # type: ignore

    def test_regret_positive_when_chosen_less_than_best(self):
        s = self._sample()
        assert s.regret > 0.0

    def test_regret_zero_when_chosen_equals_best(self):
        from agentic_core.L6_observability.regret_accounting import RegretLedger, record_variant_regret
        ledger = RegretLedger()
        s = record_variant_regret(
            ledger,
            decision_id="d-002",
            decision_layer="L0_routing",
            chosen_reward=0.8,
            best_alternative_reward=0.8,
            experiment_id="exp-1",
            arm="control",
        )
        assert s.regret == 0.0

    def test_regret_non_negative_invariant(self):
        from agentic_core.L6_observability.regret_accounting import RegretLedger, record_variant_regret
        ledger = RegretLedger()
        s = record_variant_regret(
            ledger,
            decision_id="d-003",
            decision_layer="L1_reasoning",
            chosen_reward=0.9,
            best_alternative_reward=0.5,  # chosen is better
            experiment_id="exp-2",
            arm="holdout",
        )
        assert s.regret >= 0.0

    def test_feeds_ledger(self):
        from agentic_core.L6_observability.regret_accounting import RegretLedger, record_variant_regret
        ledger = RegretLedger()
        assert ledger.total_regret() == 0.0
        record_variant_regret(
            ledger,
            decision_id="d-004",
            decision_layer="L0_routing",
            chosen_reward=0.4,
            best_alternative_reward=0.9,
            experiment_id="exp-3",
            arm="treatment",
        )
        assert ledger.total_regret() > 0.0

    def test_experiment_id_and_arm_preserved(self):
        s = self._sample()
        assert s.experiment_id == "exp-1"
        assert s.arm == "treatment"

    def test_decision_layer_delegated(self):
        s = self._sample()
        assert s.decision_layer == "L0_routing"


class TestAggregateVariantRegret:
    def test_groups_by_experiment_and_arm(self):
        from agentic_core.L6_observability.regret_accounting import (
            RegretLedger, record_variant_regret, aggregate_variant_regret,
        )
        ledger = RegretLedger()
        samples = []
        for i, arm in enumerate(["treatment", "control", "treatment"]):
            s = record_variant_regret(
                ledger,
                decision_id=f"d-{i}",
                decision_layer="L0_routing",
                chosen_reward=0.5,
                best_alternative_reward=0.8,
                experiment_id="exp-A",
                arm=arm,
            )
            samples.append(s)
        agg = aggregate_variant_regret(samples)
        assert "exp-A" in agg
        assert "treatment" in agg["exp-A"]
        assert "control" in agg["exp-A"]

    def test_empty_list_returns_empty_dict(self):
        from agentic_core.L6_observability.regret_accounting import aggregate_variant_regret
        assert aggregate_variant_regret([]) == {}

    def test_mean_regret_correct(self):
        from agentic_core.L6_observability.regret_accounting import (
            RegretLedger, record_variant_regret, aggregate_variant_regret,
        )
        ledger = RegretLedger()
        samples = [
            record_variant_regret(
                ledger,
                decision_id=f"d-{i}",
                decision_layer="L0_routing",
                chosen_reward=0.0,
                best_alternative_reward=1.0,  # regret = 1.0 each
                experiment_id="exp-B",
                arm="treatment",
            )
            for i in range(4)
        ]
        agg = aggregate_variant_regret(samples)
        assert abs(agg["exp-B"]["treatment"] - 1.0) < 1e-9

    def test_variant_regret_in_all(self):
        from agentic_core.L6_observability import regret_accounting
        assert "VariantRegretSample" in regret_accounting.__all__
        assert "record_variant_regret" in regret_accounting.__all__
        assert "aggregate_variant_regret" in regret_accounting.__all__
