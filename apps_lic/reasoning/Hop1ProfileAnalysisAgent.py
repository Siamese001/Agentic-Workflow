"""CONSOLIDATED: HOP1ProfileAnalysisAgent → HOPPipelineExecutor (2026-02-08).

DEPRECATED: This shim will be removed in a future release.
Import the canonical executor directly:
    from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor

This file is a backward-compatibility shim.
"""

import warnings

warnings.warn(
    "HOP1ProfileAnalysisAgent is deprecated. Use HOPPipelineExecutor directly.",
    DeprecationWarning,
    stacklevel=2,
)

from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor as HOP1ProfileAnalysisAgent

__all__ = ["HOP1ProfileAnalysisAgent"]
