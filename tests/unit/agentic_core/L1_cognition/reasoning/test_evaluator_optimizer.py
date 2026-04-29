"""Tests for the evaluator-optimizer loop primitive (ADR-043, W3/P3.1).

Covers:
- Accept on first critique
- Escalate on first critique
- Refine once then accept
- Refine until max_refinements → REFINE_EXHAUSTED
- Wall-clock budget exhaustion
- Token budget exhaustion
- Determinism under injected clock
- LoopBudget validation (negative values)
- Telemetry fields map onto PlannerTelemetry shape
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.evaluator_optimizer import (
    Critique,
    DraftResult,
    LoopBudget,
    LoopOutcome,
    run_evaluator_optimizer_loop,
)


def _fake_clock(ticks: list[int]):
    """Return a clock that yields successive values from ``ticks``."""
    it = iter(ticks)

    def _now() -> int:
        try:
            return next(it)
        except StopIteration:
            return ticks[-1]

    return _now


class TestAcceptPath:
    def test_accept_on_first_critique(self):
        calls: list[str] = []

        def draft_fn(prior):
            calls.append(f"draft({prior})")
            return DraftResult(draft={"plan": "v1"}, token_delta=10)

        def critique_fn(draft):
            calls.append(f"critique({draft})")
            return Critique(verdict="accept", reason="looks good", token_delta=5)

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=3, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 10]),
        )
        assert result.outcome == LoopOutcome.ACCEPT
        assert result.refinements_used == 0
        assert result.critic_iterations == 1
        assert result.token_usage == 15
        assert result.final_draft == {"plan": "v1"}
        # draft_fn called exactly once (no refinement).
        assert len([c for c in calls if c.startswith("draft(")]) == 1


class TestEscalatePath:
    def test_escalate_on_first_critique(self):
        def draft_fn(prior):
            return DraftResult(draft="plan-A", token_delta=0)

        def critique_fn(draft):
            return Critique(verdict="escalate", reason="unsafe")

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=5, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 5]),
        )
        assert result.outcome == LoopOutcome.ESCALATE
        assert result.refinements_used == 0


class TestRefinement:
    def test_refine_once_then_accept(self):
        draft_versions = ["v1", "v2"]
        critiques = [
            Critique(verdict="refine", reason="missing step"),
            Critique(verdict="accept", reason="now complete"),
        ]

        def draft_fn(prior):
            return DraftResult(draft=draft_versions.pop(0), token_delta=5)

        def critique_fn(draft):
            return critiques.pop(0)

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=3, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 10, 20, 30]),
        )
        assert result.outcome == LoopOutcome.ACCEPT
        assert result.final_draft == "v2"
        assert result.refinements_used == 1
        assert result.critic_iterations == 2
        assert result.token_usage == 10  # two draft passes @ 5 each

    def test_refine_exhausted_when_max_is_one(self):
        def draft_fn(prior):
            return DraftResult(draft="always-incomplete", token_delta=1)

        def critique_fn(draft):
            return Critique(verdict="refine", reason="still bad")

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=1, wall_clock_ms_cap=60_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 1, 2, 3, 4, 5]),
        )
        assert result.outcome == LoopOutcome.REFINE_EXHAUSTED
        assert result.refinements_used == 1
        assert result.critic_iterations == 2


class TestBudgetCaps:
    def test_wall_clock_exhaustion_returns_budget_exhausted(self):
        def draft_fn(prior):
            return DraftResult(draft="slow", token_delta=0)

        def critique_fn(draft):
            return Critique(verdict="refine", reason="slow")

        # Clock jumps past the 100ms cap after the initial draft+critique.
        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=5, wall_clock_ms_cap=100, token_cap=10_000),
            clock_ms=_fake_clock([0, 10, 500, 600, 700]),
        )
        assert result.outcome == LoopOutcome.BUDGET_EXHAUSTED

    def test_token_exhaustion_returns_budget_exhausted(self):
        def draft_fn(prior):
            # Blow the 50-token cap on the first draft alone.
            return DraftResult(draft="expensive", token_delta=100)

        def critique_fn(draft):
            return Critique(verdict="accept", reason="whatever")

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=3, wall_clock_ms_cap=10_000, token_cap=50),
            clock_ms=_fake_clock([0, 1]),
        )
        assert result.outcome == LoopOutcome.BUDGET_EXHAUSTED


class TestBudgetValidation:
    def test_negative_max_refinements_raises(self):
        with pytest.raises(ValueError, match="max_refinements"):
            LoopBudget(max_refinements=-1, wall_clock_ms_cap=10, token_cap=10)

    def test_negative_wall_clock_raises(self):
        with pytest.raises(ValueError, match="wall_clock"):
            LoopBudget(max_refinements=1, wall_clock_ms_cap=-1, token_cap=10)

    def test_negative_token_cap_raises(self):
        with pytest.raises(ValueError, match="token_cap"):
            LoopBudget(max_refinements=1, wall_clock_ms_cap=10, token_cap=-1)


class TestTelemetryShape:
    def test_loop_result_fields_map_onto_planner_telemetry(self):
        """Fields must align with PlannerTelemetry so emitter can pass through."""
        from agentic_core.L1_cognition.types.plan_contract_types import PlannerTelemetry

        def draft_fn(prior):
            return DraftResult(draft="x", token_delta=3)

        def critique_fn(draft):
            return Critique(verdict="accept", reason="ok", token_delta=1)

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=1, wall_clock_ms_cap=1000, token_cap=1000),
            clock_ms=_fake_clock([0, 25]),
        )
        telemetry = PlannerTelemetry(
            refinements_used=result.refinements_used,
            wall_clock_ms=result.wall_clock_ms,
            token_usage=result.token_usage,
            critic_iterations=result.critic_iterations,
        )
        assert telemetry.refinements_used == 0
        assert telemetry.critic_iterations == 1
        assert telemetry.token_usage == 4
        assert telemetry.wall_clock_ms == 25


class TestHistory:
    def test_history_tracks_each_critique_in_order(self):
        critiques = [
            Critique(verdict="refine", reason="first"),
            Critique(verdict="refine", reason="second"),
            Critique(verdict="accept", reason="third"),
        ]

        def draft_fn(prior):
            return DraftResult(draft="x", token_delta=0)

        def critique_fn(draft):
            return critiques.pop(0)

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=5, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 1, 2, 3, 4, 5, 6, 7]),
        )
        assert result.outcome == LoopOutcome.ACCEPT
        assert len(result.history) == 3
        assert [c.reason for c in result.history] == ["first", "second", "third"]
