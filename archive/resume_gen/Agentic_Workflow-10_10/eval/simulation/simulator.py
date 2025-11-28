from __future__ import annotations

from typing import Any, Dict, List

from tools.simulation import Engine  # existing Phase-3 simulation harness

from .models import SimScenario, SimOutcome


def run_scenario(scenario: SimScenario) -> SimOutcome:
    """Run a high-level simulation scenario using the existing Engine.

    For now this is a thin wrapper around ``simulation.Engine.run_sync``.
    It executes the named scenario ``run_count`` times (if available) and
    aggregates the "golden_eval_score" metric from each run's outcome.
    Unknown scenario ids are treated as empty, yielding zeroed scores.
    """

    scores: List[float] = []
    safety_incidents = 0
    conflict_count = 0

    for _ in range(max(scenario.run_count, 1)):
        try:
            result: Dict[str, Any] = Engine.run_sync(scenario.id, overrides=scenario.initial_context)
        except Exception:  # pragma: no cover - defensive
            continue

        outcome = result.get("outcome") or {}
        score = float(outcome.get("golden_eval_score") or 0.0)
        scores.append(score)

        if not bool(outcome.get("safety_passed", True)):
            safety_incidents += 1

        # Heuristic: treat any correction iterations > 0 as a "conflict".
        if int(outcome.get("correction_iterations", 0) or 0) > 0:
            conflict_count += 1

    if scores:
        avg_score = sum(scores) / float(len(scores))
    else:
        avg_score = 0.0

    return SimOutcome(
        scenario_id=scenario.id,
        average_scores={"golden_eval_score": avg_score},
        safety_incidents=safety_incidents,
        agent_conflict_count=conflict_count,
    )



