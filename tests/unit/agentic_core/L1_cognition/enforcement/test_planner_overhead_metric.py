"""Tests for emit_planner_overhead + emit_from_tracker (ADR-043, W4/P4.2)."""

from __future__ import annotations

import json

import pytest

from agentic_core.L1_cognition.enforcement.planner_budget import (
    PlannerBudget,
    PlannerBudgetTracker,
)
from agentic_core.L1_cognition.enforcement.planner_overhead_metric import (
    EVENT_NAME,
    emit_from_tracker,
    emit_planner_overhead,
)
from agentic_core.L1_cognition.types.plan_contract_types import PlannerTelemetry


def _tel(**over) -> PlannerTelemetry:
    base = dict(refinements_used=0, wall_clock_ms=0, token_usage=0, critic_iterations=0)
    base.update(over)
    return PlannerTelemetry(**base)


class TestEmitPlannerOverhead:
    def test_event_name_is_stable(self):
        assert EVENT_NAME == "planner_overhead_metric"

    def test_minimal_event_shape(self):
        ev = emit_planner_overhead(
            plan_id="plan-1",
            planner_enabled=True,
            telemetry=_tel(refinements_used=2, wall_clock_ms=100, token_usage=500, critic_iterations=3),
        )
        assert ev["event"] == EVENT_NAME
        assert ev["plan_id"] == "plan-1"
        assert ev["planner_enabled"] is True
        assert ev["refinements_used"] == 2
        assert ev["wall_clock_ms"] == 100
        assert ev["token_usage"] == 500
        assert ev["critic_iterations"] == 3
        assert ev["warn_threshold_hit"] is False
        assert ev["outcome_hint"] is None
        assert "budget_fraction" not in ev  # no budget passed

    def test_event_is_json_serializable(self):
        ev = emit_planner_overhead(
            plan_id="plan-x",
            planner_enabled=False,
            telemetry=_tel(token_usage=10),
            outcome_hint="ACCEPT",
        )
        assert json.loads(json.dumps(ev)) == ev

    def test_budget_fraction_included_when_budget_given(self):
        b = PlannerBudget(max_refinements=4, wall_clock_ms_cap=1000, token_cap=2000, max_critic_iterations=8)
        ev = emit_planner_overhead(
            plan_id="p",
            planner_enabled=True,
            telemetry=_tel(refinements_used=2, wall_clock_ms=500, token_usage=1000, critic_iterations=4),
            budget=b,
        )
        frac = ev["budget_fraction"]
        assert frac["refinements"] == 0.5
        assert frac["wall_clock"] == 0.5
        assert frac["tokens"] == 0.5
        assert frac["critic"] == 0.5

    def test_budget_fraction_clamps_to_one(self):
        b = PlannerBudget(max_refinements=1, wall_clock_ms_cap=10, token_cap=10, max_critic_iterations=1)
        ev = emit_planner_overhead(
            plan_id="p",
            planner_enabled=True,
            telemetry=_tel(refinements_used=10, wall_clock_ms=9999, token_usage=9999, critic_iterations=10),
            budget=b,
        )
        frac = ev["budget_fraction"]
        for key in ("refinements", "wall_clock", "tokens", "critic"):
            assert frac[key] == 1.0

    def test_outcome_hint_passes_through(self):
        ev = emit_planner_overhead(
            plan_id="p",
            planner_enabled=True,
            telemetry=_tel(),
            outcome_hint="BUDGET_EXHAUSTED",
        )
        assert ev["outcome_hint"] == "BUDGET_EXHAUSTED"

    def test_warn_threshold_passes_through(self):
        ev = emit_planner_overhead(
            plan_id="p",
            planner_enabled=True,
            telemetry=_tel(),
            warn_threshold_hit=True,
        )
        assert ev["warn_threshold_hit"] is True

    def test_empty_plan_id_rejected(self):
        with pytest.raises(ValueError, match="plan_id"):
            emit_planner_overhead(plan_id="", planner_enabled=True, telemetry=_tel())
        with pytest.raises(ValueError, match="plan_id"):
            emit_planner_overhead(plan_id="  ", planner_enabled=True, telemetry=_tel())

    def test_wrong_telemetry_type_rejected(self):
        with pytest.raises(ValueError, match="telemetry"):
            emit_planner_overhead(
                plan_id="p",
                planner_enabled=True,
                telemetry={"wrong": "type"},  # type: ignore[arg-type]
            )

    def test_wrong_planner_enabled_type_rejected(self):
        with pytest.raises(ValueError, match="planner_enabled"):
            emit_planner_overhead(
                plan_id="p",
                planner_enabled="yes",  # type: ignore[arg-type]
                telemetry=_tel(),
            )


class TestEmitFromTracker:
    def _fake_clock(self, ticks):
        it = iter(ticks)

        def _now():
            try:
                return next(it)
            except StopIteration:
                return ticks[-1]

        return _now

    def test_emit_from_tracker_matches_manual_call(self):
        b = PlannerBudget(token_cap=100, warn_fraction=0.5)
        t = PlannerBudgetTracker(budget=b, clock_ms=self._fake_clock([0, 10, 20, 30]))
        t.record_tokens(80)
        t.record_refinement()
        t.record_critic_pass()

        ev = emit_from_tracker(
            plan_id="p-tracker",
            planner_enabled=True,
            tracker=t,
            outcome_hint="ACCEPT",
        )
        assert ev["plan_id"] == "p-tracker"
        assert ev["token_usage"] == 80
        assert ev["refinements_used"] == 1
        assert ev["critic_iterations"] == 1
        assert ev["outcome_hint"] == "ACCEPT"
        assert ev["warn_threshold_hit"] is True  # 80 >= 0.5 * 100
        assert "budget_fraction" in ev
