"""Tests for PlannerBudget + PlannerBudgetTracker (ADR-043, W4/P4.1)."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.enforcement.planner_budget import (
    BudgetExhausted,
    PlannerBudget,
    PlannerBudgetTracker,
)


def _fake_clock(ticks: list[int]):
    it = iter(ticks)

    def _now() -> int:
        try:
            return next(it)
        except StopIteration:
            return ticks[-1]

    return _now


class TestPlannerBudget:
    def test_defaults_valid(self):
        b = PlannerBudget()
        assert b.max_refinements == 3
        assert b.wall_clock_ms_cap == 60_000
        assert b.token_cap == 50_000
        assert b.max_critic_iterations == 6
        assert b.warn_fraction == 0.80

    def test_custom_values_valid(self):
        b = PlannerBudget(
            max_refinements=5,
            wall_clock_ms_cap=1000,
            token_cap=500,
            max_critic_iterations=10,
            warn_fraction=0.5,
        )
        assert b.max_refinements == 5

    def test_negative_caps_rejected(self):
        with pytest.raises(ValueError, match="max_refinements"):
            PlannerBudget(max_refinements=-1)
        with pytest.raises(ValueError, match="wall_clock_ms_cap"):
            PlannerBudget(wall_clock_ms_cap=-1)
        with pytest.raises(ValueError, match="token_cap"):
            PlannerBudget(token_cap=-1)
        with pytest.raises(ValueError, match="max_critic_iterations"):
            PlannerBudget(max_critic_iterations=-1)

    def test_warn_fraction_out_of_range(self):
        with pytest.raises(ValueError, match="warn_fraction"):
            PlannerBudget(warn_fraction=1.5)
        with pytest.raises(ValueError, match="warn_fraction"):
            PlannerBudget(warn_fraction=-0.1)


class TestPlannerBudgetTracker:
    def test_initial_snapshot_is_zeroed(self):
        t = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 0]))
        snap = t.snapshot()
        assert snap["refinements_used"] == 0
        assert snap["wall_clock_ms"] == 0
        assert snap["token_usage"] == 0
        assert snap["critic_iterations"] == 0

    def test_records_accumulate(self):
        t = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 50]))
        t.record_tokens(100)
        t.record_tokens(50)
        t.record_refinement()
        t.record_critic_pass()
        t.record_critic_pass()
        snap = t.snapshot()
        assert snap["token_usage"] == 150
        assert snap["refinements_used"] == 1
        assert snap["critic_iterations"] == 2
        assert snap["wall_clock_ms"] == 50

    def test_record_tokens_rejects_negative(self):
        t = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0]))
        with pytest.raises(ValueError):
            t.record_tokens(-1)

    def test_require_remaining_ok_under_caps(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(max_refinements=3, token_cap=1000),
            clock_ms=_fake_clock([0, 10, 20]),
        )
        t.record_tokens(500)
        t.record_refinement()
        t.require_remaining()  # not exhausted

    def test_require_remaining_raises_on_refinement_cap(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(max_refinements=1),
            clock_ms=_fake_clock([0, 1, 2]),
        )
        t.record_refinement()
        with pytest.raises(BudgetExhausted, match="max_refinements"):
            t.require_remaining()

    def test_require_remaining_raises_on_critic_cap(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(max_critic_iterations=1),
            clock_ms=_fake_clock([0, 1]),
        )
        t.record_critic_pass()
        with pytest.raises(BudgetExhausted, match="max_critic_iterations"):
            t.require_remaining()

    def test_require_remaining_raises_on_wall_clock(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(wall_clock_ms_cap=100),
            clock_ms=_fake_clock([0, 200, 300]),
        )
        with pytest.raises(BudgetExhausted, match="wall_clock"):
            t.require_remaining()

    def test_require_remaining_raises_on_tokens(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(token_cap=100),
            clock_ms=_fake_clock([0, 1, 2]),
        )
        t.record_tokens(100)
        with pytest.raises(BudgetExhausted, match="tokens"):
            t.require_remaining()

    def test_warn_threshold_fires_once(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(token_cap=100, warn_fraction=0.8),
            clock_ms=_fake_clock([0, 1, 2, 3]),
        )
        assert t.warn_threshold_hit() is False
        t.record_tokens(79)
        assert t.warn_threshold_hit() is False
        t.record_tokens(1)  # 80 / 100 = 0.80 exactly
        assert t.warn_threshold_hit() is True
        # Idempotent — stays True
        assert t.warn_threshold_hit() is True

    def test_warn_fraction_zero_disables_warning(self):
        t = PlannerBudgetTracker(
            budget=PlannerBudget(token_cap=100, warn_fraction=0.0),
            clock_ms=_fake_clock([0, 1]),
        )
        t.record_tokens(99)
        assert t.warn_threshold_hit() is False

    def test_snapshot_matches_planner_telemetry_shape(self):
        from agentic_core.L1_cognition.types.plan_contract_types import PlannerTelemetry

        t = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 42]))
        t.record_tokens(200)
        t.record_refinement()
        t.record_critic_pass()
        tel = PlannerTelemetry(**t.snapshot())
        assert tel.token_usage == 200
        assert tel.refinements_used == 1
        assert tel.critic_iterations == 1
        assert tel.wall_clock_ms == 42
