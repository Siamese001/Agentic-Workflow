"""CONSOLIDATED: HOP9IntegrationAgent → HOPPipelineExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor as HOP9IntegrationAgent

__all__ = ["HOP9IntegrationAgent"]
