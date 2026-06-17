"""
apps_research Reasoning Toggles — feature flags for pipeline steps.

Aligned with the shared reasoning-toggle pattern used across app pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchReasoningToggles:
    """Feature flags controlling which pipeline steps are active."""

    enable_source_plan: bool = True
    enable_comparison_matrix: bool = True
    enable_epistemic_labeling: bool = True
    enable_source_register: bool = True
    enable_audience_targeting: bool = True
    enable_style_gate: bool = True
    enable_run_summary: bool = True
    llm_narrative_enabled: bool = False
    dry_run: bool = False


DEFAULT_TOGGLES = ResearchReasoningToggles()

__all__ = ["ResearchReasoningToggles", "DEFAULT_TOGGLES"]
