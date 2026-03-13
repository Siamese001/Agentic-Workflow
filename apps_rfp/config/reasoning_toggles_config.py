"""
apps_rfp Reasoning Toggles — feature flags for pipeline steps.

Aligned with apps_exec reasoning_toggles_config pattern.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RfpReasoningToggles:
    """Feature flags controlling which pipeline steps are active."""

    enable_industry_profiling: bool = True
    enable_roadmap_generation: bool = True
    enable_risk_matrix: bool = True
    enable_assumption_labeling: bool = True
    enable_value_case: bool = True
    enable_style_gate: bool = True
    enable_run_summary: bool = True
    enable_json_manifest: bool = True
    llm_narrative_enabled: bool = False
    dry_run: bool = False


DEFAULT_TOGGLES = RfpReasoningToggles()

__all__ = ["RfpReasoningToggles", "DEFAULT_TOGGLES"]
