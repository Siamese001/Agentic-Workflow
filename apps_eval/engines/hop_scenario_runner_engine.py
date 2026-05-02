"""HOP2 scenario_runner — wraps ScenarioRunner."""

from __future__ import annotations

from typing import Any


class HopScenarioRunnerEngine:
    """Adapter for stage 2 — benchmark scenario execution."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_eval.engines.scenario_runner import ScenarioRunner

        request = context.get("eval_request")
        retrieved = context.get("retrieved_evaluations")

        runner = ScenarioRunner()

        results: Any = None
        for method_name in ("run", "execute", "run_scenarios"):
            method = getattr(runner, method_name, None)
            if callable(method):
                try:
                    results = method(request=request, retrieved=retrieved)
                    break
                except TypeError:
                    try:
                        results = method(request, retrieved)
                        break
                    except TypeError:
                        try:
                            results = (
                                method(request) if request is not None else method()
                            )
                            break
                        except TypeError:
                            continue

        return {
            "scenario_results": results,
            "scenario_runner_completed": results is not None,
        }
