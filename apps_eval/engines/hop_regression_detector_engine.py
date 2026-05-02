"""HOP5 regression_detector — wraps RegressionDetector."""

from __future__ import annotations

from typing import Any


class HopRegressionDetectorEngine:
    """Adapter for stage 5 — regression detection vs. baseline."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_eval.engines.regression_detector import RegressionDetector

        scorecard = context.get("scorecard")

        detector = RegressionDetector()

        result: Any = None
        for method_name in ("detect", "run", "execute", "compare"):
            method = getattr(detector, method_name, None)
            if callable(method):
                try:
                    result = (
                        method(scorecard) if scorecard is not None else method()
                    )
                    break
                except TypeError:
                    continue

        return {
            "regression_result": result,
            "regression_detector_completed": result is not None,
        }
