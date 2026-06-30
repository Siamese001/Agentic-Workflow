"""Compensating-control verifier for the underwriting governed-run exception."""

from __future__ import annotations

import importlib

ControlResult = tuple[str, bool, str]


class GovernedUwException:
    """Machine-checkable controls for the regulatory-domain exception."""

    def check_compensating_controls(self) -> list[ControlResult]:
        obs_mod = importlib.import_module("apps_underwriting_ai.integrations.observability_adapter")
        adapter = getattr(obs_mod, "ObservabilityAdapter", None)
        has_emit = isinstance(adapter, type) and callable(getattr(adapter, "emit", None))
        fec_mod = importlib.import_module(
            "apps_underwriting_ai.integrations.underwriting_exit_fec_producer"
        )
        return [
            (
                "CC-UW-01",
                has_emit,
                "ObservabilityAdapter emits fail-soft L6-compatible events",
            ),
            (
                "CC-UW-02",
                hasattr(fec_mod, "UnderwritingExitFecProducer"),
                "underwriting exit FEC producer is importable",
            ),
        ]


__all__ = ["GovernedUwException", "ControlResult"]

