"""CONSOLIDATED: HOP3SenderGroundingAgent → HOPPipelineExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor as HOP3SenderGroundingAgent

__all__ = ["HOP3SenderGroundingAgent"]
