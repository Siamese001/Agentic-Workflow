"""
apps_exec Reasoning Toggles — feature flags for pipeline steps.

Aligned with apps_rg reasoning_toggles_config pattern.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecReasoningToggles:
    """Feature flags controlling which pipeline steps are active."""

    enable_capability_extraction: bool = True
    enable_audience_classification: bool = True
    enable_style_gate: bool = True
    enable_evidence_anchoring: bool = True
    enable_why_this_matters_injection: bool = True
    enable_run_summary: bool = True
    enable_json_manifest: bool = True
    llm_narrative_enabled: bool = False
    dry_run: bool = False


DEFAULT_TOGGLES = ExecReasoningToggles()
