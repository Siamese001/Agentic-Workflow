"""CONSOLIDATED: HOP1ProfileAnalysisAgent → HOPPipelineExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor as HOP1ProfileAnalysisAgent

__all__ = ["HOP1ProfileAnalysisAgent"]
