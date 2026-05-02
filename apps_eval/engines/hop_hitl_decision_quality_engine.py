"""HOP6 hitl_decision_quality — wraps HitlDecisionQualityEngine."""

from __future__ import annotations

from typing import Any


class HopHitlDecisionQualityEngine:
    """Adapter for stage 6 — HITL decision-quality assessment."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_eval.engines.hitl_decision_quality_engine import (
            HitlDecisionQualityEngine,
        )

        request = context.get("eval_request")
        scorecard = context.get("scorecard")
        regression = context.get("regression_result")

        engine = HitlDecisionQualityEngine()

        report: Any = None
        for method_name in ("score", "assess", "run", "execute"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    report = method(
                        request=request,
                        scorecard=scorecard,
                        regression=regression,
                    )
                    break
                except TypeError:
                    try:
                        report = method(request, scorecard, regression)
                        break
                    except TypeError:
                        try:
                            report = (
                                method(scorecard)
                                if scorecard is not None
                                else method()
                            )
                            break
                        except TypeError:
                            continue

        return {
            "hitl_quality_report": report,
            "hitl_decision_quality_completed": report is not None,
        }
