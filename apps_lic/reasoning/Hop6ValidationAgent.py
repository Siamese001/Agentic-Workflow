"""CONSOLIDATED: HOP6ValidationAgent → HOPPipelineExecutor (2026-02-08).

DEPRECATED: This shim will be removed in a future release.
Import the canonical executor directly:
    from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor

This file is a backward-compatibility shim.
"""

import warnings

warnings.warn(
    "HOP6ValidationAgent is deprecated. Use HOPPipelineExecutor directly.",
    DeprecationWarning,
    stacklevel=2,
)

from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor as HOP6ValidationAgent

__all__ = ["HOP6ValidationAgent"]
