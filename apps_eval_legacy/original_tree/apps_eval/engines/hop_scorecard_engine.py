"""HOP3 scorecard — wraps ScorecardEngine."""

from __future__ import annotations

from typing import Any


class HopScorecardEngine:
    """Adapter for stage 3 — weighted scorecard computation."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_eval.engines.scorecard_engine import ScorecardEngine

        scenario_results = context.get("scenario_results")

        engine = ScorecardEngine()

        scorecard: Any = None
        for method_name in ("compute", "run", "execute", "score"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    scorecard = (
                        method(scenario_results)
                        if scenario_results is not None
                        else method()
                    )
                    break
                except TypeError:
                    continue

        return {
            "scorecard": scorecard,
            "scorecard_completed": scorecard is not None,
        }
