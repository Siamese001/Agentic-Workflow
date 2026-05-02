"""HOP4 narrative_judge — wraps NarrativeJudgeScorer."""

from __future__ import annotations

from typing import Any


class HopNarrativeJudgeEngine:
    """Adapter for stage 4 — LLM-rubric narrative judging."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_eval.engines.narrative_judge_scorer import NarrativeJudgeScorer

        scenario_results = context.get("scenario_results")
        scorecard = context.get("scorecard")

        scorer = NarrativeJudgeScorer()

        verdicts: Any = None
        for method_name in ("score", "judge", "run", "execute"):
            method = getattr(scorer, method_name, None)
            if callable(method):
                try:
                    verdicts = method(
                        scenario_results=scenario_results, scorecard=scorecard
                    )
                    break
                except TypeError:
                    try:
                        verdicts = method(scenario_results, scorecard)
                        break
                    except TypeError:
                        try:
                            verdicts = (
                                method(scenario_results)
                                if scenario_results is not None
                                else method()
                            )
                            break
                        except TypeError:
                            continue

        return {
            "judge_verdicts": verdicts,
            "narrative_judge_completed": verdicts is not None,
        }
