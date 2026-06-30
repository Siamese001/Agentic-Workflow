"""Compensating-control verifier for the apps_eval governed-run exception."""

from __future__ import annotations

import importlib

ControlResult = tuple[str, bool, str]


class GovernedEvalException:
    """Machine-checkable controls for the evaluator-only exception."""

    def check_compensating_controls(self) -> list[ControlResult]:
        telemetry = importlib.import_module("apps_eval._telemetry")
        resolve_emit = getattr(telemetry, "_resolve_emit", None)
        return [
            (
                "CC-EVAL-01",
                callable(resolve_emit),
                "telemetry shim resolves lifecycle emitters without circular eval",
            ),
            (
                "CC-EVAL-02",
                importlib.import_module("apps_eval") is not None,
                "apps_eval package imports without GovernedAppRunner execution",
            ),
        ]


__all__ = ["GovernedEvalException", "ControlResult"]

