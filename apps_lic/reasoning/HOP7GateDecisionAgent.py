"""CONSOLIDATED: HOP7GateDecisionAgent → HOPPipelineExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor as HOP7GateDecisionAgent

__all__ = ["HOP7GateDecisionAgent"]
