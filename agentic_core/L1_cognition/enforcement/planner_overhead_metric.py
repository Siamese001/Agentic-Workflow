"""Planner-overhead metric emitter (ADR-043, W4/P4.2).

Pure emitter.  Returns a JSON-safe event dict that any OTel /
meta-observability consumer can ingest; does NOT perform I/O itself, so the
primitive remains deterministic and unit-testable.
"""

from __future__ import annotations

from typing import Any, Optional

from agentic_core.L1_cognition.enforcement.planner_budget import (
    PlannerBudget,
    PlannerBudgetTracker,
)
from agentic_core.L1_cognition.types.plan_contract_types import PlannerTelemetry


EVENT_NAME: str = "planner_overhead_metric"


def emit_planner_overhead(
    *,
    plan_id: str,
    planner_enabled: bool,
    telemetry: PlannerTelemetry,
    budget: Optional[PlannerBudget] = None,
    warn_threshold_hit: bool = False,
    outcome_hint: Optional[str] = None,
) -> dict[str, Any]:
    """Build the planner-overhead event dict.

    Args:
        plan_id: L1PlanContractV2.plan_id for correlation with trace.
        planner_enabled: True if this sample represents a planner-on run.
        telemetry: The :class:`PlannerTelemetry` captured during planning.
        budget: Optional :class:`PlannerBudget`.  When present, the event
            carries normalized ``budget_fraction`` fields.
        warn_threshold_hit: Pass-through soft-warn observation.
        outcome_hint: Optional string like ``"ACCEPT"`` / ``"REFINE_EXHAUSTED"``.

    Returns:
        JSON-safe dict.
    """
    if not isinstance(plan_id, str) or not plan_id.strip():
        raise ValueError("plan_id must be a non-empty string.")
    if not isinstance(planner_enabled, bool):
        raise ValueError(f"planner_enabled must be bool, got {type(planner_enabled)!r}")
    if not isinstance(telemetry, PlannerTelemetry):
        raise ValueError(f"telemetry must be PlannerTelemetry, got {type(telemetry)!r}")

    event: dict[str, Any] = {
        "event": EVENT_NAME,
        "plan_id": plan_id,
        "planner_enabled": planner_enabled,
        "refinements_used": int(telemetry.refinements_used),
        "wall_clock_ms": int(telemetry.wall_clock_ms),
        "token_usage": int(telemetry.token_usage),
        "critic_iterations": int(telemetry.critic_iterations),
        "warn_threshold_hit": bool(warn_threshold_hit),
        "outcome_hint": outcome_hint,
    }

    if budget is not None:
        event["budget_fraction"] = {
            "refinements": _fraction(telemetry.refinements_used, budget.max_refinements),
            "wall_clock": _fraction(telemetry.wall_clock_ms, budget.wall_clock_ms_cap),
            "tokens": _fraction(telemetry.token_usage, budget.token_cap),
            "critic": _fraction(telemetry.critic_iterations, budget.max_critic_iterations),
        }

    return event


def emit_from_tracker(
    *,
    plan_id: str,
    planner_enabled: bool,
    tracker: PlannerBudgetTracker,
    outcome_hint: Optional[str] = None,
) -> dict[str, Any]:
    """Convenience: build the event directly from a tracker snapshot."""
    snap = tracker.snapshot()
    telemetry = PlannerTelemetry(
        refinements_used=snap["refinements_used"],
        wall_clock_ms=snap["wall_clock_ms"],
        token_usage=snap["token_usage"],
        critic_iterations=snap["critic_iterations"],
    )
    return emit_planner_overhead(
        plan_id=plan_id,
        planner_enabled=planner_enabled,
        telemetry=telemetry,
        budget=tracker.budget,
        warn_threshold_hit=tracker.warn_threshold_hit(),
        outcome_hint=outcome_hint,
    )


def _fraction(value: int, cap: int) -> float:
    if cap <= 0:
        return 0.0
    return min(1.0, max(0.0, float(value) / float(cap)))


__all__ = [
    "EVENT_NAME",
    "emit_from_tracker",
    "emit_planner_overhead",
]
