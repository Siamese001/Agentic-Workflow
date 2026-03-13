"""
apps_eval Reasoning Toggles — feature flags for pipeline steps.

Aligned with apps_exec reasoning_toggles_config pattern.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalReasoningToggles:
    """Feature flags controlling which eval pipeline steps are active."""

    enable_scenario_runner: bool = True
    enable_scorecard: bool = True
    enable_regression_detection: bool = True
    enable_gate_validator: bool = True
    enable_scorecard_csv: bool = True
    enable_json_manifest: bool = True
    enable_run_summary: bool = True
    auto_update_baseline: bool = False
    dry_run: bool = False


DEFAULT_TOGGLES = EvalReasoningToggles()

__all__ = ["EvalReasoningToggles", "DEFAULT_TOGGLES"]
